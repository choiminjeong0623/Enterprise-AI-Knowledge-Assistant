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

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=messages,
            )

            return response.output_text

        except Exception as error:
            logger.exception(
                "Failed to generate OpenAI response."
            )

            raise OpenAIException(
                "OpenAI 응답 생성에 실패했습니다."
            ) from error

        # return response.output_text

    ## 단일 임베딩 처리
    def get_embedding(
        self,
        text: str,
    ) -> list[float]:   ## 문자열 하나를 받아 임베딩 벡터를 반환한다.
        cleaned_text = text.strip() ## 문자열 앞뒤의 불필요한 공백 제거

        if not cleaned_text:    ## 빈 문자열 검사
            raise ValueError("OpenAI embedding input text is empty.")

        try:
            ## embedding API 호출
            response = self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL, ## 텍스트를 숫자 벡터로 변환하는 Embedding 모델
                input=cleaned_text,
            )

            return response.data[0].embedding

        except Exception as error:
            logger.exception(
                "Failed to generate OpenAI embedding."
            )

            raise OpenAIException(
                "OpenAI 임베딩 생성에 실패했습니다."
            ) from error
        
    ## 다중 임베딩 처리
    def get_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        
        cleaned_texts = [
            text.strip()
            for text in texts
            if text.strip()
        ]

        if not cleaned_texts:
            raise ValueError(
                "OpenAI embedding input texts are empty."
            )

        try:
            ## embedding API 호출(다중 임베딩)
            response = self.client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=cleaned_texts,
            )

            sorted_data = sorted(
                response.data,
                key=lambda item: item.index,    ## 인덱스 순서로 정렬
            )

            return [
                item.embedding
                for item in sorted_data
            ]

        except Exception as error:
            logger.exception(
                "Failed to generate OpenAI batch embeddings."
            )

            raise OpenAIException(
                "OpenAI Batch 임베딩 생성에 실패했습니다."
            ) from error