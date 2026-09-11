import os
import sys
import datetime

# Add the project root to the sys path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.logger import get_logger

def test_custom_logger():
    """Test that the custom logger creates the file and formats correctly."""
    
    # 1. Initialize the logger
    logger = get_logger("test_logger")
    
    # 2. Log a unique test message
    test_msg = "TEST_MESSAGE: Verifying the custom logger implementation."
    logger.info(test_msg)
    
    # 3. Determine the expected log file path based on today's date
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    expected_log_file = os.path.join(log_dir, f"app_{date_str}.log")
    
    # 4. Assert that the logs folder and the log file were created
    assert os.path.exists(log_dir), f"Log directory {log_dir} was not created!"
    assert os.path.exists(expected_log_file), f"Log file {expected_log_file} was not created!"
    
    # 5. Assert that the message and formatting are in the file
    with open(expected_log_file, "r") as f:
        log_contents = f.read()
        
    assert test_msg in log_contents, "The test message was not found in the log file!"
    assert "[test_logger.py:test_custom_logger]" in log_contents, "The filename and function name formatting is missing!"
    
    print("Logger tests passed successfully! The file was created and formatted correctly.")

if __name__ == "__main__":
    test_custom_logger()
