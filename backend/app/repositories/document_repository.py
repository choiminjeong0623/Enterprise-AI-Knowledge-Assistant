from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk

from datetime import datetime


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
            status="UPLOADED",
            error_message=None,
            processed_at=None,
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
    
    # 문서 처리가 시작됐음을 기록한다.
    # 상태: UPLOADED → PROCESSING
    def mark_as_processing(
        self,
        document: Document,
    ):
        document.status = "PROCESSING"
        document.error_message = None
        document.processed_at = None

        self.db.commit()
        self.db.refresh(document)

        return document
    
    # 문서 ID만 사용해 문서를 조회한다.
    # Background Task는 인증 객체를 직접 사용하지 않고
    # 이미 생성된 document_id로 처리할 예정이므로 사용한다.
    def find_by_id(
        self,
        document_id: int,
    ):
        return (
            self.db.query(Document)
            .filter(
                Document.id == document_id
            )
            .first()
        )


    # 텍스트 추출, Chunking, Embedding 및 Chunk 저장이
    # 모두 정상 완료됐음을 기록한다.
    # 상태: # PROCESSING → COMPLETED
    def mark_as_completed(
        self,
        document: Document,
    ):
        document.status = "COMPLETED"
        document.error_message = None
        document.processed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(document)

        return document
    
    # 문서 처리 중 오류가 발생했음을 기록한다.
    # 상태: PROCESSING → FAILED
    def mark_as_failed(
        self,
        document: Document,
        error_message: str,
    ):
        document.status = "FAILED"
        document.error_message = error_message
        document.processed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(document)

        return document
    
    # 문서 처리가 시작됐음을 기록한다.
    # 상태: UPLOADED → PROCESSING
    def mark_as_processing(
        self,
        document: Document,
    ):
        document.status = "PROCESSING"
        document.error_message = None
        document.processed_at = None

        self.db.commit()
        self.db.refresh(document)

        return document