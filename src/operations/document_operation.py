import os
import sys
import shutil
import fitz  # PyMuPDF
import pandas as pd
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.exception import CustomException

# Use our scalable logger
logger = get_logger("document_operation")

class DocumentOperation:
    """
    Class responsible for low-level document operations, such as reading 
    content directly from files.
    """
    
    def read_pdf(self, file_path: str) -> str:
        """
        Reads a PDF file using the fitz (PyMuPDF) module and returns 
        the extracted text.
        
        Args:
            file_path (str): The path to the PDF file.
            
        Returns:
            str: The extracted text from all pages in the PDF.
        """
        try:
            logger.info(f"Attempting to open and read PDF: {file_path}")
            
            # Open the document
            doc = fitz.open(file_path)
            
            full_text = ""
            # Iterate through pages and extract text
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += page.get_text()
                
            doc.close()
            
            logger.info(f"Successfully extracted text from PDF: {file_path}")
            return full_text
            
        except Exception as e:
            # Leverage our custom exception handler if anything fails
            raise CustomException(e, sys)



    def combine_documents(self, doc1_filename: str, doc1_content: str, doc2_filename: str, doc2_content: str) -> str:
        """
        Combines two documents with their filenames into a single formatted string for the LLM.
        """
        try:
            logger.info("Combining two documents into a single string format.")
            return f"DOCUMENT-1 Filename <{doc1_filename}>\n{doc1_content}\n\nDOCUMENT-2 Filename <{doc2_filename}>\n{doc2_content}"
        except Exception as e:
            raise CustomException(e, sys)

    def _enforce_retention_policy(self, base_dir: str, current_date_str: str):
        """
        Enforces retention policy: max 5 files per day, max 5 days total.
        """
        try:
            if not os.path.exists(base_dir):
                return
            
            # Enforce 5 files per day max for the current day
            daily_dir = os.path.join(base_dir, current_date_str)
            if os.path.exists(daily_dir):
                files = [os.path.join(daily_dir, f) for f in os.listdir(daily_dir) if os.path.isfile(os.path.join(daily_dir, f))]
                files.sort(key=os.path.getctime)
                while len(files) > 5:
                    file_to_remove = files.pop(0)
                    os.remove(file_to_remove)
                    logger.info(f"Retention policy: Deleted old file {file_to_remove}")
            
            # Enforce 5 days max
            folders = [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            # Sort by name (which is date YYYY-MM-DD)
            folders.sort()
            while len(folders) > 5:
                folder_to_remove = folders.pop(0)
                shutil.rmtree(folder_to_remove)
                logger.info(f"Retention policy: Deleted old daily folder {folder_to_remove}")
                
        except Exception as e:
            logger.warning(f"Error enforcing retention policy: {e}")
            # Non-fatal, so we don't raise an exception that breaks the pipeline
            
    def save_comparison_result(self, df: pd.DataFrame) -> str:
        """
        Saves the comparison dataframe to docs/docComparator/YYYY-MM-DD/
        and enforces retention.
        """
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'docComparator'))
            current_date = datetime.now()
            date_str = current_date.strftime("%Y-%m-%d")
            time_str = current_date.strftime("%H%M%S")
            
            daily_dir = os.path.join(base_dir, date_str)
            os.makedirs(daily_dir, exist_ok=True)
            
            filename = f"comparison_{time_str}.csv"
            filepath = os.path.join(daily_dir, filename)
            
            df.to_csv(filepath, index=False)
            logger.info(f"Successfully saved comparison result locally to {filepath}")
            
            # Enforce retention locally
            self._enforce_retention_policy(base_dir, date_str)
            
            # AWS S3 Upload
            from src.utils.aws_utils import upload_to_s3
            s3_object_name = f"comparisons/{date_str}/{filename}"
            upload_to_s3(filepath, s3_object_name)
            logger.info(f"Uploaded comparison result to S3: {s3_object_name}")
            
            return filepath
            
        except Exception as e:
            raise CustomException(e, sys)
