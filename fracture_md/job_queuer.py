import os
import logging
import copy
import yaml
from ase import formula as formula

logger = logging.getLogger(__name__)

def queue_job(config : list, poscar_filepath : str):
    
    curr_dir = os.path.dirname(__file__)
    template = get_template(f"{curr_dir}/template.q")

    crystal_name = get_crystal_name(poscar_filepath)
    temps = config['temps']

    if not os.path.exists("jobs"):
        os.system(f"mkdir jobs")
    
    crystal_path = os.path.join("jobs", crystal_name)
    if not os.path.exists(crystal_path):
        os.system(f"mkdir {crystal_path}")
    
    
    poscar_name = os.path.basename(poscar_filepath)
    dest_path = os.path.join(crystal_path, poscar_name)
    if os.path.exists(dest_path):
        logger.warning("POSCAR already exists. Job skipped.")
        raise FileExistsError
    
    os.system(f"mv {poscar_filepath} {crystal_path}")
    
    for temp in temps:
        job_path = os.path.join(crystal_path, str(temp)+"K")
        if not os.path.exists(job_path):
            os.system(f"mkdir {job_path}")
    
        temp_conf = copy.deepcopy(config)
        temp_conf['temps'] = temp
        del temp_conf['vasp_files']

        name = poscar_name + "_" + str(temp) + "K"
        config_filepath = f'{job_path}/{name}.yaml'
        
        with open(config_filepath, 'w') as file:
            yaml.dump(temp_conf, file, default_flow_style=None)
        write_job(template, dest_path, config_filepath)

    return

def write_job(lines: list[str], poscar_filepath : str, config_filepath : str, nodes: int = 1, cores:int = 32) -> str:
    num = 0
    
    job_dir = os.path.dirname(config_filepath)
    file_path = os.path.join(job_dir, f"temp_job_{num}.q")

    # Check that file name isn't already used
    while(os.path.isfile(file_path)):
        num += 1
        file_path = os.path.join(job_dir, f"temp_job_{num}.q")
    
    job_file = open(file_path, 'w')
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
    job_file.write (f"python3 {curr_dir}/md.py {poscar_filepath} {config_filepath}")
    
    # What python file to execute needs to be written here.
    job_file.close()
    return file_path

def get_template(file_path: str) -> list[str]:
    
    if not os.path.isfile(file_path):
        raise Exception("Template not found.")
    
    file = open(file_path, 'r')
    lines = file.read().splitlines()

    file.close()
    
    return lines

def get_crystal_name(poscar_filepath : str):
    file_name : str
    try:
        file_name = os.path.basename(poscar_filepath).removesuffix(".poscar")

    except:
        logger.error("Filepath needs to point to a poscar.")
        raise NameError
    parts = file_name.split('_')

    try:
        if parts[0] == 'fractured':
            symbols = formula.Formula(parts[1])
        else:
            symbols = formula.Formula(parts[0])
    
    except:
        logger.error("File name does not follow the necessary conventions.")
        raise NameError

    species_list = [] 
    for species in symbols.count().keys():
        species_list.append(species)

    species_list.sort()

    return ''.join(species_list)

if __name__ == "__main__": 
    queue_job()