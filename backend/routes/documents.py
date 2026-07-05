from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.models import Document
from database.config import get_db
from backend.services.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/documents")

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    chunk_count: int
    created_at: str

    class Config:
        orm_mode = True

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        # Save the uploaded file to the database
        document = Document(
            user_id=current_user["id"],
            filename=file.filename,
            status="processing",
            chunk_count=0,
            created_at=datetime.utcnow(),
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Process the document asynchronously
        # Assuming `process_uploaded_document` is implemented elsewhere
        await process_uploaded_document(file, document.id, current_user["id"])

        return {"message": "Document uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while uploading the document: {str(e)}",
        )

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        documents = db.query(Document).filter(Document.user_id == current_user["id"]).all()
        return documents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving documents: {str(e)}",
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        document = db.query(Document).filter(Document.id == id, Document.user_id == current_user["id"]).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        db.delete(document)
        db.commit()
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the document: {str(e)}",
        )