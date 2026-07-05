"""Embeddings — pluggable provider, returns vectors of dimension 768.
Select with EMBEDDING_PROVIDER:
  - huggingface : HF Inference API feature-extraction (needs HF_TOKEN). Model via EMBEDDING_MODEL
                  (default BAAI/bge-base-en-v1.5, 768-dim). No local model download.
  - openai      : OpenAI-compatible /v1/embeddings (openai/azure/gemini via EMBEDDING_BASE_URL).
  - local       : fastembed (no API key, downloads an ONNX model)."""
import os
from typing import List

EMBEDDING_DIM = 768
_local = None


def _local_model():
    global _local
    if _local is None:
        from fastembed import TextEmbedding
        _local = TextEmbedding(model_name=os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5"), cache_dir=os.getenv("EMBEDDING_CACHE_DIR"))
    return _local


def _hf_embed(items: List[str]) -> List[List[float]]:
    """Hugging Face Inference API (feature-extraction). Mean-pools token-level output when the
    model returns a [tokens][dim] matrix instead of a pooled [dim] vector, so it works for both
    sentence-transformers models and raw encoders."""
    import requests
    model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    # HF serverless moved to the router ("Inference Providers"); the token must have the
    # "Make calls to Inference Providers" permission enabled. EMBEDDING_BASE_URL overrides.
    url = (os.getenv("EMBEDDING_BASE_URL")
           or f"https://router.huggingface.co/hf-inference/models/{model}/pipeline/feature-extraction")
    token = (os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
             or os.getenv("HUGGINGFACEHUB_API_TOKEN"))
    if not token:
        raise RuntimeError("HF_TOKEN (or HUGGINGFACE_API_KEY) is required for EMBEDDING_PROVIDER=huggingface")
    resp = requests.post(url,
                         headers={"Authorization": f"Bearer {token}"},
                         json={"inputs": items, "options": {"wait_for_model": True}}, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    def _pool(v):
        # v is either [dim] (already pooled) or [tokens][dim] (needs mean-pool)
        if v and isinstance(v[0], list):
            return [sum(col) / len(col) for col in zip(*v)]
        return v

    return [[float(x) for x in _pool(v)] for v in data]


def embed_batch(texts: List[str]) -> List[List[float]]:
    items = list(texts)
    if not items:
        return []
    provider = os.getenv("EMBEDDING_PROVIDER", "huggingface").lower()
    if provider == "local":
        return [list(map(float, v)) for v in _local_model().embed(items)]
    if provider in ("huggingface", "hf"):
        return _hf_embed(items)
    from openai import OpenAI
    client = OpenAI(base_url=os.getenv("EMBEDDING_BASE_URL") or None,
                    api_key=os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY"))
    resp = client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), input=items)
    return [list(map(float, d.embedding)) for d in resp.data]


def embed_text(text: str) -> List[float]:
    return embed_batch([text])[0]


def get_embedding(texts: List[str]) -> List[List[float]]:
    """Batch embed. Pass a LIST; to embed one string s use get_embedding([s])[0]."""
    return embed_batch(texts)
