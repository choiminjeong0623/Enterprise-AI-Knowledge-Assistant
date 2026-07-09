from fastapi import APIRouter, Depends

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from app.schemas.api_response import APIResponse
from app.services.gpt_service import GPTService
from app.services.document_service import DocumentService
from app.dependencies.gpt import get_gpt_service
from app.dependencies.auth import get_current_user
from app.dependencies.conversation import get_conversation_service
from app.dependencies.document import get_document_service
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
    document_service: DocumentService = Depends(get_document_service),
    gpt_service: GPTService = Depends(get_gpt_service)
):
    # sentence = request.message

    # ## 프롬프트 선택
    # if sentence.strip().endswith("?"):
    #     prompt = CHAT_PROMPT
    # else:
    #     prompt = CORRECTION_PROMPT

    # logger.info("Chat request received")

    if request.conversation_id is None: ## conversation_id가 없으면 새 대화를 만든다.
        conversation = conversation_service.create_conversation(
            user_id=current_user.id,
            title=request.message[:30],
        )
    else:
        conversation = conversation_service.get_conversation_messages(   ## conversation_id가 있으면 기존 대화를 가져온다.
            conversation_id=request.conversation_id,
            user_id=current_user.id,
        )
    
    conversation = conversation_service.create_conversation(
        user_id=current_user.id,
        title=request.message[:30],
    )

    user_message = conversation_service.save_user_message(
        conversation_id=conversation.id,
        content=request.message,
    )

    # document_context = document_service.build_context_from_chunks(
    #     user_id=current_user.id,
    #     query=request.message,
    #     limit=5,
    # )

    ## 20260709 RAG 추가
    rag_result = document_service.build_context_from_chunks(
        user_id=current_user.id,
        query=request.message,
        limit=5,
    )

    document_context = rag_result["context"]
    sources = rag_result["sources"]

    prompt = (
        "You are an Enterprise AI Knowledge Assistant. "
        "Answer the user's question clearly and accurately. "
        "When document context is provided, answer based on that context."
    )

    gpt_response = gpt_service.get_response(
        sentence=request.message,
        prompt=prompt,
        document_context=document_context
    )

    # answer = gpt_response.answer

    assistant_message = conversation_service.save_assistant_message(
        conversation_id=conversation.id,
        content=gpt_response.answer
    )

    return {
        "conversation_id": conversation.id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "sources" : sources
    }