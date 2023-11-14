from berry_mill.mill import ImageMill

def main():
    from berry_mill import ImageMill
    from typing import Any
    import sys
    import kiwi.logger

    log = kiwi.logging.getLogger('kiwi')

    mill:Any = None
    try:
        mill = ImageMill()
    except Exception as exc:
        log.error("General error:", exc)
        sys.exit(1)

    try:
        mill.run()
    except Exception as exc:
        log.error("Run error:", exc)
        if mill.args.debug:
            raise
    finally:
        mill.cleanup()
