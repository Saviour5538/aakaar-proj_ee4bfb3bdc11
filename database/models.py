import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey, DateTime, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from pgvector.sqlalchemy import Vector

DATABASE_URL_ENV = "DATABASE_URL"
Base = declarative_base()

# Database engine and session setup
engine = create_engine(os.environ[DATABASE_URL_ENV])
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Document model
class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    status = Column(String, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

# Chunk model
class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector, nullable=False)

    document = relationship("Document", back_populates="chunks")

# Conversation model
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")

# Message model
class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

User.documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
Document.chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
User.conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
Conversation.messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")