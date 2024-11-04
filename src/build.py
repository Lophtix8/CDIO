import os
from ase.io import read, write


def construct_supercell(unitcell, x_scaling, y_scaling, z_scaling):
    material_name = unitcell.split(".")[0]
    unitcell = read(f"Unitcells/{unitcell}")
    supercell = unitcell*(x_scaling, y_scaling, z_scaling)
    filename = f"{material_name}_{x_scaling}x{y_scaling}x{z_scaling}.poscar" 
    write(filename, supercell, format="vasp", sort=True, direct=True)
    os.system(f"mv {filename} Supercells")
    return filename
    
def construct_crack(filename, custom_fracture, x_fracture, y_fracture, z_fracture):
    if custom_fracture:
        return
    
    with open(f"Supercells/{filename}") as supercell:
        supercell_lines = supercell.readlines()
    
    lines_to_remove = []
    for line in supercell_lines[8:]:
        if (x_fracture[0] <= float(line.split()[0]) <= x_fracture[1])\
        or (y_fracture[0] <= float(line.split()[1]) <= y_fracture[1])\
        or (z_fracture[0] <= float(line.split()[2]) <= z_fracture[1]):
            lines_to_remove.append(line)

    for line in lines_to_remove:
        try:
            supercell_lines.remove(line)
        except:
            pass

    supercell_lines[6] = str(len(supercell_lines[8:])) + '\n'
    new_filename = f"fractured_{filename}"
    final_build = open(new_filename, 'w')
    final_build.writelines(supercell_lines)
    final_build.close()
    os.system(f"mv {new_filename} Fractured_supercells")
    
def delete_build(filename):
    os.remove(filename)

def main(config):
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
            construct_crack(supercell_filename, custom_fracture, x_fracture, y_fracture, z_fracture)
if __name__ == "__main__":
    
    config = {"vasp_files": ["Al.poscar"],
                                "x_scalings": [2, 4, 8],
                                "y_scalings": [10, 15, 25],
                                "z_scalings": [5, 10, 15],
                                "custom_fracture": False,
                                "fracture": [[0.4, 0.6], [0.4, 0.6], [0.4, 0.6]],
                                "temps": [0, 50, 300, 20],
                                "stress_plane": "100",
                                "t_interval": 5,
                                "iterations": 1000}

    main(config)

