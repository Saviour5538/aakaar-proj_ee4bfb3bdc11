"""Document ingestion — parse, overlapping-chunk, embed, store. Deterministic."""
import os
from typing import List, Dict, Tuple, Optional
from pypdf import PdfReader
from docx import Document
from .embeddings import get_embedding
from .vector_store import VectorStore

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def chunk(text: str) -> List[str]:
    text = text or ''
    out, start = [], 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        out.append(text[start:end])
        if end == len(text):
            break
        start += max(1, CHUNK_SIZE - CHUNK_OVERLAP)
    return [c for c in out if c.strip()]

def _extract(file_path: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = " ".join((page.extract_text() or "") for page in reader.pages)
        return [(text, None, None)]
    if ext == ".docx":
        doc = Document(file_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(text, None, None)]
    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return [(f.read(), None, None)]
    raise ValueError(f'Unsupported file type: {ext}')

def ingest_document(file_path: str, session_id: str, user_id: str) -> Dict[str, int]:
    store = VectorStore()
    n = 0
    prev_id = None
    for seg_text, sheet_name, row_range in _extract(file_path):
        chunks = chunk(seg_text)
        if not chunks:
            continue
        embeddings = get_embedding(chunks)
        for i, (ctext, emb) in enumerate(zip(chunks, embeddings)):
            cid = f'{session_id}:{user_id}:{n}'
            store.upsert(cid, emb, {
                'session_id': session_id, 'user_id': user_id, 'source': os.path.basename(file_path),
                'sheet_name': sheet_name, 'row_range': row_range, 'chunk_text': ctext})
            n += 1
    return {'chunks': n}
