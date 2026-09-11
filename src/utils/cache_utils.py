import numpy as np

class SimpleCache:
    """
    A semantic cache storing previous query-response pairs.
    Instead of exact string equality, it calculates the cosine similarity 
    between the incoming query embedding and cached query embeddings.
    """
    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold
        self.entries: list[dict] = []
        
    def get(self, query_emb: list[float]) -> str | None:
        for entry in self.entries:
            sim = np.dot(query_emb, entry["emb"]) / (
                np.linalg.norm(query_emb) * np.linalg.norm(entry["emb"])
            )
            if sim >= self.threshold:
                return entry["response"]
        return None
        
    def set(self, query_emb: list[float], response: str) -> None:
        self.entries.append({"emb": query_emb, "response": response})
