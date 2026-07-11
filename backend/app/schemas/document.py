from datetime import datetime

from pydantic import BaseModel

class DocumentUploadDocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    content_type: str | None
    created_at: datetime

    class Config:
        from_attributes = True

## 문서 목록 및 단건 응답 구조
class DocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    chunk_count: int
    content_type: str | None
    created_at: datetime

    class Config:
        from_attributes = True  ## SQLAlchemy 객체를 Pydantic 객체로 변환할 수 있도록 설정

## 문서 Chunk 응답 구조
class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

## 문서 Upload 응답 구조
class DocumentUploadResponse(BaseModel):
    document: DocumentUploadDocumentResponse
    chunk_count: int

## 검색 결과 응답용 Response
class DocumentSearchResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# 문서 삭제 응답 구조
class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: int