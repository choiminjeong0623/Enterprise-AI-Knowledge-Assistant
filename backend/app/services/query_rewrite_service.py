from app.clients.openai_client import OpenAIClient
from app.models.message import Message

from app.clients.logger import logger

class QueryRewriteService:
    def __init__(
        self,
        client: OpenAIClient,
    ):
        self.client = client

    ## 현재 질문(current_query) / 최근 대화(conversation_history)를 받아
    ## Vector Search에 사용할 독립적인 질문을 반환한다.
    def rewrite_query(
        self,
        current_query: str,
        conversation_history: list[Message] | None = None,
    ) -> str:
        cleaned_query = current_query.strip()

        if not cleaned_query:
            raise ValueError(
                "Current query is empty."
            )

        ## 이전 대화가 없으면 대명사나 생략된 주어를
        ## 해석할 정보가 없으므로 GPT를 호출하지 않는다.
        if not conversation_history:
            return cleaned_query

        history_text = self._build_history_text(
            conversation_history=conversation_history,
        )

        if not history_text:
            return cleaned_query

        messages = [
                    {
                        "role": "system",
                        "content": """
                You are a search query rewriting assistant.

                Your task is NOT to answer the question.

                Rewrite the user's latest question as a standalone semantic search query.

                Rules:
                - Preserve the user's original intent.
                - Use chat history only when necessary.
                - Do not invent facts.
                - Return only the rewritten query.
                - If rewriting is unnecessary, return the original question.
                - Respond in the same language as the latest question.
                """.strip(),
                    },
                    {
                        "role": "user",
                        "content": f"""
                Conversation history:
                {history_text}

                Latest question:
                {cleaned_query}

                Rewrite the latest question as a standalone search query.
                """.strip(),
                    },
                ]

        try:
            logger.info("Rewrite messages = %s", messages)
            rewritten_query = self.client.get_response(
                messages=messages,
            )

            normalized_query = self._normalize_query(
                query=rewritten_query,
            )

            if not normalized_query:
                logger.warning(
                    "Query rewrite returned an empty result. "
                    "Using original query."
                )
                return cleaned_query

            logger.info(f"Original Query: {cleaned_query}")
            logger.info(f"Rewritten Query: {normalized_query}")

            return normalized_query

        except Exception:
            logger.exception(
                "Query rewrite failed. "
                "Using original query instead."
            )
            return cleaned_query

    ## SQLAlchemy Message 객체 목록을 GPT가 읽을 수 있는 문자열로 변환한다.
    def _build_history_text(
        self,
        conversation_history: list[Message],
    ) -> str:
        history_lines: list[str] = []

        for message in conversation_history:
            ## 역할이 user, assistant가 아니면 반복을 끝낸다.
            if message.role not in [
                "user",
                "assistant",
            ]:
                continue

            role_name = (
                "User"
                if message.role == "user"
                else "Assistant"
            )

            cleaned_content = message.content.strip()

            if not cleaned_content:
                continue

            history_lines.append(
                f"{role_name}: {cleaned_content}"
            )

        return "\n".join(history_lines)
    
    def _normalize_query(
        self,
        query: str,
    ) -> str:
        normalized_query = query.strip()

        # GPT가 검색어를 따옴표로 감싼 경우 제거한다.
        if (
            len(normalized_query) >= 2
            and normalized_query[0]
            == normalized_query[-1]
            and normalized_query[0] in [
                '"',
                "'",
            ]
        ):
            normalized_query = (
                normalized_query[1:-1].strip()
            )

        prefixes = [
            "Rewritten query:",
            "Rewritten Query:",
            "Search query:",
            "Search Query:",
            "재작성된 질문:",
            "검색 질문:",
        ]

        for prefix in prefixes:
            if normalized_query.startswith(prefix):
                normalized_query = (
                    normalized_query[
                        len(prefix):
                    ].strip()
                )

                break

        return normalized_query