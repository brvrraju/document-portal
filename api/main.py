import os
import sys
import uuid
import shutil
import hashlib
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.ingestion.ingestor import DocumentIngestor
from src.analysis.analyzer import DocumentAnalyzer
from src.comparator.document_comparator import DocumentComparator
from src.utils.vector_utils import build_faiss_index
from src.utils.aws_utils import upload_to_s3, download_from_s3, list_s3_prefix
from src.chat_multi.multi_retriever import MultiDocumentConversationalRAG
from src.utils.logger import get_logger

logger = get_logger("api")

app = FastAPI(title="Document Portal API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCRATCH_DIR = "scratch"
FAISS_BASE_DIR = "faiss_index"
GLOBAL_HASHES_DIR = os.path.join(FAISS_BASE_DIR, "global_hashes")

os.makedirs(SCRATCH_DIR, exist_ok=True)
os.makedirs(FAISS_BASE_DIR, exist_ok=True)
os.makedirs(GLOBAL_HASHES_DIR, exist_ok=True)

def get_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def save_upload_file(upload_file: UploadFile, dest_dir: str = SCRATCH_DIR) -> str:
    """Saves a FastAPI UploadFile to disk temporarily and returns the path."""
    dest_path = os.path.join(dest_dir, upload_file.filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return dest_path


@app.post("/analyze")
def analyze_document(file: UploadFile = File(...)):
    try:
        # Save temp file
        file_path = save_upload_file(file)
        
        # Upload original file to S3
        upload_to_s3(file_path, f"uploads/{file.filename}")
        
        # Ingest raw text
        ingestor = DocumentIngestor()
        text = ingestor.ingest(file_path)
        
        # Analyze
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze(text)
        
        return result.model_dump()
        
    except Exception as e:
        logger.error(f"Error in /analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)):
    try:
        ref_path = save_upload_file(reference)
        act_path = save_upload_file(actual)
        
        # Upload originals to S3
        upload_to_s3(ref_path, f"uploads/compare/{reference.filename}")
        upload_to_s3(act_path, f"uploads/compare/{actual.filename}")
        
        ingestor = DocumentIngestor()
        ref_text = ingestor.ingest(ref_path)
        act_text = ingestor.ingest(act_path)
        
        combined_text = f"--- REFERENCE DOCUMENT ---\n{ref_text}\n\n--- ACTUAL DOCUMENT ---\n{act_text}"
        
        comparator = DocumentComparator()
        df = comparator.compare(combined_text)
        
        # Replace NaN with empty string to avoid JSON serialization errors
        df = df.fillna("")
        
        # Rename columns so the frontend can render them correctly
        # The frontend looks for "Page" (or "page") and "Changes" (or "changes")
        if "feature_or_topic" in df.columns and "difference_summary" in df.columns:
            df = df.rename(columns={"feature_or_topic": "Page", "difference_summary": "Changes"})
        
        # Convert DataFrame to list of dicts for JSON serialization
        return {"rows": df.to_dict(orient="records")}
        
    except Exception as e:
        logger.error(f"Error in /compare: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/index")
def chat_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: str = Form("true"),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5)
):
    try:
        # Generate session ID if missing
        if not session_id or not session_id.strip():
            session_id = str(uuid.uuid4())
            
        session_dir = os.path.join(FAISS_BASE_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        session_hashes = []
        
        # Build individual FAISS indexes for each file inside the session dir
        for idx, file in enumerate(files):
            temp_file_path = save_upload_file(file)
            
            # Compute hash for deduplication
            file_hash = get_file_hash(temp_file_path)
            session_hashes.append(file_hash)
            
            index_path = os.path.join(GLOBAL_HASHES_DIR, file_hash)
            s3_prefix = f"faiss_index/global_hashes/{file_hash}"
            
            # Check if index already exists locally
            if not os.path.exists(index_path):
                # Try to download from S3
                s3_keys = list_s3_prefix(f"{s3_prefix}/")
                if s3_keys:
                    logger.info(f"Downloading existing global index {file_hash} from S3")
                    os.makedirs(index_path, exist_ok=True)
                    for key in s3_keys:
                        local_path = os.path.join(FAISS_BASE_DIR, key.replace("faiss_index/", ""))
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        download_from_s3(key, local_path)
                else:
                    logger.info(f"Building new global index for hash {file_hash}")
                    build_faiss_index(temp_file_path, index_path)
                    
                    # Upload FAISS indexes to S3
                    upload_to_s3(f"{index_path}/index.faiss", f"{s3_prefix}/index.faiss")
                    upload_to_s3(f"{index_path}/index.pkl", f"{s3_prefix}/index.pkl")
            else:
                logger.info(f"Global index {file_hash} already exists locally")
                
        # Save session mapping
        mapping_path = os.path.join(session_dir, "session_mapping.json")
        with open(mapping_path, "w") as f:
            json.dump(session_hashes, f)
            
        upload_to_s3(mapping_path, f"faiss_index/{session_id}/session_mapping.json")
            
        return {
            "session_id": session_id,
            "use_session_dirs": use_session_dirs == "true",
            "k": k,
            "message": f"Successfully indexed {len(files)} files."
        }
        
    except Exception as e:
        logger.error(f"Error in /chat/index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/query")
def chat_query(
    question: str = Form(...),
    session_id: str = Form(...),
    use_session_dirs: str = Form("true"),
    k: int = Form(5)
):
    try:
        session_dir = os.path.join(FAISS_BASE_DIR, session_id)
        mapping_path = os.path.join(session_dir, "session_mapping.json")
        
        index_paths = []
        
        # Download from S3 if not exists locally (essential for Fargate)
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            # Find all objects for this session
            s3_keys = list_s3_prefix(f"faiss_index/{session_id}/")
            for key in s3_keys:
                local_path = os.path.join(FAISS_BASE_DIR, key.replace("faiss_index/", ""))
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                download_from_s3(key, local_path)
                
        if not os.path.exists(session_dir) or not os.listdir(session_dir):
            raise HTTPException(status_code=404, detail="Session index not found in S3 or locally. Please build the index first.")
            
        if os.path.exists(mapping_path):
            # New format: read mapping and load global hashes
            with open(mapping_path, "r") as f:
                session_hashes = json.load(f)
                
            for file_hash in session_hashes:
                index_path = os.path.join(GLOBAL_HASHES_DIR, file_hash)
                s3_prefix = f"faiss_index/global_hashes/{file_hash}"
                if not os.path.exists(index_path):
                    s3_keys = list_s3_prefix(f"{s3_prefix}/")
                    if s3_keys:
                        os.makedirs(index_path, exist_ok=True)
                        for key in s3_keys:
                            local_path = os.path.join(FAISS_BASE_DIR, key.replace("faiss_index/", ""))
                            os.makedirs(os.path.dirname(local_path), exist_ok=True)
                            download_from_s3(key, local_path)
                
                if os.path.exists(index_path):
                    index_paths.append(index_path)
        else:
            # Old format: doc_X directories
            index_paths = [
                os.path.join(session_dir, d) 
                for d in os.listdir(session_dir) 
                if os.path.isdir(os.path.join(session_dir, d))
            ]
        
        if not index_paths:
            raise HTTPException(status_code=404, detail="No indexes found in session directory.")
            
        # Initialize the MultiDocumentConversationalRAG
        rag = MultiDocumentConversationalRAG(index_paths=index_paths, top_k=k)
        
        # Answer question
        answer_dict = rag.invoke(session_id=session_id, query=question)
        
        return {"answer": answer_dict["answer"]}
        
    except Exception as e:
        logger.error(f"Error in /chat/query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount the frontend directory at the root (must be done after all API routes are defined)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
