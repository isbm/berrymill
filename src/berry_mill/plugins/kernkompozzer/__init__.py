from berry_mill import plugin
from berry_mill.cfgh import ConfigHandler
from berry_mill.plugins import PluginException
from berry_mill.plugins.kernkompozzer.kkzflow import KkzFlow
from berry_mill.logger import log

import shutil

try:
    import embdgen  # type: ignore
except ImportError:
    embdgen = None


class Kernkompozzer(plugin.PluginIf):
    """
    Plugin for Kernkonzept hypervisor
    """

    ID = "kern-hv"

    def _check_env(self) -> None:
        """
        Check necessary artifacts in the environment
        """
        for b in ["l4image"]:
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
        assert embdgen is not None, "Embdgen module is not installed"
        KkzFlow(id=self.ID, cfg=cfg.config[self.ID])()


# Register plugin
plugin.registry(Kernkompozzer(title="compose images with Kernkonzept hypervisor"))
