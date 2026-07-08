from datetime import datetime

from pydantic import BaseModel

## Response 구조 정의
class DocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    content_type: str | None
    created_at: datetime

    class Config:
        from_attributes = True  ## SQLAlchemy 객체를 Pydantic 객체로 변환할 수 있도록 설정

## Response 구조 정의
class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

## UploadResponse 구조 정의
class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    chunk_count: int