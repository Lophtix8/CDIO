import os
import argparse
from fracture_md import job_manager, md
import logging
from fracture_md import read_config,build

logger = logging.getLogger(__name__)


def prepare_jobs(config):
    job_manager.prepare_jobs(config)
    return

def queue_jobs(jobs_filepaths=[]):
    job_manager.queue_jobs(jobs_filepaths)
    return

def main():
    curr_dir = os.path.dirname(__file__)
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    parser.add_argument('type_of_job', type=str)
    args = parser.parse_args()
    config = args.config_file
    type_of_job = args.type_of_job
    
    if type_of_job == "p":
        prepare_jobs(f"{curr_dir}/{config}")
    
    elif type_of_job == "q":
        queue_jobs()
    
    elif type_of_job == "pq":
        job_manager.prepare_and_queue(config)
    
    else:
        logger.error("Invalid run option given at startup.")
        return
    return

if __name__ == "__main__":
    """
    configs = read_config.main("config_template.yaml")
    for config in configs:
        build.main(config)
    """
    main()
