"""Retrieval-augmented answering — deterministic, provider-agnostic chat."""
from typing import List, Dict, Any
from .embeddings import get_embedding
from .vector_store import VectorStore
from .llm_config import get_chat_client

TOP_K = 5

def retrieve_context(query: str, top_k: int, session_id: str, user_id: str) -> List[Dict[str, Any]]:
    store = VectorStore()
    qe = get_embedding([query])[0]
    return store.search(qe, top_k, session_id=session_id, user_id=user_id)

def answer_question(query: str, session_id: str, user_id: str) -> Dict[str, Any]:
    matches = retrieve_context(query, TOP_K, session_id, user_id)
    context = "\n\n".join((m.get('metadata') or {}).get('chunk_text', '') for m in matches)
    prompt = f"Answer the question using ONLY the context. If unknown, say so.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    client, model = get_chat_client()
    resp = client.chat.completions.create(model=model, messages=[
        {'role': 'system', 'content': 'You are a helpful assistant that answers from the provided context.'},
        {'role': 'user', 'content': prompt}])
    answer = resp.choices[0].message.content
    sources = []
    for m in matches:
        md = m.get('metadata') or {}
        src = md.get('source')
        if md.get('sheet_name'):
            src = f"{src} ({md.get('sheet_name')} {md.get('row_range') or ''})".strip()
        if src and src not in sources:
            sources.append(src)
    return {'answer': answer, 'sources': sources}
