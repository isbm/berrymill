from kiwi_boxed_plugin.tasks.system_boxbuild import SystemBoxbuildTask
import logging
import os
from docopt import docopt
from typing import List
import kiwi.tasks.system_build


log = logging.getLogger('kiwi')


class WrapperSystemBoxbuildTask(SystemBoxbuildTask):

    def __init__(self, arg_file_pth: str):
        super().__init__()
        self._arg = arg_file_pth

    def _validate_kiwi_build_command(self) -> List[str]:
        # NOTE: mainly copied from parent class!!
        # construct build command from given command line
        kiwi_build_command = [
            'system', 'build'
        ]
        kiwi_build_command += self.command_args.get(
            '<kiwi_build_command_args>'
        )
        if '--' in kiwi_build_command:
            kiwi_build_command.remove('--')
        # validate build command through docopt from the original
        # kiwi.tasks.system_build docopt information
        log.info(
            'Validating kiwi_build_command_args:{0}    {1}'.format(
                os.linesep, kiwi_build_command
            )
        )
        validated_build_command = docopt(
            doc=kiwi.tasks.system_build.__doc__,
            argv=kiwi_build_command
        )
        # rebuild kiwi build command from validated docopt parser result
        kiwi_build_command = [
            'system', 'build'
        ]
        for option, value in validated_build_command.items():
            if option.startswith('-') and value:
                if isinstance(value, bool):
                    kiwi_build_command.append(option)
                elif isinstance(value, str):
                    kiwi_build_command.extend([option, value])
                elif isinstance(value, list):
                    for element in value:
                        kiwi_build_command.extend([option, element])
        final_kiwi_build_command = []
        if self.global_args.get('--debug'):
            final_kiwi_build_command.append('--debug')
        if self.global_args.get('--type'):
            final_kiwi_build_command.append('--type')
            final_kiwi_build_command.append(self.global_args.get('--type'))
        if self.global_args.get('--profile'):
            for profile in sorted(set(self.global_args.get('--profile'))):
                final_kiwi_build_command.append('--profile')
                final_kiwi_build_command.append(profile)
        final_kiwi_build_command += kiwi_build_command

        # injected code
        #----------------------------------------------------------- 
        final_kiwi_build_command.append('--berrymill')
        final_kiwi_build_command.append(self._arg)
        #-----------------------------------------------------------

        log.info(
            'Building with:{0}    {1}'.format(
                os.linesep, final_kiwi_build_command
            )
        )
        return final_kiwi_build_command