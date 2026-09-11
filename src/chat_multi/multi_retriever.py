import sys
from typing import List, Optional, Any
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from src.chat_single.retriever import ConversationalRAG
from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.utils.llm_factory import get_llm_from_config

logger = get_logger("multi_retriever")

class MultiDocumentConversationalRAG(ConversationalRAG):
    """
    Extends the single-document ConversationalRAG to support querying across 
    multiple FAISS vector indexes by merging them at runtime.
    """
    
    def __init__(
        self,
        index_paths: List[str],
        embeddings: Optional[Embeddings] = None,
        llm: Optional[BaseChatModel] = None,
        top_k: int = 4,
        **legacy_kwargs: Any
    ) -> None:
        if not index_paths:
            raise ValueError("index_paths list cannot be empty.")
            
        # We don't call super().__init__() directly because it expects a single index_path
        # and loads a single retriever. We will initialize the inherited attributes ourselves.
        
        self.index_paths = index_paths
        self.embeddings = embeddings if embeddings is not None else OpenAIEmbeddings()
        self.top_k = top_k
        self._llm = llm if llm is not None else get_llm_from_config()
        
        # Initialize the cache from the parent class implementation
        from src.utils.cache_utils import SimpleCache
        self.cache = SimpleCache(threshold=0.90)
        
        # Load and merge the multiple FAISS indexes
        self._retriever = self._load_merged_retriever()
        
    def _load_merged_retriever(self) -> Any:
        """
        Loads multiple FAISS indexes from disk and merges them into a single primary store.
        """
        try:
            logger.info(f"Loading and merging {len(self.index_paths)} FAISS indexes...")
            
            # Load the first index to act as the primary store
            primary_store = FAISS.load_local(
                folder_path=self.index_paths[0],
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
            
            # Iteratively load and merge subsequent indexes
            for i in range(1, len(self.index_paths)):
                logger.info(f"Merging FAISS index {i+1}...")
                secondary_store = FAISS.load_local(
                    folder_path=self.index_paths[i],
                    embeddings=self.embeddings,
                    allow_dangerous_deserialization=True
                )
                primary_store.merge_from(secondary_store)
                
            logger.info("Successfully merged all FAISS indexes.")
            
            return primary_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.top_k}
            )
            
        except Exception as e:
            logger.error(f"Failed to merge FAISS indexes: {e}")
            raise CustomException(e, sys)
