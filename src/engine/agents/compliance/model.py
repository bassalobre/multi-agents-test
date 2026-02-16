from pydantic import BaseModel, Field
from typing import Optional, Literal

class ComplianceInput(BaseModel):
    query: str
    user_role: str = "standard"

class ComplianceOutput(BaseModel):
    is_safe: bool = Field(..., description="True if query is safe to proceed")
    reason: Optional[str] = Field(None, description="Reason for blocking if unsafe")
    category: Optional[str] = Field(None, description="Category of the violation (e.g., hate_speech, illegal, injection)")
    risk_level: Optional[Literal["low", "medium", "high"]] = Field(None, description="Risk level of the query")
    sanitized_query: Optional[str] = Field(None, description="Cleaned query if modification was needed")
