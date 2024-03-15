import os
import tempfile
import shutil
import glob

from berry_mill import plugin
from berry_mill.mountpoint import MountManager
from berry_mill.plugins import PluginException
from berry_mill.logger import log
from berry_mill.plugins.kernkompozzer.embedgen import EmbdGen, BuildLocation


class KkzFlow:
    ID: str

    class HvConf:
        HV_DEFAULT_BUILD_DIR = "build"
        HV_BUILD_DIR: str = "output-dir"
        HV_BUILD_IMGNAME: str = "output-image"
        HV_PDATA: str = "part-data"
        HV_PDATA_EL: list[str] = ["kernel", "initrd"]
        HV_BOOTSTRAP_IMG: str = "bootstrap-image"
        HV_DEV_TREE: str = "device-tree"
        HV_SECTION: str = "hypervisor"
        HV_CONFIG: str = "hv-conf"
        HV_CONFIG_ENTRY: str = "hv-conf-entry"
        HV_IMG_LAYOUT: str = "image-layout"

    def __init__(self, id: str, cfg: dict) -> None:
        self.ID = id
        self.cfg: dict = cfg
        self.wd: str = os.path.abspath(".") + "/" + self.cfg.get(self.HvConf.HV_BUILD_DIR, self.HvConf.HV_DEFAULT_BUILD_DIR)
        os.makedirs(self.wd, exist_ok=True)
        self._wtd: str = tempfile.mkdtemp(dir=self.wd)
        os.makedirs(self._wtd, exist_ok=True)

    @staticmethod
    def _p2a(p: str) -> str:
        assert type(p) == str, f"Path {p} is not a string"
        assert p.startswith("dir://") or p.startswith("file://"), f'Path {p} should have "dir://" schema'
        p = p.replace("file://", "dir://")  # file:// here is an alias for a directory path and only for config visualisation
        if p.startswith("dir:///"):
            return p[6:]
        return os.path.abspath(".") + "/" + p[6:]

    def _cleanup(self) -> None:
        """
        Cleanup everything
        """
        log.debug(f"Removing temporary {self._wtd}")
        shutil.rmtree(self._wtd)
        BuildLocation().remove()

    def _extract_uboot(self) -> None:
        bsip: str | None = self.cfg.get(self.HvConf.HV_SECTION, {}).get(self.HvConf.HV_BOOTSTRAP_IMG)
        if bsip is None:
            raise PluginException(self.ID, "Bootstrap image path is not defined in the configuration")
        bsip = self._p2a(bsip)
        if not os.path.exists(bsip):
            raise PluginException(self.ID, f"No such file or directory: {bsip}")
        log.info(f"Extracting bootstrap image to {self._wtd}")
        os.system(f"l4image -i {bsip} --workdir {self._wtd} extract")

    def _copy_dtb(self) -> None:
        dtb: str | None = self.cfg.get(self.HvConf.HV_SECTION, {}).get(self.HvConf.HV_DEV_TREE)
        if dtb is None:
            raise PluginException(self.ID, "No device tree directory configured")
        dtb = self._p2a(dtb)
        if not os.path.exists(dtb):
            raise PluginException(self.ID, f"Path {dtb} does not exists")

        dtf: list[str] = glob.glob(os.path.join(dtb, "*.dtb"))
        assert len(dtf) > 0, "No device tree files has been found"
        log.info("Copying device tree files")
        for f in dtf:
            shutil.copy(f, self._wtd)

    def _copy_prt_data(self, part_id: str) -> None:
        pth: str = self._p2a(self.cfg[self.HvConf.HV_PDATA].get(part_id, ""))
        for tgt in self.HvConf.HV_PDATA_EL:
            if not pth:
                continue
            dst = os.path.join(self._wtd, os.path.basename(part_id))
            log.debug(f"Copying {pth} as {dst}")
            shutil.copy(pth, dst)

    def _create_bootstrap(self) -> None:
        btp_img: str = self._p2a(self.cfg[self.HvConf.HV_SECTION][self.HvConf.HV_BOOTSTRAP_IMG])
        modlist: str = os.path.join(self._p2a(self.cfg[self.HvConf.HV_SECTION][self.HvConf.HV_CONFIG]), "modules.list")
        entry = self.cfg[self.HvConf.HV_SECTION][self.HvConf.HV_CONFIG_ENTRY]
        bimg: str = os.path.join(self._wtd, "bootstrap.uimage")
        cmd = f"l4image -i {btp_img} -o {bimg} create --modules-list-file {modlist} --search-path {self._wtd} --entry {entry} > /dev/null"

        log.info("Creating bootstrap image with the new content")
        if os.system(cmd):
            raise PluginException(self.ID, "Error while creating bootstrap image (see above log)")

    def _setup_rootfs(self) -> None:
        log.info("Setting up rootfs image(s)")
        imgmap: dict[str, str] = {}
        img_p: str
        for img_p in MountManager().get_images():
            img_f: str = os.path.basename(img_p)

            for m_tgt, m_src in self.cfg["image-map"].items():
                if m_src == img_f:
                    imgmap[os.path.join(self._wtd, m_tgt)] = os.path.abspath(img_p)

        assert imgmap, "Could not find any corresponding images"

        for dp, sp in imgmap.items():
            log.debug(f"Symlinking {sp} as {dp}")
            os.symlink(sp, dp)

    def _write_image(self) -> None:
        shutil.copy(os.path.join(self._wtd, "bootstrap.uimage"), self.wd)
        EmbdGen(
            self._wtd, cfg=self.cfg[self.HvConf.HV_IMG_LAYOUT], img_fname=self.cfg.get(self.HvConf.HV_BUILD_IMGNAME, "output.raw")
        )()

    def __call__(self, *args: plugin.Any, **kwds: plugin.Any) -> plugin.Any:
        try:
            assert self.cfg.get(self.HvConf.HV_PDATA), "No partitions found in the configuration"
            assert self.cfg.get(self.HvConf.HV_SECTION), "No hypervisor section found"
            assert self.cfg[self.HvConf.HV_SECTION].get(self.HvConf.HV_CONFIG), "No hypervisor scripts/configuration found"
            assert self.cfg[self.HvConf.HV_IMG_LAYOUT], "No image layout defined"

            # HV part
            self._extract_uboot()
            self._copy_dtb()

            # Partitions
            for p_id in self.cfg.get(self.HvConf.HV_PDATA, []):
                self._copy_prt_data(part_id=p_id)

            self._create_bootstrap()
            self._setup_rootfs()
            self._write_image()
        finally:
            log.info("Cleaning up, shutting down")
            self._cleanup()
