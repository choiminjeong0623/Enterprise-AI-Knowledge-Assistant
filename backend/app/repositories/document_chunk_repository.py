from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document import Document


class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(
        self,
        document_id: int,
        chunks: list[str],
    ):
        document_chunks = []

        for index, content in enumerate(chunks):
            document_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
            )

            document_chunks.append(document_chunk)

        self.db.add_all(document_chunks)
        self.db.commit()

        for document_chunk in document_chunks:
            self.db.refresh(document_chunk)

        return document_chunks

    def find_by_document_id(
        self,
        document_id: int,
    ):
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    def search_by_keyword(
        self,
        user_id: int,
        query: str,
        limit: int = 5,
    ):
        return (
            self.db.query(DocumentChunk, Document ) ## original file name이 필요하기 때문에 Document 추가
            .join(Document, Document.id == DocumentChunk.document_id)   ## document_chunks와 documents를 연결한다.
            .filter(
                Document.user_id == user_id,
                DocumentChunk.content.ilike(f"%{query}%"),
            )
            .order_by(DocumentChunk.created_at.desc())
            .limit(limit)
            .all()
        )