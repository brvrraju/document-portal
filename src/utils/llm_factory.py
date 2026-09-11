import os
import sys
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

# Load environment variables from the .env file at the project root (overrides system variables)
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(env_path, override=True)

from src.utils.config_loader import load_config
from src.utils.logger import get_logger
from src.utils.exception import CustomException

logger = get_logger("llm_factory")

def get_llm_from_config() -> BaseChatModel:
    """
    Reads the YAML config file and returns an initialized LangChain LLM object.
    """
    try:
        config = load_config()
        llm_config = config.get("llm", {})
        
        provider = llm_config.get("provider", "openai").lower()
        model_name = llm_config.get("model_name", "gpt-3.5-turbo")
        temperature = llm_config.get("temperature", 0.0)
        
        logger.info(f"Initializing LLM Factory: Provider={provider}, Model={model_name}")
        
        if provider == "openai":
            # Check config first, then fallback to environment variable
            api_key = llm_config.get("api_key") or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file or config.yaml.")
            return ChatOpenAI(api_key=api_key, model=model_name, temperature=temperature)
        else:
            raise ValueError(f"Unsupported LLM provider in config: {provider}")
            
    except Exception as e:
        raise CustomException(e, sys)
