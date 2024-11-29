import os
import logging
import copy
import yaml
import shutil
from ase import formula

from fracture_md import build, read_config

logger = logging.getLogger(__name__)

def prepare_and_queue(conf_path : str, project_dir="jobs", fractured=True, unfractured=False):
    """
    Function that combines prepare_jobs and queue_jobs. It will queue the jobs prepared with the given config file path.

    Args:
        conf_path (str): Path to the config file.

    Keyword Args:
        fractured=True (bool): Whether to prepare jobs for the poscars with fractures.
        unfractured=False (bool): Whether to prepare jobs for the poscars without fractures.
    """
    job_paths = prepare_jobs(conf_path, project_dir=project_dir, fractured=fractured, unfractured=unfractured)
    queue_jobs(job_paths)

def queue_jobs(job_paths : list[str] = []):
    """
    Function that queues the provided jobs, given as paths to .q files. If no paths are provided, the program will queue all non-ran jobs.

    Keyword Args:
        job_paths=[] (list[str])
    """
    for job_path in job_paths:
        os.system(f"bash {job_path}")
        #os.system(f"sbatch {job_path}")
    pass

def prepare_jobs(conf_path : str, project_dir="jobs", fractured=True, unfractured=False):
    """
    Function that prepares jobs configured in the provided config file.
    Args:
        conf_path (str): Path to the config file.

    Keyword Args:
        fractured=True (bool): Whether to prepare jobs for the poscars with fractures.
        unfractured=False (bool): Whether to prepare jobs for the poscars without fractures.

    Return:
        job_paths (list[str]): filepaths to all the jobs prepared.
    """
    job_paths = []
    sim_data = read_config.main(conf_path)
    working_dir = os.getcwd()
    abs_working_dir = ""
    if(project_dir[0] != "/"):
        abs_working_dir = os.path.join(working_dir, project_dir)
    else:
        abs_working_dir = project_dir
    
    for config in sim_data:    
            
        poscar_paths = build.main(config, abs_working_dir)
        
        if fractured:
            for poscar_path in poscar_paths['fractured'].keys():
                job_paths.extend(create_jobs(config, poscar_path))

        if unfractured:
            for poscar_path in poscar_paths['unfractured'].keys():
                job_paths.extend(create_jobs(config, poscar_path))

    return job_paths

def create_jobs(config : dict, poscar_filepath : str):
    """
    Function that prepares jobs for one poscar and provided simulation data.

    Args:
        config (dict): Simulation data given by read_config.main(conf_path).
        poscar_filepath (str): Filepath to the poscar.

    Returns:
        job_paths (list[str]): List of filepaths to the prepared jobs.

    """
    
    curr_dir = os.path.dirname(__file__)
    template_path = os.path.join(curr_dir,"template.q")

    crystal, symbols, scalings = get_crystal_info(poscar_filepath)
    temps = config['temps']
    
    poscar_name = os.path.basename(poscar_filepath)
    poscar_dir = os.path.dirname(poscar_filepath)
    
    job_paths = []

    for temp in temps:
        job_dir = os.path.join(poscar_dir, str(temp)+"K")
        os.makedirs(job_dir, exist_ok=True)
    
        temp_conf = copy.deepcopy(config)
        temp_conf['temps'] = [temp]
        temp_conf['vasp_files'] = [crystal + ".poscar"]
        temp_conf['x_scalings'] = [scalings[0]]
        temp_conf['y_scalings'] = [scalings[1]]
        temp_conf['z_scalings'] = [scalings[2]]

        name = poscar_name.removesuffix(".poscar") + "_" + str(temp) + "K"
        config_filepath = f'{job_dir}/{name}.yaml'
        
        with open(config_filepath, 'w') as file:
            yaml.dump([temp_conf], file, default_flow_style=None)
        job_path = write_job(template_path, poscar_filepath, config_filepath)
        
        job_paths.append(job_path)

    return job_paths

def write_job(template_path: str, poscar_filepath : str, config_filepath : str, nodes: int = 1, cores:int = 32) -> str:
    """
    Function that writes a job, i.e. .q file, given a template. Using provided template, the amount of nodes and cores can be modified.

    Args:
        template_path (str): Path to the template .q-file.
        poscar_path (str): Path to the poscar for the simulation.
        config_path (str): Path to the config file for the simulation.

    Keyword Args:
        nodes=1 (int): The amount of nodes for the simulation.
        cores=32 (int): The amound of cores for the simulation.

    Return:
        file_path (str): File path to the written .q files.

    """
    num = 0
    
    job_dir = os.path.dirname(config_filepath)
    file_path = os.path.join(job_dir, f"temp_job_{num}.q")
    #file_path = os.path.join(job_dir, f"temp_job_{num}.sh")

    # Check that file name isn't already used
    while(os.path.isfile(file_path)):
        num += 1
        file_path = os.path.join(job_dir, f"temp_job_{num}.q")
        #file_path = os.path.join(job_dir, f"temp_job_{num}.sh")
    
    job_file = open(file_path, 'w')
    ###
    #job_file.write("#!/bin/bash\n")
    ###

    lines = get_template(template_path)

    
    for line in lines:
        parts = line.split()
        
        # If it's an emtpy row, there is no need to go through all the if clauses
        if len(parts) == 0:
            job_file.write(line)
            continue
        
        if parts[0] == "#SBATCH":
            if parts[1] == "-N":
                parts[2] = str(nodes)
            
            if parts[1] == "-n":
                parts[2] = str(cores)

        output = ' '.join(parts)+"\n"
        job_file.write(output)
    
    curr_dir = os.path.dirname(__file__)
    job_file.write(f"time python3 {curr_dir}/md.py {poscar_filepath} {config_filepath}")
    
    # What python file to execute needs to be written here.
    job_file.close()
    return file_path

def get_template(file_path: str) -> list[str]:
    """
    Function that reads a template .q file.

    Args:
        file_path (str): File path to the template .q file.

    Returns:
        lines (list[str]): A list of all the lines in the template file.
    """
    
    if not os.path.isfile(file_path):
        raise Exception("Template not found.")
    
    file = open(file_path, 'r')
    lines = file.read().splitlines()

    file.close()
    
    return lines

def get_crystal_info(poscar_filepath : str):
    """
    Function that returns some information about the crystal given its filename.

    Args:
        poscar_filepth: File path to the poscar.

    Returns:
        crystal (str): The name of the unit crystal.
        symbols (str): A string containing only the symbols of the species in the crystal.
        scalings (list[int]): A list with the scalings in [x, y, z].

    """
    file_name : str
    try:
        file_name = os.path.basename(poscar_filepath).removesuffix(".poscar")

    except:
        logger.error("Filepath needs to point to a poscar.")
        raise NameError
    parts = file_name.split('_')
    scalings = []
    i = 0
    try:
        if parts[0] == 'fractured':
            i = 1   

        symbols = formula.Formula(parts[i])
        scalings = [int(x) for x in parts[i+1].split('x')]
    
    except:
        logger.error("File name does not follow the necessary conventions.")
        raise NameError

    species_list = [] 
    for species in symbols.count().keys():
        species_list.append(species)

    species_list.sort()
    crystal = parts[i]
    symbols = ''.join(species_list)

    return crystal, symbols, scalings

if __name__ == "__main__": 
    create_jobs()
