from pydantic import BaseModel, Field


class UserCreate(BaseModel):

    username: str = Field(
        min_length=4,
        max_length=30
    )

    password: str = Field(
        min_length=8,
        max_length=100
    )


class UserResponse(BaseModel):

    id: int

    username: str

    role: str

    class Config:
        from_attributes = True