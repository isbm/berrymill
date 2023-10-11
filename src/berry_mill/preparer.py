from typing import Dict, List, Union
from typing_extensions import Unpack
from berry_mill.kiwiapp import KiwiAppPrepare
from berry_mill.kiwrap import KiwiParent
from berry_mill.params import KiwiPrepParams


class KiwiPreparer(KiwiParent):
    def __init__(self, descr:str, **kw: Unpack[KiwiPrepParams]):
        self._params:Dict[KiwiPrepParams] = kw

        super().__init__(descr=descr,
                        profile=self._params.get("profile"),
                        debug=self._params.get("debug", False))
    
    def process(self) -> None:
        root:Union[str,None] = self._params.get("root")

        assert root is not None

        command:List[str] = ["kiwi-ng"] + self._kiwi_options + ["system", "prepare"]
        command += ["--description", self._appliance_path]
        command += ["--root", root]

        if self._params.get("allow_existing_root", False):
            command.append("--allow-existing-root")

        KiwiAppPrepare(command, repos=self._repos).run()

    def cleanup(self) -> None:
        # Nothing to clean up
        super().cleanup()

        if not self._initialized:
            print("Cleanup finished")
            return