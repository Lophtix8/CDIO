import sys
import unittest as ut
from fracture_md import build


class BuildTests(ut.TestCase):
    def test_construct_supercell(self):
        NotInDB = build.construct_supercell("MadeUpMaterial",2,2,2)
        self.assertFalse(NotInDB)
        InDB = build.construct_supercell("Al.poscar",2,2,2)
        print(InDB)
        #self.assertTrue(type(InDB) == type(str))
    def test_construct_crack(self):
        pass
    def test_delete_build(self):
        pass
    def test_main(self):
        pass

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(BuildTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
