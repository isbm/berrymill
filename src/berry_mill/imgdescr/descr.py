from __future__ import annotations

import os
import logging
import yaml
from yaml.scanner import ScannerError as YamlScannerError
import os.path
import xml.dom.minidom
from typing import Any
import lxml.etree as ET

log = logging.getLogger("kiwi")

class ApplianceDescription:
    __INHERIT = "inherit"
    __P_AD = "add"
    __P_RM = "remove"
    __P_MG = "merge"
    __P_RP = "replace"
    __P_RA = "remove_any"
    __P_ST = "set"

    def __init__(self, descr: str, parent: str = None) -> ApplianceDescription:
        self.s_dom: ET.Element = ET.fromstring(descr.encode("utf-8"))
        self.p_dom: ET.Element|None = ET.fromstring(parent.encode("utf-8")) if parent is not None else None

        self._resolve()
        self._apply()

    def to_str(self, node: ET.Element = None) -> str:
        """
        Export appliance description to an XML string.
        """
        out = []
        for l in xml.dom.minidom.parseString(ET.tostring(node if node is not None else self.p_dom, encoding="utf-8")
                                             .decode("utf-8")).toprettyxml(indent="  ").split("\n"):
            if l.strip():
                out.append(l.rstrip())
        return "\n".join(out)

    def _resolve(self) -> None:
        """
        Reads the raw description and finds inherited parts of it.
        """
        if self.p_dom is not None:
            return

        self.p_dom = self.s_dom.find(self.__INHERIT)
        if self.p_dom is None:
            return

        assert self.p_dom is not None, "No inherited descriptions found"
        assert "path" in self.p_dom.attrib, "Inherited element should contain \"path\" attribute"
        assert os.path.exists(self.p_dom.attrib["path"]), "Unable to find inherited description"

        with open(self.p_dom.attrib["path"]) as ihf:
            self.p_dom = ET.fromstring(ihf.read().encode("utf-8"))

    def _apply(self) -> None:
        """
        Apply the inheritance policies
        """
        # No inherited documents found, stop right here.
        if self.p_dom is None:
            self.p_dom = self.s_dom
            return

        for op in self.s_dom.findall("*"):
            if op.tag in [self.__P_AD, self.__P_RM, self.__P_MG, self.__P_RP, self.__P_RA, self.__P_ST]:
                self.__class__.__dict__[f"_{op.tag}"](self, op)

    def frame(f):
        def w(ref, *a, **kw):
            f.__globals__["frame"] = f.__code__.co_name[1:]
            return f(ref, *a, **kw)
        return w

    @staticmethod
    def find_all(name: str, e: ET.Element, attrs: dict[str] = None) -> list[ET.Element]:
        nodes = set()
        [nodes.add(c) if c.tag == name and (not attrs or c.attrib == attrs)
         else nodes.update(ApplianceDescription.find_all(name, c, attrs=attrs)) for c in e]

        return list(nodes)

    @staticmethod
    def find_any(name: str, e: ET.Element, attrs: dict[str] = None) -> set[ET.Element]:
        nodes = set()
        if attrs is None:
            attrs = {}
        for node in ApplianceDescription.find_all(name, e):
            matches = True
            for k, v in attrs.items():
                if k not in node.attrib or node.attrib[k] != v:
                    matches = False
                    break
            matches and nodes.add(node)
        return nodes

    @staticmethod
    def get_parent(tree, e) -> ET.Element:
        for itm in tree.iter():
            for c in itm:
                if c == e:
                    return itm

    @staticmethod
    def get_xpath(e) -> str:
        path = [e.tag]
        parent = e
        while parent.getparent() is not None:
            parent = parent.getparent()
            path.insert(0, parent.tag)
        return '/' + '/'.join(path)

    @staticmethod
    def get_last(e: ET.Element) -> list[ET.Element]:
        out: list[ET.Element] = []
        len(e) and [out.extend(ApplianceDescription.get_last(c)) for c in e] or out.append(e)

        return out

    @staticmethod
    def get_next(e: ET.Element) -> ET.Element|None:
        for s_tag in e:
            if isinstance(s_tag, ET._Comment): continue
            if s_tag is not None:
                return s_tag

    def _add(self, e: ET.Element) -> None:
        """
        Add inherited elements
        """
        for c in e:
            # Elements
            for tc in self.find_all(c.tag, self.p_dom):
                if c.attrib != tc.attrib: continue
                [tc.append(mv_c) for mv_c in c]

            # Aggregates
            is_new = True
            for tc in self.find_all(c.tag, self.p_dom):
                if c.attrib == tc.attrib:
                    is_new = False
                    break

            if is_new:
                p = self.get_parent(self.p_dom, tc)
                p is not None and p.append(c)

    @frame
    def _remove(self, e: ET.Element) -> None:
        """
        Remove inherited elements
        """
        for s_tag in e:
            if len(s_tag):
                # Aggregate
                tgt_aggr: ET.Element = None
                for tgt_aggr in self.find_all(s_tag.tag, self.p_dom):
                    if tgt_aggr.attrib == s_tag.attrib and \
                        "/".join([x for x in self.get_xpath(s_tag).split("/") if x != frame]) == self.get_xpath(tgt_aggr):
                        [[t_tag.attrib == r_tag.attrib and t_tag.getparent().remove(t_tag)
                          for t_tag in ApplianceDescription.get_last(tgt_aggr)]
                          for r_tag in ApplianceDescription.get_last(s_tag)]
            else:
                # Elements
                for tc in self.find_all(s_tag.tag, self.p_dom):
                    if s_tag.attrib == tc.attrib:
                        p = self.get_parent(self.p_dom, tc)
                        p is not None and p.remove(tc)

    @frame
    def _merge(self, e: ET.Element) -> None:
        """
        Merge inherited elements
        """
        s_tag = ApplianceDescription.get_next(e)
        if s_tag is None:
            return

        e_xp: str = "/".join([x for x in self.get_xpath(s_tag).split("/") if x != frame])
        for t_tag in ApplianceDescription.find_all(s_tag.tag, self.p_dom, s_tag.attrib):
            if self.get_xpath(t_tag) == e_xp:
                for sc in s_tag:
                    is_new = True
                    for tc in t_tag:
                        if tc.tag == sc.tag:
                            is_new = False
                            break
                    is_new and t_tag.append(sc)

    def _replace(self, e: ET.Element) -> None:
        """
        Replace inherited elements
        """
        s_tag:ET.Element = ApplianceDescription.get_next(e)
        if s_tag is None:
            return

        for tgt_aggr in self.find_all(s_tag.tag, self.p_dom):
            if tgt_aggr.attrib == s_tag.attrib:
                p = tgt_aggr.getparent()
                p.remove(tgt_aggr)
                p is not None and p.append(s_tag)

    def _remove_any(self, e: ET.Element) -> None:
        """
        Remove any data. Anything inside of the `<remove_any/>` tag
        should at least match by attributes.

        The less specific attributes, the higher is glob matcher.
        """
        s_tag = ApplianceDescription.get_next(e)
        if s_tag is None:
            return

        [t.getparent().remove(t) for t in ApplianceDescription.find_any(s_tag.tag, self.p_dom, s_tag.attrib)]


    def _set(self, e: ET.Element) -> None:
        """
        [Re]sets attributes to an element
        """
        attrs: str = e.text.strip()
        if "xpath" not in e.attrib or not attrs:
            return

        try:
            # Crude YAML with no de-idents.
            p_attrs: dict[Any, Any] = yaml.safe_load(os.linesep.join(list(filter(None, [l.strip() for l in attrs.split("\n")]))))
            [list(map(t.set, p_attrs.keys(), p_attrs.values())) for t in self.p_dom.xpath(e.attrib["xpath"])]
        except YamlScannerError as yse:
            log.error(f"Unable to parse set of attributes in YAML for XPath {e.attrib['xpath']}")
