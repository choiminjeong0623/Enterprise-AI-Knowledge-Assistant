from pydantic import BaseModel


class GPTResponse(BaseModel):

    answer: str