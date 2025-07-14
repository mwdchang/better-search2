import chromadb
from chromadb.config import Settings
import hashlib
from typing import Dict, List
import logging
logging.getLogger("chroma").setLevel(logging.ERROR)


class ChromaDB:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(
            path = db_path,
            # This doesn't seem to work, see https://github.com/vanna-ai/vanna/issues/917
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = None
        self.load_collection("default-collection")


    def load_collection(self, collection_name: str):
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )


    def delete_collection(self, collection_name: str):
        self.client.delete_collection(name=collection_name)


    def get_collections(self):
        result = {}
        collections = self.client.list_collections()
        for col in collections:
            collection = self.client.get_collection(name=col.name)
            count = collection.count()
            result[col.name] = count
        return result


    def add_document_embedding(self, id: str, embedding: List[float], metadata: Dict = None):
        self.delete(id)
        self.collection.add(
            embeddings = [embedding],
            ids = [id],
            metadatas = [metadata]
        )

    def delete(self, id: str | List[str]):
        if isinstance(id, list):
            self.collection.delete(ids=[id])
        else:
            self.collection.delete(ids=id)

    
    def search(self, embedding: List[float], filter: Dict = None, num_results: int = 5):
        """
        Search the current collection

        embedding:
            - embedding vector
        filter:
            - chromadb filter dict structure
        num_results:
            - max number of results to return
        """
        results = self.collection.query(
            query_embeddings = [embedding],
            n_results = num_results,
            where = filter
        )
        return results

