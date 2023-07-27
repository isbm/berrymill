from __future__ import annotations

import os
import shutil
import tempfile
import requests

from urllib.parse import urlparse
from typing import Dict


class KiwiBuilder:
    """
    Kiwi wrapper for appliance builder.
    """
    def __init__(self, pth:str, descr:str):
        self._repos:Dict[str, Dict[str, str]] = {}
        self._appliance_path:str = pth
        self._appliance_descr:str = descr
        self._tmpdir = tempfile.mkdtemp(prefix="berrymill-keys-", dir="/tmp")

    def add_repo(self, reponame:str, repodata:Dict[str, str]) -> KiwiBuilder:
        """
        Add a repository for the builder
        """
        repodata["key"] = "file://" + self._get_repokeys(reponame, repodata)
        self._repos[reponame] = repodata
        return self

    def _get_repokeys(self, reponame, repodata:Dict[str, str]) -> str:
        """
        Download repository keys to a temporary directory
        """
        url = urlparse(repodata["url"])
        g_path:str = f"{self._tmpdir}/{reponame}_release.key"
        if repodata.get("components", "/") != "/":
            s_url = f"{url.scheme}://{url.netloc}{os.path.join(url.path, 'dists', repodata['name'])}"
            # TODO: grab standard keys
            g_path = ""
        else:
            s_url = f"{url.scheme}://{url.netloc}{os.path.join(url.path, 'Release.key')}"
            response = requests.get(s_url, allow_redirects=True)
            with open(g_path, "wb") as f_rel:
                f_rel.write(response.content)
            response.close()

        return g_path

    def _cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        print("Cleaning up...")
        shutil.rmtree(self._tmpdir)
        print("Finished")

    def build(self) -> None:
        """
        Run builder. It supposed to be already within that directory (os.chdir).
        Directory is changed by the parent caller of the KiwiBuilder class.
        """

        print("Using appliance \"{}\" located at \"{}\"".format(self._appliance_descr, self._appliance_path))

        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")

        print(self._repos)

        self._cleanup()
