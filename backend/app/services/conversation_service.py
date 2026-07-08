from fastapi import HTTPException

from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository


class ConversationService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository

    def get_conversations(
        self,
        user_id: int,
    ):
        return self.conversation_repository.find_by_user_id(
            user_id=user_id,
        )

    def create_conversation(
        self,
        user_id: int,
        title: str,
    ):
        return self.conversation_repository.create(
            user_id=user_id,
            title=title,
        )

    def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        title: str,
    ):
        conversation = self.conversation_repository.find_by_id_and_user_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return self.conversation_repository.update_title(
            conversation=conversation,
            title=title,
        )

    def delete_conversation(
        self,
        conversation_id: int,
        user_id: int,
    ):
        conversation = self.conversation_repository.find_by_id_and_user_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        self.conversation_repository.delete(
            conversation=conversation,
        )

    def get_conversation_messages(
        self,
        conversation_id: int,
        user_id: int,
    ):
        conversation = self.conversation_repository.find_by_id_and_user_id(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        return self.message_repository.find_by_conversation_id(
            conversation_id=conversation_id,
        )

    def save_user_message(
        self,
        conversation_id: int,
        content: str,
    ):
        return self.message_repository.create(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

    def save_assistant_message(
        self,
        conversation_id: int,
        content: str,
    ):
        return self.message_repository.create(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )

    def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ):
        return self.message_repository.create(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )