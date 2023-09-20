
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

    def test_kiwrap_get_relative_file_uri(self):
        """
        Test: get_relative_file_uri without key directory defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            repo_key_path: str = "path/to/key"
            KiwiBuilder_instance._boxtmpkeydir: str = ""

            KiwiBuilder_instance._get_relative_file_uri(repo_key_path)
        except Exception as e:
            assert "Key directory not available" in str(e)

    def test_kiwrap_get_relative_file_uri(self):
        """
        Test: get_relative_file_uri without key directory defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            repo_key_path: str = ""
            KiwiBuilder_instance._boxtmpkeydir: str = "/tmp"

            KiwiBuilder_instance._get_relative_file_uri(repo_key_path)
        except Exception as e:
            assert "Key path not defined" in str(e)

    def test_kiwrap_check_repokey_no_key(self):
        """
        Test: _check_repokey without key defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "http://test", "key": ""}

            KiwiBuilder_instance._check_repokey(repodata, reponame)
        except Exception as e:
            assert "Path to the key is not defined" in str(e)

    def test_kiwrap_check_repokey_trusted_key_and_no_key_path(self, capsys: CaptureFixture):
        """
        Test: _check_repokey without key defined and trusted key are defined 
         under /etc/apt/trusted.gpg.d"
        Expected: Berrymill was not able to retrieve a fitting gpg key
        """

        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        with unittest.mock.patch.object(KiwiBuilder_instance, "_key_selection") as mock_key_selection:
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "http://test", "key": "file://"}
            mock_key_selection.return_value = ""
            KiwiBuilder_instance._check_repokey(repodata, reponame)
            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message
            assert "Berrymill was not able to retrieve a fitting gpg key" in captured.out

    def test_kiwrap_check_repokey_no_trusted_key_and_no_key_path(self, capsys: CaptureFixture):
        """
        Test: _check_repokey with no key defined and no trusted key under /etc/apt/trusted.gpg.d"
        Expected: Trusted key not foud on system
        """

        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        
        with unittest.mock.patch.object(KiwiBuilder_instance, "_key_selection") as mock_key_selection:
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "http://test", "key": "file://"}
            # Disable selection menu
            mock_key_selection.return_value = ""
            # Redirect for non existent dir 
            KiwiBuilder_instance._trusted_gpg_d = "/wrong/path"
            KiwiBuilder_instance._check_repokey(repodata, reponame)
            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message
            assert "Trusted key not foud on system" in captured.out

    def test_kiwrap_write_repokeys_wrong_key_path(self, capsys: CaptureFixture):
        """
        Write repo keys while wrong key path in config
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "https://www.example.com", "key": "file:///wrong/path"}
            repo = {reponame:repodata}

            KiwiBuilder_instance._write_repokeys_box(repo)
            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message
            assert "Failure while trying to copying the keyfile" in captured.out
        except SystemExit as e:
            assert e.code == 1

    def test_kiwrap_write_repokeys_box_root_dest(self):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Override tmp box root directory destination path
            KiwiBuilder_instance._boxtmpkeydir: str =""
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "https://www.example.com", "key": "file:///wrong/path"}
            repo = {reponame:repodata}

            KiwiBuilder_instance._write_repokeys_box(repo)
        except SystemExit as e:
            assert e.code == 1
        except Exception as ex:
            assert "Boxroot directory is not defined" in str(ex)

    def test_kiwrap__cleanup_no_tmpdir(self, capsys: CaptureFixture):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        """

        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        # Set tmpdir to empty
        KiwiBuilder_instance._tmpdir: str =""

        KiwiBuilder_instance._cleanup()
        # Capture the error message printed on stdout
        captured: tuple = capsys.readouterr()
        # Assert that the error message contains the expected error message
        assert "Error: Cleanup Failed" in captured.out

    def test_kiwrap_cleanup_no_boxtmpdiraaa(self, capsys: CaptureFixture):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
        # Set tmpdir
        KiwiBuilder_instance._tmpdir: str = "/tmp"
        # Set wrok box tmp dir
        KiwiBuilder_instance._boxtmpkeydir: str = "worng/path"
        KiwiBuilder_instance._cleanup()
        # Capture the error message printed on stdout
        captured: tuple = capsys.readouterr()        
        assert "Error: Cleanup Failed" in captured.out
    
