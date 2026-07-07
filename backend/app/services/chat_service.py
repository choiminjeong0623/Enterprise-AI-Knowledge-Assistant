from app.services.conversation_service import ConversationService
from app.services.gpt_service import GPTService
from app.conversation.history_builder import HistoryBuilder


class ChatService:

    def __init__(
        self,
        conversation_service: ConversationService,
        gpt_service: GPTService,
        history_builder: HistoryBuilder
    ):

        self.conversation_service = conversation_service
        self.gpt_service = gpt_service
        self.history_builder = history_builder

    def chat(
        self,
        user_id: int,
        conversation_id: int | None,
        message: str,
        prompt: str
    ):

        if conversation_id is None:

            conversation = self.conversation_service.create_conversation(
                user_id=user_id,
                title="새 대화"
            )

            conversation_id = conversation.id

        self.conversation_service.add_user_message(
            conversation_id,
            message
        )

        history = self.conversation_service.get_messages(
            conversation_id
        )

        messages = self.history_builder.build(
            prompt,
            history
        )

        answer = self.gpt_service.generate(
            messages
        )

        self.conversation_service.add_assistant_message(
            conversation_id,
            answer
        )

        return {

            "conversation_id": conversation_id,

            "answer": answer

        }