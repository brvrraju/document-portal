# Implementation Plan: Advanced RAG Fundamentals Integration

This plan outlines the architectural refactoring required to integrate the concepts from `AdvancedRAGFundamentals.md` into our existing `ConversationalRAG` pipeline. Currently, our pipeline relies heavily on LangChain's black-box abstraction (`create_retrieval_chain` + `RunnableWithMessageHistory`). To adopt the advanced patterns (guardrails, caching, token budgets, and strict output validation), we will transition to a more explicit, deterministic execution flow.

## Open Questions

> [!IMPORTANT]
> 1. **Framework Decoupling**: The notes provide a highly manual, step-by-step pipeline. Should I fully remove LangChain's `RunnableWithMessageHistory` and `create_retrieval_chain` to implement this exact manual flow (which gives us full control over token budgets and caching), or would you prefer I try to hack these guardrails into the existing LangChain chain? (I strongly recommend the manual approach for production reliability as outlined in the notes).
> 2. **Cache Storage**: The `SimpleCache` in the notes is in-memory. Should I implement it as a dictionary in `session_utils.py` so it persists across multiple queries during the same runtime session?
> 3. **Dependencies**: This requires `tiktoken` and `numpy`. I will ensure these are installed before proceeding.

## Proposed Changes

---

### `src/utils/guardrails.py` [NEW]
Create a utility module for input validation.
- Implement `check_input_guardrail(query: str)` with the regex patterns to block prompt injections and short queries.

### `src/utils/cache_utils.py` [NEW]
Create a utility module for semantic caching.
- Implement the `SimpleCache` class with cosine similarity checks using `numpy`.

### `src/utils/token_utils.py` [NEW]
Create a utility for enforcing strict context limits.
- Implement `truncate_to_token_budget(chunks, max_tokens, model)` using `tiktoken`.

### `src/models/rag_models.py` [NEW]
Move the Pydantic schemas out of the implementation logic.
- Define `SourceCitation` and `RAGResponse` models.
- Implement the `parse_rag_response(raw_json)` validator with confidence thresholds.

### `src/chat_single/retriever.py` [MODIFY]
Refactor `ConversationalRAG` to execute the 5-step production pipeline:
1. **Guardrail**: Call `check_input_guardrail` before anything else.
2. **Cache Check**: Embed the query and check `SimpleCache`. If a hit (>= 0.90 similarity), return immediately.
3. **Retrieval & Budgeting**: If cache miss, invoke the FAISS retriever, extract the text chunks, and pass them through `truncate_to_token_budget`.
4. **Generation**: Format a strict ChatPrompt containing the sliding window history (from `session_utils`) and retrieved chunks. Invoke the LLM with `model.with_structured_output(RAGResponse)` or pass it as a JSON payload.
5. **Validation**: Validate the parsed response, write the query embedding and response to the cache, and return.

### `tests/test_advanced_rag.py` [NEW]
Implement the pytest unit tests outlined in the notes:
- `test_guardrail_blocks_prompt_injection`
- `test_cache_hit_prevents_retrieval`
- `test_pipeline_faithfulness` (Evaluation metric test)

## Verification Plan
1. **Unit Testing**: Run `pytest tests/test_advanced_rag.py` to ensure deterministic components (guardrails, cache) work independently.
2. **Integration Testing**: Update `tests/test_retriever.py` to verify the full end-to-end flow with a dummy PDF, confirming the token truncator and Pydantic validation correctly enforce the schema.
