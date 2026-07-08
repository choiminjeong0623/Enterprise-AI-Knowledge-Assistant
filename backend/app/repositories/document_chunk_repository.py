from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


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