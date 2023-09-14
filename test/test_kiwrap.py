
import sys
sys.path.append("./src")

import pytest

from berry_mill.kiwrap import KiwiBuilder

"""
Test class KiwiBuilder
"""
import unittest.mock

class TestCollectionKiwiBuilder:

    def test_kiwrap_add_repo(self):
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        """ Define some test data """
        reponame: str = "test_repo"
        repodata: dict = {"name": "repo", "url": "http://test.com"}

        """ Mock the _get_repokeys method """
        with unittest.mock.patch.object(KiwiBuilder_instance, "_get_repokeys") as mock_get_repokey:
            with unittest.mock.patch.object(KiwiBuilder_instance, "_check_repokey") as mock_check_repokey:
                """ Mock _get_repokey to skip callby returning test.key file path"""
                mock_get_repokey.return_value: str = "test.key"
                """ Mock _check_repokey to skip callby returning 0"""
                mock_check_repokey.return_value: int = 0
                """ Add reponame and repodata with add_repo"""
                KiwiBuilder_instance.add_repo(reponame, repodata)
                """ Check repodatas added correctly """
                assert reponame in KiwiBuilder_instance._repos
                assert KiwiBuilder_instance._repos[reponame] == repodata