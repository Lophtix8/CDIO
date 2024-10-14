
from ase.build import molecule
from ase.visualize import view
from ase.build import bulk
from ase.build import nanotube
from ase.lattice.cubic import FaceCenteredCubic
from ase.io import read
from ase.io import write

h2o = molecule("H2O")
cu_prim = bulk("Cu","fcc",a=3.6)
cu_cube = bulk("Cu","fcc",a=3.6,cubic=True)
cu_super = cu_cube*(4,4,4)

cnt1 = nanotube(6,0,length=4)

atoms = FaceCenteredCubic(directions=[[1,0,0],[0,1,0],[0,0,1]], symbol="Cu", size=(4,4,4), pbc=True)

mpstruct = read("Ar.poscar")

Ar_super = mpstruct*(2,2,2)
print(Ar_super.get_scaled_positions())

print(Ar_super.get_scaled_positions()[0])

#Ar_super_new = Ar_super.get_scaled_positions()

#Ar_super.set_positions(Ar_super.get_scaled_positions, apply_constraint=False)

#write("argon_gas.poscar", Ar_super, format="vasp")

#view(Ar_super)

