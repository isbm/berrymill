from __future__ import annotations
from abc import abstractmethod
import sys
import kiwi.logger
from typing import Any, List
from typing_extensions import Unpack
import os
import shutil
import tempfile
import requests
import inquirer
from lxml import etree
from urllib.parse import ParseResult, urljoin, urlparse
from typing import Dict

from berry_mill.params import KiwiParams

log = kiwi.logging.getLogger('kiwi')


class KiwiParent:
    """
    Base Class for Kiwi Tasks, such as build and prepare.
    Implements shared functionality needed for all children
    such as repository and global kiwi params handling
    """

    def __init__(self, descr: str, **pkw: Unpack[KiwiParams]):
        self._repos: Dict[str, Dict[str, str]] = {}
        self._appliance_path: str = os.getcwd()
        self._appliance_descr: str = descr
        self._trusted_gpg_d: str = "/etc/apt/trusted.gpg.d"
        self._tmpdir: str = tempfile.mkdtemp(prefix="berrymill-keys-", dir="/tmp")
        self._kiwiparams: KiwiParams = pkw
        self._kiwi_options: List[str] = []
        self._initialized: bool = False

        if self._kiwiparams.get("debug"):
            self._kiwi_options.append("--debug")

        log.info("Using appliance \"{}\" located at \"{}\"".format(self._appliance_descr, self._appliance_path))
        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            log.warning("Failure while parsing appliance description", exc_info=err)
            self.cleanup()
            sys.exit(1)

        try:
            profiles = config_tree.xpath("//profile/@name")
        except Exception as err:
            log.warning("Failure while trying to extract profile names", exc_info=err)
            self.cleanup()
            sys.exit(1)

        if self._kiwiparams.get("profile") is None and profiles:
            log.error("No Profile selected.")
            log.warning(f"Please select one of the available following profiles using --profile:\n{profiles}")
            self.cleanup()
            sys.exit(1)

        if self._kiwiparams.get("profile"):
            profile = self._kiwiparams.get("profile", "")
            if profile in profiles:
                self._kiwi_options += ["--profile", profile]
            else:
                self.cleanup()
                log.error(f"\'{profile}\' is not a valid profile. Available: {profiles}")
                sys.exit(1)

        self._initialized = True

    def add_repo(self, reponame: str, repodata: Dict[str, str]) -> KiwiParent:
        """
        Add a repository for the builder
        """
        if reponame:
            repodata.setdefault("key", "file://" + self._get_repokeys(reponame, repodata))
            self._check_repokey(repodata, reponame)
            self._repos[reponame] = repodata
        else:
            log.error("Repository name not defined")
            self.cleanup()
            sys.exit(1)

        return self

    def _get_repokeys(self, reponame: str, repodata: Dict[str, str]) -> str:
        """
        Download repository keys to a temporary directory
        """
        # Check if repo name and date are defined
        for repo_iter, excep_iter in [(repodata, "Repository data not defined"),
                                      (reponame, "Repository name not defined"),
                                      (repodata.get('url'), "URL not found")]:
            if not repo_iter:
                raise Exception(excep_iter)

        url: ParseResult = urlparse(repodata["url"])
        g_path: str = os.path.join(self._tmpdir, f"{reponame}_release.key")
        s_url: str = ""
        if repodata.get("components", "/") != "/":
            s_url = urljoin(f"{url.scheme}://{url.netloc}/{url.path}/dists/{repodata['name']}", "")
            # TODO: grab standard keys
            g_path = ""
            return g_path
        else:
            s_url = urljoin(f"{url.scheme}://{url.netloc}/{url.path}/Release.key", "")
            response = requests.get(s_url, allow_redirects=True)
            with open(g_path, 'xb') as f_rel:
                f_rel.write(response.content)
            response.close()
            return g_path

    def _check_repokey(self, repodata: Dict[str, str], reponame) -> None:

        assert len(repodata.get("key", "")) > 0, log.warning("Path to the key is not defined")

        parsed_url = urlparse(repodata.get("key"))
        if not parsed_url.path:
            log.warning("Berrymill was not able to retrieve a fitting gpg key")
            if os.path.exists(self._trusted_gpg_d):
                keylist: List[str] = os.listdir(self._trusted_gpg_d)
                selected = self._key_selection(reponame, keylist)
                if selected:
                    repodata["key"] = ParseResult(scheme="file",
                                                  path=os.path.join(self._trusted_gpg_d, selected),
                                                  params="", query="", fragment="",
                                                  netloc="").geturl()
                    self._check_repokey(repodata, reponame)
                    return
            else:
                log.warning("Trusted key not found on system")
        if not os.path.exists(parsed_url.path):
            raise SystemExit(f"key file path wrong for repository {reponame}")

    def _key_selection(self, reponame: str, options: List[str]) -> str | None:
        none_of_above = "none of the above"
        question = [
            inquirer.List("choice",
                          message="Choose the right key for {}:".format(reponame),
                          choices=options + [none_of_above],
                          default=none_of_above,
                          carousel=True
                          ),
        ]
        answer = inquirer.prompt(question)
        log.info("You selected:", answer["choice"])

        return answer["choice"] != none_of_above and answer["choice"] or None

    def cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        log.info("Cleaning up...")
        try:
            shutil.rmtree(self._tmpdir)
        except Exception as e:
            log.warning(f"Cleanup Failed", exc_info=e)

    @abstractmethod
    def process(self) -> None:
        raise NotImplementedError()
