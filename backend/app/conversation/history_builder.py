class HistoryBuilder:

    def build_messages(
        self, 
        sentence :  str,
        prompt : str
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

        return messages