"""
Interafce Module for Kiwi Tasks (general)
"""
import os
import sys
import pathlib
from typing import Dict, List
from abc import ABC, abstractmethod

from berry_mill.boxbuild import BoxBuildTask
from berry_mill.localwrap import LocalBuildTask
from berry_mill.preparetask import PrepareTask


class KiwiApp(ABC):
    """
    Abstract Base Class
    Posing as a costum API for calling kiwi programmatically
    Functions as Interface between Berrymill and Kiwi-ng Wrappers
    """
    def __init__(self, argv: List[str], repos: Dict[str, Dict[str, str]]):
        self._repos = repos
        sys.argv = argv

    def _check_gnupg_dir(self) -> None:
        """
        creates $HOME/.gnupg directory for gpg key import check
        """
        pathlib.Path().home().joinpath(".gnupg").mkdir(exist_ok=True)

    @abstractmethod
    def run(self) -> None:
        """
        Abstract method for starting the KiwiTask
        """


class KiwiAppPrepare(KiwiApp):
    """
    Interface between Berrymill and Kiwi-ng Prepare Wrapper
    """
    def run(self) -> None:
        """
        create $HOME/.gnupg if needed and run prepare task
        """
        self._check_gnupg_dir()
        PrepareTask(self._repos).process()


class KiwiAppLocal(KiwiApp):
    """
    Interface between Berrymill and Kiwi-ng build Wrapper
    """
    def run(self) -> None:
        """
        create $HOME/.gnupg if needed and run local build task process
        """
        self._check_gnupg_dir()
        LocalBuildTask(self._repos).process()


class KiwiAppBox(KiwiApp):
    """
    Interface between Berrymill and Kiwi-ng boxbuild Wrapper
    """

    def __init__(self, argv: List[str], repos: Dict[str, Dict[str, str]], args_tmp_dir: str):
        super().__init__(argv, repos)

        self._tmpd = args_tmp_dir
        self._arg_file_name: str = "args.txt"
        self._arg_file_path: str = os.path.join(self._tmpd, self._arg_file_name)

    def run(self) -> None:

        repostring: str = self._generate_repo_string(self._repos)
        arg_file_path: str = self._get_relative_path()

        self._write_repo_string(repostring)
        BoxBuildTask(arg_file_path).process()

    def _get_relative_path(self) -> str:
        """
        Will return the os path to the .txt file
        containing the repo specific kiwi arguments,
        like --add-repo and --ignore-repos.

        The path will be relative the the boxroot in the
        appliances path
        """

        return os.path.join("/", os.path.basename(self._tmpd), self._arg_file_name)

    def _generate_repo_string(self, repos: Dict[str, Dict[str, str]]) -> str:
        """
        Accepts Repository Dict
        Generate and Return the kiwi compliant parameters
        to add repositories on the command line.
        """
        repo_build_options: List[str] = ["--ignore-repos"]

        for repo_name in repos:
            repo_content = repos.get(repo_name, dict())
            components: List[str] = repo_content.get("components", "/").split(',')
            for component in components:
                repo_build_options.append("--add-repo")
                # syntax of --add-repo value:
                # source,type,alias,priority,imageinclude,package_gpgcheck,{signing_keys},component,distribution,repo_gpgcheck
                repo_build_options.append(
                    f"{repo_content.get('url')}," +
                    f"{repo_content.get('type')}," +
                    f"{repo_name},,,," +
                    f"{{{repo_content.get('key')}}}," +
                    f"{component if component != '/' else ''}," +
                    f"{repo_content.get('name', '')}," +
                    "false"
                )

        return " ".join(repo_build_options)

    def _write_repo_string(self, repostring: str) -> None:
        """
        Write the required kiwi repo arguments in a .txt file under the boxroot
        This will avoid passing this long arg string on the command line.
        So there is no risk of running out of space for arg
        """

        with open(self._arg_file_path, "x") as f_rel:
            f_rel.write(repostring)
