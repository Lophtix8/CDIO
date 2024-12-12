"""
 Copyright (c) 2024 JALL-E
 Licensed under the MIT License. See LICENSE file in the project root for details.
"""

from ase.io.trajectory import Trajectory
from ase import Atoms
from ase import units
from ase.calculators.kim.kim import KIM
from matplotlib import pyplot as plt
import pickle, os, yaml ,numpy

property_units = {"ekin": "eV", "epot": "eV", "etot": "eV", "stress": "GPa", "msd": "Å²", "L": ""}

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
    
    atom_num = len(traj[0])
    starting_size = traj[0].get_cell()

    for atoms in traj:
        # Properties in traj object.
        atoms.calc = calc
        curr_size = atoms.get_cell()
        traj_properties.append \
            ({"ekin": atoms.get_kinetic_energy()/atom_num,
               "epot": atoms.get_potential_energy()/atom_num,
              "etot": atoms.get_total_energy()/atom_num,
              "stress": atoms.get_stress(voigt=False)/units.GPa,
              "positions": atoms.get_positions(),
              "strain": numpy.subtract(numpy.divide(curr_size,starting_size), 1)})

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

def calc_avg_temp(traj_properties: list[dict[str, float]], step_interval = [0, -1]):
    
    if step_interval[0] < 0:
        step_interval[0] = 0
    
    if step_interval[1] >= len(traj_properties):
        step_interval[1] = -1

    if step_interval[1] == -1:
        step_interval[1] = len(traj_properties)-1
    
    total_temp = 0

    for i in range(step_interval[0], step_interval[1]):
        total_temp += traj_properties[i]['temperature']

    delta_step = step_interval[1]-step_interval[0]
    avg_temp = total_temp/delta_step

    return avg_temp

def calc_avg_position(traj_properties: list[dict[str,float]], step_interval = [0, -1]):
    
    step_interval = _check_calc_interval(traj_properties, step_interval)

    delta_step = step_interval[1]-step_interval[0]

    avg_position = []

    for i in range(len(traj_properties[0]['positions'])):
        avg_position.append([0,0,0])

    for i in range(step_interval[0], step_interval[1]):
        step = traj_properties[i]
        position = step["positions"]
        for j in range(len(position)):
            for k in range(3):
                avg_position[j][k] += position[j][k]/delta_step

    return avg_position

def _check_calc_interval(traj_properties: list[dict[str, float]], step_interval):
    if step_interval[0] < 0:
        step_interval[0] = 0
    
    if step_interval[1] >= len(traj_properties):
        step_interval[1] = -1

    if step_interval[1] == -1:
        step_interval[1] = len(traj_properties)-1

    return step_interval

def calc_msd(original_position, position):
    
    sd = 0

    for i in range(len(original_position)):
        for j in range(3):
            sd += (original_position[i][j]-position[i][j])**2
    msd = sd/len(original_position)
    return msd

def calc_self_diffusion(traj_properties: list[dict[str, float]], step_interval=[0, -1], dim = 3):
    
    step_interval = _check_calc_interval(traj_properties, step_interval)

    ref_position = traj_properties[0]['positions']
    first_position = traj_properties[step_interval[0]]['positions'] 
    second_position = traj_properties[step_interval[1]]['positions']

    first_msd = calc_msd(ref_position, first_position)
    second_msd = calc_msd(ref_position, second_position)
    
    self_diffusion = (second_msd-first_msd)/2*dim

    #avg_msd = calc_avg_msd(traj_properties, step_interval=step_interval)
    #self_diffusion = 1/(2*d) * avg_msd

    return self_diffusion

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
    
    strain_tensor = not numpy.isscalar(traj_properties[0]['strain'])

    start = 0
    stop = 0
    
    for i in range(len(traj_properties)):
        strain = traj_properties[i]['strain']
        if strain_tensor:
            strain = numpy.sqrt(sum([strain[i][i]**2 for i in range(3)]))

        if strain <= strain_interval[0]:
            start = i
        
        if strain > strain_interval[1]:
            break
        
        stop = i

    delta_stress = traj_properties[stop]['stress']-traj_properties[start]['stress']
    delta_strain = traj_properties[stop]['strain']-traj_properties[start]['strain']
    
    if strain_tensor:
        delta_strain=strain = numpy.sqrt(sum([delta_strain[i][i]**2 for i in range(3)]))

    cijs = delta_stress/delta_strain

    return cijs

def calc_yield_strength_point(traj_properties: list[dict[str, float]]):
    max_stress_strain = [[0, 0], [0,0], [0,0]]
    
    for step in traj_properties:
        for i in range(3):
            temp_stress = step["stress"][i][i]
            if temp_stress > max_stress_strain[i][1]:
                max_stress_strain[i][0] = numpy.max(step['strain'])
                max_stress_strain[i][1] = temp_stress
    
    return max_stress_strain

def plot_yield_strengths(materials_properties: dict[str, list[dict[str, float]]]):

    plot_properties = {"TiN" : {'color': 'blue', 'marker': 's' },
                        "Ti2N" : {'color': 'blue', 'marker': 'D'},
                        "TiC" : {'color':'black' , 'marker': 'o'},
                        "Ti2C" : {'color':'black' , 'marker': '^'},
                        "Ti" : {'color': 'red', 'marker': '+'},
                        "Fe" : {'color': 'gray', 'marker': '.'}}


    strain_stress_points = {}

    for material, traj_properties in materials_properties.items():
        ## Check for valid stress/strain point
        max_strain_stress = calc_yield_strength_point(traj_properties[1:])
        stress_direction = get_stress_direction(material)
        
        temp = traj_properties[-1]['temperature']
        #strength = max_strain_stress[stress_direction][1]
        toughness = max_strain_stress[stress_direction][0]
        if numpy.isnan(temp) or numpy.isnan(toughness):
            continue
       
        ## End check ##

        material_name = get_material_name(material)
 
        if material_name not in strain_stress_points.keys():
            strain_stress_points[material_name] = []
            
        
        strain_stress_points[material_name].append([temp,toughness])
    for material_name, points in strain_stress_points.items():
        temp = plot_properties[material_name]
        X,Y = zip(*sorted(points))
        plt.plot(X, Y, c=temp['color'], marker=temp['marker'], label = material_name)
        plt.legend(loc = "upper left")

    plt.xlabel("Temperature (K)")
    plt.ylabel("Strain")
    plt.savefig("toughness_vs_T.pdf")


def visualize(traj_properties: list[dict[str, float]], combined_plot: bool = False, strain_interval: list[float]=[0,0], **properties: bool) -> None:
    """
    Creates plot(s) of parameters with respect to iteration step.

    Args:
        traj_properties (dict): A dictionary of traj-file properties given by read_traj_file.
        combined_plot (bool): A boolean for when you want to plot multiple properties on the same plot.
        properties (dict): A parapeter list of all properties you want to include, i.e. temperature=True.
    """

    steps = range(1, len(traj_properties))
    strains = []

    for step in steps:
        strain_tensor = traj_properties[step]['strain']
        if numpy.isscalar(strain_tensor):
            strains.append(strain_tensor)
        else:
            strain = numpy.sqrt(sum([strain_tensor[i][i]**2 for i in range(3)]))
            strains.append(strain)
    
    plt.clf()
    plt.xlabel("strain")
    legends_comb = []
    for parameter, include in properties.items():
        legends = []
        if include: # Check local bool variables temperature, ekin, epot, etot
            y = []
            if parameter == "stress":
                directions = ["x", "y", "z"]
                for direction in directions:
                    legends.append(parameter+"."+direction)
                if strain_interval[1] != 0:
                    plt.axvline(x = strain_interval[0])
                    plt.axvline(x = strain_interval[1])
                    elastic_tensor = calc_elastic_components(traj_properties, strain_interval=strain_interval)
                    plt.title(f"Elasticity in GPa: {[int(elastic_tensor[i][i]) for i in range(3)]}")
                for step in steps:
                    stress = []
                    for i in range(3):
                        stress.append(traj_properties[step][parameter][i][i])
                    y.append(stress)

                for i in range(3):
                    plt.plot(strains, [y_1[i] for y_1 in y], label=f"{parameter}_{directions[i]}")
            
            elif parameter == "msd":
                legends.append(parameter)
                for step in steps:
                    y.append(calc_msd(traj_properties[0]['positions'], traj_properties[step]['positions']))
                    
                plt.plot(steps, y, label=parameter)
                
            elif parameter == "L":
                legends.append(parameter)
                for step in steps:
                    msd = calc_msd(traj_properties[0]['positions'], traj_properties[step]['positions'])
                    y.append(numpy.sqrt(msd)/(include))
                    
                plt.plot(steps, y, label=parameter)
                
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
