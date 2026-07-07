class ConversationService:

    def __init__(
        self,
        conversation_repository,
        message_repository
    ):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository

    def create_conversation(
        self,
        user_id: int,
        title: str
    ):
        return self.conversation_repository.create(
            user_id=user_id,
            title=title
        )

    def get_conversations(
        self,
        user_id: int
    ):
        return self.conversation_repository.find_by_user(
            user_id=user_id
        )

    def get_conversation(
        self,
        conversation_id: int
    ):
        return self.conversation_repository.find_by_id(
            conversation_id=conversation_id
        )

    def update_title(
        self,
        conversation_id: int,
        title: str
    ):
        conversation = self.get_conversation(
            conversation_id
        )

        if conversation is None:
            return None

        return self.conversation_repository.update_title(
            conversation=conversation,
            title=title
        )

    def delete_conversation(
        self,
        conversation_id: int
    ):
        conversation = self.get_conversation(
            conversation_id
        )

        if conversation is None:
            return None

        self.message_repository.delete_all(
            conversation_id=conversation_id
        )

        self.conversation_repository.delete(
            conversation=conversation
        )

        return True

    def save_user_message(
        self,
        conversation_id: int,
        content: str
    ):
        return self.message_repository.save(
            conversation_id=conversation_id,
            role="user",
            content=content
        )

    def save_assistant_message(
        self,
        conversation_id: int,
        content: str
    ):
        return self.message_repository.save(
            conversation_id=conversation_id,
            role="assistant",
            content=content
        )

    def get_messages(
        self,
        conversation_id: int
    ):
        return self.message_repository.find_by_conversation(
            conversation_id=conversation_id
        )