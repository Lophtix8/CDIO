import sys
import os
import unittest as ut
from fracture_md import main


class MainTests(ut.TestCase):

    def test_main(self):
        wrong_option = main.main("ndjla","nvdjla")
        self.assertFalse(wrong_option)

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(MainTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
