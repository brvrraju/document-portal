import os
import sys

# Add the project root to the sys path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion.ingestor import DocumentIngestor

def test_ingestor_initialization():
    """Test that the DocumentIngestor can be initialized."""
    ingestor = DocumentIngestor()
    assert ingestor is not None
    print("Ingestor initialized successfully.")

def test_ingest_method():
    """Test calling the fully implemented ingest method."""
    ingestor = DocumentIngestor()
    # Passing one of our sample PDFs
    sample_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs/sample_document_1.pdf'))
    result = ingestor.ingest(sample_pdf_path)
    
    # The method now extracts text, so it should return a non-empty string
    assert result is not None
    assert isinstance(result, str)
    assert "Sample Document 1" in result
    print("Ingest method called successfully and returned extracted text.")

if __name__ == "__main__":
    # Run the tests manually if executed directly
    test_ingestor_initialization()
    test_ingest_method()
    print("All tests passed!")
