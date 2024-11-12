import os
import logging
import copy
import yaml
from ase import formula

logger = logging.getLogger(__name__)

def queue_job(config : list, poscar_filepath : str):
    
    crystal_name = get_crystal_name(poscar_filepath)
    temps = config[temps]
    
    for temp in temps:
        job_path = os.path.join(crystal_name, str(temp)+"K")

        if not os.path.exists(job_path):
            os.system(f"mkdir {job_path}")

        poscar_name = os.path.basename(poscar_filepath)
        dest_path = os.path.join(job_path, poscar_name)
        
        if os.path.exists(dest_path):
            logger.warning("POSCAR already exists. Job skipped.")
            raise FileExistsError

        os.system(f"mv {poscar_filepath} {dest_path}")

        temp_conf = copy.deepcopy(config)
        temp_conf[temps] = temp

        name = poscar_name.join(temp)
        
        with open(f'{name}.yaml', 'w') as file:
            yaml.dump(temp_conf, file)

    template = get_template("template.q")
    job = write_job(template)    

    return

def write_job(lines: list[str], nodes: int = 1, cores:int = 32) -> str:
    num = 0
    
    curr_dir = os.path.dirname(__file__)
    file_path = os.path.join(curr_dir, f"temp_job_{num}.q")

    # Check that file name isn't already used
    while(os.path.isfile(file_path)):
        num += 1
        file_path = f"temp_job_{num}.q"
    
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
    
    # What python file to execute needs to be written here.
    job_file.close()
    return file_path

def get_template(file_path: str) -> list[str]:
    
    if not os.path.isfile(file_path):
        raise Exception("Template not found.")
    
    file = open(file_path, 'r')
    lines = file.read().splitlines()
    
    return lines

def get_crystal_name(poscar_filepath : str):
    crystal : str
    try:
        crystal = os.path.basename(poscar_filepath).removesuffix(".poscar")

    except:
        logger.error("Filepath needs to point to a poscar.")
        raise NameError
    
    species_list : list[str]
    for species in formula.species(crystal):
        species_list.append(species)

    species_list.sort()

    return ''.join(species_list)

if __name__ == "__main__": 
    queue_job()