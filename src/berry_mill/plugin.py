# Plugins infrastructure
from __future__ import annotations

import os
import importlib
import argparse
from typing import Any
import kiwi.logger
from types import ModuleType
from abc import ABC, abstractmethod


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
        return self.__registry.keys()

    def __getitem__(self, __name: str) -> PluginRegistry|None:
        return __name in self.__registry and self.__registry[__name] or None


registry = PluginRegistry()


class PluginIf(ABC):
    """
    Plugin interface
    """
    title:str = ""
    name:str = ""

    def __init__(self, title:str = "", name:str = ""):
        """
        Register plugin
        """
        assert bool(name.strip()), "Cannot register plugin with the unknown title"
        assert bool(name.strip()), "Cannot register plugin with undefined name"

        self.name = name
        self.title = title

    @abstractmethod
    def setup(self, *args, **kw):
        """
        Extra setup, adding extra opts and args to the config
        """

    @abstractmethod
    def autosetup(self):
        """
        Automatic setup (derive configs etc)
        """

    @abstractmethod
    def run(self):
        """
        Runs plugin
        """


def plugins_loader(argp: argparse.ArgumentParser):
    """
    Load plugins and construct their CLI interface
    """
    for p in os.listdir(os.path.join(os.path.dirname(__file__), "plugins")):
        try:
            importlib.import_module("berry_mill.plugins." + p)
        except Exception as exc:
            log.error("Failure to import plugin \"{}\": {}".format(p, exc))

    for n in registry.plugins():
        p = registry[n]
        print(p.name, p.title)