from app.models.message import Message

class HistoryBuilder:

    def build_messages(
        self, 
        sentence :  str,
        prompt : str,
        conversation_history: list[Message] | None = None
    ) -> list[dict]:
        messages = [
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": sentence,
            },
        ]

        if conversation_history:
            ## OpenAI에 전달할 역할은 user, assistant 
            for message in conversation_history:
                if message.role not in [
                    "user",
                    "assistant",
                ]:
                    continue
                
                ## 이전 기록을 먼저 넣는다.
                messages.append(
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                )

        ## 현재 질문을 마지막에 추가한다.
        messages.append(
            {
                "role": "user",
                "content": sentence,
            }
        )


        return messages