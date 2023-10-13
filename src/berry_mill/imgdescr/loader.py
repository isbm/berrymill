from __future__ import annotations
from typing import Any
import lxml.etree as ET
from berry_mill.imgdescr.descr import ApplianceDescription

class UqList(list):
    """
    List that acts like a Set, skipping elements that already exist.
    """
    def append(self, __object: Any) -> None:
        if __object not in self:
            super().append(__object)


class Loader:
    def __init__(self) -> None:
        self.__i_stack = UqList()

    def _traverse(self, pth: str) -> None:
        """
        Traverse the inheritance path
        """
        self.__i_stack.append(pth)
        doc: ET.Element|None = None
        try:
            with open(pth) as fp:
                doc = ET.fromstring(fp.read().encode("utf-8"))
        except Exception as exc:
            raise IOError(f"Exception while accessing \"{pth}\": {exc}")

        l_iht:list[ET.Element]|None = ApplianceDescription.find_all("inherit", doc)
        if l_iht:
            self.__i_stack.append(next(iter(l_iht)).attrib["path"])
            self._traverse(self.__i_stack[-1])
        else:
            self.__i_stack.append(pth)

    def _flatten(self) -> str:
        """
        Flatten traversal path
        """
        self.__i_stack.reverse()

        # init base
        descr:ApplianceDescription|None = None
        with open(next(iter(self.__i_stack))) as fd:
            descr = ApplianceDescription(fd.read())

        for pth in self.__i_stack[1:]:
            with open(pth) as fp:
                descr = ApplianceDescription(fp.read(), descr.to_str())

        return descr.to_str()

    def load(self, pth: str) -> str:
        """
        Load appliance description
        """
        self._traverse(pth)
        out = self._flatten()

        # Reset
        self.__i_stack.clear()

        return out
