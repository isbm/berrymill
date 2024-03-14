from types import ModuleType
from typing import Any
from pathlib import Path
from berry_mill.logger import log

import os

embdgen: ModuleType | None
try:
    import embdgen  # type: ignore
    from embdgen.core.config.Factory import Factory as ConfigFactory
    from embdgen.core.utils.image import BuildLocation
except ImportError:
    embdgen = None

is_valid: bool = embdgen is not None


class EmbdGen:
    """
    Wrapper around embdgen utility to use it as library,
    instead of syscall it on its own.
    """

    def __init__(self, wd: str) -> None:
        self.cfg: ConfigFactory = ConfigFactory()
        self.wd = wd

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        d = os.path.abspath(os.path.curdir)
        os.chdir(self.wd)

        cfg_file = Path(os.path.join(self.wd, "../../foo.cfg"))
        cfg_out = Path("../blah.raw")

        bconf = self.cfg.by_type("yaml")
        assert bconf is not None, "Unable to initialise embdgen runner"

        label = bconf().load(cfg_file)

        log.info("Preparing image")
        label.prepare()

        log.debug(label)

        log.info(f"Writing image to {cfg_out}")
        label.create(cfg_out)

        os.chdir(d)
