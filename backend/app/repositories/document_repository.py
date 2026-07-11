from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


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

    ## 문서와 해당 문서의 Chunk 개수를 한번에 조회한다.
    def find_with_chunk_count_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                Document,
                func.count(     ## SELECT COUNT(DocumentChunk.id) FROM DocumentChunk
                    DocumentChunk.id
                ).label("chunk_count"),
            )
            .outerjoin(
                DocumentChunk,
                DocumentChunk.document_id
                == Document.id,
            )
            .filter(
                Document.user_id == user_id
            )
            .group_by(     ## 문서별로 Chunk 개수를 집계
                Document.id
            )
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

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

    ## Document 객체를 DB에서 삭제한다.
    ## 삭제할 문서의 ID가 아닌, 이미 조회된 SQLAlchemy Document 객체를 받는다.
    def delete(
        self,
        document: Document,
    ):
        self.db.delete(document)    ## 해당 객체를 삭제 대상으로 등록한다.
        self.db.commit()

        return document