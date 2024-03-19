from berry_mill import plugin
from berry_mill.cfgh import ConfigHandler
from berry_mill.plugins import PluginException
from berry_mill.plugins.kernkompozzer.kkzflow import KkzFlow
from berry_mill.plugins.kernkompozzer import embedgen
from berry_mill.logger import log

import shutil


class Kernkompozzer(plugin.PluginIf):
    """
    Plugin for Kernkonzept hypervisor
    """

    ID = "kern-hv"

    def _check_env(self) -> None:
        """
        Check necessary artifacts in the environment
        """
        # Is embdgen python module installed?
        assert embedgen.is_valid, "Embdgen module is not installed"

        # Required system executables
        for b in ["l4image", "mkfs.ext4", "mcopy", "fakeroot", "mkfs.vfat", "e2fsck", "resize2fs", "veritysetup"]:
            if shutil.which(b) is None:
                raise PluginException(self.ID, f'"{b}" is not installed or is not available')

    def setup(self, *args, **kw) -> None:
        """
        Setup the plugin (this method is auto-called elsewhere)
        """
        log.debug("Autosetup up module")
        self._check_env()

        return super().setup(*args, **kw)

    def run(self, cfg: ConfigHandler):
        """
        Called by berrymill during the main exec
        """
        KkzFlow(id=self.ID, cfg=cfg.config[self.ID])()


# Register plugin
plugin.registry(Kernkompozzer(title="compose images with Kernkonzept hypervisor"))
