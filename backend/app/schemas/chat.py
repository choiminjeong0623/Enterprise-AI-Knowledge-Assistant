from pydantic import BaseModel

from app.schemas.message import MessageResponse


class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: list[SourceResponse] = []

class SourceResponse(BaseModel):
    document_id: int
    document_filename: str
    chunk_index: int
    content: str