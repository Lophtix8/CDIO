import logging
    
# Creates a logger.
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Sets up logging to a logfile.
# mode='w' means file is overwritten when program starts. 
# mode='a' would change to append to end of file instead of overwrite.
file_handler = logging.FileHandler("output.log", mode='w')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Sets up logging to the console.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)