from ase.io.trajectory import Trajectory
from ase import Atoms
from ase import units

def process_data(traj_filename):
	"""
	Main function for processing data. Depending on the arguments, it will create plots, calculate properties etc.  
	"""
	traj_properties = read_traj_file(traj_filename)
	return

def read_traj_file(traj_filename, pure = False):
	"""
	Reads a trajectory file and returns a list of dictionaries containing the parameters, or the pure trajectory object.
	Currently implemented properties include kinetic energy, potential energy, total energy and temperature.
	"""
	# This could possibly be changed to return relevant properties instead. I.e. read_traj_file("example.traj", temperature=True).
	# Or to take the command line object as it's argument and manage that.
	
	try:
		traj = Trajectory(traj_filename)
	
	except:
		Exception("Trajectory file not found.")

	# If pure, simply return the traj argument.
	if pure:
		return traj

	# If not pure, process the trajectory data.
	traj_properties = []
	
	for atoms in traj:
		# Properties in traj object.
		atom_num = traj[-1].get_number_of_atoms()
		traj_properties.append \
			({"ekin": atoms.get_kinetic_energy()/atom_num,
	 		  "epot": atoms.get_potential_energy()/atom_num,
			  "etot": atoms.get_total_energy()/atom_num})
		
		# Derived properties.
		traj_properties[-1]["temp"] = traj_properties[-1]["ekin"] / (1.5 * units.kB)

	return traj_properties
	
if __name__ == "__main__":
	process_data("cu.traj")