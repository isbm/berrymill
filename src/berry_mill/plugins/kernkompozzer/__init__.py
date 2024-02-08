from berry_mill import plugin
from berry_mill.cfgh import ConfigHandler

class Kernkompozzer(plugin.PluginIf):
    """
    Plugin for Kernkonzept hypervisor
    """
    ID = "kern-hv"

    def run(self, cfg:ConfigHandler):
        """
        Called by berrymill during the main exec
        """
        print(cfg.config[self.ID])
        print("KKZ with params:", self.runtime_args, self.runtime_kw)

# Register plugin
plugin.registry(Kernkompozzer(title="compose images with Kernkonzept hypervisor"))
