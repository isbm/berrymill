from _pytest.capture import CaptureFixture
from pytest import LogCaptureFixture
import yaml
import os
import tempfile
from berry_mill.cfgh import ConfigHandler, Autodict
import pytest
import kiwi.logger

"""
Test class for Autodict
"""


class TestCollectionAutodict:
    @pytest.fixture
    def autodict_instance(self):
        return Autodict()

    @pytest.fixture
    def autodict_instance_with_value(self):
        autodict: Autodict = Autodict()
        autodict['key1'] = {'sub_key1': 'value1'}
        return autodict

    def test_autodict_get_item_with_nonexistant_key(self, autodict_instance: Autodict):
        # set test key 
        key: str = "test_key"
        # access no existent key 
        subautodict: Autodict = autodict_instance[key]
        # check that key is created if not exists 
        assert isinstance(subautodict, Autodict)

    def test_autodict_get_item_with_nondefined_value(self, autodict_instance: Autodict):
        # set only key 
        sub_dict: dict = autodict_instance["key"]
        # check that value is empty 
        assert len(sub_dict) == 0

    def test_autodict_get_item_with_defined_value(self, autodict_instance_with_value: Autodict):
        # get value 
        value: dict = autodict_instance_with_value["key1"]
        # check value 
        assert value == {'sub_key1': 'value1'}

    def test_autodict_set_item_with_non_dict_value(self, autodict_instance: Autodict):
        # set key and value 
        autodict_instance["key"]: int = 99
        # check the value
        assert autodict_instance["key"] == 99

    def test_autodict_set_item_with_defined_dict_value(self, autodict_instance_with_value: Autodict):
        try:
            # override dict type and expect exception 
            autodict_instance_with_value["key1"]: Autodict = {"test_key2": "test_value2"}
        except Exception as e:
            assert str(
                e) == "configuration type error: unable directly set to a hash, data container needs an update instead"


"""
Test class for ConfigHandler
"""


class TestCollectionConfigHandler:

    @pytest.fixture
    def config_handler(self):
        # Create instance of ConfigHandler 
        return ConfigHandler()

    def test_add_config_that_exists(self, config_handler: ConfigHandler):
        # Create temporary conf file 
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path: str = temp_file.name

        # Add config with the temporary path 
        config_handler.add_config(temp_file_path)
        # Check that file path was added 
        assert temp_file_path in config_handler._cfg

    def test_add_config_that_not_exists(self, caplog: LogCaptureFixture, config_handler: ConfigHandler):
        # Set non existent path 
        non_existent_config_path: str = "/path/to/non/existent/config.cfg"
        # add non existent path 
        with caplog.at_level(kiwi.logging.WARNING):
            config_handler.add_config(non_existent_config_path)
        # capture standard output 
        # check warning message 
        assert "no config found at" in caplog.text

    @pytest.fixture
    def valid_config(self):
        # Read default valid config file 
        config_path: str = './config/berrymill.conf.example'
        return config_path

    @pytest.fixture
    def invalid_config(self):
        # Create a temporary config file 
        invalid_config_data: str = 'key1: value1\nkey2;value2'
        with open('invalid_config.cfg', 'w') as yaml_file:
            yaml_file.write(invalid_config_data)
        yield 'invalid_config.cfg'
        # Clean up the temporary file
        os.remove('invalid_config.cfg')

    def test_parse_valid_config(self, config_handler: ConfigHandler, valid_config: str):
        """ Call the _parse_config valid config file : default cfg """
        config_handler._parse_config(valid_config)

        # Assert that the configuration was updated
        assert config_handler.config

    def test_parse_invalid_config(self, config_handler: ConfigHandler, invalid_config: str, capsys: CaptureFixture):
        try:
            # Call the _parse_config method with the invalid config file
            config_handler._parse_config(invalid_config)

            # Capture the error message printed on stdout
            captured: tuple = capsys.readouterr()

            # Assert that the error message contains the expected error message
            assert "ERROR: unable to load configuration" in captured.out
        except SystemExit as e:
            # Assert that the exit code is 1 (EPERM)
            assert e.code == 1

    @pytest.mark.skip(reason="Dependency to berrymill package not yet ready")
    def test_load_with_no_config(self, config_handler: ConfigHandler):
        config_handler.load()
        # Assert if no loaded cfg , default cfg is available
        assert str(config_handler._cfg[0]) == '/etc/berrymill.conf'

    def test_load_with_wrong_config_path(self, config_handler: ConfigHandler, capsys: CaptureFixture):
        try:
            # Mock cfg paths 
            config_handler._cfg: dict = ['/path/to/config1', '/path/to/config2']
            # Load configs 
            config_handler.load()
            #  Capture the error message printed on stdout 
            captured: tuple = capsys.readouterr()
            # Assert that the error message contains the expected error message 
            assert "ERROR: unable to load configuration" in captured.out
        except SystemExit as e:
            assert e.code == 1
