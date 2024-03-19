from berry_mill.mill import ImageMill
from berry_mill.plugins import PluginException

version = "0.2"


def main() -> None:
    """
    Main runtime
    """

    from typing import Any
    import sys
    import kiwi.logger  # type: ignore

    log = kiwi.logging.getLogger("kiwi")

    mill: Any = None
    try:
        mill = ImageMill()
    except Exception as exc:
        log.error("General error:", exc)
        sys.exit(1)

    try:
        mill.run()
    except PluginException as exc:
        log.error(exc)
    except Exception as exc:
        log.error(msg=f"Runtime error: {exc}")
        if mill.args.debug:
            raise
    finally:
        mill.cleanup()
