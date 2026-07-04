from gpt_service import get_gpt_response
from datetime import datetime
from prompt import (
    CORRECTION_PROMPT,
    CHAT_PROMPT,
)
from database import (
    create_database,
    save_conversation,
    show_recent_conversations,
    search_conversations,
    get_statistics
)
def classify_input(text):

    if text.strip().endswith("?"):
        return "chat"

    return "correction"

# 프로그램 시작 시 DB 준비
create_database()

print("=" * 40)
print("AI English Teacher")
print("=" * 40)

show_recent_conversations()

while True:

    # if sentence.lower() == "exit":
    #     print("프로그램을 종료합니다.")
    #     break
    print("\n========== 메뉴 ==========")
    print("1. 영어 문장 교정")
    print("2. 최근 대화 보기")
    print("3. 검색")
    print("4. 통계")
    print("5. 종료")

    menu = input("메뉴 선택 : ")

    if menu == "1":

        sentence = input("\n영어 문장을 입력하세요 (exit 입력 시 종료): ")
        # GPT 응답 생성
        intent = classify_input(sentence)

        if intent == "chat":
            prompt = CHAT_PROMPT
        else:
            prompt = CORRECTION_PROMPT
            
        answer, corrected_sentence = get_gpt_response(sentence, prompt)
        # 현재 시간
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 화면 출력
        print("\n===== GPT =====")
        print(answer)
        print(time)

        # 대화 저장
        save_conversation(
            sentence=sentence, 
            answer=answer, 
            corrected_sentence=corrected_sentence, 
            time=time)

    elif menu == "2":
        # 최근 대화 보기
        show_recent_conversations()

    elif menu == "3":
        # 검색하기
        keyword = input("\n검색어를 입력하세요: ")
        rows = search_conversations(keyword)

        if len(rows) == 0:
            print("\n검색 결과가 없습니다.")
        else:
            print("\n===== 검색 결과 =====")
            for index, row in enumerate(rows, start=1):
                print(f"\n[{index}]")
                print(f"시간 : {row[3]}")
                print(f"질문 : {row[0]}")
                print("-" * 40)
            
            choice = input("\n상세 내용을 보려면 번호를 입력하세요. (Enter : 취소) : ")

            if choice != "":
                selected = rows[int(choice) - 1]
                print("\n===== 상세 내용 =====")
                print("질문")
                print(selected[0])
                print("\n답변")
                print
                print(selected[1])
                print("\n수정된 문장")
                print(selected[2])
                print("\n시간")
                print(selected[3])

    elif menu == "4":

        # 통계 보기
        total, last_date = get_statistics()

        # 저장된 대화가 없을 경우
        if total == 0 and last_date is None:
            print("\n저장된 대화가 없습니다.")
            break

        print()
        print("=" * 40)
        print("학습 통계")
        print("=" * 40)
        print(f"총 질문 수 : {total}")
        print(f"최근 학습 날짜 : {last_date}")
        print()
    elif menu == "5":
        print("프로그램을 종료합니다.")
        break
