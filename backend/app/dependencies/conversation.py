from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.conversation_service import ConversationService


def get_conversation_repository(
    db: Session = Depends(get_db),
):
    return ConversationRepository(db)


def get_message_repository(
    db: Session = Depends(get_db),
):
    return MessageRepository(db)


def get_conversation_service(
    conversation_repository: ConversationRepository = Depends(
        get_conversation_repository
    ),
    message_repository: MessageRepository = Depends(
        get_message_repository
    ),
):
    return ConversationService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
    )