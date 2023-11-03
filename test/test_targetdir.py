from mock import patch
from berry_mill.builder import KiwiBuilder
import kiwi.logger

log = kiwi.logging.getLogger('kiwi')

class TestTargetDir:

    @patch("os.path.isdir", lambda f: True)
    @patch("berry_mill.kiwiapp.KiwiAppLocal.run", lambda f: True)
    def test_dir_exist(self):
        try:
            KB: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Live", target_dir="/arbitrary/dir")
            assert KB.process() == "Target directory already exists"
        except Exception as err:
            log.error(err)

    @patch("os.access")
    @patch("berry_mill.kiwiapp.KiwiAppLocal.run", lambda f: True)
    def test_dir_readonly(self, mock_os_access):
        try:
            mock_os_access.return_value = False
            KB: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml", profile="Live", target_dir="/arbitrary/dir")
            assert KB.process() == "Target directory's parent is not writable"
        except Exception as err:
            log.error(err)
        
