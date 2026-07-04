from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db):

        # self.db: Session = SessionLocal()
        self.db = db

    def save(
        self,
        sentence,
        answer,
        corrected_sentence,
        time
    ):
        ## Conversation : ORM 객체. SQL을 직접 작성하지 않는다.
        conversation = Conversation(

            sentence=sentence,

            answer=answer,

            corrected_sentence=corrected_sentence,

            time=time
        )

        self.db.add(conversation)
        self.db.commit()

    def get_recent(
        self,
        limit=5
    ):

        return (
            self.db.query(Conversation)
            .order_by(Conversation.id.desc())
            .limit(limit)
            .all()
        )