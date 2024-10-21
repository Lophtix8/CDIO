from build import *
from read_file_old import *
from md import * 

def main():

    struct_data, sim_data = read_file()
    supercell = build(struct_data) 

    run_md()
    delete_build()

if __name__ == "__main__":
    main()