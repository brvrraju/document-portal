import os
import sys
import datetime

# Add the project root to the sys path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.exception import CustomException

def test_custom_exception():
    """Test that the custom exception formats correctly and logs to file."""
    
    # 1. Force an error to happen (Divide by zero)
    try:
        a = 1 / 0
    except Exception as e:
        # 2. Wrap it in our CustomException
        # By instantiating it, it should automatically write to the log
        custom_exc = CustomException(e, sys)
        print("Successfully caught and wrapped exception:")
        print(f"Exception String: {custom_exc}")
        
        # 3. Verify the error was written to the log file
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        expected_log_file = os.path.join(log_dir, f"app_{date_str}.log")
        
        assert os.path.exists(expected_log_file), "Log file was not found!"
        
        with open(expected_log_file, "r") as f:
            log_contents = f.read()
            
        # Check if the specific error details made it into the log file
        assert "division by zero" in log_contents, "Error message missing in logs"
        assert "test_exception.py" in log_contents, "File name missing in logs"
        
    print("Exception handler tests passed! The traceback was extracted and logged correctly.")

if __name__ == "__main__":
    test_custom_exception()
