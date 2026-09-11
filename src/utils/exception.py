import sys
from src.utils.logger import get_logger

# Initialize a logger specifically for exceptions
logger = get_logger("exception_handler")

def get_error_message_detail(error, error_detail: sys):
    """
    Extracts file name, line number, and error message from the traceback.
    """
    _, _, exc_tb = error_detail.exc_info()
    
    if exc_tb is not None:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        error_message = (
            f"Error occurred in python script name [{file_name}] "
            f"line number [{line_number}] error message [{str(error)}]"
        )
    else:
        error_message = f"Error occurred: {str(error)}"
        
    return error_message


class CustomException(Exception):
    """
    Custom exception class that automatically logs the detailed error 
    traceback when instantiated.
    """
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = get_error_message_detail(error_message, error_detail=error_detail)
        
        # Log the detailed error message as an ERROR
        logger.error(self.error_message)
        
    def __str__(self):
        return self.error_message
