import os

def queue_job():
	
    template = get_template("template.q")
    job = write_job(template)    

    return

def write_job(lines: list[str], nodes: int = 1, cores:int = 32) -> str:
    num = 0
    
    curr_dir = os.path.dirname(__file__)
    file_path = os.path.join(curr_dir, f"temp_job_{num}.q")

    # Check that file name isn't already used
    while(os.path.isfile(file_path)):
        num += 1
        file_path = f"temp_job_{num}.q"
    
    job_file = open(file_path, 'w')
    for line in lines:
        parts = line.split()
        
        # If it's an emtpy row, there is no need to go through all the if clauses
        if len(parts) == 0:
            job_file.write(line)
            continue
        
        if parts[0] == "#SBATCH":
            if parts[1] == "-N":
                parts[2] = str(nodes)
            
            if parts[1] == "-n":
                parts[2] = str(cores)

        output = ' '.join(parts)+"\n"
        job_file.write(output)
    
    # What python file to execute needs to be written here.
    job_file.close()
    return file_path

def get_template(file_path: str) -> list[str]:
    
    if not os.path.isfile(file_path):
        raise Exception("Template not found.")
    
    file = open(file_path, 'r')
    lines = file.read().splitlines()
    
    return lines

if __name__ == "__main__":
	queue_job()