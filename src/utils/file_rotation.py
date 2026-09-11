import os
import shutil
from src.utils.logger import get_logger

logger = get_logger("file_rotation")

def get_sorted_items(directory: str, is_dir: bool = False):
    """Gets items in a directory sorted by creation time (oldest first)."""
    if not os.path.exists(directory):
        return []
        
    items = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if (is_dir and os.path.isdir(full_path)) or (not is_dir and os.path.isfile(full_path)):
            # Using getctime for creation time, though on some Unix systems getmtime is preferred.
            # getctime on Windows is creation time.
            items.append((full_path, os.path.getctime(full_path)))
            
    # Sort by time, oldest first
    items.sort(key=lambda x: x[1])
    return [path for path, time in items]

def clean_old_files(directory: str, max_files: int = 5) -> None:
    """Removes the oldest files in a directory if the count exceeds max_files."""
    files = get_sorted_items(directory, is_dir=False)
    
    if len(files) > max_files:
        files_to_delete = files[:len(files) - max_files]
        for f in files_to_delete:
            try:
                os.remove(f)
                logger.debug(f"Deleted old file during rotation: {f}")
            except Exception as e:
                logger.warning(f"Failed to delete file {f}: {e}")

def clean_old_folders(base_directory: str, max_folders: int = 5) -> None:
    """Removes the oldest folders in a directory if the count exceeds max_folders."""
    folders = get_sorted_items(base_directory, is_dir=True)
    
    if len(folders) > max_folders:
        folders_to_delete = folders[:len(folders) - max_folders]
        for folder in folders_to_delete:
            try:
                shutil.rmtree(folder)
                logger.debug(f"Deleted old folder during rotation: {folder}")
            except Exception as e:
                logger.warning(f"Failed to delete folder {folder}: {e}")
