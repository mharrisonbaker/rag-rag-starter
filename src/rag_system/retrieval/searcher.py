
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

class Searcher:
    def __init__(self, index_path: Path):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = self.load_index(index_path)
        self.chunk_embeddings = self.get_chunk_embeddings()

    def load_index(self, index_path: Path):
        with index_path.open("r", encoding="utf-8") as f:
            index_data = json.load(f)
        return index_data

    def get_chunk_embeddings(self):
        embeddings = []
        for chunk in self.index.get("chunks", []):
            embeddings.append(np.array(chunk["embedding"]))
        return np.array(embeddings)

    def search(self, query: str, top_k: int = 3):
        if not query:
            return []
        
        query_embedding = self.model.encode(query)
        
        if self.chunk_embeddings.shape[0] == 0:
            return []

        similarities = [cosine_similarity(query_embedding, chunk_emb) for chunk_emb in self.chunk_embeddings]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for i in top_indices:
            chunk = self.index["chunks"][i]
            results.append({
                "id": chunk["id"],
                "text": chunk["text"],
                "score": similarities[i],
                "heading": chunk.get("heading_full")
            })
        return results
