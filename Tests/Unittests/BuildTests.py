import sys
import unittest as ut
import ~/CDIO/src/build


class BuildTests(ut.TestCase):
    def test_1():
        self.assertTrue(True)

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(BuildTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
