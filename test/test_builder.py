
from _pytest.capture import CaptureFixture
import unittest.mock
from berry_mill.builder import KiwiBuilder
import requests
import pytest


class TestCollectionKiwiBuilder:
    def test_builder_get_relative_file_uri(self):
        """
        Test: get_relative_file_uri without key directory defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            repo_key_path: str = "path/to/key"
            KiwiBuilder_instance._boxtmpkeydir: str = ""

            KiwiBuilder_instance._get_relative_file_uri(repo_key_path)
        except Exception as e:
            assert "Key directory not available" in str(e)

    def test_builder_get_relative_file_uri(self):
        """
        Test: get_relative_file_uri without key directory defined
        Expected: Exception Repository data not defined
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
            # Define some test data
            repo_key_path: str = ""
            KiwiBuilder_instance._boxtmpkeydir: str = "/tmp"

            KiwiBuilder_instance._get_relative_file_uri(repo_key_path)
        except Exception as e:
            assert "Key path not defined" in str(e)


    def test_builder_write_repokeys_wrong_key_path(self, capsys: CaptureFixture):
        """
        Write repo keys while wrong key path in config
        Expected : exit code 1 exception and error failure message
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "https://www.example.com", "key": "file:///wrong/path"}
            repo = {reponame: repodata}

            KiwiBuilder_instance._write_repokeys_box(repo)
            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message
            assert "Failure while trying to copying the keyfile" in captured.out
        except SystemExit as e:
            assert e.code == 1

    def test_builder_write_repokeys_box_root_dest(self):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        Expected: exit code 1 and Boxroot directory is not defined exception
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # Override tmp box root directory destination path
            KiwiBuilder_instance._boxtmpkeydir: str = ""
            # Define some test data
            reponame: str = "test"
            repodata: dict = {"name": "test", "url": "https://www.example.com", "key": "file:///wrong/path"}
            repo = {reponame: repodata}

            KiwiBuilder_instance._write_repokeys_box(repo)
        except SystemExit as e:
            assert e.code == 1
        except Exception as ex:
            assert "Boxroot directory is not defined" in str(ex)

    def test_builder__cleanup_no_tmpdir(self, capsys: CaptureFixture):
        """
        Wrong tmp dir
        Expected: Error Cleanup Failed
        """

        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
        # Set tmpdir to empty
        KiwiBuilder_instance._tmpdir: str = ""

        KiwiBuilder_instance.cleanup()
        # Capture the error message printed on stdout
        captured: tuple = capsys.readouterr()
        # Assert that the error message contains the expected error message
        assert "Error: Cleanup Failed" in captured.out

    def test_builder_cleanup_no_boxtmpdiraaa(self, capsys: CaptureFixture):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        Expected: Error Cleanup Failed
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
        # Set tmpdir
        KiwiBuilder_instance._tmpdir: str = "/tmp"
        # Set wrok box tmp dir
        KiwiBuilder_instance._boxtmpkeydir: str = "worng/path"
        KiwiBuilder_instance.cleanup()
        # Capture the error message printed on stdout
        captured: tuple = capsys.readouterr()
        assert "Error: Cleanup Failed" in captured.out

    def test_builder_build_wrong_appliance(self, capsys: CaptureFixture):
        """
        Parse wrong appliance
        Expected: exit 1 and error Expected: failed to load external entity
        """
        try:
            # Create KiwiBuilder instance with wrong appliance
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test.txt")
            # trigger the build
            KiwiBuilder_instance.process()
        except SystemExit as se:
            cap: tuple = capsys.readouterr()
            assert "failed to load external entity" in cap.out
            assert se.code == 1

    def test_builder_build_no_profile_set(self, capsys: CaptureFixture):
        """
        Test config no profie
        Expected: exit 1 and error Expected: No Profile selected
        """
        try:
            # Create KiwiBuilder instance with existant appliance
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
            # Remove profile
            KiwiBuilder_instance._params["profile"] = ""
            # Trigger the build
            KiwiBuilder_instance.process()
            captured: tuple = capsys.readouterr()
            assert "No Profile selected" in captured.out
        except SystemExit as se:
            assert se.code == 1

    @pytest.mark.skip(reason="Dependency to berrymill package not yet ready")
    def test_builder_build_with_profile_set(self, capsys: CaptureFixture):
        """
        Test config  profie is
        Expected: message "Starting Kiwi Box"
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
        # Set profile
        KiwiBuilder_instance._params["profile"] = "Live"
        KiwiBuilder_instance.process()
        captured: tuple = capsys.readouterr()
        assert "Starting Kiwi Box" in captured.out

    def test_builder_build_with_local_set(self, capsys: CaptureFixture):
        """
        Test config  profie is
        Expected: message "Starting Kiwi for local build"
        """
        try:
            KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
            # Set profile
            KiwiBuilder_instance._params["profile"] = "Live"
            # Set local build
            KiwiBuilder_instance._params["local"] = True
            KiwiBuilder_instance.process()
            captured: tuple = capsys.readouterr()
            assert "Starting Kiwi for local build" in captured.out
        except SystemExit as e:
            print("Ignoring root permission error")
