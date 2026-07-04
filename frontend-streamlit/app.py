import streamlit as st
from database import (
    create_database,
    save_conversation,
    get_recent_conversations,
    search_conversations,
    get_statistics,
    load_recent_messages,
    export_conversations,
    delete_all_conversation
)
from ui import (
    show_title,
    show_gpt_card
)
from services.english_service import process_english
from prompt import (
    CHAT_PROMPT,
    CORRECTION_PROMPT
)

#######################################
# 이름 : app 
# 역할 : UI
#######################################

# ------------------------
# Sidebar - 최근 학습
# ------------------------
# st.sidebar.title("최근 학습")
# rows = get_recent_conversations(limit=5)
# # st.write("최근 학습 rows:", rows)

# if len(rows) == 0:
#     st.sidebar.info("저장된 대화가 없습니다.")
# else:
#     for row in rows:
#         st.sidebar.write(f" {row[0]}")  
#         st.sidebar.write(f" {row[1]}")
#         st.sidebar.caption(f" {row[2]}")
#         st.sidebar.divider()
# # ------------------------
# # 검색
# # ------------------------
# st.sidebar.subheader("검색")
# keyword = st.sidebar.text_input("검색어를 입력하세요.")

# if st.sidebar.button("검색"):
#     results = search_conversations(keyword)

#     if not results:
#         st.sidebar.info("검색 결과가 없습니다.")
#     else:
#         st.sidebar.success(f"{len(results)}건 검색되었습니다.")

#         for row in results:
#             with st.sidebar.expander(row[1]):
#                 st.write("### GPT 답변 ")
#                 st.write(row[2])

#                 if row[3]:  # corrected_sentence가 존재할 경우에만 출력
#                     st.write("### 교정 문장 ")
#                     st.write(row[3])

#                 st.caption(f"시간 : {row[3]}")

# ------------------------
# 통계
# ------------------------
statics = get_statistics()
st.sidebar.divider()
st.sidebar.subheader("통계")
st.sidebar.metric("총 질문", statics[0])
st.sidebar.write(f"최근 학습 : {statics[1] if statics[1] else '없음'}")


# ------------------------
# DB 생성
# ------------------------
create_database()

# ------------------------
# 질문 / 교정 구분
# ------------------------
def classify_input(text):

    if text.strip().endswith("?"):
        return "chat"

    return "correction"

# --------------------------
# 화면 제목
# --------------------------
st.set_page_config(
    page_title="AI English Teacher",
    page_icon="🤖",
    layout="wide"
)

show_title()
# --------------------------------
# 전체 삭제
# --------------------------------
if st.sidebar.button(" 대화 초기화"):
    delete_all_conversation()
    st.session_state.message = []
    st.rerun()
# --------------------------------
# TXT 다운로드
# --------------------------------
txt = export_conversations()
st.sidebar.download_button(
    label="TXT 다운로드",
    data=txt,
    file_name="conversation_history.txt",
    mime="text/plain"
)


# --------------------------------
# Session 생성
# --------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    history_messages = load_recent_messages()

    for question, answer in history_messages:
        st.session_state.messages.append(
            {
                "role" : "user",
                "content" : question
            }
        )
        st.session_state.messages.append(
            {
                "role" : "assistant",
                "content" : answer
            }
        )

# --------------------------------
# 기존 대화 출력
# --------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# --------------------------
# 입력창
# --------------------------
sentence = st.chat_input("영어 문장을 입력하세요.")

# --------------------------------
# 질문이 들어왔을 때
# --------------------------------
if sentence:
    st.session_state.messages.append(
        {
            "role" : "user",
            "content" : sentence
        }
    )

    with st.chat_message("user"):
        st.markdown(sentence)
    
    # GPT 호출
    with st.spinner("GPT가 응답을 생성하는 중입니다..."):
       answer, parsed = process_english(sentence)
    
    # AI 출력
    with st.chat_message("assistant"):
        # st.markdown(answer)
        with st.container():
            show_gpt_card(parsed)

        # Session 저장
        st.session_state.messages.append(
            {
                "role" : "assistant",
                "content" : answer
            }
        )

        st.success("학습 내용이 저장되었습니다.")
        st.divider()
