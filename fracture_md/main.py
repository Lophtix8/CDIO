import os
import argparse
from fracture_md import job_manager, md
import logging
from fracture_md import read_config,build


logger = logging.getLogger(__name__)

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    parser.add_argument('type_of_job', type=str)
    args = parser.parse_args()
    config = args.config_file
    type_of_job = args.type_of_job
    return config, type_of_job

def main(config, type_of_job, super_computer=True):
    curr_dir = os.path.dirname(__file__)
    
    if type_of_job == "p":
        job_manager.prepare_jobs(f"{curr_dir}/{config}")
    
    elif type_of_job == "q":
        job_manager.queue_jobs(super_computer=super_computer)
    
    elif type_of_job == "pq":
        job_manager.prepare_and_queue(config, super_computer=super_computer)
    
    else:
        logger.error("Invalid run option given at startup.")
        return
    return

if __name__ == "__main__":
    
    config, type_of_job = parser()
    main(config, type_of_job,False)
