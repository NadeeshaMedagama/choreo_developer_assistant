from typing import Optional
from .llm_service import LLMService
from ..db.vector_client import VectorClient

class ContextManager:
    def __init__(self, vector_client: "VectorClient", llm_service: Optional["LLMService"] = None):
        self.vc = vector_client
        self.llm = llm_service

    def add_context(self, text, vector=None):
        if vector is None:
            if not self.llm:
                raise ValueError("LLM service is required to compute embeddings from text")
            vector = self.llm.get_embedding(text)
        self.vc.insert_embedding(text, vector)

    def retrieve_context(self, vector, top_k=5):
        return self.vc.query_similar(vector, top_k)

    def retrieve_by_text(self, text: str, top_k: int = 5):
        if not self.llm:
            raise ValueError("LLM service is required to compute embeddings from text")
        vector = self.llm.get_embedding(text)
        return self.retrieve_context(vector, top_k)