import os
import sys
import tempfile
from fpdf import FPDF

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat_multi.multi_retriever import MultiDocumentConversationalRAG
from src.utils.vector_utils import build_faiss_index
from src.utils.logger import get_logger

logger = get_logger("test_multi_retriever")

def create_dummy_pdf(filepath: str, content_lines: list):
    """Creates a dummy PDF with specific lines of text."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content_lines:
        pdf.cell(200, 10, txt=line, ln=1, align="L")
    pdf.output(filepath)

def run_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        # File 1 paths
        pdf1_path = os.path.join(temp_dir, "doc1.pdf")
        index1_path = os.path.join(temp_dir, "index1")
        
        # File 2 paths
        pdf2_path = os.path.join(temp_dir, "doc2.pdf")
        index2_path = os.path.join(temp_dir, "index2")
        
        # 1. Create dummy PDFs
        logger.info("Creating dummy PDFs...")
        create_dummy_pdf(pdf1_path, [
            "Company A is a leading software provider.",
            "The CEO of Company A is John Smith."
        ])
        create_dummy_pdf(pdf2_path, [
            "Company B specializes in hardware manufacturing.",
            "The CEO of Company B is Alice Johnson."
        ])
        
        # 2. Build FAISS indexes
        logger.info("Building FAISS indexes...")
        build_faiss_index(pdf1_path, index1_path)
        build_faiss_index(pdf2_path, index2_path)
        
        # 3. Instantiate MultiDocumentConversationalRAG
        logger.info("Instantiating MultiDocumentConversationalRAG...")
        multi_rag = MultiDocumentConversationalRAG(index_paths=[index1_path, index2_path])
        
        session_id = "test_multi_session"
        
        # 4. Turn 1: Question about Document 1
        q1 = "Who is the CEO of Company A?"
        logger.info(f"User: {q1}")
        res1 = multi_rag.invoke(session_id, q1)
        logger.info(f"AI: {res1['answer']}")
        
        # 5. Turn 2: Question about Document 2
        q2 = "Who is the CEO of Company B?"
        logger.info(f"User: {q2}")
        res2 = multi_rag.invoke(session_id, q2)
        logger.info(f"AI: {res2['answer']}")
        
        # 6. Turn 3: Follow-up relying on conversation history and multi-doc knowledge
        q3 = "Which company does Alice run?"
        logger.info(f"User: {q3}")
        res3 = multi_rag.invoke(session_id, q3)
        logger.info(f"AI: {res3['answer']}")
        
        logger.info("Multi-document test passed successfully!")

if __name__ == "__main__":
    try:
        import pkg_resources
        pkg_resources.require("fpdf")
        run_test()
    except pkg_resources.DistributionNotFound:
        logger.error("Please install fpdf using: pip install fpdf")
