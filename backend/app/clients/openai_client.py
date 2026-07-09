from openai import OpenAI
from dotenv import load_dotenv
from app.clients.config import settings
from app.clients.logger import logger

from app.exceptions.custom_exception import OpenAIException
from app.clients.logger import logger
import os

load_dotenv()

## OpenAI SDK 역할 수행
client = OpenAI(
    api_key=settings.OPENAI_API_KEY
)

class OpenAIClient:

    def __init__(self):

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_response(
        self,
        messages: list[dict],
    ) -> str:
        if not messages:
            raise ValueError("OpenAI input messages are empty.")

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=messages,
        )

        return response.output_text