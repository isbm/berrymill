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
        self.dom = ET.fromstring("<foo><bar><baz>data</baz></bar></foo>".encode("utf-8"))

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
