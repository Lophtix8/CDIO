from ase.io import read
from ase.visualize import view

supercell = read("Supercells/Al_8x25x15.poscar")
fracture = read("Fractured_supercells/fractured_Al_8x25x15.poscar")

view(supercell)
view(fracture)