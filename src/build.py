from ase.visualize import view
from ase.io import read, write


unit_cell = read("Ti2AlN.cif")

TiAlN_super = mpstruct*(10,10,10)

view(mpstruct)


def build(config_file):
    with open(config_file, 'r', newline="@") config_file:
        materials = config_file.readlines()

    for idx, line in enumerate(config_data):
        materials.append(

def delete_build():
    pass
    
    
