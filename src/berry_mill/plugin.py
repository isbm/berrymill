# Plugins infrastructure
from __future__ import annotations

import os
import importlib
import argparse
from typing import Any
import kiwi.logger
from types import ModuleType
from abc import ABC, abstractmethod
from berry_mill.cfgh import ConfigHandler


log = kiwi.logging.getLogger('kiwi')


class PluginRegistry:
    """
    Plugin registry to keep the references on each plugin
    """
    def __init__(self) -> None:
        self.__registry = {}

    def __call__(self, __object: Any) -> PluginRegistry:
        if issubclass(__object.__class__, PluginIf):
            self.__registry[__object.name] = __object
        else:
            log.error("Plugin {} does not implements the plugin interface, skipping".format(__object.__class__))
        return self

    def plugins(self) -> list[str]:
        return sorted(self.__registry.keys())

    def __getitem__(self, __name: str) -> PluginRegistry|None:
        return __name in self.__registry and self.__registry[__name] or None

    def call(self, cfg:ConfigHandler, pname:str) -> Any:
        plugin:Any|None = self.__registry.get(pname)
        if plugin is None:
            log.error("Unable to call plugin {}: not loaded".format(pname))
        else:
            plugin.run(cfg)


registry = PluginRegistry()


class PluginIf(ABC):
    """
    Plugin interface
    """
    def __init__(self, title:str = "", name:str = "", argmap:list[PluginArgs]|None = None):
        """
        Register plugin
        """
        assert bool(name.strip()), "Cannot register plugin with the unknown title"
        assert bool(name.strip()), "Cannot register plugin with undefined name"

        self.name:str = name
        self.title:str = title
        self.argmap:list[PluginArgs] = argmap or []

    @abstractmethod
    def setup(self, *args, **kw):
        """
        Extra setup, adding extra opts and args to the config
        """

    @abstractmethod
    def run(self, cfg:ConfigHandler):
        """
        Runs plugin
        """

class PluginArgs:
    """
    Namespace for plugin arguments
    """
    def __init__(self, *args, **kw) -> None:
        self.args = args
        self.keywords = kw


def plugins_loader(sp: argparse.ArgumentParser):
    """
    Load plugins and construct their CLI interface
    """
    for p in os.listdir(os.path.join(os.path.dirname(__file__), "plugins")):
        try:
            importlib.import_module("berry_mill.plugins." + p)
        except Exception as exc:
            log.error("Failure to import plugin \"{}\": {}".format(p, exc))

    # Add to the CLI as a subcommand on --help
    for n in registry.plugins():
        p = registry[n]
        argp = sp.add_parser(p.name, help=p.title)
        for a in p.argmap:
            argp.add_argument(*a.args, **a.keywords)
