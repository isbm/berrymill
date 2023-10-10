from __future__ import annotations

import os.path
import xml.dom.minidom
from typing import Any
import lxml.etree as ET

class ApplianceDescription:
    __INHERIT = "inherit"
    __P_AD = "add"
    __P_RM = "remove"
    __P_MG = "merge"
    __P_RP = "replace"

    def __init__(self, descr: str) -> ApplianceDescription:
        self.s_dom: ET.Element = ET.fromstring(descr.encode("utf-8"))
        self.p_dom: ET.Element = None
        self._resolve()
        self._apply()



    def to_str(self, node: ET.Element = None) -> str:
        """
        Export appliance description to an XML string.
        """
        out = []
        for l in xml.dom.minidom.parseString(ET.tostring(node or self.p_dom, encoding="utf-8")
                                             .decode("utf-8")).toprettyxml(indent="  ").split("\n"):
            if l.strip():
                out.append(l.rstrip())
        return "\n".join(out)

    def _resolve(self):
        """
        Reads the raw description and finds inherited parts of it.
        """
        self.p_dom = self.s_dom.find(self.__INHERIT)

        assert self.p_dom is not None, "No inherited descriptions found"
        assert "path" in self.p_dom.attrib, "Inherited element should contain \"path\" attribute"
        assert os.path.exists(self.p_dom.attrib["path"]), "Unable to find inherited description"

        with open(self.p_dom.attrib["path"]) as ihf:
            self.p_dom = ET.fromstring(ihf.read().encode("utf-8"))

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

    @staticmethod
    def get_next(e) -> ET.Element:
        if len(e):
            for c in e:
                return c

    @staticmethod
    def get_xpath(e):
        path = [e.tag]
        parent = e
        while parent.getparent() is not None:
            parent = parent.getparent()
            path.insert(0, parent.tag)
        return '/' + '/'.join(path)

    @staticmethod
    def get_last(e: ET.Element) -> list[ET.Element]:
        out: list[ET.Element] = []
        if len(e):
            for c in e:
                out.extend(ApplianceDescription.get_last(c))
        else:
            out.append(e)

        return out

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
        for s_tag in e:
            if len(s_tag):
                # Aggregate
                tgt_aggr: ET.Element = None
                for tgt_aggr in self.find_all(s_tag.tag, self.p_dom):
                    if tgt_aggr.attrib == s_tag.attrib and \
                        "/".join([x for x in self.get_xpath(s_tag).split("/") if x != "remove"]) == self.get_xpath(tgt_aggr):
                        for r_tag in ApplianceDescription.get_last(s_tag):
                            for t_tag in ApplianceDescription.get_last(tgt_aggr):
                                if t_tag.attrib == r_tag.attrib:
                                    t_tag.getparent().remove(t_tag)
            else:
                # Elements
                for tc in self.find_all(s_tag.tag, self.p_dom):
                    if s_tag.attrib == tc.attrib:
                        p = self.get_parent(self.p_dom, tc)
                        p and p.remove(tc)

    def _merge(self, e: ET.Element):
        """
        Merge inherited elements
        """

    def _replace(self, e: ET.Element):
        """
        Replace inherited elements
        """