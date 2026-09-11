# Code Backward Trace: `test_retriever.py`

This report provides an educational backward execution trace for the primary integration test found in [`test_retriever.py`](file:///e:/AI/AI_2026_Month09/Projects/Vijay_Practice/document_portal_vj/tests/test_retriever.py). We start from the final log statement indicating success and trace backwards up the call stack to see how the system was initialized and invoked.

---

## Trace: `run_test()`

### Step 1: The Final Output
```python
logger.info("Test passed successfully!")
```
**What is executed:** The `logger.info()` method logs a string to the console.
**What is evaluated:** The script reaches the end of its block without encountering any unhandled exceptions during the `invoke` calls.
**How values are passed:** The string literal is passed directly to the logger.

### Step 2: The Follow-Up RAG Invocation (Turn 2)
```python
q2 = "Where are their headquarters?"
res2 = rag.invoke(session_id, q2)
logger.info(f"AI: {res2['answer']}")
```
**What is executed:** The `invoke` method of the `ConversationalRAG` instance is called.
**What is evaluated:** 
- The RAG system receives the query `"Where are their headquarters?"`. 
- Internally, it checks the guardrails and cache.
- Then, it fetches the conversation history for `session_id`. The LLM receives the new query *along with* the previous interaction (where the AI stated "Jane Doe is the CEO").
- The system understands that "their" refers to the company Jane Doe runs, searches the FAISS index for "headquarters", and generates the response.
**How values are passed:** The string `q2` and the `session_id` (`"test_session_123"`) are passed to `rag.invoke`. The method returns a dictionary containing the `"answer"` key, which is then extracted and logged.

### Step 3: The Initial RAG Invocation (Turn 1)
```python
q1 = "Who is the CEO?"
res1 = rag.invoke(session_id, q1)
logger.info(f"AI: {res1['answer']}")
```
**What is executed:** The first call to `rag.invoke()`.
**What is evaluated:** The RAG system searches the FAISS index for information about the CEO. Since the context contains "The CEO of the company is Jane Doe.", the LLM generates a factual response. The interaction is stored in the chat history linked to `session_id`.
**How values are passed:** The string `q1` and the same `session_id` are passed. The method returns a dictionary `res1`.

### Step 4: Instantiation of the RAG Orchestrator
```python
session_id = "test_session_123"
rag = ConversationalRAG(index_path=index_path)
```
**What is executed:** The constructor for `ConversationalRAG`.
**What is evaluated:** The orchestrator initializes its internal state, loading the FAISS vector index from disk, initializing the LLM, and preparing the `SimpleCache`.
**How values are passed:** The `index_path` (a directory path pointing to the FAISS files) is passed into the constructor.

### Step 5: Building the FAISS Index
```python
build_faiss_index(pdf_path, index_path)
```
**What is executed:** The `build_faiss_index()` function from the `vector_utils` module.
**What is evaluated:** The function loads the PDF from disk, splits its text into smaller chunks, calculates embeddings for each chunk via the OpenAI API, and saves the resulting FAISS index to the specified directory.
**How values are passed:** The absolute path to the dummy PDF (`pdf_path`) and the desired output directory (`index_path`) are passed in.

### Step 6: Creating the Dummy Data
```python
create_dummy_pdf(pdf_path)
```
**What is executed:** The `create_dummy_pdf()` helper function.
**What is evaluated:** An `FPDF` object is instantiated, and three sentences containing facts (headquarters location, CEO name, revenue) are written into a temporary PDF document.
**How values are passed:** The temporary file path `pdf_path` is passed into the function, and the PDF library saves the document to that exact location.

### Step 7: Execution Context
```python
with tempfile.TemporaryDirectory() as temp_dir:
    pdf_path = os.path.join(temp_dir, "test_doc.pdf")
    index_path = os.path.join(temp_dir, "faiss_index")
```
**What is executed:** A context manager for a temporary directory.
**What is evaluated:** The operating system creates a temporary folder. The script constructs the absolute paths for the upcoming PDF and FAISS index. When the `with` block finishes, the OS automatically cleans up the directory and all its contents.
**How values are passed:** The `tempfile` module generates the root path, which is bound to `temp_dir`. `os.path.join` concatenates it with filenames to produce `pdf_path` and `index_path`.
