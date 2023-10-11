from berry_mill.imgdescr.loader import Loader

class TestLoaderTraversal:
    """
    Unit test suite for Application Description Loader traversal
    """

    def test_loader_traversal_level_1(self):
        """
        Load chain from a first level
        """
        class XLoader(Loader):
            def load(self, pth: str) -> str:
                """
                Load appliance description
                """
                self._traverse(pth)
                self._flatten()

        l:XLoader = XLoader()
        l.load("test/chain_a.xml")
        assert l._Loader__i_stack == ['test/test_appliance.xml'], "Traversal path should point to 'test_appliance.xml'"

    def test_loader_traversal_level_last(self):
        """
        Load full chain
        """
        class XLoader(Loader):
            def load(self, pth: str) -> str:
                """
                Load appliance description
                """
                self._traverse(pth)
                self._flatten()

        l:XLoader = XLoader()
        l.load("test/chain_d.xml")

        res = ['test/test_appliance.xml', 'test/chain_a.xml', 'test/chain_b.xml', 'test/chain_c.xml']
        assert l._Loader__i_stack == res, "Traversal path should point to a four documents"
