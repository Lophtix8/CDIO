import os
from ase.io import read, write


def construct_supercell(unitcell, x_scaling, y_scaling, z_scaling):
    """This funtion creates the supercells without a crack in them, ie just multiplies the
       unitcells by a given amount and names the file accordingly.

    Args:
        unitcell (str): Name of the filename for the unitcell
        x_scaling (int)
        y_scaling (int)
        z_scaling (int)

    Returns:
        str: The name of the supercell-file
    """
    material_name = unitcell.split(".")[0]
    try:
        unitcell = read(f"material_database/{unitcell}")
    except FileNotFoundError:
        print(f"{unitcell} is not in the material database.")
        return False
    supercell = unitcell*(x_scaling, y_scaling, z_scaling)
    filename = f"{material_name}_{x_scaling}x{y_scaling}x{z_scaling}.poscar" 
    write(filename, supercell, format="vasp", sort=True, direct=True)
    os.system(f"mv {filename} Supercells")
    return filename
    
def construct_crack(filename, custom_fracture, x_fracture, y_fracture, z_fracture):
    """Takes the previously created supercells and adds a crack in them, then names them accordingly.

    Args:
        filename (str): Name of the supercell.
        custom_fracture (bool): Not implemented yet.
        x_fracture (list): Interval of atoms to remove in x-direction.
        y_fracture (list): Interval of atoms to remove in y-direction.
        z_fracture (list): Interval of atoms to remove in z-direction.
    """
    if custom_fracture:
        return
    
    with open(f"Supercells/{filename}") as supercell:
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
    final_build = open(new_filename, 'w')
    final_build.writelines(supercell_lines)
    final_build.close()
    os.system(f"mv {new_filename} Fractured_supercells")
    
def delete_build(filename):
    os.remove(filename)

def main(config):
    """Takes in configs as dictionaries and creates simulation-cells from it

    Args:
        config (dict)
    """
    try:
        os.mkdir("Supercells")
    except:
        pass
    try:
        os.mkdir("Fractured_supercells")
    except:
        pass

    for unitcell in config["vasp_files"]:
        for supercell_number in range(len(config["x_scalings"])):
            x_scaling = config["x_scalings"][supercell_number]
            y_scaling = config["y_scalings"][supercell_number]
            z_scaling = config["z_scalings"][supercell_number]
            
            x_fracture = config["fracture"][0]
            y_fracture = config["fracture"][1]
            z_fracture = config["fracture"][2]
            custom_fracture = config["custom_fracture"]

            supercell_filename = construct_supercell(unitcell, x_scaling, y_scaling, z_scaling)
            if supercell_filename:
                construct_crack(supercell_filename, custom_fracture, x_fracture, y_fracture, z_fracture)
            else:
                continue
