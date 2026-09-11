from pydantic import BaseModel, Field

class SourceCitation(BaseModel):
    document_id: str
    snippet: str

class RAGResponse(BaseModel):
    answer: str = Field(description="Direct factual answer to the query")
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[SourceCitation]

def parse_rag_response(raw_json: dict) -> RAGResponse:
    validated = RAGResponse.model_validate(raw_json)
    if validated.confidence < 0.5:
        raise ValueError("Confidence below threshold")
    return validated
