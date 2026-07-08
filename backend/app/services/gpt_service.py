from app.schemas.gpt_response import GPTResponse
from app.conversation.history_builder import HistoryBuilder
from app.clients.openai_client import OpenAIClient
from app.parsers.answer_parser import AnswerParser


class GPTService:

    def __init__(
        self,
        history_builder: HistoryBuilder,
        client: OpenAIClient
    ):
        self.history_builder = history_builder
        self.client = client

    def get_response(
        self,
        sentence: str,
        prompt: str
    ) -> GPTResponse:

        messages = [
            {
                "role": "system",
                "content": prompt
            }
        ]

        messages.extend(
            self.history_builder.build()
        )

        messages.append(
            {
                "role": "user",
                "content": sentence
            }
        )

        response = self.client.create_response(
            messages
        )

        answer = response.output_text

        return GPTResponse(
            answer=answer
        )