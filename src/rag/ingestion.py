import os
import nltk
import ssl

from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.adapters.vector_store import get_vector_store
from src.rag.embedding import get_embedding
from src.logger import logger

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')

class RAGIngestion:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.embedding = get_embedding()
        self.vector_store = get_vector_store(
            collection_name=collection_name,
            embedding=self.embedding
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def load_documents(self, directory_path: str) -> List[Document]:
        documents = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)

                try:
                    if file.endswith(".txt"):
                        loader = TextLoader(file_path, encoding="utf-8")
                        documents.extend(loader.load())
                    elif file.endswith(".md"):
                        try:
                            from langchain_community.document_loaders import UnstructuredMarkdownLoader
                            
                            loader = UnstructuredMarkdownLoader(file_path)
                        except ImportError:
                            loader = TextLoader(file_path, encoding="utf-8")
                        
                        documents.extend(loader.load())
                    elif file.endswith(".pdf"):
                        loader = PyPDFLoader(file_path)
                        documents.extend(loader.load())
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        return documents

    def ingest(self, directory_path: str):
        logger.info(f"Loading documents from {directory_path}...")
        docs = self.load_documents(directory_path)
        logger.info(f"Loaded {len(docs)} documents.")
        
        if not docs:
            logger.warning("No documents found.")
            return

        logger.info("Splitting documents...")
        chunks = self.text_splitter.split_documents(docs)
        logger.info(f"Created {len(chunks)} chunks.")

        logger.info("Indexing to Qdrant...")
        self.vector_store.add_documents(chunks)
        logger.info("Ingestion complete.")
