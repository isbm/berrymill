
import sys
sys.path.append("./src")

import pytest

from berry_mill.kiwrap import KiwiBuilder

"""
Test class KiwiBuilder
"""
import unittest.mock

class TestCollectionKiwiBuilder:
    
    @pytest.fixture
    def KiwiBuilder_instance(self):
        return KiwiBuilder("appliance_example.kiwi")

    def test_kiwrap_add_repo(self, KiwiBuilder_instance: KiwiBuilder):
        """ Define some test data """
        reponame: str = "test_repo"
        repodata: dict = {"name": "repo", "url": "http://test.com"}

        """ Mock the _check_repokey method """
        with unittest.mock.patch.object(KiwiBuilder_instance, "_check_repokey") as mock_check_repokey:
            """ Mock _check_repokey to skip callby returning 0"""
            mock_check_repokey.return_value = 0
            """ Add reponame and repodata with add_repo"""
            KiwiBuilder_instance.add_repo(reponame, repodata)
            """ Check repodatas added correctly """
            assert reponame in KiwiBuilder_instance._repos
            assert KiwiBuilder_instance._repos[reponame] == repodata