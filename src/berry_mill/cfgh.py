import copy
import yaml
import os
import sys
from typing import Any, List
import kiwi.logger

log = kiwi.logging.getLogger('kiwi')


class Autodict(dict):
    def __getitem__(self, __key: Any) -> Any:
        if __key not in self.keys():
            self[__key] = Autodict()
        return super().__getitem__(__key)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        if type(self.get(__key)) == dict:
            raise Exception(f"configuration type error: unable directly set to a hash, data container needs an update instead")
        return super().__setitem__(__key, __value)


class ConfigHandler:
    def __init__(self, cf_path: str = ""):
        """
        """
        self._cfg:List[str] = []
        self.__conf:Autodict = Autodict()

        if not cf_path:
            # Load default /etc/berrymill/berrymill.conf
            # or in the current directory "berrymill.conf"

            default_conf:str = "/etc/berrymill/berrymill.conf"
            if os.path.exists(default_conf):
                self._cfg.append(default_conf)
            elif os.path.exists(os.path.basename(default_conf)):
                self._cfg.append(os.path.basename(default_conf))
            else:
                log.warning("no default config found at {}".format(default_conf))

    def add_config(self, cf_path: str):
        """
        Add an additional config overlay, if any
        """
        if os.path.exists(cf_path):
            self._cfg.append(cf_path)
        else:
            log.warning("no config found at {}".format(cf_path))

    def _parse_config(self, cf_path:str) -> None:
        """
        Parse YAML config from the path and store it to the main storage.
        """
        try:
            data:Any = yaml.load(open(cf_path), Loader=yaml.SafeLoader)
        except Exception as exc:
            log.error("unable to load configuration at {}: {}".format(cf_path, exc))
            sys.exit(1)

        self.__conf.update(data)

    def load(self) -> None:
        """
        Load all the configs
        """
        if not self._cfg:
            log.error("no configuration found")
            sys.exit(1)

        for cfgpath in self._cfg:
            self._parse_config(cf_path=cfgpath)

    @property
    def config(self) -> dict:
        """
        Return a deep copy of the configuration.
        This prevents from its accidental modification.
        """
        return copy.deepcopy(self.__conf)

    def raw_unsafe_config(self) -> dict:
        """
        Return the original config, which may be modified.
        """
        return self.__conf
