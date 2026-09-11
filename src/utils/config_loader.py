import yaml
import os
import sys
from src.utils.logger import get_logger
from src.utils.exception import CustomException

logger = get_logger("config_loader")

def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Loads a YAML configuration file and returns it as a dictionary.
    """
    try:
        # Resolve path relative to the project root
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', config_path))
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Configuration file not found at {abs_path}")
            
        with open(abs_path, 'r') as file:
            config = yaml.safe_load(file)
            
        logger.info(f"Successfully loaded configuration from {config_path}")
        return config
        
    except Exception as e:
        raise CustomException(e, sys)
