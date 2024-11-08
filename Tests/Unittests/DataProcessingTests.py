import sys, os
import unittest as ut
<<<<<<< HEAD
import fracture_md.process_data as pd
=======
import src.process_data as pd
>>>>>>> b494d214a83eacad85a8f0b973a383259aa9ef8d


class DataProcessingTests(ut.TestCase):
    curr_dir = os.path.dirname(__file__)
    def test_read_traj(self):
<<<<<<< HEAD
        traj_file = os.path.join(self.curr_dir, '..', 'ExampleFiles', "cu.traj")
=======
        traj_file = os.path.join(traj_file, '..', 'Tests', "cu.traj")
>>>>>>> b494d214a83eacad85a8f0b973a383259aa9ef8d
        traj_data = pd.read_traj_file(traj_file)
        
        temp = traj_data[0]["temperature"]

        # Check that starting temperature is ~ 300 K
        self.assertTrue((temp-300)/300 < 0.05)

    def test_graph_creator(self):
<<<<<<< HEAD
        traj_file = os.path.join(self.curr_dir, '..', 'ExampleFiles', "cu.traj")
        print(traj_file)
=======
        traj_file = os.path.join(traj_file, '..', 'Tests', "cu.traj")
>>>>>>> b494d214a83eacad85a8f0b973a383259aa9ef8d
        traj_data = pd.read_traj_file(traj_file)
        
        pd.visualize(traj_data, temperature=True, ekin=True)
        pd.visualize(traj_data, epot=True, combined_plot=True)

        self.assertTrue(os.path.exists("temperature.pdf"))
        self.assertTrue(os.path.exists("ekin.pdf"))
        self.assertTrue(os.path.exists("combined.pdf"))
<<<<<<< HEAD

        os.remove("temperature.pdf")
        os.remove("ekin.pdf")
        os.remove("combined.pdf")        
=======
        
>>>>>>> b494d214a83eacad85a8f0b973a383259aa9ef8d

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(DataProcessingTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())