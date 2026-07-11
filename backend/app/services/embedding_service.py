from app.clients.openai_client import OpenAIClient
from app.clients.logger import logger
from app.clients.config import settings

class EmbeddingService:
    def __init__(
        self,
        client: OpenAIClient,
    ):
        self.client = client

    ##  단일 임베딩 생성
    def create_embedding(
        self,
        text: str,
    ) -> list[float]:

        return self.client.get_embedding(text)

    ## 여러 임베딩 생성
    def create_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        batch_size = int(
            settings.OPENAI_EMBEDDING_BATCH_SIZE
        )

        if batch_size < 1:
            raise ValueError(
                "Embedding batch size must be greater than 0."
            )

        all_embeddings: list[list[float]] = []

        for start_index in range(
            0,
            len(texts),
            batch_size,
        ):
            end_index = start_index + batch_size

            batch_texts = texts[
                start_index:end_index
            ]

            logger.info(
                "Creating embedding batch. "
                "start=%s end=%s batch_count=%s",
                start_index,
                min(end_index, len(texts)),
                len(batch_texts),
            )

            batch_embeddings = (
                self.client.get_embeddings(
                    texts=batch_texts,
                )
            )

            if (
                len(batch_texts)
                != len(batch_embeddings)
            ):
                raise ValueError(
                    "The number of batch texts and "
                    "batch embeddings must be equal."
                )

            all_embeddings.extend(
                batch_embeddings
            )

        if len(texts) != len(all_embeddings):
            raise ValueError(
                "The number of texts and embeddings "
                "must be equal."
            )

        return all_embeddings