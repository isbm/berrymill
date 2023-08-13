from __future__ import annotations

from typing import List, Set
from lxml import etree
import os
import sys
import subprocess
import shutil
import tempfile
import requests

from urllib.parse import urlparse
from typing import Dict


class KiwiBuilder:
    """
    Kiwi wrapper for appliance builder.
    """
    def __init__(self, pth:str, descr:str, profile:str="", box_memory:str="", debug:bool=False, clean:bool=False, cross:bool=False, cpu:str="", arch:str="x86_64", local:bool=False, target_dir:str="/tmp"):
        self._repos:Dict[str, Dict[str, str]] = {}
        self._appliance_path:str = pth
        self._appliance_descr:str = descr
        self._local:bool = local
        self._profile:str = profile
        self._box_mem:str = box_memory
        self._debug:bool = debug
        self._clean:bool = clean
        self._cpu:str = cpu
        self._cross:bool = cross
        self._arch:str = arch

        if target_dir.endswith("/"):
            target_dir = target_dir.removesuffix("/")
        if target_dir.find(" ") != -1:
            print("ERROR: target directory contains at least one space ' '")
            sys.exit(1)

        self._target_dir = target_dir
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
        # options that are solely accepted by kiwi-ng
        kiwi_options = []

        # options, solely accepted by box-build plugin
        box_options:List[str] = ["--box","ubuntu"]

        if self._debug:
            kiwi_options.append("--debug")
            box_options.append("--box-debug")
        
        if len(self._cpu) > 0:
            box_options.insert(0, "--cpu")
            box_options.insert(1, self._cpu)
        
        if len(self._box_mem) > 0:
            box_options.append("--box-memory")
            box_options.append(self._box_mem)
        
        if self._arch == "aarch64":
            box_options.append("--machine")
            box_options.append("virt")
        
        if self._cross and self._arch == "x86_64":
            box_options.append("--aarch64")
            box_options.append("--cpu")
            box_options.append("cortex-a57")
            box_options.append("--machine")
            box_options.append("virt")
            box_options.append("--no-accel")

            kiwi_options.append("--target-arch")
            kiwi_options.append("aarch64")


        try:
            config_tree = etree.parse(f"{self._appliance_path}/{self._appliance_descr}")
        except Exception as exc:
            print("ERROR: while trying to parse image description")
            sys.exit(1)
        
        try: 
            image_name:list = config_tree.xpath("//image/@name")
        except Exception as exc:
            print("ERROR: while trying to extract image name")
            sys.exit(1)
        
        self._target_dir += f"/{image_name[0]}"

        if len(self._profile) > 0:
            profiles = config_tree.xpath("//profile/@name")
            # TODO handle multiple profiles exist problem
            print(profiles)
        
        if self._clean:
            clean_target = self._target_dir
            if len(self._profile) > 0:
                clean_target += f".{self._profile}"
            if self._local:
                subprocess.run(["sudo", "rm", "-rf", clean_target])
        
        
        repo_build_options:List[str] = ["--ignore-repos"]
        alias = "repo1"
        for repo in self._repos:
            repo_build_options.append("--add-repo")
            # source,type,alias,priority,imageinclude,package_gpgcheck,{signing_keys},components,distribution,repo_gpgcheck
            repo_build_options.append(f"{self._repos[repo].get('url')},apt-deb,{repo},,,,{{{self._repos[repo].get('key')}}},{self._repos[repo].get('components').replace(',',' ')},{self._repos[repo].get('name')},false")
            alias += "1"
        
        if self._local:
            try:
                command = ["kiwi-ng"] + kiwi_options + ["system", "build"] + ["--description"] + [self._appliance_path] + ["--target-dir"] + [self._target_dir] + repo_build_options

                subprocess.run(command)
            except Exception as exc:
                print(command)
                print("ERROR: while calling kiwi in local mode")
                sys.exit(1)     
        else:
            try:
                command = ["kiwi-ng"]+ kiwi_options + ["system", "boxbuild"] + box_options + ["--"]+ ["--description"] + [self._appliance_path] + ["--target-dir"] + [self._target_dir] + repo_build_options
                subprocess.run(["echo", "\""] + command + ["\""])
                # subprocess.run(command)
            except Exception as exc:
                print(command)
                print("ERROR: while calling kiwi in boxbuild mode")
                sys.exit(1)
            
                
        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")

        print(self._repos)

        self._cleanup()
