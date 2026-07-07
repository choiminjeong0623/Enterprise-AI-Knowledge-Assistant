from fastapi import Depends

from app.dependencies.database import get_db

from app.repositories.message_repository import MessageRepository


def get_message_repository(
    db=Depends(get_db)
):

    return MessageRepository(db)