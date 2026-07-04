import sqlite3

DB_NAME = "english_teacher.db"

## 프로그램 시작 시 DB와 테이블을 준비하는 함수
def create_database():
    connection = sqlite3.connect(DB_NAME)

    cursor = connection.cursor()    # cursor : SQL을 실행하는 사람

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation(
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        corrected_sentence TEXT,
        created_at TEXT NOT NULL

        )
    """)

    # 변경사항 저장
    connection.commit()

    # 연결 종료
    connection.close()

##  GPT 대화를 DB에 저장하는 함수.
def save_conversation(
    sentence,
    answer,
    corrected_sentence,
    time
):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversation (question, answer, corrected_sentence, created_at)
        VALUES(?, ?, ?, ?)
        """,
        (sentence, answer, corrected_sentence, time)
    )
    connection.commit()
    connection.close()

## 최근 대화 N개를 가져오는 함수
def get_recent_conversations(limit=5):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            question,
            created_at
        FROM conversation
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows  = cursor.fetchall()
    connection.close()
    return rows 

## 가져온 대화를 화면에 출력하는 함수
def show_recent_conversations(limit=5):

    rows = get_recent_conversations(limit)  # rows 반환

    if len(rows) == 0:
        print("\n저장된 대화가 없습니다.")
        return
    
    print("=" * 50)
    print("최근 학습 기록")
    print("=" * 50)

    for row in rows:            # 출력
        print()
        print(f"시간 : {row[3]}")
        print(f"질문 : {row[0]}")
        print("-" * 50)

## GPT가 이전 대화를 기억하도록 메시지 형식으로 변환하는 함수
def build_history(limit=5):

    rows = get_recent_conversations(limit)
    history = []

    rows.reverse()  # 최근 대화가 마지막에 오도록 순서 변경

    for row in rows:
        history.append({
            "role" : "user",
            "content" : row[0]
        })

        history.append({
            "role" : "assistant",
            "content" : row[2]
        })
    return history

## 키워드 검색 함수.
def search_conversations(keyword):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
       SELECT
            id,
            question,
            answer,
            corrected_sentence,
            created_at
        FROM conversation
        WHERE question LIKE ?
        ORDER BY id DESC
        """,
        (f"%{keyword}%",)
    )
    
    rows = cursor.fetchall()
    connection.close()

    return rows

## 통계 함수
def get_statistics():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 
            COUNT(*)
            , MAX(created_at)
        FROM conversation
        """
    )

    reuslt = cursor.fetchone()

    if reuslt == (0, None):
        total_count = 0
        last_date = None
    else:
        total_count = reuslt[0]
        last_date = reuslt[1]
    
    connection.close()

    return total_count, last_date

def get_conversation_by_id(id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            question,
            answer,
            corrected_sentence,
            created_at
        FROM conversation
        WHERE id = ?
        """,
        (id,)
    )

    row = cursor.fetchone()
    connection.close()

    return row

def load_recent_messages(limit=20):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            question,
            answer
        FROM conversation
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()
    connection.close()
    rows.reverse()  # 최근 대화가 마지막에 오도록 순서 변경
    
    return rows

## TXT 내보내기 함수
def export_conversations():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
            SELECT
                question,
                answer,
                created_at
            FROM conversation
            ORDER BY id ASC
        """

    )

    rows = cursor.fetchall()
    connection.close()

    text = ""

    for question, answer, created_at in rows:
        text += f"Q : {question}\n"
        text += f"A : {answer}\n"
        text += f"[{created_at}]\n"
        text += "-" * 60
        text += "\n"

    return text

## 전체 삭제 함수
def delete_all_conversation():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM conversation"
    )

    connection.commit()
    connection.close()