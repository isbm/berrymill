import kiwi.logger
from pytest import CaptureFixture, LogCaptureFixture
from berry_mill.preparer import KiwiPreparer

log = kiwi.logging.getLogger('kiwi')

class TestCollectionKiwiPreparer:

    def test_preparer_prep_with_no_root_location(self):
        """
        Start preparing the sysroot when no output location for
        the root folder is given
        Expected: AssertionError
        """
        try:
            KiwiPreparer_instance:KiwiPreparer = KiwiPreparer("test/descr/test_appliance.xml", profile="Virtual")

            KiwiPreparer_instance.process()
        except AssertionError as asserr:
            assert "output directory for root folder mandatory" in str(asserr)

    def test_preparer_prep_with_wrong_appliance_descr(self, caplog: LogCaptureFixture):
        """
        Start preparing the sysroot when no valid 
        appliance descr is given
        Expected: SystemExit
        """
        try:
            with caplog.at_level(kiwi.logging.WARNING):
                KiwiPreparer_instance:KiwiPreparer = KiwiPreparer("test.txt", root="/tmp")
                KiwiPreparer_instance.process()
        except SystemExit as e:
            assert e.code == 1
            assert "while parsing appliance description" in caplog.text

            