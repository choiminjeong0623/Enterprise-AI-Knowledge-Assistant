from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str
    ):
        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def find_by_id(
        self,
        conversation_id: int
    ):
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def find_by_user(
        self,
        user_id: int
    ):
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def update_title(
        self,
        conversation: Conversation,
        title: str
    ):
        conversation.title = title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def delete(
        self,
        conversation: Conversation
    ):
        self.db.delete(conversation)
        self.db.commit()