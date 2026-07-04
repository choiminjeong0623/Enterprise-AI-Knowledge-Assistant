from datetime import datetime
from gpt_service import get_gpt_response
from database import save_conversation
from prompt import (
    CHAT_PROMPT,
    CORRECTION_PROMPT
)

# ------------------------
# 질문 / 교정 구분
# ------------------------
def classify_input(sentence):
    if sentence.strip().endswith("?"):
        prompt = CHAT_PROMPT
    else:
        prompt = CORRECTION_PROMPT
    
    return prompt

def process_chat(sentence):
    prompt = classify_input(sentence)

    answer, parsed = get_gpt_response(sentence, prompt)
    
    # --------------------------
    # 현재 시간
    # --------------------------
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------
    # SQLite 저장
    # --------------------------
    save_conversation(
        sentence=sentence, 
        answer=answer, 
        corrected_sentence=parsed["corrected"], 
        time=time
    )

    return answer, parsed