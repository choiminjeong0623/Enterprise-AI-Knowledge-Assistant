from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        original_filename: str,
        stored_filename: str,
        content_type: str | None,
    ):
        document = Document(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def find_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )

    def find_by_id_and_user_id(
        self,
        document_id: int,
        user_id: int,
    ):
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )