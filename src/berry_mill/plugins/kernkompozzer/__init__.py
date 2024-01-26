from berry_mill import plugin

class Kernkompozzer(plugin.PluginIf):
    """
    Plugin for Kernkonzept hypervisor
    """

    def autosetup(self):
        return super().autosetup()

    def setup(self, *args, **kw):
        return super().setup(*args, **kw)

    def run(self):
        print("KKZ")

# Register plugin
plugin.registry(Kernkompozzer(title="compose images with Kernkonzept hypervisor", name="kern-hv"))
