import argparse
import build
import read_config
#from md import * 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str)
    args = parser.parse_args()
    config_file = args.config_file
    

    sim_data = read_config.get_config_data(config_file)
    
    for config in sim_data:
        build.main(config)

    #run_md()
    #delete_build()

if __name__ == "__main__":
    main()
