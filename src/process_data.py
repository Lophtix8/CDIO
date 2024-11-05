from ase.io.trajectory import Trajectory
from ase import Atoms
from ase import units
from matplotlib import pyplot as plt

def process_data(traj_filename: str):
	"""
	Main function for processing data. Depending on the arguments, it will create plots, calculate properties etc.
	"""
	# This is just a temporary example
	traj_properties = read_traj_file(traj_filename)
	visualize(traj_properties, ekin=True, epot=True, etot=True, combined_plot=True)
	visualize(traj_properties, temperature=True)
	return

def read_traj_file(traj_filename: str) -> list[dict[str, float]]:
	"""
	Reads a trajectory file and returns a list of dictionaries containing the parameters, or the pure trajectory object.
	Currently implemented properties include kinetic energy, potential energy, total energy and temperature.

	Args:
		traj_filename (str): The filename of the traj file

	Returns:
		traj_properties (list): A list of dictionaries. Each entry in the list contains the properties of that step. \n 
		For example, the temperature at the 3rd step is located at: 
		traj_properties[2][temperature] 
		

	"""
	# This could possibly be changed to return relevant properties instead. I.e. read_traj_file("example.traj", temperature=True).
	# Or to take the command line object as it's argument and manage that.
	
	try:
		traj = Trajectory(traj_filename)
	
	except:
		raise Exception("Trajectory file not found.")

	# If not pure, process the trajectory data.
	traj_properties = []
	
	for atoms in traj:
		# Properties in traj object.
		atom_num = len(traj[-1])
		traj_properties.append \
			({"ekin": atoms.get_kinetic_energy()/atom_num,
	 		  "epot": atoms.get_potential_energy()/atom_num,
			  "etot": atoms.get_total_energy()/atom_num})
		
		# Derived properties.
		traj_properties[-1]["temperature"] = traj_properties[-1]["ekin"] / (1.5 * units.kB)

	return traj_properties

def visualize(traj_properties: dict[int, dict[str, float]], combined_plot: bool = False, **properties: bool) -> None:
	"""
	Creates plot(s) of parameters with respect to iteration step.

	Args:
		traj_properties (dict): A dictionary of traj-file properties given by read_traj_file.
		combined_plot (bool): A boolean for when you want to plot multiple properties on the same plot.
		properties (dict): A parapeter list of all properties you want to include, i.e. temperature=True.
	"""
	
	steps = range(len(traj_properties))
	
	plt.clf()
	for parameter, include in properties.items():
		if include: # Check local bool variables temperature, ekin, epot, etot
			y = []
			for step in steps:
				y.append(traj_properties[step][parameter])

			plt.plot(steps, y)
			
			if not combined_plot:
				plt.savefig(parameter+".pdf")
				plt.clf()
	
	if combined_plot and properties is not {}: 
		plt.savefig("combined.pdf")

if __name__ == "__main__":
	process_data("cu.traj")
