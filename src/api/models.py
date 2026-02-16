from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    role: str = "standard"

class IngestRequest(BaseModel):
    directory_path: str = "docs"
