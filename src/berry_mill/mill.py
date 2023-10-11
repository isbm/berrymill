import argparse
import sys
import os
import yaml

from berry_mill.cfgh import ConfigHandler, Autodict
from berry_mill.localrepos import DebianRepofind
from berry_mill.sysinfo import get_local_arch
from berry_mill.preparer import KiwiPreparer
from berry_mill.builder import KiwiBuilder

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

        p:argparse.ArgumentParser = argparse.ArgumentParser(prog="berrymill",
                                                            description="berrymill is a root filesystem generator for embedded devices",
                                                            epilog="Have a lot of fun!")
        
        p.add_argument("-s", "--show-config", action="store_true", help="shows the building configuration")
        p.add_argument("-d", "--debug", action="store_true", help="turns on verbose debugging mode")
        p.add_argument("-a", "--arch", help="specify target arch")
        p.add_argument("-c", "--config", type=str, help="specify configuration other than default")
        p.add_argument("-i", "--image", required=True, help="path to the image appliance, if it is not found in the current directory")
        p.add_argument("-p", "--profile", help="select profile for images that makes use of it")
        p.add_argument("--clean", action="store_true", help="cleanup previous build results prior build.")

        sub_p = p.add_subparsers(help="Course of action for berrymill",dest="subparser_name")
        
        prepare_p:argparse.ArgumentParser= sub_p.add_parser("prepare", help="prepare sysroot")
        prepare_p.add_argument("--root", required=True, help="directory of output sysroot")
        prepare_p.add_argument("--allow-existing-root", action="store_true", help="allow existing root")

        build_p:argparse.ArgumentParser = sub_p.add_parser("build", help="build image")
        build_p.add_argument("--box-memory", type=str, default="8G", help="specify main memory to use for the QEMU VM (box)")

        # --cross sets a cpu -> dont allow user to choose cpu when cross is enabled
        cpu_group = build_p.add_mutually_exclusive_group()
        cpu_group.add_argument("--cpu", help="cpu to use for the QEMU VM (box)")
        cpu_group.add_argument("--cross", action="store_true", help="cross image build on x86_64 to aarch64 target")

        build_p.add_argument("--target-dir", required=True, type=str, help="store image results in given dirpath")
        build_p.add_argument("-l", "--local", action="store_true", help="build image on current hardware")
        build_p.add_argument("--no-accel", action="store_true", help="disable KVM acceleration for boxbuild")


        self.args:argparse.Namespace = p.parse_args()

        self.cfg:ConfigHandler = ConfigHandler()
        if self.args.config:
            self.cfg.add_config(self.args.config)
        self.cfg.load()

        # Set appliance paths
        self._appliance_path: str = os.path.dirname(self.args.image or ".")
        if self._appliance_path == ".":
            self._appliance_path = ""

        self._appliance_descr: str = os.path.basename(self.args.image or ".")
        if self._appliance_descr == ".":
            self._appliance_descr = ""
        if not self._appliance_descr:
            for pth in os.listdir(self._appliance_path or "."):
                if pth.split('.')[-1] in ["kiwi", "xml"]:
                    self._appliance_descr = pth
                    break

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

    def run(self) -> None:
        """
        Build an image
        """

        self._init_local_repos()

        if self.args.show_config:
            print(yaml.dump(self.cfg.config))
            return

        if not self._appliance_descr:
            raise Exception("Appliance description was not found.")

        if self._appliance_path:
            os.chdir(self._appliance_path)



        if self.args.subparser_name == "build":
            kiwip = KiwiBuilder(self._appliance_descr, 
                            box_memory= self.args.box_memory, 
                            profile= self.args.profile, 
                            debug=self.args.debug, 
                            clean= self.args.clean,
                            cross= self.args.cross,
                            cpu= self.args.cpu,
                            local= self.args.local,
                            target_dir= self.args.target_dir,
                            accel= self.args.no_accel                          
                            )
        elif self.args.subparser_name == "prepare":           
            kiwip = KiwiPreparer(self._appliance_descr,
                            root=self.args.root,
                            debug=self.args.debug,
                            profile=self.args.profile,
                            allow_existing_root=self.args.allow_existing_root
                            )
        else:
            raise argparse.ArgumentError(message="No Action defined (build, prepare)")
        
        # parameter "cross" implies a amd64 host and an arm64 target-arch 
        for r in self.cfg.config["repos"]:
            for rname, repo in (self.cfg.config["repos"][r].get(self.args.arch or get_local_arch()) or {}).items():
                kiwip.add_repo(rname, repo)

        try:
            kiwip.process()
        except Exception as err:
            print(err)
        finally:
            kiwip.cleanup()


