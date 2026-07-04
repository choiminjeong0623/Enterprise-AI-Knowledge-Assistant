from app.repositories.conversation_repository import ConversationRepository

class HistoryBuilder:
    def __init__(self, repository):
        self.repository = repository
    
    def build(self, limit=5):
        history = []

        conversations = self.repository.get_recent(limit)

        for c in conversations:

            history.append(
                {
                    "role": "user",
                    "content": c.sentence
                }
            )

            history.append(
                {
                    "role": "assistant",
                    "content": c.corrected_sentence
                }
            )

        return history

# def build_history(db, limit=5):

#     history = []

#     repository = ConversationRepository(db)
#     conversations = repository.get_recent()

#     for c in conversations:

#         history.append(
#             {
#                 "role": "user",
#                 "content": c.sentence
#             }
#         )

#         history.append(
#             {
#                 "role": "assistant",
#                 "content": c.corrected_sentence
#             }
#         )

#     return history