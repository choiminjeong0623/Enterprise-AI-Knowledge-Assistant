from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):

    conversation_id: Optional[int] = None

    message: str


class ChatResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    conversation_id: Optional[int] = None

    answer: str