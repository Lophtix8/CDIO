"""
 Copyright (c) 2024 JALL-E
 Licensed under the MIT License. See LICENSE file in the project root for details.
"""

import logging
import logging.config
from fracture_md import setup_logging
import os
import argparse
from fracture_md import job_manager


logger = logging.getLogger("main")

def queue_jobs(jobs_filepaths=[]):
    job_manager.queue_jobs(jobs_filepaths)
    return

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    parser.add_argument('type_of_job', type=str)
    args = parser.parse_args()
    config = args.config_file
    type_of_job = args.type_of_job
    return config, type_of_job

def main(config, type_of_job):
    curr_dir = os.path.dirname(__file__)    
    if type_of_job == "p":
        job_manager.prepare_jobs(f"{curr_dir}/{config}")
    
    elif type_of_job == "q":
        queue_jobs()
    
    elif type_of_job == "pq":
        job_manager.prepare_and_queue(config)
    
    else:
        logger.error("Invalid run option given at startup.")
        return
    return

if __name__ == "__main__":
    setup_logging.setup_logging('logging.conf')
    logger.info("Starting main program.")
    config, type_of_job = parser()
    main(config, type_of_job)
    
