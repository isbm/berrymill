from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler
from berry_mill.mountpoint import MountManager
from urllib.parse import urlparse

import copy
import os
import shutil

class RootOverlay(PluginIf):
    """
    Root overlay plugin allows to choose between different
    roots to overlay on a specific image or partition.

    The image/partition should be write-able.
    """

    ID = "overlay"

    def _abs_p(self, pth:str) -> str:
        """
        Expand path
        """
        uri = urlparse(pth)
        assert uri.scheme == "dir", "Wrong path definition"
        if uri.hostname is not None: # Path is relative
            pth = "./{}{}".format(uri.hostname, uri.path)
        else:
            pth = uri.path

        return pth

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

        for pn in p_cfg.get("partitions", []):
            mp = MountManager().get_partition_mountpoint_by_ord(pn)
            if mp is None:
                raise Exception("Could not find a mountpoint for partition {}".format(pn))

            for r in p_cfg.get("roots", []):
                r = self._abs_p(r)
                shutil.copytree(r, mp, symlinks=True, dirs_exist_ok=True)

        print("Running plugin {}".format(self.title))
        print(p_cfg)

# Register plugin
registry(RootOverlay(title="overlay rootfs with specific artifacts",
                     argmap=[PluginArgs("-r", "--dir", help="overlay directories, comma-separated")]))
