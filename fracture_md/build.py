import os, shutil
from ase.io import read, write
from ase import Atoms
from os.path import abspath, dirname
import shutil
import logging

logger = logging.getLogger(__name__)

DIR_NAME = dirname(abspath(__file__))

def construct_supercell(dirpath, unitcell, x_scaling, y_scaling, z_scaling):
    """This funtion creates the supercells without a crack in them, ie just multiplies the
       unitcells by a given amount and names the file accordingly.

    Args:
        dirpath (str): The path to where we will save the poscar-file.
        unitcell (str): Name of the filename for the unitcell
        x_scaling (int)
        y_scaling (int)
        z_scaling (int)

    Returns:
        str: The name of the supercell-file
    """
    material_name = unitcell.split(".")[0]

    curr_dir = os.path.dirname(__file__)

    try:
        unitcell = read(os.path.join(curr_dir, f"material_database/{unitcell}"))
    except FileNotFoundError:
        return False
    
    supercell = unitcell*(x_scaling, y_scaling, z_scaling)
    filename = f"{material_name}_{x_scaling}x{y_scaling}x{z_scaling}.poscar" 
    write(os.path.join(dirpath,filename), supercell, format="vasp", sort=True, direct=True)
    return filename, supercell

def construct_crack(dirpath, filename, supercell, custom_fracture, x_fracture, y_fracture, z_fracture):
    """Takes the previously created supercells and adds a crack in them, then names them accordingly.

    Args:
        dirpath (str): The path to where we will save the poscar-file.
        filename (str): Name of the supercell.
        supercell (Atoms()): An Atoms()-object of the supercell to put a crack into.
        custom_fracture (bool): Not implemented yet.
        x_fracture (list): Interval of atoms to remove in x-direction.
        y_fracture (list): Interval of atoms to remove in y-direction.
        z_fracture (list): Interval of atoms to remove in z-direction.
    """
    fractured_supercell = Atoms()
    fractured_supercell.set_cell(supercell.get_cell())
    if custom_fracture:
        return
    for atom in supercell:

        position = atom.scaled_position
        if (x_fracture[0] <= position[0] <= x_fracture[1])\
        and (y_fracture[0] <= position[1] <= y_fracture[1])\
        and (z_fracture[0] <= position[2] <= z_fracture[1]):
            continue
        else:
            fractured_supercell.append(atom)
    
    new_filename = f"fractured_{filename}" 
    write(os.path.join(dirpath,new_filename), fractured_supercell, format="vasp", sort=True, direct=True)
    

def delete_build(filename):
    os.remove(filename)

def main(config,project_dir):
    """Takes in configs as dictionaries and creates simulation-cells from it

    Args:
        config (dict): The config-dictionary is parsed from the input config-file specified in the user manual.
        project_dir (str): The path to where we will save the simulations.
    """
    
    file_paths = {'fractured' : {}, 'unfractured' : {}}

    for unitcell in config["vasp_files"]:
        dirpath = os.path.join(project_dir, unitcell.split('.')[0])
        os.makedirs(dirpath, exist_ok=True)

        for supercell_number in range(len(config["x_scalings"])):
            x_scaling = config["x_scalings"][supercell_number]
            y_scaling = config["y_scalings"][supercell_number]
            z_scaling = config["z_scalings"][supercell_number]
            
            x_fracture = config["fracture"][0]
            y_fracture = config["fracture"][1]
            z_fracture = config["fracture"][2]
            custom_fracture = config["custom_fracture"]
            
            supercell_filename, supercell = construct_supercell(dirpath, unitcell, x_scaling, y_scaling, z_scaling)
            if supercell_filename:
                construct_crack(dirpath, supercell_filename, supercell, custom_fracture, x_fracture, y_fracture, z_fracture)
                unfractured_filepath = os.path.join(dirpath, supercell_filename)
                fractured_filepath = os.path.join(dirpath, f"fractured_{supercell_filename}")
                file_paths['unfractured'][unfractured_filepath] = config
                file_paths['fractured'][fractured_filepath] = config
            else:
                continue
    logger.info(f"Successfully built {len(file_paths['fractured'].keys())} fractured supercells.")
    return file_paths
