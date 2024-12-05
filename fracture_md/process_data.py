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

def get_stress_direction(crystal_name: str):
	crystal_properties = crystal_name.split('_')
	
	stress_index = 2
	if crystal_properties[0] == "fractured":
		stress_index = 3
	
	cell_index = 4 # break the code
	stress_plane = crystal_properties[stress_index]
	if stress_plane == "100":
		cell_index = 0
	elif stress_plane == "010":
		cell_index = 1
	elif stress_plane == "001":
		cell_index = 2
	else:
		raise Exception("Stress plane can must have one 1s and two 0s.")
	return cell_index

def get_material_name(crystal_name: str):
	crystal_properties = crystal_name.split('_')
	name_index = 0
	if crystal_properties[0] == "fractured":
		name_index = 1

	return crystal_properties[name_index]
	

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
	
	crystal_name = os.path.basename(traj_filename)
	
	cell_index = get_stress_direction(crystal_name)

	atom_num = len(traj[0])
	starting_size = traj[0].cell[cell_index,cell_index]

	for atoms in traj:
		# Properties in traj object.
		atoms.calc = calc
		curr_size = atoms.cell[cell_index,cell_index]
		traj_properties.append \
			({"ekin": atoms.get_kinetic_energy()/atom_num,
	 		  "epot": atoms.get_potential_energy()/atom_num,
			  "etot": atoms.get_total_energy()/atom_num,
			  "stress": atoms.get_stress(voigt=False)/units.GPa,
			  "strain": (curr_size/starting_size)-1})

		# Derived properties.
		traj_properties[-1]["temperature"] = traj_properties[-1]["ekin"] / (1.5 * units.kB)

	return traj_properties

def get_results_dirs(job_dir: str) -> list[str]:
	"""
	Returns a list of paths to the simulation result directories in a job directory.

	Args:
		job_dir (str): The filepath to the job directory.

	Returns:
		results_dirs (list): List of paths to the directories containing the simulation results.
	"""
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

def write_all_to_pkl(job_dir: str) -> list[str]:
	"""
	Function that goes through an entire job directory and puts all the relevant information from the .traj files into corresponding .pkl files.
	If there is already a .pkl file, it will skip reading the .traj file.

	Args:
		job_dir (str): The job directory that will be gone through.
	
	Returns:
		pickle_paths (list): List of filepaths to the newly created .pkl files.
	"""
	results_dirs = get_results_dirs(job_dir)
	pickle_paths = []
	for results_dir in results_dirs:
		trajectory_paths = [os.path.join(results_dir, x) for x in os.listdir(results_dir) \
					  		if x.endswith(".traj")]
		for trajectory_path in trajectory_paths:
			
			### Read the corresponding config file to get corresponding OpenKIM potential ###
			crystal_name = os.path.basename(trajectory_path).rstrip('.traj')
			crystal_properties = crystal_name.split('_')
			
			temp = ""
			if crystal_properties[0] == "fractured":
				temp = crystal_properties[4]
			else:
				temp = crystal_properties[3]
			
			conf_file_path = os.path.join(results_dir.rstrip("/Simulation_results"), temp, crystal_name+".yaml")
			config_file = open(conf_file_path)
			config_data = yaml.safe_load(config_file)[0]
			config_file.close()
			### End config reading ###

			pickle_path = trajectory_path.rstrip('.traj') + ".pkl"
			if not os.path.isfile(pickle_path): # Write to .pkl if there isn't one already
				trajectory_data = read_traj_file(trajectory_path, config_data["potential"])
				write_to_pkl(trajectory_data, pickle_path)
				pickle_paths.append(pickle_path)

	return pickle_paths


def read_all_from_pkl(job_dir: str) -> dict[str, list[str, float]]:
	"""
	Function that goes through an entire job directory and reads all the result .pkl files. 
	It then returns a dictionary with the material as the key and the trajectory properties as the value.

	Args:
		job_dir (str): The job directory to go through.

	Returns:
		crystal_traj_properties (dict): Dictionary with the material as the key and the trajectory properties as the value. In the format given by process_data.read_traj_file()
	"""
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
	"""
	Function that writes trajectory properties onto a .pkl file.

	Args:
		traj_properties (list): Trajectory properties as given by process_data.read_traj_file().
		pkl_path (str): The filepath to where the .pkl file should be created.
	"""
	file = open(pkl_path, 'wb') 
	pickle.dump(traj_properties, file)
	file.close()

def read_from_pkl(pkl_path: str) -> list[dict[str, float]]:
	"""
	Function that reads a .pkl file and returns the trajectory properties stored within it.

	Args:
		pkl_path (str): Filepath to the .pkl containing the trajectory properties.
	
	Returns:
		traj_properties (list): Trajectory properties as given by proces_data.read_traj_file()
	"""
	file = open(pkl_path, 'rb')
	traj_properties = pickle.load(file)
	file.close()
	return traj_properties

def calc_elastic_components(traj_properties: list[dict[str, float]], strain_interval: list[int]=[0,0.05]):
	"""
	Calculates a 3x3 elasticity matrix using the stress matrices in the trajectory properties and the provided strain interval.

	Args:
		traj_properties (list): Trajectory properties as given by process_data.read_traj_file().
		strain_interval (list): List of two floats, defining the interval to calculate the elasticity tensor in.
	
	Returns:
		cijs (ndarray): 3x3 matrix of elasticity constants. 
	"""
	
	if len(strain_interval) > 2:
		raise TypeError("data_points has to be a 2-dimensional vector of numbers.")

	if strain_interval[0] < 0:
		raise ValueError("Start of strain inverval cannot be below zero.")

	if strain_interval[0] > strain_interval[1]:
		raise ValueError("Start of strain interval cannot be above end of strain interval.")
	
	start = 0
	stop = 0
	for i in range(len(traj_properties)):
		strain = traj_properties[i]['strain']
		if strain <= strain_interval[0]:
			start = i
		
		if strain > strain_interval[1]:
			break
		
		stop = i

	delta_stress = traj_properties[stop]['stress']-traj_properties[start]['stress']
	delta_strain = traj_properties[stop]['strain']-traj_properties[start]['strain']

	cijs = delta_stress/delta_strain

	return cijs

def calc_yield_strength_point(traj_properties: list[dict[str, float]]):
	max_stress_strain = [[0, 0], [0,0], [0,0]]
	
	for step in traj_properties:
		for i in range(3):
			temp_stress = step["stress"][i][i]
			if temp_stress > max_stress_strain[i][1]:
				max_stress_strain[i][0] = step['strain']
				max_stress_strain[i][1] = temp_stress
	
	return max_stress_strain

def plot_yield_strengths(materials_properties: dict[str, list[dict[str, float]]]):
	plt.clf()
	strain_stress_points = {}

	for material, traj_properties in materials_properties.items():
		material_name = get_material_name(material)
		if material_name not in strain_stress_points.keys():
			strain_stress_points[material_name] = []

		max_strain_stress = calc_yield_strength_point(traj_properties)
		stress_direction = get_stress_direction(material)
		x = max_strain_stress[stress_direction][0]
		y = max_strain_stress[stress_direction][1]

		strain_stress_points[material_name].append([x,y])
		
		color = "grey"
		if "C" in material_name:
			color = "black"
		elif "N" in material_name:
			color = "blue"

		plt.scatter(x, y, c=color)
	
	for material_name, points in strain_stress_points.items():
		tot_x = 0
		tot_y = 0
		for point in points:
			tot_x += point[0]
			tot_y += point[1]
		points_len = len(points)
		plt.text(tot_x/points_len, tot_y/points_len, material_name)

	plt.savefig("scatterplot.pdf")


def visualize(traj_properties: list[dict[str, float]], combined_plot: bool = False, strain_interval: list[float]=[0,0], **properties: bool) -> None:
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
				y = []
				directions = ["x", "y", "z"]
				for direction in directions:
					legends.append(parameter+"."+direction)
				if strain_interval[1] != 0:
					plt.axvline(x = strain_interval[0])
					plt.axvline(x = strain_interval[1])
					elastic_tensor = calc_elastic_components(traj_properties, strain_interval=strain_interval)
					plt.text(0, 0, f"Elasticity in GPa: {[elastic_tensor[i][i] for i in range(3)]}")
				for step in steps:
					stress = []
					for i in range(3):
						stress.append(traj_properties[step][parameter][i][i])
					y.append(stress)

				for i in range(3):
					plt.plot(strains, [y_1[i] for y_1 in y], label=f"{parameter}_{directions[i]}")
			else:
				legends.append(parameter)

				for step in steps:
					y.append(traj_properties[step][parameter])

				plt.plot(strains, y, label=parameter)
			
			if not combined_plot:
				plt.ylabel(property_units[parameter])
				plt.legend()
				plt.savefig(parameter+".pdf")
				plt.clf()
			else:
				legends_comb += legends
	
	
	if combined_plot and properties is not {}:
		plt.legend(legends_comb, loc="lower right") 
		plt.savefig("combined.pdf")

if __name__ == "__main__":
	process_data("cu.traj")
