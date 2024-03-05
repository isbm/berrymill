"""
Interface Module to kiwi's boxbuidtaks
"""

from typing import List
from kiwi_boxed_plugin.tasks.system_boxbuild import SystemBoxbuildTask  # type: ignore
import kiwi.logger  # type: ignore
import kiwi.tasks.system_build  # type: ignore


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
    def __init__(self, repostring: str) -> None:
        super().__init__()
        self._repo_conf = repostring.split(' ')

    def _validate_kiwi_build_command(self) -> List[str]:
        # construct build command from given command line
        # forward appliance file name
        params = ['--kiwi-file', self.global_args['--kiwi-file']] 
        # add box build parameters
        params += super()._validate_kiwi_build_command()
        # add repository configuration
        params += self._repo_conf

        return params
