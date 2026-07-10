from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


## DocumentChunk 테이블 스키마를 설정한다.
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    ## 각 문서의 Chunk 의 임베딩 벡터를 저장하는 컬럼
    ## 임베딩 : 실수 배열
    embedding = Column(
        Text,
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship(
        "Document",  ## DocumentChunk-Document FK 관계를 설정한다.
        back_populates="chunks",
    )
