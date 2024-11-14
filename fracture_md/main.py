import os
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

def prompt_user(): 
    which_config = input("Which config-file to run?\n")
    type_of_job = input("Only prepare jobs (1), queue prepared jobs (2) or prepare and queue simulations (3)\n")
    return which_config, type_of_job

def prepare_jobs(config):
    job_manager.prepare_jobs(config)
    return

def queue_jobs():
    #job_manager.queue_jobs()
    run_jobs()
    return

def prepare_and_queue(config):
    job_manager.prepare_jobs(config)
    #job_manager.queue_jobs()
    run_jobs()
    return

def main():
    curr_dir = os.path.dirname(__file__)
    config, type_of_job = prompt_user()
    
    if type_of_job == "1":
        prepare_jobs(f"{curr_dir}/{config}")
    
    elif type_of_job == "2":
        queue_jobs()
    
    elif type_of_job == "3":
        prepare_and_queue(f"{curr_dir}/{config}")
    
    else:
        print("Invalid option, exiting")
        return
    return

if __name__ == "__main__":
    main()
