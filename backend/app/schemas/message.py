from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageCreateRequest(BaseModel):

    role: str

    content: str


class MessageResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    role: str

    content: str

    created_at: datetime