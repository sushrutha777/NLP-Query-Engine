# document_processor.py
import os
import uuid
from pathlib import Path
from typing import List
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from nltk.tokenize import sent_tokenize
import nltk
nltk.download("punkt", quiet=True)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class DocumentProcessor:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.docs_meta = {}     # doc_id -> {filename, text}
        self.doc_ids = []       # preserves order
        self.model = SentenceTransformer(model_name)
        self.index = None       # FAISS index
        self.embeddings = None
        self.id_map = []        # FAISS idx -> doc_id

    def _read_text_file(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def save_and_extract(self, file_bytes: bytes, filename: str) -> str:
        ext = filename.split(".")[-1].lower()
        file_id = str(uuid.uuid4())
        save_path = UPLOAD_DIR / f"{file_id}-{filename}"
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        text = ""
        if ext in ["txt", "csv"]:
            text = self._read_text_file(save_path)
        elif ext == "docx":
            try:
                from docx import Document
                doc = Document(save_path)
                text = "\n".join(p.text for p in doc.paragraphs)
            except Exception:
                text = self._read_text_file(save_path)
        elif ext == "pdf":
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(str(save_path))
            except Exception:
                text = self._read_text_file(save_path)
        else:
            text = self._read_text_file(save_path)

        self.docs_meta[file_id] = {"filename": filename, "text": text}
        self.doc_ids.append(file_id)
        return file_id

    def build_index(self, batch_size: int = 16):
        """Encode documents and build FAISS index."""
        if not self.doc_ids:
            self.index = None
            self.embeddings = None
            self.id_map = []
            return
        texts = [self.docs_meta[d]["text"] or "" for d in self.doc_ids]
        # Encode in batches
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype="float32")
        self.embeddings = embeddings
        dim = embeddings.shape[1]
        # Use simple flat L2 index for demo
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.id_map = self.doc_ids.copy()

    def query(self, q: str, top_k: int = 5):
        """Return list of {doc_id, filename, score, snippet} ordered by similarity."""
        if self.index is None or not self.id_map:
            return []
        q_emb = self.model.encode([q], show_progress_bar=False).astype("float32")
        D, I = self.index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.id_map):
                continue
            doc_id = self.id_map[idx]
            meta = self.docs_meta.get(doc_id, {})
            text = meta.get("text", "") or ""
            snippet = " ".join(sent_tokenize(text)[:2]) if text else ""
            results.append({
                "doc_id": doc_id,
                "filename": meta.get("filename", ""),
                "score": float(dist),
                "snippet": snippet
            })
        return results
