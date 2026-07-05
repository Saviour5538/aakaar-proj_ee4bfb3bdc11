"""AI router — deterministic. Mounted under /api by the server (prefix /api/ai)."""
import os, tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from ai.ingest import ingest_document
from ai.rag import answer_question

router = APIRouter(prefix='/api/ai')

class QueryRequest(BaseModel):
    query: str
    session_id: str = 'default'
    user_id: str = 'default'

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

@router.post('/ingest')
async def ingest(file: UploadFile = File(...), session_id: str = Form('default'), user_id: str = Form('default')):
    suffix = os.path.splitext(file.filename or '')[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(await file.read()); tmp.close()
        return ingest_document(tmp.name, session_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp.name)

@router.post('/query', response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        result = answer_question(req.query, req.session_id, req.user_id)
        return QueryResponse(answer=result['answer'], sources=result['sources'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
