import os
import sys
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.utils.config_loader import load_config

logger = get_logger("ingestor")

class DocumentIngestor:
    """
    Class responsible for handling the ingestion and parsing of various documents.
    """
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize the DocumentIngestor.
        Configures the token-based chunking strategy as per advanced RAG best practices.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Load supported extensions from centralized config
        config = load_config()
        exts = config.get("ingestion", {}).get("supported_extensions", ['.pdf', '.docx', '.txt', '.md'])
        self.supported_extensions = set(exts)
        
        # Using tiktoken encoder as it strictly bounds output by token count while respecting boundaries
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
    def _get_loader(self, file_path: str):
        """
        Returns the appropriate LangChain loader based on the file extension.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file extension: {ext}. Supported: {self.supported_extensions}")
            
        if ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.docx':
            return Docx2txtLoader(file_path)
        elif ext == '.txt':
            return TextLoader(file_path)
        elif ext == '.md':
            return UnstructuredMarkdownLoader(file_path)
    
    def ingest(self, file_path: str) -> str:
        """
        Ingests a document from the provided file path and extracts its raw text.
        
        Args:
            file_path (str): The absolute or relative path to the document.
            
        Returns:
            str: The raw text content extracted from the document.
        """
        try:
            logger.info(f"Ingesting raw text from document: {file_path}")
            loader = self._get_loader(file_path)
            raw_docs = loader.load()
            
            # Combine all pages/sections into a single string
            extracted_text = "\n\n".join([doc.page_content for doc in raw_docs])
            return extracted_text
            
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {e}")
            raise CustomException(e, sys)

    def ingest_and_chunk(self, file_path: str) -> List[Document]:
        """
        Ingests a document and immediately applies the token-based chunking strategy.
        
        Args:
            file_path (str): The path to the document.
            
        Returns:
            List[Document]: A list of LangChain Document objects, split into appropriate chunks.
        """
        try:
            logger.info(f"Ingesting and chunking document: {file_path}")
            loader = self._get_loader(file_path)
            raw_docs = loader.load()
            
            logger.info("Applying RecursiveCharacterTextSplitter.from_tiktoken_encoder...")
            chunked_docs = self.text_splitter.split_documents(raw_docs)
            
            logger.info(f"Successfully created {len(chunked_docs)} chunks.")
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Failed to ingest and chunk document {file_path}: {e}")
            raise CustomException(e, sys)
