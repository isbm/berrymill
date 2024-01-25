from berry_mill.plugin import PluginIf, registry

class MyPlugin(PluginIf):
    """
    A bogus plugin
    """

    def autosetup(self): pass
    def setup(self, *a, **kw): pass
    def run(self):
        """
        Run plugin
        """
        print("Running plugin {}".format(self.PLUGIN))

# Register plugin
registry(MyPlugin(title="My Bogus Plugin", name="myplug"))
