import kiwi.logger
from _pytest.capture import CaptureFixture
import unittest.mock

from pytest import LogCaptureFixture
from berry_mill.kiwrap import KiwiParent
import requests

log = kiwi.logging.getLogger('kiwi')

class TestCollectionKiwiParent:
    """
    Test class KiwiBuilder
    Tests the add_repo(), get_repokeys() use cases
    """

    def test_kiwrap_add_repo(self):
        """
        Verify that repo name and repo data: url, key, type.. are added correctly
        """
        KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
        # Define some test data
        reponame: str = "test_repo"
        repodata: dict = {"name": "repo", "url": "http://test.com"}

        # Mock _get_repokeys a,d _check_repokeys method
        with unittest.mock.patch.object(KiwiParent_instance, "_get_repokeys") as mock_get_repokey:
            # Mock the _check_repokeys method """
            with unittest.mock.patch.object(KiwiParent_instance, "_check_repokey") as mock_check_repokey:
                # Mock _get_repokey to skip callby returning test.key file path
                mock_get_repokey.return_value: str = "test.key"
                # Mock _check_repokey to skip callby returning 0
                mock_check_repokey.return_value: int = 0
                # Add reponame and repodata with add_repo
                KiwiParent_instance.add_repo(reponame, repodata)
                # Check repodatas added correctly
                assert reponame in KiwiParent_instance._repos
                assert KiwiParent_instance._repos[reponame] == repodata

    def test_kiwrap_add_repo_no_url(self):
        """
        Test: add_repo() method with wrong url
        Expected : Exception URL not found
        """
        try:
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "repo", "url": ""}
            KiwiParent_instance.add_repo(reponame, repodata)
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
            KiwiParent_instance: KiwiParent = KiwiParent("test.txt")
            # Define some test data
            reponame: str = ""
            repodata: dict = {"name": "test", "url": "http://test.com"}
            KiwiParent_instance.add_repo(reponame, repodata)
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
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "test", "url": ""}
            KiwiParent_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "URL not found" in str(e)

    def test_kiwrap_get_repokeys_wrong_url(self):
        """
        Test: get_repokeys() with wrong url defined
        Expected: Exception o connection adapters were found
        """
        try:
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {"name": "test", "url": "no_schema"}
            KiwiParent_instance._get_repokeys(reponame, repodata)
        except requests.exceptions.InvalidSchema as e:
            assert "No connection adapters were found" in str(e)

    def test_kiwrap_get_repokeys_no_reponame(self):
        """
        Test: get_repokeys without repo name defined
        Expected: Exception Repository name not defined
        """
        try:
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            reponame: str = ""
            repodata: dict = {"name": "test", "url": "http://test"}

            KiwiParent_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "Repository name not defined" in str(e)

    def test_kiwrap_get_repokeys_no_repodata(self):
        """
        Test: get_repokeys without repo data defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            reponame: str = "test_repo"
            repodata: dict = {}

            KiwiParent_instance._get_repokeys(reponame, repodata)
        except Exception as e:
            assert "Repository data not defined" in str(e)

    def test_kiwrap_check_repokey_no_key(self, caplog: LogCaptureFixture):
        """
        Test: _check_repokey without key defined
        Expected: Exception Repository data not defined
        """
        
        KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
        # Define some test data
        reponame: str = "test"
        repodata: dict = {"name": "test", "url": "http://test", "key": ""}

        try:
            with caplog.at_level(kiwi.logging.WARNING):
                KiwiParent_instance._check_repokey(repodata, reponame)
        except AssertionError:
            assert "Path to the key is not defined" in caplog.text

    def test_kiwrap_check_repokey_trusted_key_and_no_key_path(self, caplog: LogCaptureFixture):
        """
        Test: _check_repokey without key defined and trusted key are defined
         under /etc/apt/trusted.gpg.d"
        Expected: Berrymill was not able to retrieve a fitting gpg key
        """

        KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")
        with unittest.mock.patch.object(KiwiParent_instance, "_key_selection") as mock_key_selection:
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "http://test", "key": "file://"}
            mock_key_selection.return_value = ""
            try:
                with caplog.at_level(kiwi.logging.WARNING):
                    KiwiParent_instance._check_repokey(repodata, reponame)
                assert "Berrymill was not able to retrieve a fitting gpg key" in caplog.text
            except SystemExit:
                pass

    def test_kiwrap_check_repokey_no_trusted_key_and_no_key_path(self, capsys: CaptureFixture):
        """
        Test: _check_repokey with no key defined and no trusted key under /etc/apt/trusted.gpg.d"
        Expected: Trusted key not foud on system
        """

        KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml", profile="Virtual")

        with unittest.mock.patch.object(KiwiParent_instance, "_key_selection") as mock_key_selection:
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "http://test", "key": "file://"}
            # Disable selection menu
            mock_key_selection.return_value = ""
            # Redirect for non existent dir
            KiwiParent_instance._trusted_gpg_d = "/wrong/path"
            try:
                KiwiParent_instance._check_repokey(repodata, reponame)
            except SystemExit as s:
                assert s.args == ("key file path wrong for repository test",)
    
    def test_kiwrap_build_wrong_appliance(self, caplog: LogCaptureFixture):
        """
        Parse wrong appliance
        Expected: exit 1 and error Expected: failed to load external entity
        """
        try:
            with caplog.at_level(kiwi.logging.WARNING):
                KiwiParent_instance:KiwiParent = KiwiParent("test.txt")
                KiwiParent_instance.process()
        except SystemExit as e:
            assert e.code == 1
            assert "while parsing appliance description" in caplog.text

    def test_kiwrap_build_no_profile_set(self, capsys: CaptureFixture):
        """
        Test config no profie
        Expected: exit 1 and error Expected: No Profile selected
        """
        try:
            # Create KiwiParent instance with existant appliance
            KiwiParent_instance: KiwiParent = KiwiParent("test/descr/test_appliance.xml")
            # Remove profile
            KiwiParent_instance._params["profile"] = ""
            # Trigger the build
            KiwiParent_instance.process()
            captured: tuple = capsys.readouterr()
            assert "No Profile selected" in captured.out
        except SystemExit as se:
            assert se.code == 1

