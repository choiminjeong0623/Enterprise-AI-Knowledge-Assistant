from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.message import (
    get_message_repository
)

from app.repositories.message_repository import (
    MessageRepository
)

from app.schemas.message import (
    MessageCreateRequest,
    MessageResponse
)

router = APIRouter(

    prefix="/messages",

    tags=["Message"]

)


@router.get(
    "/{conversation_id}",
    response_model=list[MessageResponse]
)
def get_messages(

    conversation_id: int,

    repository: MessageRepository = Depends(
        get_message_repository
    )

):

    return repository.find_by_conversation(
        conversation_id
    )


@router.post(
    "/{conversation_id}",
    response_model=MessageResponse
)
def save_message(

    conversation_id: int,

    request: MessageCreateRequest,

    repository: MessageRepository = Depends(
        get_message_repository
    )

):

    return repository.save(

        conversation_id=conversation_id,

        role=request.role,

        content=request.content

    )