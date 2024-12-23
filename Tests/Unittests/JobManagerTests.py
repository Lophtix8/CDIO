import sys, os
import unittest as ut
from fracture_md import read_config, job_manager, build

class JobQueuerTests(ut.TestCase):
    curr_dir = os.path.dirname(__file__)
    conf_path = os.path.join(curr_dir, "..", "..", "fracture_md", "config_test.yaml")
    poscar_path = os.path.join(conf_path, "..", "Fractured_supercells", "fractured")

    sim_data = read_config.main(conf_path)
    job_manager.prepare_and_queue(conf_path)

if __name__ == "__main__":
    tests = [ut.TestLoader().loadTestsFromTestCase(JobQueuerTests)]
    testsuite = ut.TestSuite(tests)
    result = ut.TextTestRunner(verbosity=0).run(testsuite)
    sys.exit(not result.wasSuccessful())