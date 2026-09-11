import os
import logging
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a custom logger that writes to a file in the logs/ folder.
    The log format includes timestamp, log level, filename, function name, and message.
    """
    # 1. Create logs directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    
    # 2. Set up the log file name (e.g., app_2026-09-05.log)
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"app_{date_str}.log")
    
    # 3. Create the logger
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if the logger already exists
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Set the base logging level
        
        # 4. Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # 5. Define the custom format requested: 
        # Timestamp | Log Level | Filename | Function Name | Message
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(funcName)s] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 6. Add the handler to the logger
        logger.addHandler(file_handler)
        
        # Optional: Also log to console so you can see it in terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
