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
        # Force to help
        if len(sys.argv) == 1:
            sys.argv.append("--help")
        
        p = argparse.ArgumentParser(prog="imagemill",
                                    description="imagemill is a root filesystem generator for embedded devices",
                                    epilog="Have a lot of fun!")
        p.add_argument("-c", "--config", type=str, help="specify configuration other than default")
        p.add_argument("-s", "--show-config", action="store_true", help="shows the building configuration")
        p.add_argument("-d", "--debug", action="store_true", help="turns on verbose debugging mode")

        self.args = p.parse_args()
        self.cfh:ConfigHandler = ConfigHandler()

    def run(self) -> None:
        """
        Run imagemill
        """
