#Later on this will be the script that runs all the individual unittestes that are created from each new feature.

import sys, unittest

class ReadTests(unittest.TestCase):
    def test_pejpejpej(self):
        self.assertTrue(False)

class BuildTests(unittest.TestCase):
    def test_hejhejhej(self):
        self.assertTrue(True)

if __name__ == "__main__":
    tests = [unittest.TestLoader().loadTestsFromTestCase(ReadTests)]
    testsuite = unittest.TestSuite(tests)
    result = unittest.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
