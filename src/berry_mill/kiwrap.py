from __future__ import annotations
from abc import abstractmethod

from typing import List
from typing_extensions import Unpack
import os
import sys
import shutil
import tempfile
import requests
import inquirer
from lxml import etree
from urllib.parse import ParseResult, urlparse
from typing import Dict

from berry_mill.params import KiwiParams


class KiwiParent:
    def __init__(self, descr:str, **pkw: Unpack[KiwiParams]):
        self._repos:Dict[str, Dict[str, str]] = {}
        self._appliance_path:str = os.getcwd()
        self._appliance_descr:str = descr

        self._trusted_gpg_d:str = "/etc/apt/trusted.gpg.d"

        self._tmpdir:str = tempfile.mkdtemp(prefix="berrymill-keys-", dir="/tmp")

        self._kiwiparams:Dict[KiwiParams] = pkw

        self._kiwi_options:List[str] = []

        self._initialized:bool = False

        if self._kiwiparams.get("debug", False):
            self._kiwi_options.append("--debug")

        print("Using appliance \"{}\" located at \"{}\"".format(self._appliance_descr, self._appliance_path))

        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            print("ERROR: Failure {} while parsing appliance description".format(err))
            sys.exit(1)

        try:
            profiles = config_tree.xpath("//profile/@name")
        except Exception as err:
            print("ERROR: Failure {} while trying to extract profile names", err)
            self.cleanup()
            sys.exit(1)


        if not self._kiwiparams.get("profile") and profiles:
            print("No Profile selected.")
            print("Please select one of the available following profiles using --profile:")
            print(profiles)
            self.cleanup()
            sys.exit(1)

        if self._kiwiparams.get("profile"):
            profile = self._kiwiparams.get("profile")
            if profile in profiles:
                self._kiwi_options += ["--profile", profile]
            else:
                self.cleanup()
                print(f"\'{profile}\' is not a valid profile. Available: {profiles}")
                sys.exit(1)

        self._initialized = True
    
    def add_repo(self, reponame:str, repodata:Dict[str, str]) -> KiwiParent:
        """
        Add a repository for the builder
        """
        if reponame:
            repodata.setdefault("key", "file://" + self._get_repokeys(reponame, repodata))
            self._check_repokey(repodata, reponame)
            self._repos[reponame] = repodata
        else:
            print("Repository name not defined")
            self.cleanup()
            sys.exit(1)

        return self

    def _get_repokeys(self, reponame: str, repodata:Dict[str, str]) -> str:
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
        g_path:str = os.path.join(self._tmpdir, f"{reponame}_release.key")

        if repodata.get("components", "/") != "/":
            s_url: str = os.path.join(url.scheme + "://" + url.netloc, url.path, 'dists', repodata['name'])
            # TODO: grab standard keys
            g_path = ""
            return g_path
        else:
            s_url: str = os.path.join(url.scheme + "://" + url.netloc, url.path, 'Release.key')
            response = requests.get(s_url, allow_redirects=True)
            with open(g_path, "wb") as f_rel:
                f_rel.write(response.content)
            response.close()
            return g_path
    def _check_repokey(self, repodata:Dict[str, str], reponame) -> None:
        if not repodata.get("key"):
            raise Exception("Path to the key is not defined")
        parsed_url = urlparse(repodata.get("key"))
        if not parsed_url.path:
            print("Berrymill was not able to retrieve a fitting gpg key")
            if os.path.exists(self._trusted_gpg_d):
                keylist:List[str] = os.listdir(self._trusted_gpg_d)
                selected = self._key_selection(reponame, keylist)
                if selected:
                    repodata["key"] = ParseResult(scheme="file",
                                                path=os.path.join(self._trusted_gpg_d, selected),
                                                params=None, query=None, fragment=None,
                                                netloc=None).geturl()
                    self._check_repokey(repodata, reponame)
                    return
            else:
                print("Trusted key not foud on system")
        if not os.path.exists(parsed_url.path):
            self.cleanup()
            Exception(parsed_url.path + " does not exist" if parsed_url.path else f"key file path not specified for {reponame}")

    def _key_selection(self, reponame:str, options:List[str]) -> str | None:
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
        print("You selected:", answer["choice"])

        return answer["choice"] != none_of_above and answer["choice"] or None
    
    def cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        print("Cleaning up...")
        try:
            shutil.rmtree(self._tmpdir)
        except Exception as e:
            print(f"Error: Cleanup Failed : {e}")

    @abstractmethod
    def process(self) -> None:
        raise NotImplementedError()


