import asyncio
import os
from src.analysis.analyzer import DocumentAnalyzer
from src.comparator.document_comparator import DocumentComparator
from src.ingestion.ingestor import DocumentIngestor

async def main():
    print("Ingesting...")
    ingestor = DocumentIngestor()
    # just create dummy files
    with open("scratch/dummy1.txt", "w") as f:
        f.write("This is document 1 about AI.")
    with open("scratch/dummy2.txt", "w") as f:
        f.write("This is document 2 about AI, but better.")
        
    ref_text = ingestor.ingest("scratch/dummy1.txt")
    act_text = ingestor.ingest("scratch/dummy2.txt")
    
    combined_text = f"--- REFERENCE DOCUMENT ---\n{ref_text}\n\n--- ACTUAL DOCUMENT ---\n{act_text}"
    print("Comparing...")
    comparator = DocumentComparator()
    df = comparator.compare(combined_text)
    print("DataFrame generated.")
    
    try:
        import json
        print("Testing JSON serialization...")
        data = {"rows": df.to_dict(orient="records")}
        json.dumps(data)
        print("JSON Serialization OK")
    except Exception as e:
        print(f"JSON Serialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
