import os
from typing import Any
from berry_mill.plugin import PluginIf, PluginArgs, registry
from berry_mill.cfgh import ConfigHandler
from berry_mill.mountpoint import MountManager
from urllib.parse import ParseResult, urlparse

import copy
import shutil
import kiwi.logger  # type: ignore


log = kiwi.logging.getLogger("kiwi")
log.set_color_format()


class RootOverlay(PluginIf):
    """
    Root overlay plugin allows to choose between different
    roots to overlay on a specific image or partition.

    The image/partition should be write-able.
    """

    ID = "overlay"

    def _abs_p(self, pth: str) -> str:
        """
        Expand path
        """
        uri: ParseResult = urlparse(pth)
        assert uri.scheme == "dir", "Wrong path definition"
        if uri.hostname is not None:  # Path is relative
            pth = "./{}{}".format(uri.hostname, uri.path)
        else:
            pth = uri.path

        return pth

    def run(self, cfg: ConfigHandler) -> None:
        """
        Run overlay plugin
        """
        log.info(f"Running plugin {self.title}")

        p_cfg: dict[str, Any] = copy.deepcopy(cfg.config[self.ID])
        if self.args.dir:
            roots: list[str] = []
            for r in self.args.dir.split(","):
                if r.startswith("dir://"):
                    roots.append(r)
                else:
                    raise Exception("URI must be in dir:// scheme: {}".format(r))
            p_cfg["roots"] = roots

        log.debug(f"Given configuration: {p_cfg}")

        for pn in p_cfg.get("partitions", []):
            mp: str | None = MountManager().get_partition_mountpoint_by_ord(pn)
            if mp is None:
                raise Exception("Could not find a mountpoint for partition {}".format(pn))

            assert MountManager().is_writable(mp), f"Mountpoint {mp} on partrition {pn} seems not writable"

            for r in p_cfg.get("roots", []):
                r = self._abs_p(r)
                log.info(f"Applying root overlay at {r}")
                shutil.copytree(r, mp, symlinks=True, dirs_exist_ok=True)


# Register plugin
registry(
    RootOverlay(
        title="overlay rootfs with specific artifacts",
        argmap=[PluginArgs("-r", "--dir", help="overlay directories, comma-separated")],
    )
)
