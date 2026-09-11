# Document Portal

This is a Python project designed for interacting with and analyzing PDF documents.

## Planned Features

*   **Document Ingestion:** Capabilities to upload and process PDF documents.
*   **Document Comparator:** Tools to compare content and identify differences between multiple documents.
*   **Document Analysis:** Automated extraction of insights, summaries, and key information from documents.
*   **Single Document Chat:** An interactive interface to query and converse with the contents of a single PDF.
*   **Multi-Document Chat:** An interactive interface to query and synthesize information across multiple PDFs simultaneously.

## Getting Started

*(Instructions for setup and execution will be added here as the project develops.)*











How to use logger:

from src.utils.logger import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("This is an information message")
    logger.error("This is an error message")


how to use execption handler:
import sys
from src.utils.exception import CustomException

def some_buggy_function():
    try:
        x = 1 / 0
    except Exception as e:
        # Wrap the error, which automatically logs it with the full traceback
        raise CustomException(e, sys)

