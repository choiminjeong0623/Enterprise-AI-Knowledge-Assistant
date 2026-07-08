# Enterprise AI Knowledge Assistant

Enterprise AI Knowledge Assistant는 사용자가 로그인 후 AI Assistant와 질의응답을 수행하고, 대화 이력을 Conversation 단위로 관리할 수 있는 Full-stack AI 애플리케이션입니다.

현재 버전은 **인증 기반 AI Chat Application MVP** 단계입니다.  
문서 기반 RAG 기능은 아직 구현 전이며, 다음 단계에서 Knowledge Base 기능을 확장할 예정입니다.

---

## 1. Project Overview

이 프로젝트의 최종 목표는 단순 ChatGPT Clone이 아니라, 기업 내부 문서와 지식 베이스를 기반으로 사용자의 질문에 답변할 수 있는 **Enterprise AI Knowledge Assistant**를 만드는 것입니다.

현재까지는 RAG 기능을 구현하기 전 단계로, 그 기반이 되는 다음 기능들을 구현했습니다.

- 사용자 로그인
- JWT 기반 인증
- AI Chat API
- Conversation History 관리
- Message 저장 및 조회
- React 기반 Chat UI
- 인증 라우팅
- 만료 / 잘못된 토큰 처리
- 기본 Chat UX 안정화

---

## 2. Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- OpenAI API Client
- Repository / Service Layer Architecture

### Frontend

- React
- TypeScript
- Vite
- React Router
- Axios
- CSS

## 3. Current Status

현재 프로젝트는 다음 범위까지 구현되어 있습니다.

```txt
Backend MVP 완료
Frontend React MVP 완료
RAG Knowledge Base 구현 전