import uuid
from datetime import datetime
from database.models import Base, engine, SessionLocal, User, Document, Chunk, Conversation, Message

def seed_database():
    session = SessionLocal()
    try:
        # Clear existing data
        session.query(Message).delete()
        session.query(Conversation).delete()
        session.query(Chunk).delete()
        session.query(Document).delete()
        session.query(User).delete()

        # Seed Users
        user1 = User(
            id=str(uuid.uuid4()),
            email="alice@example.com",
            password_hash="hashed_password_1",
            role="admin",
            created_at=datetime.utcnow()
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="bob@example.com",
            password_hash="hashed_password_2",
            role="member",
            created_at=datetime.utcnow()
        )
        session.add(user1)
        session.add(user2)

        # Seed Documents
        document1 = Document(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            filename="example.pdf",
            status="processed",
            chunk_count=5,
            created_at=datetime.utcnow()
        )
        document2 = Document(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            filename="example.docx",
            status="pending",
            chunk_count=0,
            created_at=datetime.utcnow()
        )
        session.add(document1)
        session.add(document2)

        # Seed Conversations
        conversation1 = Conversation(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            title="Project Discussion",
            created_at=datetime.utcnow()
        )
        conversation2 = Conversation(
            id=str(uuid.uuid4()),
            user_id=user2.id,
            title="Document Review",
            created_at=datetime.utcnow()
        )
        session.add(conversation1)
        session.add(conversation2)

        # Seed Messages
        message1 = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation1.id,
            role="user",
            content="What is the status of the project?",
            sources=None,
            created_at=datetime.utcnow()
        )
        message2 = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation2.id,
            role="assistant",
            content="The document is under review.",
            sources=None,
            created_at=datetime.utcnow()
        )
        session.add(message1)
        session.add(message2)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()