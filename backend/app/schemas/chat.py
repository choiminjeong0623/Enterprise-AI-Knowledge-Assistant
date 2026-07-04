from pydantic import BaseModel

# ------------------------------------------------
# BaseModel : 요청/응답 데이터 검증 및 직렬화
# Spring => DTO. Request/Response 분리
# ------------------------------------------------
class ChatRequest(BaseModel):
    message : str

class ChatResponse(BaseModel):
    answer : str