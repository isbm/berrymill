from berry_mill.mill import ImageMill

version = "0.2"


def main():
    from berry_mill import ImageMill
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
    except Exception as exc:
        log.error("Runtime error: {}".format(exc))
        if mill.args.debug:
            raise
    finally:
        mill.cleanup()
