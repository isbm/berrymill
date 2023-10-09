from berry_mill.imgdescr import ApplianceDescription
import pytest


class TestImgDescr_Packages:
    """
    Unit test suite for `<packages/>` aggregate.
    """

    def setup_method(self, method):
        """
        Setup test method
        """
        self.ad = ApplianceDescription(open("test/appliance_add_packages.xml").read())

    def teardown_method(self, method):
        """
        Teardown test results
        """
        del self.ad

    def test_id_pkg_init(self):
        """
        Initial parse
        """
        assert "schemaversion" in self.ad.dom_tree.attrib, "Schema is missing"
        assert "name" in self.ad.dom_tree.attrib, "Name is missing"
