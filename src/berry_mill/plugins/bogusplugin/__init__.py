from berry_mill.plugin import PluginIf, PluginArgs, registry

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
        print("Running plugin {}".format(self.title))

# Register plugin
registry(MyPlugin(title="example plugin",
                  name="example",
                  argmap=[
                      PluginArgs("-a", "--first", help="first argument"),
                      PluginArgs("-b", "--second", help="some other argument example"),
                    ]))
