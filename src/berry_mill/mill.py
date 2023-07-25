import argparse
import sys
import os

from berry_mill.cfgh import ConfigHandler, Autodict
from berry_mill.kiwrap import KiwiBuilder
from berry_mill.localrepos import DebianRepofind

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

        p:argparse.ArgumentParser = argparse.ArgumentParser(prog="imagemill",
                                                            description="imagemill is a root filesystem generator for embedded devices",
                                                            epilog="Have a lot of fun!")
        p.add_argument("-c", "--config", type=str, help="specify configuration other than default")
        p.add_argument("-s", "--show-config", action="store_true", help="shows the building configuration")
        p.add_argument("-d", "--debug", action="store_true", help="turns on verbose debugging mode")
        p.add_argument("-i", "--image", help="path to the image appliance, if it is not found in the current directory")
        p.add_argument("-l", "--local", action="store_true", help="build the appliance directly on the current hardware")

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
                if pth.endswith(".kiwi"):
                    self._appliance_descr = pth
                    break

        # Set repos
        repos = DebianRepofind().get_repos()
        self.cfg.raw_unsafe_config()["repos"]["local"] = Autodict()
        for r in repos:
            jr = r.to_json()
            for arch in jr.keys():
                if not self.cfg.raw_unsafe_config()["repos"]["local"].get(arch):
                    self.cfg.raw_unsafe_config()["repos"]["local"][arch] = Autodict()
                self.cfg.raw_unsafe_config()["repos"]["local"][arch].update(jr[arch])


    def run(self) -> None:
        """
        Run imagemill
        """

        if not self._appliance_descr:
            raise Exception("Appliance description was not found.")
        if self._appliance_path:
            os.chdir(self._appliance_path)

        print("Using appliance \"{}\" located at \"{}\"".format(self._appliance_descr, self._appliance_path))

        KiwiBuilder(self._appliance_path, self._appliance_descr).build()

        print(self.cfg.config)