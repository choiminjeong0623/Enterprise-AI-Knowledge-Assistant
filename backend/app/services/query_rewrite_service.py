from app.clients.openai_client import OpenAIClient
from app.models.message import Message


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

        ## 대화가 없으면 GPT를 호출하지 않는다.
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
                "content": (
                    "You rewrite follow-up questions into "
                    "standalone search queries.\n"
                    "Use the conversation history only to resolve "
                    "missing subjects, pronouns, and references.\n"
                    "Do not answer the question.\n"                 ## GPT가 답변하지 않고 검색 질문만 반환하게 한다.
                    "Do not add information that is not present in "
                    "the conversation.\n"
                    "Return only one rewritten search query.\n"     ## 설명이나 따옴표 없이 질문 한 문장만 반환하게 한다.
                    "If the current question is already standalone, "
                    "return it unchanged."
                ),
            },
            {
                "role": "user",
                "content": (
                    "[Conversation History]\n"
                    f"{history_text}\n\n"
                    "[Current Question]\n"
                    f"{cleaned_query}"
                ),
            },
        ]

        rewritten_query = self.client.get_response(
            messages=messages,
        ).strip()

        if not rewritten_query:
            return cleaned_query

        return rewritten_query

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