from __future__ import annotations

import os
import shutil
import tempfile
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
        repodata["key"] = self._get_repokeys(repodata["url"])
        self._repos[reponame] = repodata
        return self

    def _get_repokeys(self, url:str) -> str:
        """
        Download repository keys to a temporary directory
        """

        return f"file://{self._tmpdir}/somekey.gpg"

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
