from app.models.message import Message


class MessageRepository:

    def __init__(self, db):

        self.db = db

    def save(
        self,
        conversation_id: int,
        role: str,
        content: str
    ):

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        self.db.add(message)

        self.db.commit()

        self.db.refresh(message)

        return message

    def find_by_conversation(
        self,
        conversation_id: int
    ):

        return (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
            .all()
        )

    def delete_all(
        self,
        conversation_id: int
    ):

        (
            self.db.query(Message)
            .filter(
                Message.conversation_id == conversation_id
            )
            .delete()
        )

        self.db.commit()