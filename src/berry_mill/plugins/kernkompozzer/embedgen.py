from types import ModuleType
from typing import Any
from pathlib import Path
from berry_mill.logger import log

import os
import yaml  # type: ignore

embdgen: ModuleType | None
try:
    import embdgen  # type: ignore
    from embdgen.core.config.Factory import Factory as ConfigFactory  # type: ignore

    # This import is required in kkzflow, during the plugin init
    # and is deliberately not imported directly from the embdgen
    # for the reason to avoid to duplicate this whole check
    from embdgen.core.utils.image import BuildLocation  # type: ignore
except ImportError:
    embdgen = None

is_valid: bool = embdgen is not None


class EmbdGen:
    """
    Wrapper around embdgen utility to use it as library,
    instead of syscall it on its own.
    """

    def __init__(self, wd: str, cfg: dict[Any, Any], img_fname: str) -> None:
        self.f_label: ConfigFactory = ConfigFactory()
        self.wd: str = wd
        self.cfg: dict[Any, Any] = cfg
        self.output_fname: str = img_fname

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        d = os.path.abspath(os.path.curdir)
        os.chdir(self.wd)

        cfg_out = Path(f"../{self.output_fname}")

        bconf = self.f_label.by_type("yaml")
        assert bconf is not None, "Unable to initialise embdgen runner"

        label = bconf().load_str(yaml.dump(self.cfg))

        log.info("Preparing image")
        label.prepare()

        log.debug(label)

        log.info(f"Writing image to {cfg_out}")
        label.create(cfg_out)

        os.chdir(d)
