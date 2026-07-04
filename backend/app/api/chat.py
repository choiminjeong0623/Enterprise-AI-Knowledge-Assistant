from fastapi import APIRouter, Depends

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.api_response import APIResponse
from app.services.gpt_service import GPTService
from app.dependencies.gpt import get_gpt_service
from app.clients.logger import logger
from app.clients.prompt import (
    CHAT_PROMPT,
    CORRECTION_PROMPT,
)


# ------------------------------------------------
# APIRouter : API를 기능별로 분리하는 객체
# Spring => @RestController
# ------------------------------------------------
router = APIRouter()

@router.post("/chat")
# ------------------------------------------------
# Depends : FastAPI의 DI 메커니즘
# FaseAPI가 요청마다 필요한 Session을 생성하고, 함수에 전달한 뒤, 요청이 끝나면 
# 정리(close)까지 담당한다.
# 필요한 객체를  프레임워크가 대신 생성하고 관리해준다.(IoC + DI)
# ------------------------------------------------
def chat(request : ChatRequest, service : GPTService = Depends(get_gpt_service)):

    sentence = request.message

    ## 프롬프트 선택
    if sentence.strip().endswith("?"):
        prompt = CHAT_PROMPT
    else:
        prompt = CORRECTION_PROMPT

    logger.info("Chat request received")

    ## GPT 서비스 호출
 
    result = service.get_response(sentence, prompt)
    # result = get_gpt_response(
    #     sentence,
    #     prompt,
    #     db
    # )

    logger.info("Chat response completed")

    return APIResponse(
        success=True,
        message="Chat completed.",
        data=ChatResponse(
            answer=result.answer
        )
    )