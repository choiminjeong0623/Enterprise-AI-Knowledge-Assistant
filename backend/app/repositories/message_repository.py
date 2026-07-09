from sqlalchemy.orm import Session
from sqlalchemy import Sequence

from app.models.message import Message

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ):
        message = Message(
            conversation_id=conversation_id,    ## 이미 생성된 conversation_id를 넣는다.
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def find_by_conversation_id(
        self,
        conversation_id: int,
    ):
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def find_by_conversation(
        self,
        conversation_id: int,
    ):
        return self.find_by_conversation_id(
            conversation_id=conversation_id,
        )