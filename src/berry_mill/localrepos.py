"""
Find out local repos of the current distro.
"""

from abc import ABCMeta, abstractmethod
from typing import List


class Repodata:
    def __init__(self) -> None:
        self.type: str = ""
        self.components: List[str] = []
        self.url: str = ""
        self.trusted: bool = False
        self.name: str = ""


class BaseRepofind(metaclass=ABCMeta):
    """
    Repofind mixin
    """

    @abstractmethod
    def get_repos(self) -> List[str]:
        """
        Return list of repositories
        """


class DebianRepofind(BaseRepofind):
    """
    Debian repositories
    """
    def _get_sources_list(self) -> List[str]:
        """
        Return repositories
        """
        with open("/etc/apt/sources.list") as sl:
            for l in [x.strip() for x in sl.readlines() if x and not x.strip().startswith("#")]:
                print(">>>", l)

        return ["x"]

    def _get_sources_list_d(self) -> List[str]:
        """
        """
        return []

    def get_repos(self) -> List[str]:
        """
        Return all local repositories
        """
        return self._get_sources_list() + self._get_sources_list_d()