from fastapi import APIRouter, Depends, HTTPException

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

    cleaned_message = request.message.strip()

    ## 공백인 메시지가 저장되거나 GPT에 전달되는 것을 막는다.
    if not cleaned_message:
        raise HTTPException(
            status_code=400,
            detail="Message is required.",
        )

    logger.info(
        "Chat request received. user_id=%s conversation_id=%s",
        current_user.id,
        request.conversation_id,
    )

    if request.conversation_id is None: ## conversation_id가 없으면 새 대화를 만든다.
        conversation = conversation_service.create_conversation(
            user_id=current_user.id,
            title=request.message[:30],
        )
    else:
        conversation = (
            conversation_service
            .conversation_repository
            .find_by_id_and_user_id
            (
                conversation_id=request.conversation_id,
                user_id=current_user.id,
            )
        )
    if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )


    ## 사용자 메시지 저장
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
    ## 20260710 Vector Search 추가
    rag_result = document_service.build_context_from_chunks(
        user_id=current_user.id,
        query=request.message,
        limit=5,
    )

    ## Context와 Sources 분리
    document_context = rag_result["context"]

    if not document_context:
        assistant_message = (
            conversation_service.save_assistant_message(
                conversation_id=conversation.id,
                content=(
                    "업로드된 문서에서 질문과 관련된 내용을 "
                    "찾을 수 없습니다."
                ),
            )
        )

        return {
            "conversation_id": conversation.id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "sources": [],
        }

    sources = rag_result["sources"]

    ## 문서 Context가 있으면 문서 기반 답변
    ## 지원되지 않는 내용을 임의로 생성하지 않음
    ## 문서가 부족하면 부족하다고 명시
    prompt = (
        "You are an Enterprise AI Knowledge Assistant.\n"
        "Answer the user's question clearly and accurately.\n"
        "When document context is provided, answer based on "
        "that context.\n"
        "Do not invent facts that are not supported by the "
        "provided context.\n"
        "If the uploaded documents do not contain enough "
        "information, clearly say so."
    )

    gpt_response = gpt_service.get_response(
        sentence=request.message,   ## 사용자 질문
        prompt=prompt,              ## Assistant 역할 및 답변 규칙
        document_context=document_context   ## vector search로 가져온 top-k chunk
    )

    # answer = gpt_response.answer

    ## Assistant 메시지 저장
    assistant_message = conversation_service.save_assistant_message(
        conversation_id=conversation.id,
        content=gpt_response.answer
    )

    logger.info(
        "Chat response generated. "
        "user_id=%s conversation_id=%s source_count=%s",
        current_user.id,
        conversation.id,
        len(sources),
    )

    return {
        "conversation_id": conversation.id,
        "user_message": user_message,
        "assistant_message": assistant_message,
        "sources" : sources
    }