import sys
import os
import argparse
import shutil
from tempfile import mkdtemp
from typing import Tuple
import kiwi.logger
import yaml

from berry_mill.imgdescr.loader import Loader
from berry_mill.kiwrap import KiwiParent

from .cfgh import ConfigHandler, Autodict
from .localrepos import DebianRepofind
from .sysinfo import get_local_arch
from .preparer import KiwiPreparer
from .builder import KiwiBuilder
from .sysinfo import has_virtualization, is_vm

log = kiwi.logging.getLogger('kiwi')
log.set_color_format()

no_nested_warning: str = str(
    """
    Nested virtualization is NOT enabled. This can cause the build to fail
    as a virtual enviroment using qemu is utilized to build the image.

    You can either:
    Enable nested virtualization or build locally
    """
)


class ImageMill:
    """
    ImageMill class
    """
    def __init__(self):
        """
        Constructor
        """
        # Display just help if run alone
        if len(sys.argv) == 1:
            sys.argv.append("--help")

        p: argparse.ArgumentParser = argparse.ArgumentParser(
            prog="berrymill",
            description="berrymill is a root filesystem generator for embedded devices",
            epilog="Have a lot of fun!")
        # default arguments
        self._add_default_args(p)
        sub_p = p.add_subparsers(help="Course of action for berrymill", dest="subparser_name")
        # prepare specific arguments
        prepare_p: argparse.ArgumentParser = sub_p.add_parser("prepare", help="prepare sysroot")
        self._add_prepare_args(prepare_p)

        # build specific arguments
        build_p: argparse.ArgumentParser = sub_p.add_parser("build", help="build image")
        self._add_build_args(build_p)
        self.args: argparse.Namespace = p.parse_args()

        self.cfg: ConfigHandler = ConfigHandler()
        if self.args.config:
            self.cfg.add_config(self.args.config)

        self.cfg.load()
        # Set appliance paths
        self._appliance_path, self._appliance_descr = self._get_appliance_path_info(self.args.image)

        os.chdir(self._appliance_path)

        self._tmp_backup_dir: str = mkdtemp(prefix="berrymill-tmp-", dir="/tmp")
        self._appliance_abspath: str = os.path.join(os.getcwd(), self._appliance_descr)
        self._bac_appliance_abspth: str = os.path.join(self._tmp_backup_dir, self._appliance_descr)
        try:
            self._construct_final_appliance()
        finally:
            self.cleanup()

    def _add_default_args(self, p: argparse.ArgumentParser) -> None:
        """ Add Defautl Arguments to parser accepted after berrymill"""
        p.add_argument("-s", "--show-config", action="store_true", help="shows the configuration of repositories")
        p.add_argument("-d", "--debug", action="store_true", help="turns on verbose debugging mode")
        p.add_argument("-a", "--arch", help="specify target arch")
        p.add_argument("-c", "--config", type=str, help="specify configuration other than default")
        p.add_argument("-i", "--image", required=True, help="path to the image appliance, if it's not in the current directory")
        p.add_argument("-p", "--profile", help="select profile for images that makes use of it")
        p.add_argument("--clean", action="store_true", help="cleanup previous build results prior build.")

    def _add_prepare_args(self, p: argparse.ArgumentParser) -> None:
        """ Add Prepare Specific Arguments to parser accepted after berrymill [default args] prepare"""
        p.add_argument("--root", required=True, help="directory of output sysroot")
        p.add_argument("--allow-existing-root", action="store_true", help="allow existing root")

    def _add_build_args(self, p: argparse.ArgumentParser) -> None:
        """ Add Build Specific Arguments to parser accepted after berrymill [default args] build"""
        # --cross sets a cpu -> dont allow user to choose cpu when cross is enabled
        build_fashion = p.add_mutually_exclusive_group()
        build_fashion.add_argument("--cpu", help="cpu to use for the QEMU VM (box)")
        build_fashion.add_argument("--cross", action="store_true", help="cross image build on x86_64 to aarch64 target")
        build_fashion.add_argument("-l", "--local", action="store_true", help="build image on current hardware")

        p.add_argument("--target-dir", required=True, type=str, help="store image results in given dirpath")
        p.add_argument("--no-accel", action="store_true", help="disable KVM acceleration for boxbuild")
        p.add_argument("--box-memory", type=str, default="8G", help="specify main memory to use for the QEMU VM (box)")

    def _get_appliance_path_info(self, image: str) -> Tuple[str, str]:
        """ Return Appliance Dirname, Basename"""
        appliance_path: str = os.path.dirname(image or ".")
        if appliance_path == ".":
            appliance_path = ""

        appliance_descr: str = os.path.basename(image or ".")
        if appliance_descr == ".":
            appliance_descr = ""

        if not appliance_path:
            for pth in os.listdir(appliance_path or "."):
                if pth.split('.')[-1] in ["kiwi", "xml"]:
                    appliance_descr = pth
                    appliance_path = os.getcwd()
                    break

        if not appliance_descr:
            raise Exception("Appliance description was not found.")

        if not appliance_path:
            raise Exception("Appliance Path not found")

        return appliance_path, appliance_descr

    def _init_local_repos(self) -> None:
        """
        Initialise local repositories, those are already configured on the local machine.
        """
        if not self.cfg.raw_unsafe_config().get("use-global-repos", False):
            return

        if self.cfg.raw_unsafe_config()["repos"].get("local") is not None:
            return
        else:
            self.cfg.raw_unsafe_config()["repos"]["local"] = Autodict()

        for r in DebianRepofind().get_repos():
            jr = r.to_json()
            for arch in jr.keys():
                if not self.cfg.raw_unsafe_config()["repos"]["local"].get(arch):
                    self.cfg.raw_unsafe_config()["repos"]["local"][arch] = Autodict()
                self.cfg.raw_unsafe_config()["repos"]["local"][arch].update(jr[arch])
        return

    def _construct_final_appliance(self) -> None:
        """
        Constructs final kiwi appliance which is used by kiwi
        1. moves the appliance description to a tmp dir, so kiwi wont use this "wrong" one
        2. Constructs the right appliance and safes it named as the one passed to berrymill orginially
        """
        final_rendered_xml_string = Loader().load(self._appliance_abspath)
        shutil.move(self._appliance_abspath, self._bac_appliance_abspth)
        with open(self._appliance_abspath, "w") as ma:
            ma.write(final_rendered_xml_string)

    def run(self) -> None:
        """
        Build an image
        """
        self._init_local_repos()
        if self.args.show_config:
            print(yaml.dump(self.cfg.config))
            return

        kiwip: KiwiParent | None = None
        if self.args.subparser_name == "build":
            # parameter "cross" implies a amd64 host and an arm64 target-arch
            if self.args.cross:
                self.args.arch = "arm64"

            if not self.args.local and is_vm() and not has_virtualization():
                log.warning(no_nested_warning)
                raise SystemExit()

            os.environ["KIWI_BOXED_PLUGIN_CFG"] = \
                self.cfg.raw_unsafe_config().get("boxed_plugin_conf", "/etc/berrymill/kiwi_boxed_plugin.yml")
            kiwip = KiwiBuilder(
                self._appliance_descr,
                box_memory=self.args.box_memory,
                profile=self.args.profile,
                debug=self.args.debug,
                clean=self.args.clean,
                cross=self.args.cross,
                cpu=self.args.cpu,
                local=self.args.local,
                target_dir=self.args.target_dir,
                no_accel=self.args.no_accel
                )
        elif self.args.subparser_name == "prepare":
            kiwip = KiwiPreparer(
                self._appliance_descr,
                root=self.args.root,
                debug=self.args.debug,
                profile=self.args.profile,
                allow_existing_root=self.args.allow_existing_root
                )
        else:
            raise argparse.ArgumentError(argument=None, message="No Action defined (build, prepare)")

        for r in self.cfg.config["repos"]:
            for rname, repo in (self.cfg.config["repos"][r].get(self.args.arch or get_local_arch()) or {}).items():
                kiwip.add_repo(rname, repo)

        try:
            kiwip.process()
        finally:
            self.cleanup()
            kiwip.cleanup()

    def cleanup(self) -> None:
        """
        Cleanup Temporary directories and files
        """
        if (os.path.exists(self._bac_appliance_abspth)):
            shutil.move(self._bac_appliance_abspth, self._appliance_abspath)
        shutil.rmtree(self._tmp_backup_dir, ignore_errors=True)
