import chromadb
from flask import current_app
import os

_client = None
_collection = None

def get_collection(collection_name="welfare_knowledge"):
    global _client, _collection
    if _collection is None:
        persist_dir = current_app.config.get("CHROMA_PERSIST_DIR", "./vector_db/chroma_data")
        os.makedirs(persist_dir, exist_ok=True)
        try:
            import chromadb.api.shared_system_client
            chromadb.api.shared_system_client.SharedSystemClient.clear_system_cache()
        except Exception:
            pass
        _client = chromadb.PersistentClient(path=persist_dir)
        _collection = _client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_documents(texts: list, metadatas: list, ids: list):
    from .embedder import embed_texts
    collection = get_collection()
    embeddings = embed_texts(texts)
    collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)

def similarity_search(query: str, n_results: int = 5) -> list:
    from .embedder import embed_query
    collection = get_collection()
    if collection.count() == 0:
        return []
    embedding = embed_query(query)
    results = collection.query(query_embeddings=[embedding], n_results=n_results,
                               include=["documents","metadatas","distances"])
    docs = []
    for i, doc in enumerate(results["documents"][0]):
        docs.append({
            "content": doc,
            "metadata": results["metadatas"][0][i],
            "score": 1 - results["distances"][0][i],
        })
    return docs
