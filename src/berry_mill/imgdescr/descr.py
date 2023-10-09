from __future__ import annotations

import os.path
import xml.dom.minidom
from typing import Any
import xml.etree.ElementTree as ET

def p(d):
    out = []
    for x in xml.dom.minidom.parseString(d).toprettyxml(indent="  ").split("\n"):
        if x.strip():
            out.append(x.rstrip())
    print("\n".join(out))

class ApplianceDescription:
    __INHERIT = "inherit"
    __P_AD = "add"
    __P_RM = "remove"
    __P_MG = "merge"
    __P_RP = "replace"

    def __init__(self, descr: str) -> ApplianceDescription:
        self.s_dom: ET.Element = ET.fromstring(descr)
        self.p_dom: ET.Element = None
        self._resolve()
        self._apply()

        p(ET.tostring(self.p_dom, encoding="utf-8").decode("utf-8"))

    def _resolve(self):
        """
        Reads the raw description and finds inherited parts of it.
        """
        self.p_dom = self.s_dom.find(self.__INHERIT)

        assert self.p_dom is not None, "No inherited descriptions found"
        assert "path" in self.p_dom.attrib, "Inherited element should contain \"path\" attribute"
        assert os.path.exists(self.p_dom.attrib["path"]), "Unable to find inherited description"

        with open(self.p_dom.attrib["path"]) as ihf:
            self.p_dom = ET.fromstring(ihf.read())

    def _apply(self):
        """
        Apply the inheritance policies
        """
        for op in self.s_dom.findall("*"):
            if op.tag in [self.__P_AD, self.__P_RM, self.__P_MG, self.__P_RP]:
                self.__class__.__dict__[f"_{op.tag}"](self, op)

    @staticmethod
    def find_all(name: str, e: ET.Element) -> set[ET.Element]:
        nodes = []
        for c in e:
            if c.tag == name:
                nodes.append(c)
            nodes.extend(ApplianceDescription.find_all(name, c))
        return nodes

    @staticmethod
    def get_parent(tree, e) -> ET.Element:
        for itm in tree.iter():
            for c in itm:
                if c == e:
                    return itm

    def _add(self, e: ET.Element):
        """
        Add inherited elements
        """
        for c in e:
            # Elements
            for tc in self.find_all(c.tag, self.p_dom):
                if c.attrib != tc.attrib: continue
                for mv_c in c:
                    tc.append(mv_c)

            # Aggregates
            is_new = True
            for tc in self.find_all(c.tag, self.p_dom):
                if c.attrib == tc.attrib:
                    is_new = False
                    break

            if is_new:
                p = self.get_parent(self.p_dom, tc)
                p and p.append(c)

    def _remove(self, e: ET.Element):
        """
        Remove inherited elements
        """

    def _merge(self, e: ET.Element):
        """
        Merge inherited elements
        """

    def _replace(self, e: ET.Element):
        """
        Replace inherited elements
        """