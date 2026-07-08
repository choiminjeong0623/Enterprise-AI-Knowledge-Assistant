from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.conversation import get_conversation_service
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from app.schemas.message import MessageResponse
from app.services.conversation_service import ConversationService

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get("", response_model=list[ConversationResponse])
def get_conversations(
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
):
    return conversation_service.get_conversations(
        user_id=current_user.id,
    )


@router.post("", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreate,
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
):
    return conversation_service.create_conversation(
        user_id=current_user.id,
        title=request.title,
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    request: ConversationUpdate,
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
):
    return conversation_service.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=request.title,
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
):
    conversation_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    return {"message": "Conversation deleted successfully"}


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    current_user=Depends(get_current_user),
    conversation_service: ConversationService = Depends(
        get_conversation_service
    ),
):
    return conversation_service.get_conversation_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )