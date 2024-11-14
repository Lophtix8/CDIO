import job_manager
import os


def prompt_user(): 
    which_config = input("Which config-file to run?\n")
    type_of_job = input("Only prepare jobs (1), queue prepared jobs (2) or prepare and queue simulations (3)\n")
    return which_config, type_of_job

def prepare_jobs(config):
    job_manager.prepare_jobs(config)

def queue_jobs():
    job_manager.queue_jobs()

def prepare_and_queue(config):
    job_manager.prepare_jobs(config)
    job_manager.queue_jobs()
    
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

if __name__ == "__main__":
    main()
