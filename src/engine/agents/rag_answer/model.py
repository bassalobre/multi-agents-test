from typing import List
from pydantic import BaseModel, Field

class RAGAnswerOutput(BaseModel):
    answer: str = Field(..., description="The generated answer based ONLY on the context. If context is insufficient, state exactly what is missing.")
    context_sufficient: bool = Field(..., description="True if the provided context is sufficient to answer the question, False otherwise.")
    citations: List[str] = Field(default_factory=list, description="List of source filenames or chunks used to answer the question.")
