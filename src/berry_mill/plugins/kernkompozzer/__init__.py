from berry_mill import plugin
from berry_mill.cfgh import ConfigHandler

class Kernkompozzer(plugin.PluginIf):
    """
    Plugin for Kernkonzept hypervisor
    """
    ID = "kern-hv"

    def setup(self, *args, **kw):
        return super().setup(*args, **kw)

    def run(self, cfg:ConfigHandler):
        print(cfg.config[self.ID])
        print("KKZ")

# Register plugin
plugin.registry(Kernkompozzer(title="compose images with Kernkonzept hypervisor"))
