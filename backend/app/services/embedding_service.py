from app.clients.openai_client import OpenAIClient


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
        embeddings: list[list[float]] = []
       
        for text in texts:
            embedding = self.create_embedding(text)
            embeddings.append(embedding)

        return embeddings