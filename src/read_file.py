import sys
import yaml
import argparse
from pathlib import Path
from config_logger import logger


def read_file(config_file):
    """The main function of the program. It reads the config file and creates
    a list for the dictionaries that will contain the config data.

    Returns:
        List: Contains dictionaries for each block in the config file.
    """
    
    try:
        file = open(config_file)
    except:
        logger.error("Config file does not exist.")
        sys.exit()
    
    logger.info("Loading config file...")
    try:  
        config_data = yaml.safe_load(file)
    except:
        logger.error("Could not load config file.")
        sys.exit()
        
    check_config_data(config_data)
    logger.info("Done!")
    
    return config_data

def check_config_data(config_data):
    """A function that checks for errors in the config file.

    Args:
        config_data (list): A list of dictionaries with the config data.
    """
    
    # More fail-safe checks can be added like checking that all datatypes are correct.
    
    logger.info("Checking data in config file...")
    keys_to_check = {"vasp_files", "x_scalings", "y_scalings", "z_scalings",
                     "custom_fracture", "temps", "stress_plane", "t_interval",
                     "iterations"}
    
    for config in config_data:
        if not keys_to_check.issubset(config.keys()):
            missing_keys = keys_to_check - config.keys()
            logger.error("Missing arguments in config: " + ', '.join(missing_keys))
            sys.exit()
        
        existing_files = []
        for file in config["vasp_files"]:
            if not Path(file).exists():
                logger.warning("Removing file '" + file + "' from dictionary since it does not exist.")  
            else:
                existing_files.append(file)
        
        config["vasp_files"] = existing_files
        
        x_len = len(config["x_scalings"])
        y_len = len(config["y_scalings"])
        z_len = len(config["z_scalings"])
        temp_len = len(config["temps"])
        
        if not x_len == y_len == z_len == temp_len:
            logger.error("Inconsistent number of scalings and/or temps.")
            sys.exit() 
    return


if __name__ == "__main__":
    # Parser should probably be moved to main program.
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    args = parser.parse_args()
    config_file = args.config_file
    read_file(config_file)