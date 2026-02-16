from typing import List

from src.rag.retrieval import RAGRetrieval
from src.logger import logger

class EngineRetriever:
    def __init__(self):
        self.rag_retriever = RAGRetrieval()

    def search(self, search_terms: List[str]) -> str:
        all_docs = []
            
        for term in search_terms:
            logger.info(f"Retrieving for term: '{term}'")

            docs = self.rag_retriever.get_context(term, k=5)
            all_docs.extend(docs)
            
        unique_docs = {doc.page_content: doc for doc in all_docs}.values()
                
        context_str = "\n\n".join([f"Source: {doc.metadata.get('source', 'unknown')}\nContent: {doc.page_content}" for doc in unique_docs])
                
        if not context_str:
            logger.warning("No documents found for RAG.")
            context_str = "No relevant documents found."

        return context_str
