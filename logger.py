import logging
import os

# def setup_logger(log_filename):
#     log_folder = "logs"    
#     os.makedirs(log_folder, exist_ok=True)    
#     log_path = os.path.join(log_folder, log_filename)
#     logging.basicConfig(
#         filename=log_path,
#         level=logging.INFO,
#         format="%(asctime)s %(levelname)s %(message)s"
#     )


# def logger(logger_name, log_filename):
#     log_folder = "logs"
#     os.makedirs(log_folder, exist_ok=True)
    
#     logger = logging.getLogger(logger_name)
#     logger.setLevel(logging.INFO)
    
#     if not logger.handlers:
#         log_path = os.path.join(log_folder, log_filename)
#         file_handler = logging.FileHandler(log_path)
#         formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
#         file_handler.setFormatter(formatter)
#         logger.addHandler(file_handler)
        
#     return logger


def get_logger(logger_name, log_filename):
    # This finds the absolute path of 'logger_config.py' (which is in the root directory)
    # and forces the 'logs' folder to always be created there.
    root_dir = os.path.dirname(os.path.abspath(__file__))
    log_folder = os.path.join(root_dir, "logs")
    
    os.makedirs(log_folder, exist_ok=True)
    
    # Initialize isolated logger instance
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding multiple handlers if the file is imported multiple times
    if not logger.handlers:
        log_path = os.path.join(log_folder, log_filename)
        file_handler = logging.FileHandler(log_path)
        
        # Format structure
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        
    return logger
