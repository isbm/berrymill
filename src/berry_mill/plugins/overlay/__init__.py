from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler

import copy

class RootOverlay(PluginIf):
    """
    Root overlay plugin allows to choose between different
    roots to overlay on a specific image or partition.

    The image/partition should be write-able.
    """

    ID = "overlay"

    def run(self, cfg:ConfigHandler):
        """
        Run overlay plugin
        """
        p_cfg = copy.deepcopy(cfg.config[self.ID])
        if self.args.dir:
            roots:list[str] = []
            for r in self.args.dir.split(","):
                if r.startswith("dir://"):
                    roots.append(r)
                else:
                    raise Exception("URI must be in dir:// scheme: {}".format(r))
            p_cfg["roots"] = roots

        print("Running plugin {}".format(self.title))
        print(p_cfg)

# Register plugin
registry(RootOverlay(title="overlay rootfs with specific artifacts",
                     argmap=[PluginArgs("-r", "--dir", help="overlay directories, comma-separated")]))
