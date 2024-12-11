import sys
import yaml
import argparse
import os
from pathlib import Path
import logging
from ase.calculators.kim.kim import KIM

logger = logging.getLogger("read_config")

def main(config_file):
    """The main function of the program. It reads the config file and creates
    a list for the dictionaries that will contain the config data.
    
    Args:
        config_file (str): The config file for the simulation.

    Returns:
        config_data (list): Contains dictionaries for each block in the config file.
    """

    try:
        file = open(config_file)
    except:
        logger.error("Config file does not exist, exiting the program.")
        sys.exit(1)
    
    try: 
        logger.info("Loading config file...")
        config_data = yaml.safe_load(file)
    except:
        logger.error("Could not load config file, exiting the program.")
        sys.exit(1)
        
    try:
        logger.info("Checking data in config file...")
        config_data = check_data(config_data)
    except (ValueError, TypeError, KeyError, FileNotFoundError) as e: 
        logger.error(f"An error was found: {e}, exiting the program.")
        sys.exit(1)
        
    logger.info("Checking config data complete!")
    
    return config_data

def check_data(config_data):
    """A function that checks for errors in the config file.

    Args:
        config_data (list): A list of dictionaries with the config data.
    
    Returns:
        config_data (list): A possible modification of the input config_data.
    """
    
    # More fail-safe checks can be added.
    
    keys_to_check = {"vasp_files", "x_scalings", "y_scalings", "z_scalings",
                     "custom_fracture", "fracture", "temps", "stress_plane", "t_interval",
                     "iterations", "potential", "strain_rate", "strain_interval", 
                     "relaxation_iterations", "relaxation_rate", "allocated_time"}
    
    for config in config_data:
        
        # Check so that all keys exist.
        if not keys_to_check.issubset(config.keys()):
            missing_keys = keys_to_check - config.keys()
            logger.error("Missing arguments in config: " + ', '.join(missing_keys))
            raise KeyError("KeyError")
        
        list_keys = {"vasp_files", "x_scalings", "y_scalings", "z_scalings",
                     "temps", "fracture"}
        int_keys = {"t_interval", "iterations", "relaxation_iterations", "strain_interval"}
        str_keys = {"stress_plane", "potential", "allocated_time"}
        bool_keys = {"custom_fracture"}
        float_keys = {"strain_rate", "relaxation_rate"}
        
        #Check that datatypes are valid
        if not all(isinstance(config[key], list) for key in list_keys):
            logger.error("Argument type should be list but is not.")
            raise TypeError("TypeError")
        
        if not all(isinstance(config[key], int) for key in int_keys):
            logger.error("Argument type should be int but is not.")
            raise TypeError("TypeError")
            
        if not all(isinstance(config[key], str) for key in str_keys):
            logger.error("Argument type should be str but is not.")
            raise TypeError("TypeError")
            
        if not all(isinstance(config[key], bool) for key in bool_keys):
            logger.error("Argument type should be bool but is not.")
            raise TypeError("TypeError")

        if not all(isinstance(config[key], float) for key in float_keys):
            logger.error("Argument type should be float but is not.")
            raise TypeError("TypeError")
        
        # Check so that the given OpenKim potential is installed on your system.
        try:
            potential_id = config["potential"]
            KIM(potential_id)
        except:
            logger.error(f"The potential_id: '{potential_id}' was not found.")
            raise ValueError("ValueError")
        
        # Check so that fracture has exactly three intervals. 
        if not config["custom_fracture"] and len(config["fracture"]) != 3:
            logger.error("fracture should have three dimensions.")
            raise ValueError("ValueError")
            
        # Check so that all files exist.
        curr_dir = os.path.dirname(__file__)
        for file in config["vasp_files"]:
            dest_path = os.path.join(curr_dir, f"material_database/{file}")
            if not Path(dest_path).exists():
                logger.error(f"The file: '{file}' was not found.")
                raise FileNotFoundError("FileNotFoundError")
        
        x_len = len(config["x_scalings"])
        y_len = len(config["y_scalings"])
        z_len = len(config["z_scalings"])
        
        # Lengths should be equal for the simulation to run correctly.
        if not x_len == y_len == z_len:
            logger.error("Inconsistent number of scalings.")
            raise ValueError("ValueError")
        
        if config["t_interval"] < 0:
            logger.error("t_interval needs to be a positive integer.")
            raise ValueError("ValueError")
        
        if config["iterations"] < 0:
            logger.error("iterations needs to be a positive integer.")
            raise ValueError("ValueError")
            
    return config_data


if __name__ == "__main__":
    # Parser should probably be moved to main program.
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    args = parser.parse_args()
    config_file = args.config_file
    main(config_file)
