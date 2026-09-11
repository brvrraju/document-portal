import os
from fpdf import FPDF

def create_sample_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    pdf.output(filename)

if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    
    content1 = "This is the first sample document. It contains some basic information that will be used to test our document ingestion, single document chat, and analysis modules. The content here is simple, but it represents what a typical text-heavy PDF might look like."
    create_sample_pdf("docs/sample_document_1.pdf", "Sample Document 1 - Introduction", content1)
    
    content2 = "This is the second sample document. It contains slightly different information. We will use this document to test our document comparator and multi-document chat features. By comparing this document to the first one, we can evaluate the system's ability to find differences and synthesize information across multiple sources."
    create_sample_pdf("docs/sample_document_2.pdf", "Sample Document 2 - Advanced Topics", content2)
    
    print("Successfully generated sample PDFs in the docs/ folder.")
