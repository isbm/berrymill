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
        l.load("test/chain_a.xml")
        assert l._Loader__i_stack == ['test/test_appliance.xml'], "Traversal path should point to 'test_appliance.xml'"

    def test_loader_traversal_level_last(self):
        """
        Load full chain
        """
        l:self.XLoader = self.XLoader()
        l.load("test/chain_d.xml")

        res = ['test/test_appliance.xml', 'test/chain_a.xml', 'test/chain_b.xml', 'test/chain_c.xml']
        assert l._Loader__i_stack == res, "Traversal path should point to a four documents"

    def test_loader_traversal_level_root(self):
        """
        Load no chain at all
        """
        l:self.XLoader = self.XLoader()
        l.load("test/test_appliance.xml")

        assert l._Loader__i_stack == ["test/test_appliance.xml"], "Wrong root traversal"
