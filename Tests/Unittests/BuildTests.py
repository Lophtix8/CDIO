import sys
import unittest as ut
import os
from fracture_md import build


class BuildTests(ut.TestCase):

    def test_construct_supercell(self):
        NotInDB = build.construct_supercell("MadeUpMaterial",2,2,2)
        self.assertFalse(NotInDB)
        
        Al = build.construct_supercell("Al.poscar",2,2,2)
        self.assertTrue(type(Al) == str)
        self.assertTrue(os.path.isfile("Supercells/Al_2x2x2.poscar"))
        self.assertFalse(os.path.isfile("Supercells/SiC_WrongDimensions.poscar"))
        
        SiC = build.construct_supercell("SiC.poscar",1,2,3)
        self.assertTrue(type(SiC) == str)
        self.assertTrue(os.path.isfile("Supercells/SiC_1x2x3.poscar"))
        self.assertFalse(os.path.isfile("Supercells/SiC_WrongDimensions.poscar"))

    def test_construct_crack(self):
        custom_fracture = build.construct_crack("Al.poscar", True, "x", "y", "z")
        self.assertIsNone(custom_fracture)

        build.construct_crack("SiC_1x2x3.poscar", False, [0,0.5], [0,0.5], [0,0.5])
        self.assertTrue(os.path.isfile("Fractured_supercells/fractured_SiC_1x2x3.poscar"))
        self.assertFalse(os.path.isfile("Fractured_supercells/SiC_WrongDimensions.poscar"))
        with open("Fractured_supercells/fractured_SiC_1x2x3",'r') as f:
            nr_atoms_frac = f.readlines()[6]
        with open("Supercells/SiC_1x2x3",'r') as f:
            nr_atoms = f.readlines()[6]
        
        self.assertGreaterEqual(int(nr_atoms),int(nr_atoms_frac))

    def test_delete_build(self):
        self.assertTrue(os.path.isfile("Fractured_supercells/fractured_SiC_1x2x3.poscar"))
        build.delete_build("Fractured_supercells/fractured_SiC_1x2x3.poscar")
        self.assertFalse(os.path.isfile("Fractured_supercells/fractured_SiC_1x2x3.poscar"))

        self.assertTrue(os.path.isfile("Supercells/Al_2x2x2.poscar"))
        build.delete_build("Supercells/Al_2x2x2.poscar")
        self.assertFalse(os.path.isfile("Supercells/Al_2x2x2.poscar"))

      
    def test_main(self):
        pass

if __name__ == "__main__":
    os.mkdir("Supercells")
    os.mkdir("Fractured_supercells")
    tests = [ut.TestLoader().loadTestsFromTestCase(BuildTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
