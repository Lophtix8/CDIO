from ase.io.trajectory import Trajectory
from ase import Atoms
from ase import units
from ase.calculators.kim.kim import KIM
from matplotlib import pyplot as plt
import pickle, os, yaml ,numpy

property_units = {"ekin": "eV", "epot": "eV", "etot": "eV", "stress": "GPa"}

def process_data(traj_filename: str):
	"""
	Main function for processing data. Depending on the arguments, it will create plots, calculate properties etc.
	"""
	# This is just a temporary example
	traj_properties = read_traj_file(traj_filename)
	visualize(traj_properties, ekin=True, epot=True, etot=True, combined_plot=True)
	visualize(traj_properties, temperature=True)
	return

def read_traj_file(traj_filename: str, potential_id: str) -> list[dict[str, float]]:
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

	traj_properties = []

	print(f"Reading trajectory file for: {os.path.basename(traj_filename).rstrip('.traj')}")

	calc = KIM(potential_id)
    
	atom_num = len(traj[0])
	starting_z = traj[0].cell[2,2]

	for atoms in traj:
		# Properties in traj object.
		atoms.calc = calc
		curr_z = atoms.cell[2,2]
		traj_properties.append \
			({"ekin": atoms.get_kinetic_energy()/atom_num,
	 		  "epot": atoms.get_potential_energy()/atom_num,
			  "etot": atoms.get_total_energy()/atom_num,
			  "stress": atoms.get_stress()/units.GPa,
			  "strain": (curr_z/starting_z)-1})

		# Derived properties.
		traj_properties[-1]["temperature"] = traj_properties[-1]["ekin"] / (1.5 * units.kB)

	return traj_properties

def get_results_dirs(job_dir: str) -> list[str]:
	results_dirs = []
	if not os.path.isabs(job_dir):
		job_dir = os.path.join(os.getcwd(), job_dir)

	material_dirs = [os.path.join(job_dir, x) for x in os.listdir(job_dir) \
				   	 if os.path.isdir(os.path.join(job_dir, x))]
	
	for material_dir in material_dirs:
		results_dir = os.path.join(material_dir, "Simulation_results")
		
		if not os.path.isdir(results_dir):
			continue # In case the simulation has not been run yet
		results_dirs.append(results_dir)

	return results_dirs

def write_all_to_pkl(job_dir: str):
	results_dirs = get_results_dirs(job_dir)
	for results_dir in results_dirs:
		trajectory_paths = [os.path.join(results_dir, x) for x in os.listdir(results_dir) \
					  		if x.endswith(".traj")]
		for trajectory_path in trajectory_paths:
			
			### Read the corresponding config file to get corresponding OpenKIM potential ###
			crystal_name = os.path.basename(trajectory_path).rstrip('.traj')
			crystal_properties = crystal_name.split('_')
			
			temp = ""
			if crystal_properties[0] == "fractured":
				temp = crystal_properties[3]
			else:
				temp = crystal_properties[2]
			
			conf_file_path = os.path.join(results_dir.rstrip("/Simulation_results"), temp, crystal_name+".yaml")
			config_file = open(conf_file_path)
			config_data = yaml.safe_load(config_file)[0]
			config_file.close()
			### End config reading ###

			trajectory_data = read_traj_file(trajectory_path, config_data["potential"])
			pickle_path = trajectory_path.rstrip('.traj') + ".pkl"
			write_to_pkl(trajectory_data, pickle_path)


def read_all_from_pkl(job_dir: str) -> dict[str, list[str, float]]:
	results_dirs = get_results_dirs(job_dir)
	pickle_paths = []
	for results_dir in results_dirs:

		pickle_paths += [os.path.join(results_dir, x) for x in os.listdir(results_dir) \
				 			if x.endswith('.pkl')]
	
	crystal_traj_properties = {}
	for pickle_path in pickle_paths:
		crystal_name = os.path.basename(pickle_path).strip('.pkl')
		traj_properties = read_from_pkl(pickle_path)
		crystal_traj_properties[crystal_name] = traj_properties

	return crystal_traj_properties

def write_to_pkl(traj_properties: list[dict[str, float]], pkl_path: str) -> None:
	file = open(pkl_path, 'wb') 
	pickle.dump(traj_properties, file)
	file.close()

def read_from_pkl(pkl_path: str) -> list[dict[str, float]]:
	file = open(pkl_path, 'rb')
	traj_properties = pickle.load(file)
	file.close()
	return traj_properties

def calc_elastic_tensor(traj_properties: list[dict[str, float]], data_points: list[int]=[0,10]):
	
	if len(data_points) > 2 or type(data_points[0]) != int or type(data_points[1]) != int:
		raise TypeError("data_points has to be a 2-dimensional vector of integers.")

	if (data_points[0]) > len(traj_properties) or data_points[1] > len(traj_properties):
		return

	stress_derivative = []
	start = data_points[0]
	stop = data_points[1]
	
	delta_stress = traj_properties[stop]['stress']-traj_properties[start]['stress']
	delta_strain = traj_properties[stop]['strain']-traj_properties[start]['strain']

	cijs = delta_stress/delta_strain

	return cijs
	


def visualize(traj_properties: list[dict[str, float]], combined_plot: bool = False, **properties: bool) -> None:
	"""
	Creates plot(s) of parameters with respect to iteration step.

	Args:
		traj_properties (dict): A dictionary of traj-file properties given by read_traj_file.
		combined_plot (bool): A boolean for when you want to plot multiple properties on the same plot.
		properties (dict): A parapeter list of all properties you want to include, i.e. temperature=True.
	"""

	steps = range(len(traj_properties))
	strains = []

	for step in steps:
		strains.append(traj_properties[step]['strain'])
	
	plt.clf()
	plt.xlabel("strain")
	legends_comb = []
	for parameter, include in properties.items():
		legends = []
		if include: # Check local bool variables temperature, ekin, epot, etot
			if parameter == "stress":
				directions = ["xx", "yy", "zz", "yz", "xz", "xy"]
				for direction in directions:
					legends.append(parameter+"."+direction)
			else:
				legends.append(parameter)

			y = []
			for step in steps:
				y.append(traj_properties[step][parameter])

			plt.plot(strains, y)
			
			if not combined_plot:
				plt.ylabel(property_units[parameter])
				plt.legend(legends, loc="lower right")
				plt.savefig(parameter+".pdf")
				plt.clf()
			else:
				legends_comb += legends
	
	
	if combined_plot and properties is not {}:
		plt.legend(legends_comb, loc="lower right") 
		plt.savefig("combined.pdf")

if __name__ == "__main__":
	process_data("cu.traj")
