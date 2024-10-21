from os import remove
from ase.io import read, write
from ase.visualize import view


def build(material, x_scaling, y_scaling, z_scaling, x_fracture, y_fracture, z_fracture):

    unitcell = read(material)
    supercell = unitcell*(x_scaling, y_scaling, z_scaling)

    material_name = material.split(".")[0]
    filename = f"{material_name}_{x_scaling}x{y_scaling}x{z_scaling}.poscar"
      
    write(filename, supercell, format="vasp", sort=True, direct=True)
    
    if z_fracture:
        view(supercell)


    # material_information: 
    # filenames(list), 
    # x(list), 
    # y(list), 
    # z(list), 
    # custom_fracture(bool), 
    # fracture_intervals(list(list)), 
    # temperature(list), 
    # miller_plane(string), 
    # time_interval(int), 
    # interations(int)

    
def delete_build(filename):
    remove(filename)
    
def main(supercell_specification):
    for filename in supercell_specification["vasp_files"]:
        for supercell_number in range(supercell_specification["x_scalings"]):
            x_scaling = supercell_specification["x_scalings"][supercell_number]
            y_scaling = supercell_specification["y_scalings"][supercell_number]
            z_scaling = supercell_specification["z_scalings"][supercell_number]
            
            x_fracture = supercell_specification["fracture"][0]
            y_fracture = supercell_specification["fracture"][1]
            z_fracture = supercell_specification["fracture"][2]
            
            build(filename, x_scaling, y_scaling, z_scaling, x_fracture, y_fracture, z_fracture)
    
if __name__ == "__main__":
    main()

