import sys
import unittest as ut
import os
from fracture_md import build


class BuildTests(ut.TestCase):

    def test_construct_supercell(self):
        NotInDB = build.construct_supercell("MadeUpMaterial",2,2,2)
        self.assertFalse(NotInDB)

    def test_construct_crack(self):
        custom_crack = build.construct_crack("AnyMaterial", True, 0, 0, 0)
        self.assertFalse(custom_crack)

    def test_delete_build(self):
        f = open("FileToBeDeleted", 'w')
        f.write("This will be deleted if the function works properly")
        f.close()
        self.assertTrue(os.path.isfile("FileToBeDeleted"))
        build.delete_build("FileToBeDeleted")
        self.assertFalse(os.path.isfile("FileToBeDeleted"))

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(BuildTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
