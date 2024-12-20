import sys
import unittest as ut
import os
from ase.io import read
from ase import Atoms
from fracture_md import build


curr_dir = os.path.dirname(os.path.realpath(__file__))

class BuildTests(ut.TestCase):

    def test_construct_supercell(self):
        NotInDB = build.construct_supercell("Made_up_project_dir", "MadeUpMaterial",2,2,2)
        self.assertFalse(NotInDB)
        build.construct_supercell(f"{curr_dir}/Mock_jobs", "Al2O3.poscar", 5,5,5)
        InDB = os.path.isfile(f"{curr_dir}/Mock_jobs/Al2O3_5x5x5.poscar")
        self.assertTrue(InDB)
        build.construct_supercell(f"{curr_dir}/Mock_jobs", "SiO2.poscar", 10,5,5)
        InDB = os.path.isfile(f"{curr_dir}/Mock_jobs/SiO2_10x5x5.poscar")
        self.assertTrue(InDB)
        wrong_scaling = os.path.isfile(f"{curr_dir}/Mock_jobs/SiO2_5x5x5.poscar")
        self.assertFalse(wrong_scaling)

    def test_construct_crack(self):
        AlO = read(f"{curr_dir}/Mock_jobs/Al2O3_5x5x5.poscar")
        custom_crack = build.construct_crack(f"{curr_dir}/Mock_jobs", "AnyMaterial", AlO, True, [0,1], [0,1], [0,1])
        self.assertFalse(custom_crack)
        build.construct_crack(f"{curr_dir}/Mock_jobs", f"Al2O3_5x5x5.poscar", AlO, False, [0,0], [0,0], [0,0])
        zero_crack_exists = os.path.isfile(f"{curr_dir}/Mock_jobs/fractured_Al2O3_5x5x5.poscar")
        self.assertTrue(zero_crack_exists)
        zero_crack_size = os.path.getsize(f"{curr_dir}/Mock_jobs/fractured_Al2O3_5x5x5.poscar")
        build.construct_crack(f"{curr_dir}/Mock_jobs", f"Al2O3_5x5x5.poscar", AlO, False, [0,0.5], [0,0.5], [0,0.5])
        crack_size = os.path.getsize(f"{curr_dir}/Mock_jobs/fractured_Al2O3_5x5x5.poscar")
        original_size = os.path.getsize(f"{curr_dir}/Mock_jobs/Al2O3_5x5x5.poscar")
        self.assertFalse(zero_crack_size < original_size)
        self.assertTrue(crack_size < original_size)

    def test_delete_build(self):
        self.assertTrue(os.path.isfile(f"{curr_dir}/Mock_jobs/SiO2_10x5x5.poscar"))
        build.delete_build(f"{curr_dir}/Mock_jobs/SiO2_10x5x5.poscar")
        self.assertFalse(os.path.isfile(f"{curr_dir}/Mock_jobs/SiO2_10x5x5.poscar"))
        pass

if __name__ == "__main__":
    os.system(f"mkdir {curr_dir}/Mock_jobs")
    build.construct_supercell(f"{curr_dir}/Mock_jobs", "Al2O3.poscar", 5,5,5)
    build.construct_supercell(f"{curr_dir}/Mock_jobs", "SiO2.poscar", 10,5,5)
    tests = [ut.TestLoader().loadTestsFromTestCase(BuildTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())
    os.system(f"rm -r {curr_dir}/Mock_jobs")
