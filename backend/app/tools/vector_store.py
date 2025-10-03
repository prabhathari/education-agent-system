from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
from app.config import settings

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            port=settings.qdrant_port
        )
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = settings.collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        collections = self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )
    
    async def add_document(self, text: Any, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector store with validation"""
        # Convert to string and validate
        if text is None:
            return ""
        
        text_str = str(text).strip()
        if not text_str:
            return ""
        
        try:
            doc_id = str(uuid.uuid4())
            embedding = self.encoder.encode(text_str).tolist()
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={"text": text_str, **metadata}
                    )
                ]
            )
            return doc_id
        except Exception as e:
            print(f"[VectorStore] Error: {e}")
            return ""
    
    async def search(self, query: Any, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents with validation"""
        if query is None:
            return []
        
        query_str = str(query).strip()
        if not query_str:
            return []
        
        try:
            query_vector = self.encoder.encode(query_str).tolist()
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            return [
                {
                    "text": hit.payload.get("text", ""),
                    "metadata": {k: v for k, v in hit.payload.items() if k != "text"},
                    "score": hit.score
                }
                for hit in results
            ]
        except Exception as e:
            print(f"[VectorStore] Search error: {e}")
            return []