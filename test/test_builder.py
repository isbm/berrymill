import kiwi.logger
from pytest import CaptureFixture, LogCaptureFixture
from berry_mill.builder import KiwiBuilder
import pytest

log = kiwi.logging.getLogger('kiwi')

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

    def test_builder_cleanup_no_tmpdir(self, caplog: LogCaptureFixture):
        """
        Wrong tmp dir
        Expected: Error Cleanup Failed
        """
        log.info("Testing....")

        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
        # Set tmpdir to empty
        KiwiBuilder_instance._tmpdir: str = ""
        
        # Capture the error message printed on stdout
        with caplog.at_level(kiwi.logging.WARNING):
            KiwiBuilder_instance.cleanup()
        # Assert that the error message contains the expected error message
        assert "Cleanup Failed" in caplog.text
        

    def test_builder_cleanup_no_boxtmpdiraaa(self, caplog: LogCaptureFixture):
        """
        Write repo keys from tmp dir to a wrong boxroot destination
        Expected: Error Cleanup Failed
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Virtual")
        # Set tmpdir
        KiwiBuilder_instance._tmpdir: str = "/tmp"
        # Set wrok box tmp dir
        KiwiBuilder_instance._boxtmpkeydir: str = "worng/path"
        
        # Capture the error message printed on stdout
        with caplog.at_level(kiwi.logging.WARNING):
            KiwiBuilder_instance.cleanup()
        # Assert that the error message contains the expected error message
        assert "Cleanup Failed" in caplog.text

    def test_builder_build_wrong_appliance(self, caplog: LogCaptureFixture):
        """
        Parse wrong appliance
        Expected: exit 1 and error Expected: failed to load external entity
        """
        try:
            with caplog.at_level(kiwi.logging.WARNING):
                Kiwibuilder_instance:KiwiBuilder = KiwiBuilder("test.txt")
                Kiwibuilder_instance.process()
        except SystemExit as e:
            assert e.code == 1
            assert "while parsing appliance description" in caplog.text

    def test_builder_build_no_profile_set(self, caplog: LogCaptureFixture):
        """
        Test config no profie
        Expected: exit 1 and error Expected: No Profile selected
        """
        # Create KiwiBuilder instance with existant appliance
        with caplog.at_level(kiwi.logging.ERROR):
            try:
                KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
            except SystemExit as s:
                assert "No Profile selected" in caplog.text
                assert s.code == 1


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

    def test_kiwrap_build_with_local_set_no_root_rights(self, caplog: LogCaptureFixture):
        """
        Test config profile is
        Expected: message "Starting Kiwi for local build"
        """
        KiwiBuilder_instance: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
        # Set profile
        KiwiBuilder_instance._params["profile"] = "Live"
        # Set local build
        KiwiBuilder_instance._params["local"] = True
        KiwiBuilder_instance._params["target_dir"] = "/tmp"
        with caplog.at_level(kiwi.logging.WARNING):
            KiwiBuilder_instance.process()
        assert "Operation requires root privileges" in caplog.text

    @pytest.mark.skip(reason="Dependency to berrymill package not yet ready")
    def test_kiwrap_build_with_profile_set(self, capsys: CaptureFixture):
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
