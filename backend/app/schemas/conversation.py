from typing import Optional

from pydantic import BaseModel, ConfigDict


class ConversationCreateRequest(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str