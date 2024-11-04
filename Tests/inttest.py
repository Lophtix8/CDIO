#This will contain all inttests later on

"""import sys, unittest

import md
from asap3 import Trajectory

md.run_md()
traj = Trajectory("cu.traj")

class MdTests():

	def file_test(self):
		self.assertTrue(len(traj) != 0)

if __name__ == "__main__":
        tests = [unittest.TestLoader().loadTestsFromTestCase(MdTests)]
        testsuite = unittest.TestSuite(tests)
        result = unittest.TextTestRunner(verbosity=0).run(testsuite)
        sys.exit(not result.wasSuccessful())

"""
