import argparse
import sys

from berry_mill.cfgh import ConfigHandler


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

    def run(self) -> None:
        """
        Run imagemill
        """
        print(self.cfg.config)
