from langchain_qdrant import QdrantVectorStore
from langchain_core.embeddings import Embeddings

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.config import QDRANT_URL

def get_vector_store(collection_name: str = "documents", embedding: Embeddings = None):
    client = QdrantClient(url=QDRANT_URL)

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedding,
    )
