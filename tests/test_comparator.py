import os
import sys

# Add the project root to the sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.comparator.document_comparator import DocumentComparator

def test_document_comparator():
    print("Initializing DocumentComparator (will read config.yaml & .env)...")
    try:
        comparator = DocumentComparator()
        
        # We can feed it some dummy combined text to test the pipeline
        dummy_text = """
        [Document 1]
        The system uses a monolithic architecture and connects to a PostgreSQL database.
        
        [Document 2]
        The system uses a microservices architecture and connects to a MongoDB database.
        """
        
        custom_instructions = "Focus specifically on architecture and database differences."
        
        print("Running comparison... (Ensure your OPENAI_API_KEY is valid in .env)")
        df = comparator.compare(dummy_text, custom_instructions)
        
        print("\nSuccess! Comparison Results DataFrame:")
        print("-" * 50)
        print(df.to_string(index=False))
        print("-" * 50)
        
    except Exception as e:
        print(f"\nTest failed or was interrupted: {e}")
        print("--> Make sure you have added a valid OPENAI_API_KEY to your .env file!")
        print("--> Make sure the model name in your config is valid for your OpenAI account.")

if __name__ == "__main__":
    test_document_comparator()
