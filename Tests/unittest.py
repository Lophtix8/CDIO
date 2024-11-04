#Later on this will be the script that runs all the individual unittestes that are created from each new feature.

"""
import sys, unittest
from md import calcenergy
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.lattice.cubic import FaceCenteredCubic
from asap3 import EMT

class MdTests(unittest.TestCase):

	def test_calcenergy(self):
		size = 10
		# Set up a crystal
		atoms = FaceCenteredCubic(directions=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
						symbol="Cu",
						size=(size, size, size),
						pbc=True)

		# Describe the interatomic interactions with the Effective Medium Theory
		atoms.calc = EMT()

		# Set the momenta corresponding to T=300K
		MaxwellBoltzmannDistribution(atoms, temperature_K=300)

		ekin, epot, init_T, etot = calcenergy(atoms)

		print(init_T)

		self.assertTrue(abs((init_T-300)/300) < 0.05)

if __name__ == "__main__":
	tests = [unittest.TestLoader().loadTestsFromTestCase(MdTests)]
	testsuite = unittest.TestSuite(tests)
	result = unittest.TextTestRunner(verbosity=0).run(testsuite)
	sys.exit(not result.wasSuccessful())
"""
