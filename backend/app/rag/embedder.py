from sentence_transformers import SentenceTransformer
from flask import current_app
import numpy as np

_model = None

def get_embedder():
    global _model
    if _model is None:
        model_name = current_app.config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model

def embed_texts(texts: list) -> list:
    model = get_embedder()
    return model.encode(texts, convert_to_numpy=True).tolist()

def embed_query(query: str) -> list:
    model = get_embedder()
    return model.encode([query], convert_to_numpy=True)[0].tolist()
