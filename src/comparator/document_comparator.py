import sys
import pandas as pd
# LangChain imports
from src.utils.prompt_registry import PROMPT_REGISTRY
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from src.utils.logger import get_logger
from src.utils.exception import CustomException
from src.models.comparator_models import ComparisonList, ComparisonResult
from src.utils.llm_factory import get_llm_from_config
from src.operations.document_operation import DocumentOperation

logger = get_logger("document_comparator")


class DocumentComparator:
    """
    Class responsible for comparing documents using an LLM pipeline.
    """
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initializes the comparator. If no LLM is injected, it automatically 
        loads one from the YAML configuration file.
        """
        self.llm = llm if llm is not None else get_llm_from_config()
        # 1. Setup the parser with the Pydantic object
        self.parser = PydanticOutputParser(pydantic_object=ComparisonList)

    def compare(self, combined_text: str, custom_instructions: str = "") -> pd.DataFrame:
        """
        Compares text from documents by passing it through an LLM pipeline, 
        parsing the JSON, and converting it to a Pandas DataFrame.
        
        Args:
            combined_text (str): The concatenated text of the documents to compare.
            custom_instructions (str): Any specific instructions for the prompt.
            
        Returns:
            pd.DataFrame: A dataframe containing the structured comparison.
        """
        try:
            logger.info("Initializing document comparison pipeline...")
            
            # 2. Retrieve the Prompt Template from the registry
            template_str = PROMPT_REGISTRY.get("document_comparator")
            
            prompt = PromptTemplate(
                template=template_str,
                input_variables=["combined_text", "custom_instructions"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
            
            # 3. Create the LangChain pipeline (Prompt -> LLM -> Parser)
            chain = prompt | self.llm | self.parser
            
            logger.info("Invoking LLM for comparison...")
            # Execute the pipeline
            parsed_result: ComparisonList = chain.invoke({
                "combined_text": combined_text,
                "custom_instructions": custom_instructions
            })
            
            # 4. Format the result as a Pandas DataFrame
            logger.info("Converting LLM response into a pandas DataFrame...")
            
            # Convert Pydantic objects to dictionaries
            data = [comp.model_dump() for comp in parsed_result.comparisons]
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Save the result and enforce retention policy
            doc_op = DocumentOperation()
            saved_path = doc_op.save_comparison_result(df)
            logger.info(f"Comparison results automatically saved to: {saved_path}")
            
            logger.info("Successfully completed document comparison.")
            return df
            
        except Exception as e:
            raise CustomException(e, sys)
