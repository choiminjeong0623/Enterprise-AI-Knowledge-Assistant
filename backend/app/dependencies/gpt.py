from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.conversation_repository import (ConversationRepository)
from app.conversation.history_builder import (HistoryBuilder)
from app.clients.openai_client import (OpenAIClient)
from app.parsers.answer_parser import (AnswerParser)
from app.services.gpt_service import (GPTService)
from app.dependencies.message import (
    get_message_repository
)
from app.repositories.message_repository import (
    MessageRepository
)


# def get_gpt_service(
#     db: Session = Depends(get_db)
# ):
#     repository = ConversationRepository(db)

#     history_builder = HistoryBuilder(repository)
#     client = OpenAIClient()

#     return GPTService(history_builder,client)

def get_openai_client():
    return OpenAIClient()


def get_history_builder(
    db: Session = Depends(get_db),
    repository: MessageRepository = Depends(
        get_message_repository
    )
):

    return HistoryBuilder(
        repository=repository
    )



def get_gpt_service(
    history_builder: HistoryBuilder = Depends(get_history_builder),
    client: OpenAIClient = Depends(get_openai_client),
):
    return GPTService(
        history_builder=history_builder,
        client=client,
    )