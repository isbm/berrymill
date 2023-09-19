
import sys
sys.path.append("./src")

import pytest
import requests

from berry_mill.kiwrap import KiwiBuilder

import unittest.mock
from _pytest.capture import CaptureFixture

class TestCollectionKiwiBuilder:
    """
    Test class KiwiBuilder
    Tests the add_repo(), get_repokeys() use cases
    """
    def test_kiwrap_add_repo(self):
        """
        Verify that repo name and repo data: url, key, type.. are added correctly
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        # Define some test data
        reponame: str = "test_repo"
        repodata: dict = {"name": "repo", "url": "http://test.com"}

        # Mock _get_repokeys a,d _check_repokeys method
        with unittest.mock.patch.object(KiwiBuilder_instance, "_get_repokeys") as mock_get_repokey:
            # Mock the _check_repokeys method """
            with unittest.mock.patch.object(KiwiBuilder_instance, "_check_repokey") as mock_check_repokey:
                # Mock _get_repokey to skip callby returning test.key file path
                mock_get_repokey.return_value: str = "test.key"
                # Mock _check_repokey to skip callby returning 0
                mock_check_repokey.return_value: int = 0
                # Add reponame and repodata with add_repo
                KiwiBuilder_instance.add_repo(reponame, repodata)
                # Check repodatas added correctly
                assert reponame in KiwiBuilder_instance._repos
                assert KiwiBuilder_instance._repos[reponame] == repodata

    def test_kiwrap_add_repo_no_url(self):
        """
        Test: add_repo() method with wrong url
        Expected : Exception URL not found 
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "repo", "url": ""}
            KiwiBuilder_instance.add_repo(reponame, repodata)
        except Exception as e:
            assert "URL not found" in str(e)

    def test_kiwrap_add_repo_no_repo_name(self, capsys: CaptureFixture):
        """
        Test: add_repo() without repo name defined
        Expected: 
          Exception Repository name not defined
          Exit code 1
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = ""
            repodata: dict = {"name": "test", "url": "http://test.com"}
            KiwiBuilder_instance.add_repo(reponame, repodata)
            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message
            assert "Repository name not defined" in captured.out
        except SystemExit as e:
            assert e.code == 1

    def test_kiwrap_get_repokeys_no_url(self):
        """
        Test: get_repokeys() without url defined
        Expected: Exception URL not found
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "test", "url": ""}
            KiwiBuilder_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "URL not found" in str(e)

    def test_kiwrap_get_repokeys_wrong_url(self):
        """
        Test: get_repokeys() with wrong url defined
        Expected: Exception o connection adapters were found
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "test", "url": "no_schema"}
            KiwiBuilder_instance._get_repokeys(reponame, repodata)
        except requests.exceptions.InvalidSchema as e:
            assert "No connection adapters were found" in str(e)

    def test_kiwrap_get_repokeys_no_reponame(self):
        """
        Test: get_repokeys without repo name defined
        Expected: Exception Repository name not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = ""
            repodata: dict = {"name": "test", "url": "http://test"}

            KiwiBuilder_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "Repository name not defined" in str(e)

    def test_kiwrap_get_repokeys_no_repodata(self):
        """
        Test: get_repokeys without repo data defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {}

            KiwiBuilder_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "Repository data not defined" in str(e)
