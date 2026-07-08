from fastapi import APIRouter, Depends

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.api_response import APIResponse
from app.services.gpt_service import GPTService
from app.dependencies.gpt import get_gpt_service
from app.dependencies.auth import get_current_user
from app.dependencies.conversation import get_conversation_service
from app.clients.logger import logger
from app.clients.prompt import (
    CHAT_PROMPT,
    CORRECTION_PROMPT,
)


# ------------------------------------------------
# APIRouter : API를 기능별로 분리하는 객체
# Spring => @RestController
# ------------------------------------------------
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)
# ------------------------------------------------
# Depends : FastAPI의 DI 메커니즘
# FaseAPI가 요청마다 필요한 Session을 생성하고, 함수에 전달한 뒤, 요청이 끝나면 
# 정리(close)까지 담당한다.
# 필요한 객체를  프레임워크가 대신 생성하고 관리해준다.(IoC + DI)
# ------------------------------------------------

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
    gpt_service: GPTService = Depends(get_gpt_service)
):
    sentence = request.message

    ## 프롬프트 선택
    if sentence.strip().endswith("?"):
        prompt = CHAT_PROMPT
    else:
        prompt = CORRECTION_PROMPT

    logger.info("Chat request received")

    conversation_id = request.conversation_id

    if conversation_id is None:
        conversation = conversation_service.create_conversation(
            user_id=current_user.id,
            title=request.message[:30],
        )
        conversation_id = conversation.id

    user_message = conversation_service.save_user_message(
        conversation_id=conversation_id,
        content=request.message,
    )

    gpt_response = gpt_service.get_response(
    sentence=request.message,
    prompt=prompt,
)

    answer = gpt_response.answer

    assistant_message = conversation_service.save_assistant_message(
        conversation_id=conversation_id,
        content=answer,
    )

    return {
        "conversation_id": conversation_id,
        "user_message": user_message,
        "assistant_message": assistant_message,
    }