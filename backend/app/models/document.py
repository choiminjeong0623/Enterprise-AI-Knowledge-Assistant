from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base

## Document 테이블 스키마를 정의한다.
class Document(Base):
    __tablename__ = "documents"

    ## PK 지정
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",  ## Document-DocumentChunk FK 관계를 설정한다.
        cascade="all, delete-orphan",
    )