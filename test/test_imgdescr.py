from berry_mill.imgdescr import ApplianceDescription

class TestImgDescr_Packages:
    """
    Unit test suite for `<packages/>` aggregate.
    """

    def setup_method(self, method):
        """
        Setup test method
        """
        self.ad = ApplianceDescription(open("test/descr/appliance_add_packages.xml").read())

    def teardown_method(self, method):
        """
        Teardown test results
        """
        del self.ad

    def test_id_pkg_init(self):
        """
        Initial parse
        """
        assert "schemaversion" in self.ad.s_dom.attrib, "Schema is missing"
        assert "name" in self.ad.s_dom.attrib, "Name is missing"

    def test_id_pkg_resolve_inherit(self):
        """
        Resolve links: inherit
        """
        assert self.ad.s_dom.find("inherit") is not None, "Appliance description has to have inheritance"

    def test_id_pkg_resolve_add_one_package(self):
        """
        Add one package
        """
        pkgs = None
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib["type"] == "image":
                pkgs = aggr
                break

        assert pkgs is not None, "Package for the images are missing"

        found = False
        for p in pkgs:
            if p.attrib["name"] == "humperdoo":
                found = True
                break

        assert found, "Humperdoo ran away :)"

    def test_id_pkg_resolve_add_packages_aggregate_init(self):
        """
        Add <packages type="delete"/> aggregate
        """
        pkg = None
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib.get("type") == "delete":
                pkg = aggr.findall("package")
                break

        assert pkg is not None, "Packages for deletion should be found"

    def test_id_pkg_resolve_add_packages_aggregate_content(self):
        """
        Add <packages type="delete"/> aggregate
        """
        pkg = None
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib.get("type") == "delete":
                pkg = aggr.findall("package")
                break

        assert len(pkg) == 1, "Should be one package in the aggregate"

    def test_id_pkg_resolve_add_packages_aggregate_attr(self):
        """
        Add <packages type="delete"/> aggregate
        """
        pkg = None
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib.get("type") == "delete":
                pkg = aggr.findall("package")
                break

        assert "name" in pkg[0].attrib, "Should have name attribute"

    def test_id_pkg_resolve_add_packages_aggregate_pkg_name(self):
        """
        Add <packages type="delete"/> aggregate
        """
        pkg = None
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib.get("type") == "delete":
                pkg = aggr.findall("package")
                break

        assert pkg[0].attrib["name"] == "dracula-kiwi-salad", "Should have a proper package name"

    def test_id_pkg_export(self):
        """
        Rough test for overall export
        """
        assert "humperdoo" in self.ad.to_str(), "No fun"

    def test_id_pkg_remove_aggregate(self):
        """
        Remove one aggregate
        """
        for aggr in self.ad.p_dom.findall("packages"):
            if aggr.attrib.get("type") == "iso":
                assert False, "No ISO images supposed to be made"

    def test_id_pkg_remove_any_aggregate(self):
        """
        Remove any aggregate that matches only a part of the
        """
        pkg = self.ad.p_dom.findall("repository")
        assert len(pkg) == 1, "Should be only one repository left"

    def test_id_pkg_set_user_attrs(self):
        """
        Select `<user/>` by XPath and update attributes from YAML
        """
        u_tag = self.ad.p_dom.xpath("//user")
        assert len(u_tag) == 1, "Should be only one user"

    def test_id_pkg_set_user_attrs_data(self):
        """
        Select `<user/>` by XPath and update attributes from YAML
        """
        u_tag = self.ad.p_dom.xpath("//user")[0]
        assert u_tag.attrib["password"] == "linux", "Password should be default set to 'linux'"
        assert u_tag.attrib["pwdformat"] == "plain", "Password should be in plain format"
