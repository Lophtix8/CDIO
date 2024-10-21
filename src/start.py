
from ase.visualize import view
from ase.io import read
from ase.io import write


mpstruct = read("Li3Fe.poscar")
Ar_super = mpstruct*(2,2,2)

write("life.poscar", Ar_super, format="vasp", sort=True, direct=True)

position_string = ""
#print(Ar_super.get_scaled_positions())
for coordinate_triple in Ar_super.get_scaled_positions():
    print(str(coordinate_triple))
    for coordinate in coordinate_triple:
        #print(coordinate)
        position_string += '{0:.9f}'.format(coordinate) + "  "
    
    position_string += '\n'
    #position_string += str(coordinate_triple)#'{0:.9f}'.format
print(position_string)

#write("life.poscar", Ar_super, format="vasp")

"""
with open("life.poscar",'r') as f:
    definition_string = ""
    for line in f.readlines():
        if line.startswith("Cartesian"):
            break
        else:
            print(line)
            definition_string += str(line)

write_string = definition_string + "Direct\n" + position_string

#with open("life.poscar", 'w') as f:
    #f.write(write_string)

mpstruct_test = read("life.poscar")
view(mpstruct_test)"""
