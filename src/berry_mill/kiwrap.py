from __future__ import annotations

from typing import List, Set
from typing import TypedDict
from typing_extensions import Unpack
from lxml import etree
import os
import sys
import subprocess
import shutil
import tempfile
import requests
import inquirer
from platform import machine

from urllib.parse import urlparse, quote
from typing import Dict


class KiwiParams(TypedDict):
    """
    Dictionary for Kiwi Parameters

    Attributes:

        profile (str, Optional): select profile for images that makes use of it.
        box_memory (str, Default: 8G): specify main memory to use for the QEMU VM (box).
        debug (bool, Default: False): run in debug mode. This means the box VM stays open and the kiwi log level is set to debug(10).
        clean (bool, Default: False): cleanup previous build results prior build.
        cross (bool, Default: False): cross image build on x86_64 to aarch64 target.
        cpu (str, Optional): cpu to use for the QEMU VM (box)
        local (bool, Default: False): run build process locally on this machine. Requires sudo setup and installed KIWI toolchain.
        target_dir (str, Default:/var/tmp/IMAGE_NAME[.PROFILE_NAME]): store image results in given dirpath.
    """
    profile: str
    box_memory: str
    debug: bool
    clean: bool
    cross: bool
    cpu: str
    local: bool
    target_dir: str


class KiwiBuilder:
    """
    Kiwi wrapper for appliance builder.
    """
    # TODO handle TypeError
    def __init__(self, pth:str, descr:str, **kw: Unpack[KiwiParams]):
        self._repos:Dict[str, Dict[str, str]] = {}
        self._appliance_path:str = pth
        self._appliance_descr:str = descr
        self._params:Dict[KiwiParams] = kw

        if self._params.get("target_dir"):
            self._params["target_dir"] = self._params["target_dir"].rstrip("/")

        self._tmpdir = tempfile.mkdtemp(prefix="berrymill-keys-", dir="/tmp")
        
        self._fcleanbox = False
        # tmp boxroot dir only needed when build mode is not local
        if not self._params.get("local", False):
            boxdir = os.path.join(self._appliance_path, "boxroot")
            if not os.path.exists(boxdir):
                # flag for cleanup to remember to also delete boxroot dir if 
                # it hasnt existed before already
                self._fcleanbox = True
                os.makedirs(boxdir)
            self._boxtmpdir = tempfile.mkdtemp(prefix="berrymill-keys-",\
                                               dir= os.path.join(self._appliance_path, "boxroot"))

    def add_repo(self, reponame:str, repodata:Dict[str, str]) -> KiwiBuilder:
        """
        Add a repository for the builder
        """
        repodata.setdefault("key", "file://" + self._get_repokeys(reponame, repodata))
        self._check_repokey(repodata, reponame)
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
    
    def _get_relative_file_uri(self, repo_key_path) -> str:
        """
        Change the file:// URIs in the repo key values to be relative to the boxroot
        """
        return "file:///" + \
               quote( \
               os.path.join( \
               os.path.basename(self._boxtmpdir), os.path.basename(repo_key_path)))        
   
    def _check_repokey(self, repodata:Dict[str, str], reponame) -> None:
            k = repodata.get("key")
            # key can never be none due to .setdefault() in _get_repo_keys  
            parsed_url = urlparse(k)
            if not parsed_url.path:
                print("Berrymill was not able to retrieve a fitting gpg key")
                if os.path.exists("/etc/apt/trusted.gpg.d"):
                    print("Trusted keys found on system")
                    keylist:List[str] = os.listdir("/etc/apt/trusted.gpg.d")
                    selected = self._key_selection(reponame, keylist)
                    if selected:
                        repodata["key"] = "file://" + os.path.join("/etc/apt/trusted.gpg.d", selected)
                        self._check_repokey(repodata, reponame)
                        return
                #print(f"ERROR: key file path is empty for {reponame}")
                #self._cleanup()
                #sys.exit(1)
            if not os.path.exists(parsed_url.path):    
                print(f"ERROR: Failure while trying to handle the keyfile at {reponame}")
                print(f"{parsed_url.path if parsed_url.path else 'file://'} does not exist")
                self._cleanup()
                sys.exit(1)    

    def _write_repokeys_box(self, repos:Dict[str, Dict[str, str]]) -> None:
        """
        Write repo keys from the self._tmp dir to the boxroot, so kiwi box can access the keys
        It expects a file:// uri to be present in repos[reponame][key]
        """
        dst = self._boxtmpdir

        for reponame in repos.keys():
            k = repos.get(reponame, {}).get("key")
            parsed_url = urlparse(k)
            try:
                shutil.copy(parsed_url.path, dst)
            except Exception as exc:
                print(f"ERROR: Failure while trying to copying the keyfile at {parsed_url.path}")
                print(exc)
                self._cleanup()
                sys.exit(1)    
            repos.get(reponame, {})["key"] = self._get_relative_file_uri(parsed_url.path)

    def _cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        print("Cleaning up...")
        shutil.rmtree(self._tmpdir)
        if not self._params.get("local", False):
            shutil.rmtree(self._boxtmpdir)
            if self._fcleanbox:
                # if Flag fcleanbox is true an empty boxroot is guranteed to exist
                shutil.rmtree(os.path.join(self._appliance_path, "boxroot"))
        print("Finished")

    def _key_selection(self, reponame:str, options:List[str]) -> str | None:
        question = [
        inquirer.List("choice",
                  message="Choose the right key for {}:".format(reponame),
                  choices=options + ["none of the above"],
                  default="none of the above",
                  carousel=True
                  ),
        ]
        answer = inquirer.prompt(question)
        print("You selected:", answer["choice"])
        if answer["choice"] == "none of the above":
            return None
        return answer["choice"]

    
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

        if self._params.get("debug", False):
            kiwi_options.append("--debug")
            box_options.append("--box-debug")
        
        if self._params.get("cpu"):
            box_options = ["--cpu", self._params.get("cpu")] + box_options
        
        if self._params.get("box_memory"):
            box_options += ["--box-memory", self._params.get("box_memory")]
        
        if machine() == "aarch64":
            box_options += ["--machine", "virt"]
        
        # TODO: When using cross, e.g. cpu param needs to be disabled
        if self._params.get("cross") and machine() == "x86_64":
            box_options += ["--aarch64", "--cpu", "cortex-a57", "--machine", "virt", "--no-accel"]
            kiwi_options += ["--target-arch", "aarch64"]


        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            print("ERROR: Failure {} while parsing appliance description".format(err))
            sys.exit(1)
        
        try: 
            image_name:list = config_tree.xpath("//image/@name")
        except Exception as err:
            print("ERROR: Failure {} while trying to extract image name", err)
            sys.exit(1)
        
        target_dir = self._params.get("target_dir", "/var/tmp")
        target_dir += f"/{image_name[0]}"

        if self._params.get("profile"):
            profile = self._params.get("profile")
            profiles = config_tree.xpath("//profile/@name")
            if profile in profiles:
                kiwi_options += ["--profile", profile]
            else:
                raise Exception(f"\'{profile}\' is not a valid profile. Available: {profiles}")
        
        if self._params.get("clean", False):
            clean_target = target_dir
            if self._params.get("profile"):
                clean_target += f".{self._params.get('profile')}"
            if self._params.get("local", False):
                shutil.rmtree(clean_target)
        
        
        repo_build_options:List[str] = ["--ignore-repos"]

        if not self._params.get("local", False):
            self._write_repokeys_box(self._repos)

        for repo_name in self._repos.keys():
            repo_content = self._repos.get(repo_name)
            components = repo_content.get("components").split(',')
            for component in components:
                repo_build_options.append("--add-repo")
                # syntax of --add-repo value:
                # source,type,alias,priority,imageinclude,package_gpgcheck,{signing_keys},component,distribution,repo_gpgcheck
                repo_build_options += [f"{repo_content.get('url')},{repo_content.get('type')},{repo_name},,,,{{{repo_content.get('key')}}},{component if component != '/' else ''},{repo_content.get('name')},false"]
        
        if self._params.get("local", False):
            try:
                command = ["kiwi-ng"] + kiwi_options\
                        + ["system", "build", "--description", '.']\
                        + ["--target-dir", target_dir] + repo_build_options
                # for debugging, no usage of print() to ensure better readability of insanely long kiwi command with no confusion of important ',' chars
                # subprocess.run(["echo", "\""] + command + ["\""])
                subprocess.run(command)
            except Exception as exc:
                print(exc)
                sys.exit(1)     
        else:
            try:
                command = ["kiwi-ng"]+ kiwi_options\
                        + ["system", "boxbuild"] + box_options\
                        + ["--", "--description", '.'] + ["--target-dir", target_dir]\
                        + repo_build_options
                # subprocess.run(["echo", "\""] + command + ["\""])
                subprocess.run(command)
            except Exception as exc:
                print(exc)
                sys.exit(1)
            
                
        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")

        print(self._repos)

        self._cleanup()
