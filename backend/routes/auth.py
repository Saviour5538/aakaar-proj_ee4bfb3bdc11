from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta
from database.models import User
from database.config import get_db
from backend.services.auth import (
    get_current_user,
    create_access_token,
    hash_password,
    verify_password,
)
import uuid
import os

router = APIRouter(prefix="/auth")

# Constants
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set")
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Reduced from 1440 for security

# Pydantic Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., regex="^(admin|member)$")  # Validate role against allowed values


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str


# Route Handlers
@router.post("/register", operation_id="register", status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}


@router.post("/login", operation_id="login", response_model=TokenResponse)
async def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    # Authenticate user
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", operation_id="get_current_user", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )