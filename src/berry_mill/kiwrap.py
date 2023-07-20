from __future__ import annotations

from typing import List, Set
import os


class KiwiBuilder:
    """
    Kiwi wrapper for appliance builder.
    """
    def __init__(self, pth:str, descr:str):
        self._repos:Set[str] = set()
        self._appliance_path:str = pth
        self._appliance_descr:str = descr

    def add_repo(self, repo:str) -> KiwiBuilder:
        """
        Add a repository for the builder
        """
        self._repos.add(repo)
        return self

    def build(self) -> None:
        """
        Run builder. It supposed to be already within that directory (os.chdir).
        Directory is changed by the parent caller of the KiwiBuilder class.
        """

        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")
