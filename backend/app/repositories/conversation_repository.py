from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str,
    ):
        conversation = Conversation(
            # id=conversation_id    ## Conversation 객체 생성 시 DB가 자동으로 id를 생성하기 때문에 선언하지 않는다.
            user_id=user_id,
            title=title,
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def find_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    def find_by_id_and_user_id(
        self,
        conversation_id: int,
        user_id: int,
    ):
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

    def update_title(
        self,
        conversation: Conversation,
        title: str,
    ):
        conversation.title = title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def delete(
        self,
        conversation: Conversation,
    ):
        self.db.delete(conversation)
        self.db.commit()