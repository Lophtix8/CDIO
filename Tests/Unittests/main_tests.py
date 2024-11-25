import sys
import os
import unittest as ut
from fracture_md import main


class MainTests(ut.TestCase):

    def test_run_jobs(self):
        pass

    def test_prepare_jobs(self):
        pass

    def test_queue_jobs(self):
        pass

    def test_main(self):
        pass

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(MainTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
