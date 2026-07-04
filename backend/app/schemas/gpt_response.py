# ------------------------------------------------
# pydantic : 데이터 전달 객체 
# Spring => DTO
# ------------------------------------------------
from pydantic import BaseModel

class GPTResponse(BaseModel):
    answer : str
    parsed : dict