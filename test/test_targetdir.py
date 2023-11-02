from berry_mill.kiwrap import KiwiBuilder
from mock import patch

class TestTargetDir:

    @patch("os.path.isdir", lambda f: True)
    def test_dir_exist(self):
        try:
            KB: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
            assert KB.build() == "Target directory already exists"
        except Exception as err:
            print(err)

    @patch("os.access")
    def test_dir_readonly(self, mock_os_access):
        try:
            mock_os_access.return_value = False
            KB: KiwiBuilder = KiwiBuilder("test/descr/test_appliance.xml")
            assert KB.build() == "Target directory's parent is not writable"
        except Exception as err:
            print(err)
        
