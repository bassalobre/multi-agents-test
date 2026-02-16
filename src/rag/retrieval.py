from typing import List, Tuple

from langchain_core.documents import Document

from src.adapters.vector_store import get_vector_store
from src.rag.embedding import get_embedding
from src.logger import logger

class RAGRetrieval:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.embedding = get_embedding()
        self.vector_store = get_vector_store(collection_name=self.collection_name, embedding=self.embedding)

    def get_context(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve relevant documents for a given query.
        """
        logger.info(f"Retrieving context for query: '{query}'...")
        docs = self.vector_store.similarity_search(query, k=k)
        logger.info(f"Retrieved {len(docs)} documents.")
        return docs

    def get_context_with_score(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        Retrieve relevant documents with their similarity scores.
        """
        logger.info(f"Retrieving context with scores for query: '{query}'...")
        docs_with_score = self.vector_store.similarity_search_with_score(query, k=k)
        logger.info(f"Retrieved {len(docs_with_score)} documents.")
        return docs_with_score
