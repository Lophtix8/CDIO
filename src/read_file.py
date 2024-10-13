from pathlib import Path
import sys
import logging

def read_file():
    # Main function that reads from file and should return the dictionary to build
    
    logger = setup_logging()
    
    config_file = input("Enter name of the config file: ").strip()
    try:
        f = open(config_file)
    except:
        print("Error: Config file does not exist.")
        sys.exit()
    lines = f.read()
    blocks = lines.split("\n\n")
    
    configs = []
    print("Converting data...")
    for block in blocks:
        configs.append(return_config_dicts(block))
        
    # Add some fail-safe checks here on the dictionaries. For instance to check that the length of
    # the x- y- and z-scaling lists are of the same length.
    # Also the logging needs to be fixed, right now it is only setup but not used.
    # It should be replace the print messages.
        
    print("Converting data succeded!")
    

def return_config_dicts(block):
    # Function that creates the dictionary for each block in the config file
    config_data = block.split('\n')
    config_dict = {}
    
    config_dict["vasp_files"] = get_vasp_files(config_data[0])
    config_dict["x_scalings"] = get_integer_list(config_data[1])
    config_dict["y_scalings"] = get_integer_list(config_data[2])
    config_dict["z_scalings"] = get_integer_list(config_data[3])
    config_dict["custom_frac"] = get_bool(config_data[4])
    config_dict["fracture"] = get_fracture_info(config_data[5])
    config_dict["temps"] = get_integer_list(config_data[6])
    config_dict["stress_plane"] = get_int(config_data[7])
    config_dict["t_interval"] = get_int(config_data[8])
    config_dict["iters"] = get_int(config_data[9])
    
    print(config_dict)
    return config_dict


def get_vasp_files(files_str):
    # Gets the vasp file names from the config file and checks so they exist.
    
    vasp_files = files_str.strip().split()
    for file_name in vasp_files:
        if not Path(file_name).exists():
            print("Error: File '" + file_name + "' does not exist.")
            #sys.exit()                 
    return vasp_files


def get_integer_list(string_of_ints):
    # Gets the values from the config file that are lists of ints, i.e temp, scalings etc.
    try:
        scalings = list(map(int, string_of_ints.strip().split()))
    except: 
        print("Error: Cannot convert element to an integer.")
        sys.exit()
    return scalings

def get_bool(custom_frac_str):
    # Gets the custom frac bool.
    
    custom_frac_str = custom_frac_str.strip().lower()
    if custom_frac_str == "false" or custom_frac_str == "true":
        return custom_frac_str
    else:
        print("Error: custom_frac value is not a bool.")
        sys.exit()

def get_fracture_info(fracture_str):
    # Gets the coordinates/intervals of the fracture.
    # Changed format on this line in config so that the x, y and z values can be separated easily. See config_test.txt.
    # Can change this back later of course, it is an idea of how it can be solved in a nice way.
    try:
        fracture_lst = fracture_str.strip().split(';')
        fracture_coords = [list(map(float, a.strip().split())) for a in fracture_lst]
    except:
        print("Error: Invalid format on fracture intervals or coordinates.")
        sys.exit()
    return fracture_coords

def get_int(int_as_string):
    # Gets values that are only an int.
    try:
        integer = int(int_as_string.strip())
    except:
        print("Error: Cannot convert string to an int.")
        sys.exit()
    return integer
    

def setup_logging(log_file='read_file.log', log_to_console=True, log_level=logging.DEBUG):
    
    # Creates a logger for this program
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Sets up logging to a logfile
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Sets up logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


if __name__ == "__main__":
	read_file()