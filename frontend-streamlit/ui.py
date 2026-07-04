import streamlit as st

# -----------------------------
# 제목
# -----------------------------
def show_title():
    st.title("AI English Teacher")
    st.write("영어 문장을 입력하면 GPT가 교정해줍니다. 질문을 입력하면 GPT가 답변해줍니다.")

# -----------------------------
# GPT 결과 카드
# -----------------------------
def show_gpt_card(parsed):
    st.success("교정 문장")
    st.write(parsed["corrected"])
    st.info("수정 이유")
    st.write(parsed["reason"])
    st.success("🇰🇷 한국어 번역")
    st.write(parsed["translation"])
    st.warning("더 좋은 표현")
    st.write(parsed["better"])

    st.divider()
    st.subheader(" AI 영어 분석")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Grammar",
            parsed["grammar"]
        )
        st.metric(
            "Vocabulary",
            parsed["vocabulary"]
        )

    with col2:
        st.metric(
            "Naturalness",
            parsed["naturalness"]
        )
        st.metric(
            "Level",
            parsed["level"]
        )

# -----------------------------
# Dashboard
# -----------------------------
def show_dashboard(statistics):
    total_count, last_date = statistics
    st.sidebar.metric(
        "총 질문",
        total_count
    )
    st.sidebar.caption(
        f"최근 학습\n{last_date}"
    )
