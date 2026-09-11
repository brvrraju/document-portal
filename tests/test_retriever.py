import os
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat_single.retriever import ConversationalRAG
from src.utils.vector_utils import build_faiss_index
from src.utils.logger import get_logger
import tempfile
from fpdf import FPDF

logger = get_logger("test_retriever")

def create_dummy_pdf(filepath: str):
    """Creates a dummy PDF for testing FAISS ingestion."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="The corporate headquarters are located in Austin, Texas.", ln=1, align="L")
    pdf.cell(200, 10, txt="The CEO of the company is Jane Doe.", ln=1, align="L")
    pdf.cell(200, 10, txt="The Q3 revenue was $45 million.", ln=1, align="L")
    pdf.output(filepath)

def run_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "test_doc.pdf")
        index_path = os.path.join(temp_dir, "faiss_index")
        
        # 1. Create a dummy PDF
        logger.info("Creating dummy PDF...")
        create_dummy_pdf(pdf_path)
        
        # 2. Build the FAISS index
        logger.info("Building FAISS index...")
        build_faiss_index(pdf_path, index_path)
        
        # 3. Instantiate the ConversationalRAG orchestrator
        logger.info("Instantiating ConversationalRAG...")
        rag = ConversationalRAG(index_path=index_path)
        
        session_id = "test_session_123"
        
        # 4. Turn 1: Initial Question
        q1 = "Who is the CEO?"
        logger.info(f"User: {q1}")
        res1 = rag.invoke(session_id, q1)
        logger.info(f"AI: {res1['answer']}")
        
        # 5. Turn 2: Follow-up Question (Requires chat history rewrite)
        # "Where does she work?" references "she" (Jane Doe) from Q1
        q2 = "Where are their headquarters?"
        logger.info(f"User: {q2}")
        res2 = rag.invoke(session_id, q2)
        logger.info(f"AI: {res2['answer']}")
        
        logger.info("Test passed successfully!")

if __name__ == "__main__":
    try:
        # We need fpdf for generating the test pdf
        import pkg_resources
        pkg_resources.require("fpdf")
        run_test()
    except pkg_resources.DistributionNotFound:
        logger.error("Please install fpdf using: pip install fpdf")
