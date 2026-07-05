"""pgvector store — self-sufficient: creates its own extension + tables and uses explicit
`%s::vector` casts (no adapter registration needed). Runs from a clean database."""
import os
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json


def _vec(v) -> str:
    return "[" + ",".join(repr(float(x)) for x in v) + "]"


class VectorStore:
    TABLE = "vectorstore_chunks"
    DIM = 768

    def _conn(self):
        dsn = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        if not dsn:
            raise RuntimeError("DATABASE_URL (or POSTGRES_URL) is not set")
        conn = psycopg2.connect(dsn)
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                "CREATE TABLE IF NOT EXISTS vectorstore_chunks ("
                "id TEXT PRIMARY KEY, embedding vector(768), metadata JSONB, "
                "session_id TEXT, user_id TEXT, chunk_text TEXT)")
            conn.commit()
        return conn

    def upsert(self, id, vector, metadata):
        meta = metadata or {}
        conn = self._conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO vectorstore_chunks (id, embedding, metadata, session_id, user_id, chunk_text) "
                    "VALUES (%s, %s::vector, %s, %s, %s, %s) "
                    "ON CONFLICT (id) DO UPDATE SET embedding=EXCLUDED.embedding, "
                    "metadata=EXCLUDED.metadata, chunk_text=EXCLUDED.chunk_text",
                    (id, _vec(vector), Json(meta), meta.get("session_id"),
                     meta.get("user_id"), meta.get("chunk_text")))
            conn.commit()
        finally:
            conn.close()

    def search(self, query_embedding, top_k, **filters) -> List[Dict[str, Any]]:
        where, params = [], []
        for k in ("session_id", "user_id"):
            if filters.get(k) is not None:
                where.append(k + " = %s")
                params.append(filters[k])
        clause = ("WHERE " + " AND ".join(where)) if where else ""
        conn = self._conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, metadata, embedding <=> %s::vector AS distance "
                    "FROM vectorstore_chunks " + clause + " ORDER BY distance ASC LIMIT %s",
                    [_vec(query_embedding)] + params + [top_k])
                rows = cur.fetchall()
            return [{"id": r[0], "metadata": r[1], "distance": float(r[2])} for r in rows]
        finally:
            conn.close()
