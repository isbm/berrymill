# Plugins infrastructure
from __future__ import annotations

import os
import sys
import importlib
import argparse
import yaml  # type: ignore
import kiwi.logger  # type: ignore
import traceback

from typing import Any
from types import ModuleType
from berry_mill.cfgh import ConfigHandler


log = kiwi.logging.getLogger("kiwi")
log.set_color_format()


class PluginRegistry:
    """
    Plugin registry to keep the references on each plugin
    """
    def __init__(self) -> None:
        self.__registry = {}

    def __call__(self, __object: Any) -> PluginRegistry:
        if issubclass(__object.__class__, PluginIf):
            if __object.ID == PluginIf.ID or not __object.ID:
                log.error("Plugin {} should have unique ID, skipping".format(__object.__class__))
            else:
                self.__registry[__object.ID] = __object
        else:
            log.error("Plugin {} does not implements the plugin interface, skipping".format(__object.__class__))
        return self

    def plugins(self) -> list[str]:
        return sorted(self.__registry.keys())

    def __getitem__(self, __name: str) -> PluginRegistry|None:
        return __name in self.__registry and self.__registry[__name] or None

    def call(self, cfg: ConfigHandler, pname: str, *args, **kw) -> Any:
        plugin: Any | None = self.__registry.get(pname)
        if plugin is None:
            log.error("Unable to call plugin {}: not loaded".format(pname))
        else:
            plugin.setup(*args, **kw)
            plugin.run(cfg)


registry = PluginRegistry()


class PluginIfDeco(type):
    def __init__(cls, name, base, clsd):
        def run(self, cfg: ConfigHandler):
            log.debug("Running {} plugin".format(cls.ID))
            try:
                clsd["run"](self, cfg)
            except Exception as exc:
                log.error(exc)

                # Don't hate me for this... :)
                if "-d" in sys.argv or "--debug" in sys.argv:
                    print("-" * 80)
                    traceback.print_exception(exc, limit=None, file=sys.stderr)
                    print("-" * 80)

            cls.teardown(self)  # type: ignore

        setattr(cls, "run", run)


class PluginIf(metaclass=PluginIfDeco):
    """
    Plugin interface
    """

    ID: str = "default"

    def __init__(self, title: str = "", argmap: list[PluginArgs] | None = None):
        """
        Register plugin
        """
        assert bool(title.strip()), "Cannot register plugin with the unknown title"

        self.title: str = title.lower()
        self.argmap: list[PluginArgs] = argmap or []
        self.runtime_args: tuple[()] = ()
        self.runtime_kw: dict[str, str] = {}

        self.__args = None

    @property
    def args(self):
        return self.__args

    @args.setter
    def args(self, p):
        if self.__args is None:
            self.__args = p

    def get_config(self, cfg: ConfigHandler, optname: str | None = None):
        """
        Get default config or override it
        """
        wd: dict[str, Any] = cfg.config.get(self.ID, {})
        optconf = optname or "{}.conf".format(self.ID)
        if optconf:
            if os.path.exists(optconf):
                try:
                    wd += yaml.load(open(optconf), Loader=yaml.SafeLoader)
                except Exception as exc:
                    log.error('Unable to update plugin config from file "{}". Please check the syntax and try again.')
                    raise
            else:
                if not wd:
                    log.warn(
                        'Unable to find config file "{}" for {}, default config is not available either'.format(optconf, self.ID)
                    )
                    log.warn("Probably nothing happened...")
        return wd

    def setup(self, *args, **kw):
        """
        Extra setup, adding extra opts and args to the config
        """
        assert not self.runtime_args
        self.runtime_args = args
        self.runtime_kw = kw

    def teardown(self):
        """
        Flush args after running
        """
        self.runtime_args = ()
        self.runtime_kw = {}

    def run(self, cfg: ConfigHandler):
        """
        Runs plugin
        """
        raise NotImplementedError("Method should be implemented")

    # TODO: Probably must be moved to mount manager?
    def get_partition_name_from_loopdev(self, devname) -> str:
        devname = os.path.basename(devname).replace("loop", "")
        partsect: str = "single"
        if len(devname.split("p")) == 2:
            partsect = "prt-{}".format(devname.split("p")[-1])
        return partsect


class PluginArgs:
    """
    Namespace for plugin arguments
    """

    def __init__(self, *args, **kw) -> None:
        self.args = args
        self.keywords = kw
        self.keywords["help"] = self.keywords.get("help", "").lower()


def plugins_loader(sp: argparse._SubParsersAction[argparse.ArgumentParser]):
    """
    Load plugins and construct their CLI interface
    """
    for lp in os.listdir(os.path.join(os.path.dirname(__file__), "plugins")):
        if "." in lp:
            continue
        try:
            importlib.import_module("berry_mill.plugins." + lp)
        except Exception as exc:
            log.error('Failure to import plugin "{}": {}'.format(lp, exc))

    # Add to the CLI as a subcommand on --help
    for n in registry.plugins():
        p: PluginIf | None = registry[n]
        if p is None:
            continue
        argp: argparse.ArgumentParser = sp.add_parser(p.ID, help=p.title)
        for a in p.argmap:
            argp.add_argument(*a.args, **a.keywords)


def plugins_args(ns: argparse.Namespace) -> None:
    """
    Pass args namespace to each plugin
    """
    for n in registry.plugins():
        p: PluginIf | None = registry[n]
        if p is not None:
            p.args = ns
