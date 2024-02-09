from typing import Any
from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler
import kiwi.logger
import os
import urllib


log = kiwi.logging.getLogger('kiwi')
log.set_color_format()

class FsImagePtr:
    def __init__(self, fs_scheme, fs_path):
        self.scheme = fs_scheme
        self.path = fs_path

    def __repr__(self) -> str:
        return "<{}, type of {} for {} at {}>".format(self.__class__.__name__, self.scheme, self.path, hex(id(self)))


class SbomPlugin(PluginIf):
    """
    Plugin to scan filesystems and generate SBOM in various formats
    """

    ID:str = "sbom"
    SCHEMES:list[str] = ["dir", "oci"]

    def is_filesystem(self, p) -> bool:
        """
        Return True if a given filename is a mountable filesystem
        """
        out:str = ""
        with os.popen("file {}".format(p)) as fp:
            out = " ".join(list(filter(None, fp.read().split("\n"))))

        return "filesystem" in out.lower()

    def find_images(self, *paths) -> list[FsImagePtr]:
        """
        Find images with filesystems
        """
        out:list[str] = []
        for p in paths:
            log.debug("Looking for images in {}".format(p))
            if not "://" in p:
                raise Exception("Invalid url: \"{}\"".format(p))
            upr:urllib.parse.ParseResult = urllib.parse.urlparse(p)
            assert upr.scheme in self.SCHEMES, "Unknown scheme in URL: {}".format(p)

            imgp:str = ""
            if upr.netloc:
                imgp = "./{}".format(upr.netloc) + upr.path # Relative
            else:
                imgp = upr.path # Absolute

            for f in os.listdir(imgp):
                f = os.path.join(imgp, f)
                if self.is_filesystem(f):
                    out.append(FsImagePtr(upr.scheme, f))
        return out

    def get_fs_sbom(self, fs_p:str):
        """
        Generate SBOM data for a given filesystem
        """
        # mount
        # generate
        # umount

    def check_env(self):
        """
        Check the environment
        """
        for p, m in (["/usr/bin/syft", "Syft is not installed"],
                     ["/usr/bin/file", "File type command (/usr/bin/file) is not found"]):
            assert os.path.exists(p), m
        assert os.getuid() == 0, "Plugin {} requires root priviledges".format(self.ID)

    def run(self, cfg:ConfigHandler):
        """
        Run SBOM plugin
        """
        self.check_env()

        sbom_data:dict[str, Any] = self.get_config(cfg)
        log.debug("SBOM: {}".format(sbom_data))
        assert "images" in sbom_data, "{}: No images or image paths has been configured".format(self.ID)

        for img in self.find_images(*sbom_data["images"]):
            if img.scheme == "dir":
                self.get_fs_sbom(img.path)
            else:
                raise Exception("Scheme {} not yet supported".format(img.scheme))

        print(sbom_data)

# Register plugin
registry(SbomPlugin(title="SBOM generator on various filesystems", argmap=[]))
