from __future__ import annotations

from typing import Any
from berry_mill.imgdescr import ApplianceDescription
import lxml.etree as ET

class TestImgDescr_ApplianceDescription_Static:
    """
    Unit tests suite for static methods
    """

    def setup_method(self, m):
        """
        Setup test method
        """
        with open("test/descr/appliance_add_packages.xml") as x_files:
            self.dom = ET.fromstring(x_files.read().encode("utf-8"))

    def teardown_method(self, m):
        """
        Teardown test results from a method
        """
        del self.dom

    def test_find_all_one(self):
        """
        Test find_all() static method
        """
        xd: Any = ET.fromstring("<foo><bar><baz>data</baz></bar></foo>".encode("utf-8"))
        out:set[ET.Element] = ApplianceDescription.find_all("baz", xd)

        assert out is not None and len(out) == 1, "Should be something, right?"

    def test_find_all_one_name(self):
        """
        Test find_all() static method
        """
        xd: Any = ET.fromstring("<foo><bar><baz>data</baz></bar></foo>".encode("utf-8"))
        out:set[ET.Element] = ApplianceDescription.find_all("baz", xd)

        assert list(out)[0].tag == "baz", "No baz, no bar!"

    def test_find_all_many(self):
        """
        Test find_all() static method
        """
        xd: Any = ET.fromstring("<foo><bar><baz>some</baz><baz>more</baz><baz>data</baz></bar></foo>".encode("utf-8"))
        out:set[ET.Element] = ApplianceDescription.find_all("baz", xd)

        assert len(out) == 3, "Data should be length of 3"

    def test_find_all_many_names(self):
        """
        Test find_all() static method
        """
        xd: Any = ET.fromstring("<foo><bar><baz>some</baz><baz>more</baz><baz>data</baz></bar></foo>".encode("utf-8"))
        for t in ApplianceDescription.find_all("baz", xd):
            assert t.tag == "baz", "Baz should be baz!"

    def test_find_all_none(self):
        """
        Test find_all() static method
        """
        xd: Any = ET.fromstring("<foo><bar><baz>data</baz></bar></foo>".encode("utf-8"))
        out:set[ET.Element] = ApplianceDescription.find_all("spam", xd)

        assert out == [], "Result should be an empty list"

    def test_find_all_precise(self):
        """
        Test find_all() static method
        """
        xd: Any = ApplianceDescription.find_all("package", self.dom, {"name": "humperdoo"})
        assert xd[0].attrib["name"] == "humperdoo", "Humperdoo ran away somewhere"

    def test_get_parent(self):
        """
        Test get_parent() static method
        """
        xd: Any = ApplianceDescription.get_parent(
            self.dom, ApplianceDescription.find_all("package", self.dom, {"name": "humperdoo"})[0])

        assert xd.attrib["type"] == "image", "Humperdoo liks to paint dags!"

    def test_get_parent_none(self):
        """
        Test get_parent() static method
        """
        assert ApplianceDescription.get_parent(ET.fromstring("<foo><baz>data</baz></foo>".encode("utf-8")),
                                               ET.Element("junk")) is None, "Humperdoo does not likes junk"

    def test_get_next(self):
        """
        Test get_next() static method
        """
        p: ET.Element = ApplianceDescription.find_all("packages", self.dom, {"type": "image"})[0]
        assert ApplianceDescription.get_next(p).attrib["name"] == "humperdoo", "Humperdoo is missing"

    def test_get_xpath(self):
        """
        Test get_xpath() static method
        """
        p: ET.Element = ApplianceDescription.find_all("package", self.dom, {"name": "humperdoo"})[0]
        assert ApplianceDescription.get_xpath(p) == "/image/add/packages/package", "Humperdoo is somewhere else"

    def test_get_last(self):
        """
        Test get_xpath() static method
        """
        p: ET.Element = ApplianceDescription.find_all("packages", self.dom, {"type": "image"})[0]
        assert ApplianceDescription.get_last(p)[0].attrib["name"] == "humperdoo", "Humperdoo was not found"
