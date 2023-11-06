from typing import List
from typing_extensions import Unpack
import kiwi.logger
from kiwi.exceptions import KiwiPrivilegesError, KiwiRootDirExists
from .kiwiapp import KiwiAppPrepare
from .kiwrap import KiwiParent
from .params import KiwiPrepParams

log = kiwi.logging.getLogger('kiwi')


class KiwiPreparer(KiwiParent):
    """
    Main Class for Berrymill to prepare the "kiwi-ng system prepare" call
    """

    def __init__(self, descr: str, **kw: Unpack[KiwiPrepParams]):
        super().__init__(descr=descr,
                         profile=kw.get("profile", ""),
                         debug=kw.get("debug", False))

        self._params: KiwiPrepParams = kw

    def process(self) -> None:
        """
        Create the arguments for kiwi-ng call and run the Kiwi Prepare Task
        """
        root: str | None = self._params.get("root")

        assert root is not None, "output directory for root folder mandatory"

        command: List[str] = ["kiwi-ng"] + self._kiwi_options + ["system", "prepare"]
        command += ["--description", self._appliance_path]
        command += ["--root", root]

        if self._params.get("allow_existing_root"):
            command.append("--allow-existing-root")

        try:
            KiwiAppPrepare(command, repos=self._repos).run()
        except KiwiPrivilegesError:
            log.error("Operation requires root privileges")
        except KiwiRootDirExists as exc:
            log.error(exc.message)

    def cleanup(self) -> None:
        # Nothing to clean up
        super().cleanup()
        if self._initialized:
            log.info("Cleanup finished")
            return
