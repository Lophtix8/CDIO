"""
 Copyright (c) 2024 JALL-E
 Licensed under the MIT License. See LICENSE file in the project root for details.
"""

import logging
import logging.config
from configparser import ConfigParser
import os

def setup_logging(log_config_file):
    """Set up logging configuration from a file."""
    execution_path = os.getcwd()
    log_file_path = os.path.join(execution_path, 'fracture_md.log')
    
    current_directory = os.path.dirname(os.path.abspath(__file__))
    log_config_file_path = os.path.join(current_directory, log_config_file)
    
    config_parser = ConfigParser()
    with open(log_config_file_path, 'r') as f:
        config_parser.read_file(f)
        
    config_parser.set('handler_file_handler', 'args', f"('{log_file_path}', 'a')")
    
    with open(log_config_file_path, 'w') as f:
        config_parser.write(f)
    
    logging.config.fileConfig(log_config_file_path)
    return