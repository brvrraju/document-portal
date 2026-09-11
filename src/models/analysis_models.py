from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentAnalysisResult(BaseModel):
    """
    Structured output schema for document metadata and summary extraction.
    """
    title: Optional[str] = Field(default=None, description="The title of the document, if available.")
    author: Optional[str] = Field(default=None, description="The author(s) of the document, if available.")
    creation_date: Optional[str] = Field(default=None, description="The date the document was created or published, if available.")
    key_topics: List[str] = Field(description="A list of 3-5 core topics or themes discussed in the document.")
    summary: str = Field(description="A concise summary of the document's content.")
