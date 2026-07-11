from app.clients.openai_client import OpenAIClient
from app.conversation.history_builder import HistoryBuilder
from app.schemas.gpt_response import GPTResponse
from app.models.message import Message

class GPTService:
    def __init__(
        self,
        history_builder: HistoryBuilder,
        client: OpenAIClient,
    ):
        self.history_builder = history_builder
        self.client = client

    def get_response(
        self,
        sentence: str,
        prompt: str,
        document_context: str | None = None,
        conversation_history: list[Message] | None = None,
    ) -> GPTResponse:
        
        ## Assistant 역할 및 답변 규칙
        final_prompt = prompt

        if document_context:
            final_prompt = (
                f"{prompt}\n\n"
                "[Document Context]\n"
                "Use the following document context to answer the user's question. "
                "If the context is relevant, base your answer on it. "
                "If the context is not relevant or insufficient, say that the uploaded documents do not contain enough information.\n\n"
                f"{document_context}"   ## vector search로 가져온 top-k chunk
            )

        messages = self.history_builder.build_messages(
            sentence=sentence,
            prompt=final_prompt,
            conversation_history=conversation_history,
        )

        if not messages:
            raise ValueError("GPT messages are empty.")
        
        answer = self.client.get_response(
            messages=messages,
        )

        return GPTResponse(answer=answer)