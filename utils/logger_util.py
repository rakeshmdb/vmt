import logging  
import os
from datetime import date


root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_path = os.path.join(root_path, "logs")
class LoggerUtility:  

    def __init__(self, script_name):
        self.file_name = str(date.today()) + "_" + script_name + "_" + "migrations_log.txt"
        
    def create_log_name(script_name):
        print(script_name)
        file_name = str(date.today()) + "_" + script_name + "_" + "migrations_log.txt"
        migrations_log_path = os.path.join(logs_path, file_name)
        return migrations_log_path

    @staticmethod  
    def setup_logger(script_name="genai"):  
        # Create a logger  
        logger = logging.getLogger('my_logger')  
        logger.setLevel(logging.DEBUG)  

        # Check if logger already has handlers
        if not logger.handlers:
            # Create console handler and set level to debug  
            console_handler = logging.StreamHandler()  
            console_handler.setLevel(logging.DEBUG)  

            # Create file handler and set level to debug
            file_handler = logging.FileHandler(LoggerUtility.create_log_name(script_name))
            file_handler.setLevel(logging.DEBUG)

            # Create formatter  
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  

            # Add formatter to console_handler  
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # Add console_handler to logger  
            logger.addHandler(console_handler)  

            # Add file_handler to logger
            logger.addHandler(file_handler)
    
        return logger  
