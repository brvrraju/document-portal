import os
import sys
import json
from datetime import datetime
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from src.models.analysis_models import DocumentAnalysisResult
from src.utils.llm_factory import get_llm_from_config
from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.utils.file_rotation import clean_old_files, clean_old_folders

logger = get_logger("analyzer")

class DocumentAnalyzer:
    """
    Analyzes document text to extract structured metadata and a summary using an LLM.
    Saves results according to a specific file and folder rotation policy.
    """
    
    def __init__(self, llm: Optional[BaseChatModel] = None, base_save_dir: str = "docs/docComparator"):
        self._llm = llm if llm is not None else get_llm_from_config()
        # Bind the LLM to output the exact Pydantic schema
        self.structured_llm = self._llm.with_structured_output(DocumentAnalysisResult)
        self.base_save_dir = base_save_dir
        
    def analyze(self, text: str) -> DocumentAnalysisResult:
        """
        Analyzes the text and extracts structured metadata and a summary.
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty.")
            
        system_prompt = (
            "You are an expert document analyst. Extract the title, author, and creation date if available. "
            "Identify 3-5 key topics and write a concise summary of the document's content. "
            "If any metadata field is truly unavailable in the text, leave it null/empty, but always provide topics and a summary."
        )
        
        try:
            logger.info("Invoking LLM for structured analysis...")
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Document Text:\n\n{text[:15000]}") # Truncate to avoid extreme context bloat, adjust if needed
            ]
            
            result: DocumentAnalysisResult = self.structured_llm.invoke(messages)
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze document: {e}")
            raise CustomException(e, sys)
            
    def save_analysis(self, result: DocumentAnalysisResult, filename_prefix: str = "analysis") -> str:
        """
        Saves the analysis result into a date-specific folder and applies rotation policies.
        Returns the path to the saved file.
        """
        try:
            # 1. Determine current date folder
            date_str = datetime.now().strftime("%Y-%m-%d")
            date_folder = os.path.join(self.base_save_dir, date_str)
            os.makedirs(date_folder, exist_ok=True)
            
            # 2. Save the file
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = os.path.join(date_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.model_dump(), f, indent=4)
                
            logger.info(f"Saved analysis to {filepath}")
            
            # 3. Apply rotation logic
            # Keep only latest 5 files in this date folder
            logger.info("Applying file rotation policy...")
            clean_old_files(date_folder, max_files=5)
            
            # Keep only latest 5 date folders in the base directory
            logger.info("Applying folder rotation policy...")
            clean_old_folders(self.base_save_dir, max_folders=5)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save analysis or rotate files: {e}")
            raise CustomException(e, sys)
