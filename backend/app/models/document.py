from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    stored_filename = Column(
        String(255),
        nullable=False,
    )

    content_type = Column(
        String(100),
        nullable=True,
    )
    ## 문서 처리 상태 코드
    ## UPLOADED : 원본 파일과 Document 정보만 저장됨
    ## PROCESSING : 텍스트 추출/Chunking/Embedding 진행 중
    ## COMPLETED : 모든 처리가 완료되어 검색 가능
    ## FAILED : 처리 중 오류 발생
    status = Column(
        String(20),
        default="UPLOADED",
        nullable=False,
    )

    error_message = Column(
        Text,
        nullable=True,
    )
    ## 처리가 완료된 시각
    processed_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )