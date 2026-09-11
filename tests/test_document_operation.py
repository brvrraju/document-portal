import os
import sys

# Add the project root to the sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.operations.document_operation import DocumentOperation

def test_document_read():
    """Test reading the sample PDF using the DocumentOperation class."""
    
    # Path to our sample pdf
    sample_pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../docs/sample_document_1.pdf'))
    
    print(f"Testing reading PDF at: {sample_pdf_path}")
    
    # Initialize the class and call read
    doc_ops = DocumentOperation()
    extracted_text = doc_ops.read_pdf(sample_pdf_path)
    
    # Verifications
    assert extracted_text is not None, "Text extracted is None!"
    assert len(extracted_text) > 0, "Text extracted is empty!"
    
    print("Successfully read the PDF! Here is a snippet of the text:")
    print("-" * 50)
    print(extracted_text)
    print("-" * 50)
    print("DocumentOperation test passed successfully!")

if __name__ == "__main__":
    test_document_read()
