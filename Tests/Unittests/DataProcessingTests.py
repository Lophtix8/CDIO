class DataProcessingTests(ut.TestCase):
    def test_1(self):
        self.assertTrue(True)

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(DataProcessingTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())