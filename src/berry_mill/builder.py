"""
Module for building steps
"""
import os
import shutil
import tempfile
from urllib.parse import urlparse, quote
from typing import Dict, List
from platform import machine
import kiwi.logger
from typing_extensions import Unpack
from lxml import etree
from kiwi.exceptions import KiwiError, KiwiPrivilegesError, KiwiRootDirExists
from berry_mill.kiwiapp import KiwiAppLocal, KiwiAppBox
from .kiwrap import KiwiParent
from .params import KiwiBuildParams

log = kiwi.logging.getLogger('kiwi')

class KiwiBuilder(KiwiParent):
    """
    Main Class for Berrymill to prepare the kiwi-ng system (box)build calls
    """

    def __init__(self, descr:str, **kw: Unpack[KiwiBuildParams]):
        super().__init__(descr=descr,
                        profile=kw.get("profile", ""),
                        debug=kw.get("debug", False))
        
        self._params:KiwiBuildParams = kw

        if self._params.get("target_dir"):
            self._params["target_dir"] = self._params["target_dir"].rstrip("/")

        self._boxrootdir:str = os.path.join(self._appliance_path, "boxroot")
        log.debug(f"Using box root at {self._boxrootdir}")
        self._fcleanbox:bool = False
        # tmp boxroot dir only needed when build mode is not local
        if not self._params.get("local"):
            if not os.path.exists(self._boxrootdir):
                # flag for cleanup to remember to also delete boxroot dir if
                # it hasnt existed before already
                self._fcleanbox = True
                os.makedirs(self._boxrootdir)
                log.debug(f"No box root found at {self._boxrootdir}. Creating one")
            self._boxtmpkeydir:str = tempfile.mkdtemp(prefix="berrymill-keys-", dir=self._boxrootdir)
            self._boxtmpargdir:str = tempfile.mkdtemp(prefix="berrymill-args-", dir=self._boxrootdir)


    def _get_relative_file_uri(self, repo_key_path) -> str:
        """
        Change the file:// URIs in the repo key values to be relative to the boxroot
        """
        assert bool(self._boxtmpkeydir), "Key directory not available"
        assert bool(repo_key_path), "Key path not defined"

        return "file:///" + quote(os.path.join(os.path.basename(self._boxtmpkeydir), os.path.basename(repo_key_path)))


    def _write_repokeys_box(self, repos:Dict[str, Dict[str, str]]) -> bool:
        """
        Write repo keys from the self._tmp dir to the boxroot, so kiwi box can access the keys
        It expects a file:// uri to be present in repos[reponame][key]

        Returns True on success
        """
        assert bool(self._boxtmpkeydir), "Boxroot directory is not defined"

        for reponame in repos:
            k = repos.get(reponame, {}).get("key")
            parsed_url = urlparse(k)
            try:
                shutil.copy(str(parsed_url.path), self._boxtmpkeydir)
                repos.get(reponame, {})["key"] = self._get_relative_file_uri(parsed_url.path)
            except Exception as exc:
                log.warning(f"Failure while trying to copying the keyfile at {parsed_url.path}", exc_info= exc)
                return False
        return True
    
    def process(self) -> None:
        """
        Run builder. It supposed to be already within that directory (os.chdir).
        Directory is changed by the parent caller of the KiwiBuilder class.
        """
        try:
            config_tree = etree.parse(f"{self._appliance_descr}")
        except Exception as err:
            log.error(f"Failure while parsing appliance description", exc_info= err)
            return

        try:
            image_name:list = config_tree.xpath("//image/@name")
        except Exception as err:
            log.error(f"Failure while trying to extract image name", exc_info= err)
            return

        assert self._params.get("target_dir") is not None, log.warning("No Target Directory for built image files specified")

        target_dir = os.path.join(self._params.get("target_dir"), image_name[0])

        if self._kiwiparams.get("profile"):
            target_dir = os.path.join(target_dir, self._kiwiparams.get("profile"))

        # if target_dir exists with no --clean option, fail early.
        if not self._params.get("clean", False) and os.path.isdir(target_dir):
            raise Exception("Target directory already exists. Hint: use --clean option.")

        # parent directory should be writable
        if not os.access(os.path.dirname(target_dir), os.W_OK):
            raise Exception("Target directory's parent is not writable, please use writable directory")

        # options that are solely accepted by kiwi-ng
        kiwi_options = self._kiwi_options
        # options, solely accepted by box-build plugin
        box_options:List[str] = ["--box","ubuntu"]

        if self._kiwiparams.get("debug"):
            box_options.append("--box-debug")

        if self._params.get("cpu"):
            box_options = ["--cpu", self._params.get("cpu","")] + box_options

        if self._params.get("box_memory"):
            box_options += ["--box-memory", self._params.get("box_memory", "8G")]

        if machine() == "aarch64":
            box_options += ["--machine", "virt"]

        allow_no_accel:bool = True
        # TODO: When using cross, e.g. cpu param needs to be disabled
        if self._params.get("cross") and machine() == "x86_64":
            box_options += ["--aarch64", "--cpu", "cortex-a57", "--machine", "virt", "--no-accel"]
            kiwi_options += ["--target-arch", "aarch64"]
            allow_no_accel = False

        if self._params.get("no_accel") and allow_no_accel:
            box_options.append("--no-accel")

        if self._params.get("clean"):
            shutil.rmtree(target_dir, ignore_errors=True)

        if self._params.get("local"):
            command = ["kiwi-ng"] + kiwi_options\
                    + ["system", "build", "--description", "."]\
                    + ["--target-dir", target_dir] 
            try:
                log.info("Starting Kiwi for local build")            
                KiwiAppLocal(command, repos=self._repos).run()
            except KiwiPrivilegesError:
                log.error("Operation requires root privileges")
            except KiwiRootDirExists as exc:
                log.error(exc.message)
            except KiwiError as kiwierr:
                log.warning(f"KiwiError: {type(kiwierr).__name__} [{kiwierr.message}]")
                return
        else:
            if not self._write_repokeys_box(self._repos):
                return
            command = ["kiwi-ng"]+ kiwi_options\
                    + ["system", "boxbuild"] + box_options\
                    + ["--", "--description", '.'] + ["--target-dir", target_dir]\

            try:
                log.info("Starting Kiwi Box")
                KiwiAppBox(command, repos=self._repos, args_tmp_dir=self._boxtmpargdir).run()
            except KiwiError as kiwierr:
                log.warning(f"KiwiError:, {type(kiwierr).__name__}", exc_info= kiwierr)
                return

    def cleanup(self) -> None:
        """
        Cleanup the environment after the build
        """
        super().cleanup()
        if not self._initialized:
            log.info("Cleanup finished")
            return
        try:
            if not self._params.get("local"):
                shutil.rmtree(self._boxtmpkeydir, ignore_errors=True)
                shutil.rmtree(self._boxtmpargdir, ignore_errors=True)
                if self._fcleanbox:
                    # if Flag fcleanbox is true an empty boxroot is guranteed to exist
                    shutil.rmtree(self._boxrootdir, ignore_errors=True)
        except Exception as e:
            log.warning(f"Error: Cleanup Failed", exc_info= e)

        log.info("Cleanup finished")
