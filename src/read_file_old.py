from pathlib import Path
import sys
import logging

def read_file():
    """The main function of the program. It reads the config file and creates
    a list for the dictionaries that will contain the config data.

    Returns:
        List: Contains dictionaries for each block in the config file.
    """
    
    try:
        # Insert the config file that should be used.
        f = open("config_test.txt")
    except:
        logger.error("Config file does not exist.")
        sys.exit()
    
    logger.info("Reading config file...")   
    lines = f.read()
    
    # Divides the config file into blocks.
    # A block specifies simulation data/settings for one or more vasp-files.
    blocks = lines.split("\n\n")
    
    configs = []
    
    i = 1
    for block in blocks:
        configs.append(return_config_dicts(block, i))
        i += 1
    
    print(configs)
    logger.info("Done!")
    
    return configs
    

def return_config_dicts(block, i):
    """Converts each line of a block into the desired datatype and format.
    It calls other functions for the data conversion for each line and checks
    for possible errors in the config file.

    Args:
        block (str): Contains settings for simulation on one or more vasp-files.
        i (int): The block number, i.e the i:th block in the config file.

    Returns:
        dict: Contains the data of a block in the desired format.
    """
    
    logger.info("Converting data for config block " + str(i) + "...")
    config_data = block.strip().split('\n')
    
    if len(config_data) != 10:
        logger.error("Invalid format on the config block.")
        sys.exit()
    
    config_dict = {}
    config_dict["vasp_files"] = get_vasp_files(config_data[0])
    config_dict["x_scalings"] = get_integer_list(config_data[1])
    config_dict["y_scalings"] = get_integer_list(config_data[2])
    config_dict["z_scalings"] = get_integer_list(config_data[3])
    config_dict["custom_frac"] = get_bool(config_data[4])
    config_dict["fracture"] = get_fracture_info(config_data[5], config_dict["custom_frac"])
    config_dict["temps"] = get_integer_list(config_data[6])
    config_dict["stress_plane"] = get_int(config_data[7])
    config_dict["t_interval"] = get_int(config_data[8])
    config_dict["iters"] = get_int(config_data[9])
    
    if not (len(config_dict["x_scalings"]) == len(config_dict["y_scalings"])
            and len(config_dict["x_scalings"]) == len(config_dict["z_scalings"])
            and len(config_dict["x_scalings"]) == len(config_dict["temps"])):
        logger.error("Inconsistent number of x-, y-, z-scalings and/or temps")
    
    logger.info("Succeded converting data for block " + str(i) + "!")
    
    # Suggestion: Change temps list to an int, i.e only one temp for each block.
    # Possibility for more fail-safe checks.
    
    return config_dict


def get_vasp_files(files_str):
    """Converts a string to a list with paths to vasp-files.

    Args:
        files_str (str): Contains the vasp-file names separated with a space.

    Returns:
        list: A list with the vasp-file paths.
    """
    
    # Uncomment sys.exit() when we have vasp-files.
    vasp_files = files_str.strip().split()
    for file_name in vasp_files:
        if not Path(file_name).exists():
            #logger.error("File '" + file_name + "' does not exist.")
            #sys.exit()
            continue              
    return vasp_files


def get_integer_list(string_of_ints):
    """Converts a string to a list of ints. Each int should be >=0.

    Args:
        string_of_ints (str): Contains the ints separated with a space.

    Returns:
        list: A list of ints. It can for instance be the supercell sizes.
    """
    try:
        integers = list(map(int, string_of_ints.strip().split()))
        for element in integers:
            if element < 0:
                logger.error("All integers must be larger than or equal to zero.")
                sys.exit()
    except: 
        logger.error("Cannot convert element to an integer.")
        sys.exit()
    return integers

def get_bool(custom_frac_str):
    """Converts a string to a bool. In this case a bool saying if the fracture
    is specified in coordinates or intervals.

    Args:
        custom_frac_str (str): A string that should be true or false.

    Returns:
        bool: The string converted to either true or false.
    """
    
    custom_frac_str = custom_frac_str.strip().lower()
    if custom_frac_str == "false":
        return False
    elif custom_frac_str == "true":
        return True
    else:
        logger.error("Custom fracture is not a bool.")
        sys.exit()

def get_fracture_info(fracture_str, custom_frac):
    """Converts a string of fracture intervals/coordinates to a list. The list
    will either contain lists with atom coordinates: [x_i, y_i, z_i], or three
    lists with intervals in each direction: [x_start, x_stop].

    Args:
        fracture_str (str): Specifies the fracture as a string.
        custom_frac (bool): Specifies which format fracture_str will be on.

    Returns:
        _type_: _description_
    """
    try:
        fracture_lst = fracture_str.strip().split(';')
        fracture_coords = [list(map(float, a.strip().split())) for a in fracture_lst]
    except:
        logger.error("Invalid format on fracture intervals/coordinates.")
        sys.exit()
        
    if custom_frac and all(len(lst) == 3 for lst in fracture_coords):
        return fracture_coords
    elif not (custom_frac and all(len(lst) == 2 for lst in fracture_coords) and
              len(fracture_coords) == 3):
        return fracture_coords
    else:
        logger.error("Invalid format on fracture intervals/coordinates.")
        sys.exit()
        

def get_int(int_as_string):
    """Converts a string to an int.

    Args:
        int_as_string (str): The string to be converted to an int.

    Returns:
        int: The int that has been converted. Can for instance be the
        number of iterations in the simulation.
    """

    try:
        integer = int(int_as_string.strip())
        if integer < 0:
            logger.error("All integers must be larger than or equal to zero.")
    except:
        logger.error("Cannot convert string to an int.")
        sys.exit()
    return integer
    

def setup_logging(log_file='read_file.log', log_to_console=True, log_level=logging.DEBUG):
    """A function that sets up logging for the program so that it is easier to
    debug. It specifies which file it writes to and rules for logging in the
    console and file. 

    Args:
        log_file (str, optional): Specifies the file for the logging. 
        Defaults to 'read_file.log'.
        log_to_console (bool, optional): Specifies if console should be used for
        logging. Defaults to True.
        log_level (class 'function', optional): Sets the minimum level of logging
        messages for them to be written to the log file. Defaults to logging.DEBUG.

    Returns:
        class logging.Logger: The logger with the specified rules for this program.
    """
    
    # Creates a logger.
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Sets up logging to a logfile.
    # mode='w' means file is overwritten when program starts. 
    # mode='a' would change to append to end of file instead of overwrite.
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Sets up logging to the console.
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


if __name__ == "__main__":
    logger = setup_logging()
    read_file()