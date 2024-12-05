
from fracture_md import read_config,build,job_manager


def main():
    conf_path = input("Please type the name of the config file")

    sim_data = read_config.main(conf_path)
    for config in sim_data:
        poscar_paths = build.main(config)
        for poscar_paths in poscar_paths['fractured'].keys():
            job_manager.create_job(config,poscar_paths)
