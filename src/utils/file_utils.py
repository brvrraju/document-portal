import os
import sys
import shutil
from src.utils.logger import get_logger
from src.utils.exception import CustomException

logger = get_logger("file_utils")

def save_uploaded_file(file_content: bytes, destination_path: str) -> str:
    """
    Saves uploaded file content (as bytes) to the specified destination path.
    """
    try:
        logger.info(f"Attempting to save uploaded file to: {destination_path}")
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(file_content)
        logger.info(f"Successfully saved file to: {destination_path}")
        return destination_path
    except Exception as e:
        raise CustomException(e, sys)

def delete_file(file_path: str) -> bool:
    """
    Deletes the file at the given file path.
    """
    try:
        logger.info(f"Attempting to delete file: {file_path}")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Successfully deleted file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        raise CustomException(e, sys)

def save_file_from_path(source_path: str, destination_path: str) -> str:
    """
    Copies an existing file from a source path to a new destination path.
    """
    try:
        logger.info(f"Attempting to copy file from {source_path} to {destination_path}")
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file does not exist: {source_path}")
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        shutil.copy2(source_path, destination_path)
        logger.info(f"Successfully copied file to: {destination_path}")
        return destination_path
    except Exception as e:
        raise CustomException(e, sys)
