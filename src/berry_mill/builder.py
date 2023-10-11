from __future__ import annotations

from typing import List
from typing_extensions import Unpack
from lxml import etree
import os
import sys
import shutil
import tempfile

from urllib.parse import urlparse, quote
from typing import Dict
from berry_mill.kiwiapp import KiwiAppLocal, KiwiAppBox
from kiwi.kiwi import KiwiError
from platform import machine
from berry_mill.kiwrap import KiwiParent

from berry_mill.params import KiwiBuildParams, KiwiParams



class KiwiBuilder(KiwiParent):
    """
    Main Class for Berrymill to prepare the kiwi-ng system (box)build calls
    """
    # TODO handle TypeError
    def __init__(self, descr:str, **kw: Unpack[KiwiBuildParams]):
        self._params:Dict[KiwiBuildParams] = kw
        
        super().__init__(descr=descr,
                        profile=self._params.get("profile"),
                        debug=self._params.get("debug", False))

        if self._params.get("target_dir"):
            self._params["target_dir"] = self._params["target_dir"].rstrip("/")

        self._boxrootdir:str = os.path.join(self._appliance_path, "boxroot")
        print(self._boxrootdir)
        self._fcleanbox:bool = False
        # tmp boxroot dir only needed when build mode is not local
        if not self._params.get("local", False):
            boxdir:str = os.path.join(self._appliance_path, "boxroot")
            if not os.path.exists(boxdir):
                # flag for cleanup to remember to also delete boxroot dir if
                # it hasnt existed before already
                self._fcleanbox = True
                os.makedirs(boxdir)

            self._boxtmpkeydir:str = tempfile.mkdtemp(prefix="berrymill-keys-", dir= self._boxrootdir)

            self._boxtmpargdir:str = tempfile.mkdtemp(prefix="berrymill-args-", dir= self._boxrootdir)


    def _get_relative_file_uri(self, repo_key_path) -> str:
        """
        Change the file:// URIs in the repo key values to be relative to the boxroot
        """
        if not self._boxtmpkeydir:
            raise Exception("Key directory not available")
        if not repo_key_path:
            raise Exception("Key path not defined")
        return "file:///" + \
               quote( \
               os.path.join( \
               os.path.basename(self._boxtmpkeydir), os.path.basename(repo_key_path)))


    def _write_repokeys_box(self, repos:Dict[str, Dict[str, str]]) -> None:
        """
        Write repo keys from the self._tmp dir to the boxroot, so kiwi box can access the keys
        It expects a file:// uri to be present in repos[reponame][key]
        """
        dst = self._boxtmpkeydir
        if not dst:
            raise Exception("ERROR: Boxroot directory is not defined")

        for reponame in repos:
            k = repos.get(reponame, {}).get("key")
            parsed_url = urlparse(k)
            try:
                shutil.copy(parsed_url.path, dst)
            except Exception as exc:
                print(f"ERROR: Failure while trying to copying the keyfile at {parsed_url.path}")
                print(exc)
                return
            repos.get(reponame, {})["key"] = self._get_relative_file_uri(parsed_url.path)

    def process(self) -> None:
        """
        Run builder. It supposed to be already within that directory (os.chdir).
        Directory is changed by the parent caller of the KiwiBuilder class.
        """
        # options that are solely accepted by kiwi-ng
        kiwi_options = self._kiwi_options
        # options, solely accepted by box-build plugin
        box_options:List[str] = ["--box","ubuntu"]

        if self._kiwiparams.get("debug", False):
            box_options.append("--box-debug")

        if self._params.get("cpu"):
            box_options = ["--cpu", self._params.get("cpu")] + box_options

        if self._params.get("box_memory"):
            box_options += ["--box-memory", self._params.get("box_memory")]

        if machine() == "aarch64":
            box_options += ["--machine", "virt"]

        allow_no_accel:bool = True
        # TODO: When using cross, e.g. cpu param needs to be disabled
        if self._params.get("cross") and machine() == "x86_64":
            box_options += ["--aarch64", "--cpu", "cortex-a57", "--machine", "virt", "--no-accel"]
            kiwi_options += ["--target-arch", "aarch64"]
            allow_no_accel = False

        if self._params.get("accel", False) and allow_no_accel:
            box_options.append("--no-accel")

        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            print("ERROR: Failure {} while parsing appliance description".format(err))
            return

        try:
            image_name:list = config_tree.xpath("//image/@name")
        except Exception as err:
            print("ERROR: Failure {} while trying to extract image name", err)
            return

        target_dir = os.path.join(
            self._params.get("target_dir","/tmp"),\
            f"{image_name[0]}.{self._kiwiparams.get('profile', '')}")

        if self._params.get("clean", False):
            clean_target = target_dir
            if self._params.get("profile"):
                clean_target += f".{self._params.get('profile')}"
            if self._params.get("local", False):
                shutil.rmtree(clean_target)

        if not self._params.get("local", False):
            self._write_repokeys_box(self._repos)

        if self._params.get("local", False):
            command = ["kiwi-ng"] + kiwi_options\
                    + ["system", "build", "--description", "."]\
                    + ["--target-dir", target_dir] 

            try:
                print("Starting Kiwi for local build")                
                KiwiAppLocal(command, repos=self._repos).run()
            except KiwiError as kiwierr:
                print("KiwiError:", type(kiwierr).__name__)
                print(kiwierr)
                return
        else:
            command = ["kiwi-ng"]+ kiwi_options\
                    + ["system", "boxbuild"] + box_options\
                    + ["--", "--description", '.'] + ["--target-dir", target_dir]\

            try:
                print("Starting Kiwi Box")
                KiwiAppBox(command, repos=self._repos, args_tmp_dir=self._boxtmpargdir).run()
            except KiwiError as kiwierr:
                print("KiwiError:", type(kiwierr).__name__)
                print(kiwierr)
                return

        # run kiwi here with "appliance_init" which is a ".kiwi" file
        os.system("ls -lah")

        print(self._repos)



    def cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        super().cleanup()
        if not self._initialized:
            print("Cleanup finished")
            return
        try:
            if not self._params.get("local", False):
                if os.path.exists(self._boxtmpkeydir):
                    shutil.rmtree(self._boxtmpkeydir)
                if os.path.exists(self._boxtmpargdir):
                    shutil.rmtree(self._boxtmpargdir)
                if self._fcleanbox:
                    # if Flag fcleanbox is true an empty boxroot is guranteed to exist
                    shutil.rmtree(os.path.join(self._appliance_path, "boxroot"))
        except Exception as e:
            print(f"Error: Cleanup Failed : {e}")

        print("Cleanup finished")
