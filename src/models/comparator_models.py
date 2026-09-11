from typing import List
from pydantic import BaseModel, Field

class ComparisonResult(BaseModel):
    feature_or_topic: str = Field(description="The specific topic, feature, or section being compared.")
    doc_1_details: str = Field(description="Information found from Document 1 regarding this topic.")
    doc_2_details: str = Field(description="Information found from Document 2 regarding this topic.")
    difference_summary: str = Field(description="A concise summary of how they differ.")

class ComparisonList(BaseModel):
    comparisons: List[ComparisonResult] = Field(description="A list of all comparisons extracted from the text.")
