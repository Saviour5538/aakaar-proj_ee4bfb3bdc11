from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

# Type variables for generic service
ModelType = TypeVar("ModelType")

class BaseService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, obj_in: dict) -> ModelType:
        try:
            obj = self.model(**obj_in)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating {self.model.__name__}: {str(e)}")

    def read(self, db: Session, id: str) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found.")
        return obj

    def update(self, db: Session, id: str, obj_in: dict) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found.")
        try:
            for key, value in obj_in.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating {self.model.__name__}: {str(e)}")

    def delete(self, db: Session, id: str) -> None:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found.")
        try:
            db.delete(obj)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting {self.model.__name__}: {str(e)}")