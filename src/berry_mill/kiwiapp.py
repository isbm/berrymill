import os
import sys
from typing import Dict, List
from berry_mill.boxwrap import WrapperSystemBoxbuildTask

from berry_mill.localwrap import WrapperSystemBuildTask

class KiwiApp:
    
    def __init__(self, argv:List[str], repos:Dict[str, Dict[str,str]]):
        self._repos = repos
        sys.argv = argv

    def run(self) -> None:
        pass


class KiwiAppLocal(KiwiApp):
    
    def run(self) -> None:
        WrapperSystemBuildTask().run(self._repos)


class KiwiAppBox(KiwiApp):
    
    def __init__(self, argv:List[str], repos:Dict[str, Dict[str,str]], args_tmp_dir:str = None):
        super().__init__(argv, repos)

        self._tmpd = args_tmp_dir
        self._arg_file_name:str = "args.txt"
        self._arg_file_path: str = os.path.join(self._tmpd, self._arg_file_name)
    
    def run(self) -> None:

        self._write_repo_string(
            self._generate_repo_string(self._repos)
        )
        WrapperSystemBoxbuildTask(
            arg_file_pth=self._get_relative_path()
        ).process()

    def _get_relative_path(self) -> str:
        
        return os.path.join("/",os.path.basename(self._tmpd), self._arg_file_name)
    
    def _generate_repo_string(self, repos:Dict[str, Dict[str,str]]) -> str:

        repo_build_options:List[str] = ["--ignore-repos"]

        for repo_name in repos:
            repo_content = repos.get(repo_name)
            components = repo_content.get("components", "/").split(',')
            for component in components:
                repo_build_options.append("--add-repo")
                # syntax of --add-repo value:
                # source,type,alias,priority,imageinclude,package_gpgcheck,{signing_keys},component,distribution,repo_gpgcheck
                repo_build_options += [
                    f"{repo_content.get('url')}," +\
                    f"{repo_content.get('type')}," +\
                    f"{repo_name},,,,"+\
                    f"{{{repo_content.get('key')}}}," +\
                    f"{component if component != '/' else ''}," +\
                    f"{repo_content.get('name', '')}," +\
                    "false"
                    ]
                
        return " ".join(repo_build_options)

    def _write_repo_string(self, repostring:str) -> None:

        with open(self._arg_file_path, "x") as f_rel:
            f_rel.write(repostring)
