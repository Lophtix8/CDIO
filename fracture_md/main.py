import argparse
import build
import read_config
import logging
import logging.config
import md
from os.path import dirname, abspath
import os
#from md import * 

def main():
    logging.config.fileConfig('logging.conf')
    
    logger = logging.getLogger(__name__)
    
    # Name of config file is needed when program is run from terminal.
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    args = parser.parse_args()
    config_file = args.config_file
    
    logger.info("Running read_config...")
    
    sim_data = read_config.main(config_file)
    
    logger.info("Running build with config data...")
    
    for config in sim_data:
        build.main(config)
    
    sim_queue = f"{dirname(abspath(__file__))}/Fractured_supercells"
    for file in os.listdir(sim_queue):
        try:
            md.run_md(file, 300, 100, 0.01)
        except:
            print("I am stuck here")
            continue

if __name__ == "__main__":
    main()
