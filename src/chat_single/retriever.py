import os
import sys
from typing import Dict, List, Optional, Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import OpenAIEmbeddings

from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.utils.llm_factory import get_llm_from_config
from src.utils.session_utils import get_session_history, get_pruned_messages
from src.utils.vector_utils import load_faiss_retriever

from src.utils.guardrails import check_input_guardrail
from src.utils.cache_utils import SimpleCache
from src.utils.token_utils import truncate_to_token_budget
from src.models.rag_models import RAGResponse, parse_rag_response, SourceCitation
from dotenv import load_dotenv

# Ensure we have environment variables
load_dotenv(override=True)

logger = get_logger("retriever")

class ConversationalRAG:
    """Production-grade conversational RAG orchestrator for single documents."""
    
    def __init__(
        self,
        index_path: str,
        embeddings: Optional[Embeddings] = None,
        llm: Optional[BaseChatModel] = None,
        top_k: int = 4,
        **legacy_kwargs: Any
    ) -> None:
        self.index_path = index_path
        self.embeddings = embeddings if embeddings is not None else OpenAIEmbeddings()
        self.top_k = top_k
        
        self._llm = llm if llm is not None else get_llm_from_config()
        self._retriever = load_faiss_retriever(self.index_path, self.top_k, self.embeddings)
        self.cache = SimpleCache(threshold=0.90)
        
    def invoke(self, session_id: str, query: str) -> Dict[str, Any]:
        """Process a conversational query using the advanced RAG pipeline."""
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")
            
        try:
            # 1. Guardrail
            logger.info(f"Checking guardrails for query: {query}")
            check_input_guardrail(query)
            
            # 2. Embedding & Cache
            logger.info("Checking cache...")
            q_emb = self.embeddings.embed_query(query)
            if cached := self.cache.get(q_emb):
                logger.info("Cache hit!")
                # Parse the cached response back into RAGResponse
                resp = RAGResponse.model_validate_json(cached)
                return {
                    "session_id": session_id,
                    "answer": resp.answer,
                    "sources": [s.snippet for s in resp.sources]
                }
                
            # 3. Context retrieval & Token budget
            logger.info("Retrieving context...")
            docs = self._retriever.invoke(query)
            raw_chunks = [d.page_content for d in docs]
            
            # The model could be different, let's assume it's gpt-4o or similar for tiktoken
            # We'll use 1500 tokens as budget for context as an example
            chunks = truncate_to_token_budget(raw_chunks, max_tokens=1500)
            
            # 4. Prompt build & generation
            logger.info("Building prompt and generating response...")
            history = get_session_history(session_id)
            history.add_user_message(query)
            
            # We fetch up to 3 previous turns (pruned messages)
            # This is custom sliding window
            messages = get_pruned_messages(session_id, max_messages=6)
            
            context_str = "\n\n".join(chunks)
            system_prompt = (
                f"Answer the question using only the retrieved context:\n\n{context_str}\n\n"
                f"You must return your answer in JSON matching the required schema."
            )
            
            # We'll construct the prompt manually
            from langchain_core.messages import SystemMessage
            prompt_msgs = [SystemMessage(content=system_prompt)] + messages
            
            # Bind the LLM to output the RAGResponse structure
            structured_llm = self._llm.with_structured_output(RAGResponse)
            
            logger.info("Invoking LLM...")
            # We get a RAGResponse object directly
            raw_llm_output: RAGResponse = structured_llm.invoke(prompt_msgs)
            
            # 5. Output Validation
            # Since structured output is enabled, the LLM gives us a RAGResponse.
            # But we can still parse it to enforce confidence threshold.
            # We'll use the raw dict format to reuse the parse_rag_response function for validation.
            validated_response = parse_rag_response(raw_llm_output.model_dump())
            
            history.add_ai_message(validated_response.answer)
            
            self.cache.set(q_emb, validated_response.model_dump_json())
            
            return {
                "session_id": session_id,
                "answer": validated_response.answer,
                "sources": [s.snippet for s in validated_response.sources]
            }
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise CustomException(e, sys)
            
    def ask(self, query: str, session_id: str = "default", return_sources: bool = False) -> Any:
        """Legacy helper method matching previous class interfaces."""
        result = self.invoke(session_id=session_id, query=query)
        if return_sources:
            return result
        return result["answer"]
