# Enterprise AI Knowledge Assistant

기업 내부 문서를 업로드하고, 문서 기반 질의응답 기능으로 확장하는
엔터프라이즈 AI 어시스턴트 프로젝트입니다.

## Current Status

- GPT 기반 채팅: 완료
- JWT 인증 및 대화 관리: 완료
- React 채팅 UI: 완료
- PDF/TXT 업로드 및 텍스트 추출: 완료
- 문서 Chunking 및 DB 저장: 완료
- Embedding: 예정
- Vector Search: 예정
- RAG 답변 생성: 예정
- AI Agent: 예정
- MLOps: 예정

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: React, TypeScript, Vite
- AI: OpenAI Responses API
- Document Processing: pypdf, text chunking

## Phase 1. GPT Chat Foundation

### 목표

LLM 기반 채팅 기능의 기본 구조를 구현하는 단계다.
사용자의 질문을 받아 GPT 응답을 생성하고, 이를 서비스 구조 안에서 재사용할 수 있도록 분리했다.

### 구현 기능

* GPT 응답 생성 기능 구현
* System Prompt 기반 응답 생성
* 사용자 질문을 OpenAI API에 전달
* GPT 응답을 `GPTResponse` 형태로 반환
* OpenAI API 호출 로직을 `OpenAIClient`로 분리
* GPT 응답 생성 로직을 `GPTService`로 분리
* 기존 대화 이력을 prompt messages에 포함할 수 있도록 `HistoryBuilder` 구조 설계

### 주요 구현 흐름

```txt
사용자 질문
→ System Prompt 생성
→ 기존 대화 이력 추가
→ User Message 추가
→ OpenAIClient 호출
→ GPTResponse 반환
```

### 사용 기술 스택

```txt
Python
OpenAI Responses API
Prompt Engineering
Service Layer
OpenAIClient
GPTService
Pydantic Response Schema
```

### 관련 파일

```txt
backend/app/services/gpt_service.py
backend/app/clients/openai_client.py
backend/app/conversation/history_builder.py
backend/app/schemas/gpt_response.py
```

---

## Phase 2. Backend Foundation

### 목표

Streamlit 중심 구조가 아니라, 실무형 API 서버 구조로 전환하는 단계다.
FastAPI를 기반으로 인증, 채팅, 대화 이력 관리 API를 구현했다.

### 구현 기능

* FastAPI 서버 구성
* CORS 설정
* Logging Middleware 추가
* JWT 로그인 구현
* Access Token 발급
* Authorization Header 기반 사용자 인증
* 현재 로그인 사용자 조회
* Conversation 모델 구현
* Message 모델 구현
* Conversation CRUD API 구현
* Message 저장 및 조회 구현
* Repository / Service Layer 구조 적용
* FastAPI `Depends` 기반 Dependency Injection 구조 적용

### 구현 API

```txt
POST   /auth/login

POST   /chat

GET    /conversations
POST   /conversations
PATCH  /conversations/{conversation_id}
DELETE /conversations/{conversation_id}
GET    /conversations/{conversation_id}/messages
```

### 주요 구현 흐름

```txt
API Layer
→ Dependency Layer
→ Service Layer
→ Repository Layer
→ Database
```

### 사용 기술 스택

```txt
Python
FastAPI
Pydantic
SQLAlchemy
SQLite
JWT
python-jose
APIRouter
Depends
Repository Pattern
Service Layer Pattern
```

### 관련 파일

```txt
backend/app/main.py

backend/app/api/auth.py
backend/app/api/chat.py
backend/app/api/conversation.py

backend/app/dependencies/auth.py
backend/app/dependencies/database.py
backend/app/dependencies/conversation.py
backend/app/dependencies/gpt.py

backend/app/models/user.py
backend/app/models/conversation.py
backend/app/models/message.py

backend/app/repositories/user_repository.py
backend/app/repositories/conversation_repository.py
backend/app/repositories/message_repository.py

backend/app/services/auth_service.py
backend/app/services/conversation_service.py
backend/app/services/gpt_service.py

backend/app/schemas/auth.py
backend/app/schemas/chat.py
backend/app/schemas/conversation.py
backend/app/schemas/message.py
```

---

## Phase 3. React Frontend MVP

### 목표

사용자가 실제로 로그인하고, 채팅하고, 대화 이력을 관리할 수 있는 React 기반 프론트엔드를 구현하는 단계다.

### 구현 기능

* Vite + React + TypeScript 프로젝트 구성
* Login Page 구현
* JWT Access Token 저장
* Axios Client 구성
* Axios Request Interceptor로 Authorization Header 자동 첨부
* Axios Response Interceptor로 401 / 403 처리
* React Router 기반 인증 라우팅 구현
* ProtectedRoute 구현
* PublicOnlyRoute 구현
* 로그아웃 구현
* ChatPage 구현
* Chat UI 구현
* User / Assistant 메시지 말풍선 구분
* Conversation Sidebar 구현
* Conversation 목록 조회
* Conversation 선택
* Conversation 생성
* Conversation 삭제
* Conversation 제목 수정
* Conversation별 Message 조회
* 메시지 자동 스크롤
* Assistant Loading Bubble 구현
* Optimistic UI 구현
* Error State 처리
* Empty State 처리
* 잘못된 토큰 입력 후 `/login` 이동 테스트 완료

### 주요 사용자 흐름

```txt
로그인
→ Access Token 저장
→ ChatPage 이동
→ Conversation 목록 조회
→ 메시지 입력
→ /chat API 호출
→ User Message 즉시 표시
→ Assistant Loading Bubble 표시
→ Assistant 응답 표시
→ Conversation History 유지
```

### 사용 기술 스택

```txt
React
TypeScript
Vite
React Router
Axios
CSS
localStorage
React useState
React useEffect
React useRef
Optimistic UI
```

### 관련 파일

```txt
frontend/src/api/axiosClient.ts
frontend/src/api/authApi.ts
frontend/src/api/chatApi.ts
frontend/src/api/conversationApi.ts

frontend/src/components/auth/ProtectedRoute.tsx
frontend/src/components/auth/PublicOnlyRoute.tsx

frontend/src/components/conversation/ConversationSidebar.tsx
frontend/src/components/conversation/ConversationSidebar.css

frontend/src/pages/LoginPage.tsx
frontend/src/pages/LoginPage.css
frontend/src/pages/ChatPage.tsx
frontend/src/pages/ChatPage.css

frontend/src/types/conversation.ts
frontend/src/utils/authStorage.ts

frontend/src/App.tsx
frontend/src/main.tsx
frontend/src/index.css
```

---

## Phase 4. Document Upload Pipeline

### 목표

RAG 기능을 구현하기 위한 첫 번째 기반 단계다.
사용자가 PDF 또는 TXT 문서를 업로드하면 서버에 저장하고, 텍스트를 추출한 뒤 chunk 단위로 분할하여 DB에 저장하는 기능을 구현했다.

### 구현 기능

* PDF / TXT 파일 업로드 API 구현
* 업로드 파일 서버 저장
* 고유 파일명 생성
* 문서 메타데이터 저장
* PDF 텍스트 추출
* TXT 텍스트 추출
* UTF-8 / CP949 인코딩 대응
* 긴 텍스트 chunk 분할
* chunk overlap 적용
* `documents` 테이블 저장
* `document_chunks` 테이블 저장
* 사용자별 문서 목록 조회
* 문서별 chunk 목록 조회
* Swagger 기반 문서 업로드 테스트

### 구현 API

```txt
POST /documents/upload
GET  /documents
GET  /documents/{document_id}/chunks
```

### 주요 처리 흐름

```txt
PDF/TXT 업로드
→ 파일 확장자 검증
→ uploads/documents 폴더에 파일 저장
→ 텍스트 추출
→ chunk 분할
→ documents 테이블에 메타데이터 저장
→ document_chunks 테이블에 chunk 저장
→ document + chunk_count 반환
```

### 저장 데이터

#### documents 테이블

```txt
id
user_id
original_filename
stored_filename
content_type
created_at
```

#### document_chunks 테이블

```txt
id
document_id
chunk_index
content
created_at
```

### 사용 기술 스택

```txt
FastAPI UploadFile
Python pathlib
Python uuid4
Python os
pypdf
SQLAlchemy
SQLite
Repository Pattern
Service Layer
Text Chunking
Text Extraction
```

### 관련 파일

```txt
backend/app/api/document.py

backend/app/models/document.py
backend/app/models/document_chunk.py

backend/app/repositories/document_repository.py
backend/app/repositories/document_chunk_repository.py

backend/app/services/document_service.py
backend/app/services/text_extraction_service.py
backend/app/services/text_chunking_service.py

backend/app/dependencies/document.py

backend/app/schemas/document.py
```

---
