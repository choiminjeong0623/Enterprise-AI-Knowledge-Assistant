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

    def create_response(self, messages):
        try:
            logger.info("Sending request to OpenAI")
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=messages
            )
            logger.info("OpenAI completed")
        except Exception as e:
            # logger.exception(e)
            logger.exception(e)
            raise

        return response