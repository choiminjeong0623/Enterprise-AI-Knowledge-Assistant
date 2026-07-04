from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.conversation_repository import (ConversationRepository)
from app.conversation.history_builder import (HistoryBuilder)
from app.clients.openai_client import (OpenAIClient)
from app.parsers.answer_parser import (AnswerParser)
from app.services.gpt_service import (GPTService)


def get_gpt_service(
    db: Session = Depends(get_db)
):
    repository = ConversationRepository(db)

    history_builder = HistoryBuilder(repository)
    client = OpenAIClient()
    parser = AnswerParser()

    return GPTService(repository,history_builder,client,parser)