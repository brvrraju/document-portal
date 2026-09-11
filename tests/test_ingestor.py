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

def test_ingest_method_scaffolding():
    """Test calling the ingest method (currently scaffolding)."""
    ingestor = DocumentIngestor()
    # Passing one of our sample PDFs to the scaffolding method
    sample_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs/sample_document_1.pdf'))
    result = ingestor.ingest(sample_pdf_path)
    
    # Since it's scaffolding, it should return None right now
    assert result is None
    print("Ingest method called successfully (returned None as expected for scaffolding).")

if __name__ == "__main__":
    # Run the tests manually if executed directly
    test_ingestor_initialization()
    test_ingest_method_scaffolding()
    print("All tests passed!")
