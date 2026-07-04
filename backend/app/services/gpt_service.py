from datetime import datetime

from app.schemas.gpt_response import GPTResponse
from app.conversation.history_builder import HistoryBuilder
from app.repositories.conversation_repository import ConversationRepository
from app.clients.openai_client import OpenAIClient
from app.parsers.answer_parser import AnswerParser

# ------------------------------------------------
# Service 역할
# - Message 생성
# - Client 호출
# - Parser 호출
# ------------------------------------------------
class GPTService:
    def __init__(self, repository, history_builder, client, parser):
        self.repository = repository
        self.history_builder = history_builder
        self.client = client        
        self.parser = parser

    def get_response(self, sentence, prompt):
        
        messages = [
            {
                "role": "system",
                "content": prompt
            }
        ]

        messages.extend(
            self.history_builder.build()
        )

        messages.append(
            {
                "role": "user",
                "content": sentence
            }
        )

        response = self.client.create_response(
            messages
        )

        answer = response.output_text

        parsed = self.parser.parse(
            answer
        )

        self.repository.save(
            sentence=sentence,
            answer=answer,
            corrected_sentence=parsed["corrected"],
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        return GPTResponse(
            answer=answer,
            parsed=parsed
        )
# def get_gpt_response(sentence, prompt, db):

#     messages = [
#         {
#             "role" : "system",
#             "content" : prompt
#         }
#     ]

#     logger.info("Building conversation history")

#     # History 생성
#     messages.extend(build_history(db))

#     logger.info("OpenAI response received")

#     #현재 사용자의 입력
#     messages.append(
#         {
#             "role" : "user",
#             "content" : sentence
#         }
#     )

#     # GPT 호출
#     response = create_response(messages)
#     answer = response.output_text

#     # 결과 Parsing
#     parsed = parse_answer(answer)

#     # 저장
#     repository = ConversationRepository(db)
#     repository.save(
#         sentence=sentence,
#         answer=answer,
#         corrected_sentence=parsed["corrected"],
#         time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     )
#     logger.info("Conversation saved")

#     # 결과 DTO 반환
#     return GPTResponse(
#         answer=answer,
#         parsed=parsed
#     )


    