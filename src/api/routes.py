import os

from fastapi import FastAPI, HTTPException

from src.api.models import QueryRequest, IngestRequest

app = FastAPI(title="Multi-Agent RAG System API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
def ask_agent(request: QueryRequest):
    from src.engine.orchestrator import Orchestrator

    try:
        orchestrator = Orchestrator()
        
        response = orchestrator.run(request.query, request.role)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest_documents(request: IngestRequest):
    from src.rag.ingestion import RAGIngestion

    try:
        if not os.path.exists(request.directory_path):
             raise HTTPException(status_code=400, detail=f"Directory '{request.directory_path}' not found.")
        
        rag = RAGIngestion()
        rag.ingest(request.directory_path)
        
        return {"status": "success", "message": f"Ingestion completed for directory: {request.directory_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
