import os, shutil
from ase.io import read, write
from os.path import abspath, dirname
import shutil
import logging

logging.getLogger(__name__)

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
    write(os.path.join(filepath,filename), supercell, format="vasp", sort=True, direct=True)
    return filename
    
def construct_crack(dirpath, filename, custom_fracture, x_fracture, y_fracture, z_fracture):
    """Takes the previously created supercells and adds a crack in them, then names them accordingly.

    Args:
        dirpath (str): The path to where we will save the poscar-file.
        filename (str): Name of the supercell.
        custom_fracture (bool): Not implemented yet.
        x_fracture (list): Interval of atoms to remove in x-direction.
        y_fracture (list): Interval of atoms to remove in y-direction.
        z_fracture (list): Interval of atoms to remove in z-direction.
    """
    curr_dir = os.path.dirname(__file__)

    if custom_fracture:
        return
    
    with open(os.path.join(curr_dir, f"Supercells/{filename}")) as supercell:
        supercell_lines = supercell.readlines()
    
    lines_to_remove = []
    for line in supercell_lines[8:]: #the coordinates start on line 8 in poscar-files
        if (x_fracture[0] <= float(line.split()[0]) <= x_fracture[1])\
        and (y_fracture[0] <= float(line.split()[1]) <= y_fracture[1])\
        and (z_fracture[0] <= float(line.split()[2]) <= z_fracture[1]):
            lines_to_remove.append(line)

    for line in lines_to_remove:
        try:
            supercell_lines.remove(line)
        except:
            pass

    supercell_lines[6] = str(len(supercell_lines[8:])) + '\n' #the number of atoms is always on line 6 in poscar-files
    new_filename = f"fractured_{filename}"
    final_build = open(os.path.join(dirpath,new_filename), 'w')
    final_build.writelines(supercell_lines)
    final_build.close()
    

def delete_build(filename):
    os.remove(filename)

def main(config,dirpath):
    """Takes in configs as dictionaries and creates simulation-cells from it

    Args:
        config (dict): The config-dictionary is parsed from the input config-file specified in the user manual.
        dirpath (str): The path to where we will save the poscar-file.
    """

    file_paths = {'fractured' : {}, 'unfractured' : {}}

    for unitcell in config["vasp_files"]:
        for supercell_number in range(len(config["x_scalings"])):
            x_scaling = config["x_scalings"][supercell_number]
            y_scaling = config["y_scalings"][supercell_number]
            z_scaling = config["z_scalings"][supercell_number]
            
            x_fracture = config["fracture"][0]
            y_fracture = config["fracture"][1]
            z_fracture = config["fracture"][2]
            custom_fracture = config["custom_fracture"]

            supercell_filename = construct_supercell(dirpath, unitcell, x_scaling, y_scaling, z_scaling)
            if supercell_filename:
                construct_crack(dirpath, supercell_filename, custom_fracture, x_fracture, y_fracture, z_fracture)
                unfractured_filepath = os.path.join(dirpath, supercell_filename)
                fractured_filepath = os.path.join(dirpath, f"fractured_{supercell_filename}")
                file_paths['unfractured'][unfractured_filepath] = config
                file_paths['fractured'][fractured_filepath] = config
            else:
                continue

    return file_paths
