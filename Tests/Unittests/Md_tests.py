import sys, unittest, os
from fracture_md import md
import logging

from ase.lattice.cubic import FaceCenteredCubic
from asap3 import EMT

logging.disable(logging.CRITICAL)

class MD_Tests(unittest.TestCase):
    
    def test_clacenergy(self):
        # Testing base values for calcenergy
        size = 10
        test_crystal = FaceCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        	                	symbol="Cu",
        	                	size=(size, size, size),
                	        	pbc=True)
        test_crystal.calc = EMT()
        epot, ekin, int_T, etot = md.calcenergy(test_crystal)
        
        self.assertTrue(ekin == 0.0)
        self.assertTrue(int_T == 0.0)
        self.assertTrue(epot == -0.0006011545839133374)
        self.assertTrue(etot == -0.0006011545839133374)
   

if __name__ == "__main__":
	tests = [unittest.TestLoader().loadTestsFromTestCase(MD_Tests)]
	testsuite = unittest.TestSuite(tests)
	result = unittest.TextTestRunner(verbosity=0).run(testsuite)
	sys.exit(not result.wasSuccessful())