from typing import Any
from berry_mill.plugin import PluginIf, registry
from berry_mill.cfgh import ConfigHandler
from berry_mill.mountpoint import MountManager
import kiwi.logger  # type: ignore
import os
import tempfile
import json
import shutil


log = kiwi.logging.getLogger('kiwi')
log.set_color_format()


class CvePlugin(PluginIf):
    """
    Intrusion detection and CVE scanner
    """

    ID:str = "cve"

    def get_fs_cve(self, fs_p:str, format:str, verbose=False):
        """
        Generate CVE data for a given filesystem
        """
        imgp = MountManager().get_image_path(fs_p)
        assert bool(imgp), "No image path found for {} mountpoint".format(fs_p)

        loopdev = MountManager().get_loop_device_by_mountpoint(fs_p)
        assert bool(loopdev), "No loop device found for {} mountpoint".format(fs_p)


        # generate CVE
        tfl:str = ""
        with tempfile.NamedTemporaryFile(suffix="-bml-CVE", delete=False) as tf:
            tfl = tf.name

        os.system("sh -c 'grype {} {}-o {}' > {}".format(fs_p, not verbose and "-q " or "", format, tfl))
        log.debug("Intrusion report data is written to {}".format(tfl))

        # Prettyformat if JSON
        if "-json" in format:
            out = json.dumps(json.load(open(tfl)), indent=2)
        else:
            with open(tfl) as fo:
                out = fo.read()

        os.remove(tfl)
        log.debug("CVE tempfile {} was removed".format(tfl))

        spf_p:str = fs_p + "." + format.replace("-", ".")
        with open(spf_p, "w") as spf:
            log.debug("Writing CVE data to {}".format(spf_p))
            spf.write(out)

        dst = imgp + ".cve." + self.get_partition_name_from_loopdev(loopdev) + "." + format.replace("-", ".")
        shutil.move(spf_p, dst)
        log.info("CVE summary is written to {}".format(dst))

    def check_env(self):
        """
        Check the environment
        """
        assert os.path.exists("/usr/bin/grype"), "Grype vulnerability scanner is not installed"
        assert os.getuid() == 0, "Plugin {} requires root priviledges".format(self.ID)

    def run(self, cfg:ConfigHandler):
        """
        Run CVE plugin
        """
        self.check_env()
        cve_data:dict[str, Any] = self.get_config(cfg)

        for mp in MountManager().get_mountpoints():
            log.debug("Scanning vulnerabilities {}".format(mp))
            self.get_fs_cve(mp, format=cve_data.get("format", "cyclonedx-json"),
                             verbose=cve_data.get("verbose"))


# Register plugin
registry(CvePlugin(title="Intrusion detection and opened CVE scanner", argmap=[]))
