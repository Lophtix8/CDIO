import sys, unittest
#from md import calcenergy
from ase.md.verlet import VelocityVerlet
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.lattice.cubic import FaceCenteredCubic
from asap3 import EMT

from ..src.read_config_file import get_config_data
from ..src.read_config_file import check_data

"""
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
"""

class ConfigFileTests(unittest.TestCase):
    
    def test_get_config_data(self): 
        config_data = read_config_file.get_config_data("config_test1.yaml")
        self.assertTrue(isinstance(config_data, list))
        self.assertTrue(len(config_data) == 2)
        self.assertTrue(isinstance(config_data[1], dict))
        self.assertTrue(isinstance(config_data[2], dict))
        
    def test_check_data(self):
        data = [{"vasp_files": ["copper.vasp", "copper2.vasp"], "x_scalings": [5, 10, 15],
                "y_scalings": [5, 10, 20], "z_scalings": [10, 20, 30], "custom_fracture": False,
                "temps": [0, 100, 200], "stress_plane": "010", "iterations": 100, "t_interval": 5}]
        
        with self.assertRaises(KeyError):
            config_data = read_config_file.check_data(data)
        
        data[0]["fracture"] = [[0, 0.5], [0, 0.5], [0, 0]]
        config_data = read_config_file.check_data(data)
        self.assertIsNotNone(config_data)
        
        data[0]["x_scalings"] = [5, 10]
        with self.assertRaises(ValueError):
            config_data = read_config_file.check_data(data)
            
        data[0]["x_scalings"] = "Not a list"
        with self.assertRaises(TypeError):
            config_data = read_config_file.check_data(data)
            

if __name__ == "__main__":
	tests = [unittest.TestLoader().loadTestsFromTestCase(MdTests)]
	testsuite = unittest.TestSuite(tests)
	result = unittest.TextTestRunner(verbosity=0).run(testsuite)
	sys.exit(not result.wasSuccessful())

