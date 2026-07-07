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
router = APIRouter()

@router.post("/chat")
# ------------------------------------------------
# Depends : FastAPI의 DI 메커니즘
# FaseAPI가 요청마다 필요한 Session을 생성하고, 함수에 전달한 뒤, 요청이 끝나면 
# 정리(close)까지 담당한다.
# 필요한 객체를  프레임워크가 대신 생성하고 관리해준다.(IoC + DI)
# ------------------------------------------------
def chat(

    request: ChatRequest,

    current_user: User = Depends(
        get_current_user
    ),

    gpt_service: GPTService = Depends(
        get_gpt_service
    ),

    conversation_service: ConversationService = Depends(
        get_conversation_service
    )

):

    conversation_id = request.conversation_id

    if conversation_id is None:

        conversation = conversation_service.create_conversation(

            user_id=current_user.id,

            title=request.message[:30]

        )

        conversation_id = conversation.id

    conversation_service.save_user_message(

        conversation_id,

        request.message

    )

    result = gpt_service.get_response(

        request.message,

        CHAT_PROMPT

    )

    conversation_service.save_assistant_message(

        conversation_id,

        result.answer

    )

    return APIResponse(

        success=True,

        message="Success",

        data=ChatResponse(

            conversation_id=conversation_id,

            answer=result.answer

        )

    )