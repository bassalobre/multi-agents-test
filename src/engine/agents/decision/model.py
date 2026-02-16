from typing import List, Literal
from pydantic import BaseModel, Field

class DecisionOutput(BaseModel):
    decision: Literal["direct", "rag"] = Field(..., description="The strategy to use: 'direct' or 'rag'.")
    reason: str = Field(..., description="Explanation for the decision.")
    search_terms: List[str] = Field(default_factory=list, description="Optimized search keywords if RAG is chosen.")
