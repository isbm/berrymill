from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler

class MyPlugin(PluginIf):
    """
    A bogus plugin
    """

    def setup(self, *a, **kw): pass
    def run(self, cfg:ConfigHandler):
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
