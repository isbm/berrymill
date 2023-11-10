import unittest
from unittest.mock import patch

from pytest import LogCaptureFixture
import kiwi.logger
from berry_mill.builder import KiwiBuilder

class TestTargetDir:

    @patch("os.path.isdir", lambda f: True)
    @patch("berry_mill.kiwiapp.KiwiAppLocal.run", lambda f: True)
    def test_dir_exist(self, caplog: LogCaptureFixture):
        with caplog.at_level(kiwi.logging.ERROR):
            kb: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Live", target_dir="/arbitrary/dir")
            kb.process()
        assert "Target directory already exists" in caplog.text
        
