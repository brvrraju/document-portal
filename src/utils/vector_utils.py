import sys
from typing import Any
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.ingestion.ingestor import DocumentIngestor

from src.utils.logger import get_logger
from src.utils.exception import CustomException

logger = get_logger("vector_utils")

def build_faiss_index(file_path: str, index_path: str, embeddings=None) -> None:
    """
    Reads a document, splits it into chunks using the robust DocumentIngestor, 
    embeds the chunks, and saves a FAISS index.
    
    Args:
        file_path: Absolute path to the source document.
        index_path: Absolute path to the directory where FAISS index should be saved.
        embeddings: Optional embeddings model, defaults to OpenAIEmbeddings.
    """
    try:
        logger.info(f"Ingesting and chunking document from {file_path}")
        ingestor = DocumentIngestor()
        docs = ingestor.ingest_and_chunk(file_path)
        
        logger.info(f"Building FAISS index and saving to {index_path}")
        if embeddings is None:
            embeddings = OpenAIEmbeddings()
            
        vectorstore = FAISS.from_documents(docs, embeddings)
        vectorstore.save_local(index_path)
        
        logger.info("Successfully built FAISS index")
        
    except Exception as e:
        logger.error(f"Failed to build FAISS index: {e}")
        raise CustomException(e, sys)

def load_faiss_retriever(index_path: str, top_k: int, embeddings=None) -> Any:
    """
    Loads a serialized FAISS vector store and returns it as a retriever.
    
    Args:
        index_path: Path to the FAISS index.
        top_k: Number of documents to retrieve.
        embeddings: Optional embeddings model.
    """
    try:
        if embeddings is None:
            embeddings = OpenAIEmbeddings()
            
        vectorstore = FAISS.load_local(
            folder_path=index_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k}
        )
    except Exception as e:
        logger.error(f"Failed to load FAISS index from {index_path}: {e}")
        raise CustomException(e, sys)
