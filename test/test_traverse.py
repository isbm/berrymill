from berry_mill.imgdescr.loader import Loader
from berry_mill.imgdescr.descr import ApplianceDescription
import lxml.etree as ET

class TestLoaderTraversal:
    """
    Unit test suite for Application Description Loader traversal
    """

    def setup_class(self):
        class XLoader(Loader):
            def load(self, pth: str) -> str:
                """
                Load appliance description
                """
                self._traverse(pth)
                self._flatten()

        self.XLoader = XLoader

    def test_loader_traversal_level_1(self):
        """
        Load chain from a first level
        """

        l:self.XLoader = self.XLoader()
        l.load("test/descr/chain_a.xml")
        assert l._Loader__i_stack == ['test/descr/test_appliance.xml', 'test/descr/chain_a.xml'], "Traversal path should point to 'test_appliance.xml'"

    def test_loader_traversal_level_last(self):
        """
        Load full chain
        """
        l:self.XLoader = self.XLoader()
        l.load("test/descr/chain_d.xml")

        res = ['test/descr/test_appliance.xml', 'test/descr/chain_a.xml', 'test/descr/chain_b.xml', 'test/descr/chain_c.xml', 'test/descr/chain_d.xml']
        assert l._Loader__i_stack == res, "Traversal path should point to a four documents"

    def test_loader_traversal_level_root(self):
        """
        Load no chain at all
        """
        l:self.XLoader = self.XLoader()
        l.load("test/descr/test_appliance.xml")

        assert l._Loader__i_stack == ["test/descr/test_appliance.xml"], "Wrong root traversal"

    def test_loader_traversal_flatten_c(self):
        """
        Load full chain, changes from the level C should be applied.
        """
        l:Loader = Loader()
        lusers = ApplianceDescription.find_all("user", ET.fromstring(l.load("test/descr/chain_d.xml")))

        assert len(lusers) == 1, "Only one luser expected"
        assert "password" in lusers[0].attrib, "Luser should have a password"
        assert lusers[0].attrib["password"] == "lainooks :-)", "Password mismatch"
