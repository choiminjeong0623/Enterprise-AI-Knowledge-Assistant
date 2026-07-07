from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.conversation import get_conversation_service

from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse
)

from app.services.conversation_service import ConversationService

from app.models.user import User

router = APIRouter(

    prefix="/conversation",

    tags=["Conversation"]

)

@router.post("/")
def create_conversation(

    request: ConversationCreateRequest,

    current_user: User = Depends(get_current_user),

    service: ConversationService = Depends(
        get_conversation_service
    )

):

    title = request.title or "새 대화"

    conversation = service.create_conversation(

        user_id=current_user.id,

        title=title

    )

    return conversation


@router.get(
    "",
    response_model=list[ConversationResponse]
)
def get_conversations(

    current_user: User = Depends(get_current_user),

    service: ConversationService = Depends(
        get_conversation_service
    )

):

    return service.get_conversations(
        current_user.id
    )


@router.delete(
    "/{conversation_id}"
)
def delete_conversation(

    conversation_id: int,

    service: ConversationService = Depends(
        get_conversation_service
    )

):

    service.delete_conversation(
        conversation_id
    )

    return {

        "message": "Conversation deleted."

    }