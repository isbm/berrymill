from typing import Any
from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler
from berry_mill.mountpoint import MountPoint
import kiwi.logger
import os
import tempfile
import json
from berry_mill.imagefinder import ImageFinder


log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class SbomPlugin(PluginIf):
    """
    Plugin to scan filesystems and generate SBOM in various formats
    """

    ID:str = "sbom"

    def get_fs_sbom(self, fs_p:str, format:str):
        """
        Generate SBOM data for a given filesystem
        """
        tdir = MountPoint().mount(fs_p)

        # generate SBOM
        tfl:str = ""
        with tempfile.NamedTemporaryFile(suffix="-bml-SBOM", delete=False) as tf:
            tfl = tf.name

        os.system("sh -c 'syft -q {} -o {}' > {}".format(tdir, format, tfl))

        log.debug("SBOM data is written to {}".format(tfl))

        # Prettyformat if JSON
        if "-json" in format:
            out = json.dumps(json.load(open(tfl)), indent=2)
        else:
            with open(tfl) as fo:
                out = fo.read()

        os.remove(tfl)
        log.debug("SBOM tempfile {} was removed".format(tfl))

        spf_p:str = fs_p + "." + format.replace("-", ".")
        with open(spf_p, "w") as spf:
            log.debug("Writing SBOM to {}".format(spf_p))
            spf.write(out)

        MountPoint().umount(tdir)


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
        imgf = ImageFinder()

        sbom_data:dict[str, Any] = self.get_config(cfg)
        log.debug("SBOM: {}".format(sbom_data))
        assert "images" in sbom_data, "{}: No images or image paths has been configured".format(self.ID)

        for img in imgf.find_images(*sbom_data["images"]):
            if img.scheme == "dir":
                log.debug("Generating SBOM data for {}".format(img.path))
                self.get_fs_sbom(img.path, format=sbom_data.get("format", "spdx-json"))
            else:
                raise Exception("Scheme {} not yet supported".format(img.scheme))

        print(sbom_data)

# Register plugin
registry(SbomPlugin(title="SBOM generator on various filesystems", argmap=[]))
