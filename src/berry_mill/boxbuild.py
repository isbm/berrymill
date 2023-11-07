"""
Interface Module to kiwi's boxbuidtaks
"""

from typing import List
from kiwi_boxed_plugin.tasks.system_boxbuild import SystemBoxbuildTask
import kiwi.logger
import kiwi.tasks.system_build


log = kiwi.logging.getLogger('kiwi')

class BoxBuildTask(SystemBoxbuildTask):
    """
    Wrapper Class
    Overwrites self._validate_kiwi_build_command(...).
    The method is mostly copied from the Base Class
    Only Code to add --berrymill parameter is added.
    The value of the --berrymill parameter will be the temporary path
    to the repository arguments.
    
    The Box will parse this, read the .txt file
    and call kiwi accordingly
    """
    def __init__(self, arg_file_pth: str) -> None:
        super().__init__()
        self._arg = arg_file_pth

    def _validate_kiwi_build_command(self) -> List[str]:
        # construct build command from given command line
        return super()._validate_kiwi_build_command() + ["--berrymill", self._arg]