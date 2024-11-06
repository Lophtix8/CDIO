import sys, unittest

from fracture_md import read_config

class ConfigFileTests(unittest.TestCase):
    
    def test_get_config_data(self): 
        config_data = read_config.get_config_data("config_test1.yaml")
        self.assertTrue(isinstance(config_data, list))
        self.assertTrue(len(config_data) == 2)
        self.assertTrue(isinstance(config_data[1], dict))
        self.assertTrue(isinstance(config_data[2], dict))
        
    def test_check_data(self):
        data = [{"vasp_files": ["copper.vasp", "copper2.vasp"], "x_scalings": [5, 10, 15],
                "y_scalings": [5, 10, 20], "z_scalings": [10, 20, 30], "custom_fracture": False,
                "temps": [0, 100, 200], "stress_plane": "010", "iterations": 100, "t_interval": 5}]
        
        with self.assertRaises(KeyError):
            config_data = read_config.check_data(data)
        
        data[0]["fracture"] = [[0, 0.5], [0, 0.5], [0, 0]]
        config_data = read_config.check_data(data)
        self.assertIsNotNone(config_data)
        
        data[0]["x_scalings"] = [5, 10]
        with self.assertRaises(ValueError):
            config_data = read_config.check_data(data)
            
        data[0]["x_scalings"] = "Not a list"
        with self.assertRaises(TypeError):
            config_data = read_config.check_data(data)
        

if __name__ == "__main__":
	tests = [unittest.TestLoader().loadTestsFromTestCase(ConfigFileTests)]
	testsuite = unittest.TestSuite(tests)
	result = unittest.TextTestRunner(verbosity=0).run(testsuite)
	sys.exit(not result.wasSuccessful())
	main()
