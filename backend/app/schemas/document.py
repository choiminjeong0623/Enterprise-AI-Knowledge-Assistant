from datetime import datetime

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    content_type: str | None

    status: str
    error_message: str | None
    processed_at: datetime | None
    created_at: datetime

    chunk_count: int

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    content_type: str | None

    chunk_count: int

    status: str
    error_message: str | None
    processed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchResponse(BaseModel):
    id: int
    document_id: int
    document_filename: str
    chunk_index: int
    content: str
    similarity: float
    created_at: datetime


class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: int

class DocumentRetryResponse(BaseModel):
    message: str
    document_id: int
    status: str