from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document import Document

import json

class DocumentChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_many(
        self,
        document_id: int,
        chunks: list[str],
        embeddings: list[list[float]],  ## 20260710 embeddings 추가
    ):
        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks and embeddings must be equal."
            )

        document_chunks = []

        # for index, content in enumerate(chunks):
        #     document_chunk = DocumentChunk(
        #         document_id=document_id,
        #         chunk_index=index,
        #         content=content,
        #     )

        for index, content in enumerate(chunks):
            embedding_json = json.dumps(
                embeddings[index]
            )

            document_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
                embedding=embedding_json
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

    ## 현재 사용자가 소유한 문서 중 임베딩이 존재하는 모든 Chunk를 조회한다.
    def find_all_with_embeddings_by_user_id(
        self,
        user_id: int,
    ):
        return (
            self.db.query(
                DocumentChunk,
                Document,
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .filter(
                Document.user_id == user_id,
                DocumentChunk.embedding.isnot(None),
            )
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
                Document.status == "COMPLETED",     ## 문서 업로드가 '성공(COMPLETED)'인 데이터만 조회한다.
                DocumentChunk.content.ilike(f"%{query}%"),
            )
            .order_by(DocumentChunk.created_at.desc())
            .limit(limit)
            .all()
        )
    
    ## 문서 생성 실패 시 Retry 하기 위해
    ## 기존 Chunk들을 삭제한다.
    def delete_by_document_id(
        self,
        document_id: int,
    ) -> int:
        deleted_count = (
            self.db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id
                == document_id
            )
            .delete(
                synchronize_session=False   ## SQLAlchemy Session이 현재 메모리에 들고 있는 객체를 일일히 동기화하지 않고 바로 삭제함.
            )
        )

        self.db.commit()

        return deleted_count