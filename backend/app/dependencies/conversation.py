from fastapi import Depends

from app.dependencies.database import get_db

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.services.conversation_service import ConversationService


def get_conversation_service(
    db=Depends(get_db)
):

    conversation_repository = ConversationRepository(db)

    message_repository = MessageRepository(db)

    return ConversationService(
        conversation_repository,
        message_repository
    )