import sys
import unittest as ut


class ReadTests(ut.TestCase):
    def test_pejpejpej(self):
        self.assertTrue(False)

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(ReadTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
