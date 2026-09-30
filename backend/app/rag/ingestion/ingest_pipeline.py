import os
from flask import current_app
from ..vector_store import add_documents

def ingest_knowledge_base():
    kb_dir = current_app.config.get("KNOWLEDGE_BASE_DIR", "./knowledge_base")
    total = 0
    for root, dirs, files in os.walk(kb_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if filename.endswith(".pdf"):
                total += _ingest_pdf(path, filename)
            elif filename.endswith(".txt"):
                total += _ingest_txt(path, filename)
    print(f"[RAG] Ingested {total} chunks from knowledge base")
    return total

def _ingest_pdf(path: str, filename: str) -> int:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(path)
        chunks, metadatas, ids = [], [], []
        for page_num, page in enumerate(doc):
            text = page.get_text().strip()
            if len(text) < 50:
                continue
            for i, chunk in enumerate(_split_text(text, 512, 64)):
                chunk_id = f"{filename}_p{page_num}_c{i}"
                chunks.append(chunk)
                metadatas.append({"source": filename, "page": page_num + 1, "type": "pdf"})
                ids.append(chunk_id)
        if chunks:
            add_documents(chunks, metadatas, ids)
        return len(chunks)
    except Exception as e:
        print(f"[RAG] Error ingesting {filename}: {e}")
        return 0

def _ingest_txt(path: str, filename: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks, metadatas, ids = [], [], []
        for i, chunk in enumerate(_split_text(text, 512, 64)):
            chunks.append(chunk)
            metadatas.append({"source": filename, "page": 1, "type": "txt"})
            ids.append(f"{filename}_c{i}")
        if chunks:
            add_documents(chunks, metadatas, ids)
        return len(chunks)
    except Exception as e:
        print(f"[RAG] Error ingesting {filename}: {e}")
        return 0

def _split_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks
