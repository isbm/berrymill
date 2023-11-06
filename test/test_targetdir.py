import unittest
from unittest.mock import patch
from berry_mill.builder import KiwiBuilder

class TestTargetDir(unittest.TestCase):

    @patch("os.path.isdir", lambda f: True)
    @patch("berry_mill.kiwiapp.KiwiAppLocal.run", lambda f: True)
    def test_dir_exist(self):
        with self.assertRaises (Exception) as msg:
            kb: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Live", target_dir="/arbitrary/dir")
            kb.process()
        self.assertTrue("Target directory already exists" in str(msg.exception))

    @patch("os.access")
    @patch("berry_mill.kiwiapp.KiwiAppLocal.run", lambda f: True)
    def test_dir_readonly(self, mock_os_access):
        with self.assertRaises (Exception) as msg:
            mock_os_access.return_value = False
            kb: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Live", target_dir="/arbitrary/dir")
            kb.process()
        self.assertTrue("Target directory's parent is not writable" in str(msg.exception))

        
