import os
import argparse
from fracture_md import job_manager, md


def run_jobs():
    for material in os.listdir("jobs"):
        poscars_to_run = []
        temps_to_run = []    
        for file in os.listdir(f"jobs/{material}"):
            if file.endswith(".poscar"):
                poscars_to_run.append(f"{material}/{file}")
            elif file.endswith("K"):
                temps_to_run.append(file.split("K")[0])

        for poscar in poscars_to_run:
            for temp in temps_to_run:
                md.run_md(poscar,float(temp),100,0.01)
    return

def prepare_jobs(config):
    job_manager.prepare_jobs(config)
    return

def queue_jobs():
    #job_manager.queue_jobs()
    run_jobs()
    return

def main():
    curr_dir = os.path.dirname(__file__)
    #config, type_of_job = prompt_user()
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
        job_manager.prepare_jobs(f"{curr_dir}/{config}")
        job_manager.queue_jobs(f"{curr_dir}/{config}")
    
    else:
        print("Invalid option. Exiting...")
        return
    return

if __name__ == "__main__":
    main()
