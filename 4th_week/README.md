# 🚀 클라우드 거버넌스 AI 서비스

클라우드 거버넌스 관련 질문에 답변하고, 슬라이드 및 보고서를 HTML 형식으로 생성해주는 통합 AI 서비스입니다.

## 📋 목차

1. [프로젝트 개요](#-프로젝트-개요)
2. [시스템 아키텍처](#-시스템-아키텍처)
3. [기술 스택](#-기술-스택)
4. [설치 및 설정](#-설치-및-설정)
5. [사용법](#-사용법)
6. [시스템 구성요소](#-시스템-구성요소)
7. [예시](#-예시)

## 🎯 프로젝트 개요

이 시스템은 다음과 같은 기능을 제공합니다:

- **질문 응답**: 클라우드 거버넌스 관련 전문적인 질문에 대한 상세한 답변
- **슬라이드 생성**: 프레젠테이션용 슬라이드 자동 생성 (HTML 형식)
- **보고서 요약**: 구조화된 보고서 요약 생성 (HTML 형식)
- **RAG 기반 검색**: 문서 기반 정확한 정보 제공
- **MCP Protocol**: Model Context Protocol을 통한 에이전트 간 통신

## 🏗️ 시스템 아키텍처

본 시스템은 **마이크로서비스 아키텍처**를 채택하여 다음과 같이 구성됩니다:

### 1. API 서버 (Port 8000)

- **FastAPI 기반** 메인 API 서버
- 사용자 요청 처리 및 응답 제공
- RESTful API 엔드포인트 제공

### 2. MCP 도구 서버 (Port 8001)

- **FastMCP 기반** 도구 전용 서버
- Model Context Protocol을 통한 도구 제공
- RAG 검색, 슬라이드 포맷팅, 보고서 요약 등의 전문 도구

### 3. 에이전트 시스템

- **통합 에이전트 아키텍처**로 효율적인 작업 처리
- Task Management Agent를 통한 모든 작업 통합 처리
- MCP 클라이언트를 통한 도구 활용

## 🚀 주요 기능

- **🔍 질문 답변**: 클라우드 거버넌스 관련 전문 지식 제공
- **📊 슬라이드 생성**: HTML 형식의 아름다운 프레젠테이션 슬라이드 자동 생성
- **📋 보고서 요약**: HTML 형식의 구조화된 보고서 요약 생성
- **📄 RAG 검색**: 관련 문서에서 정보 검색 및 활용
- **🔧 MCP 도구**: 모듈화된 도구 시스템

## 🛠️ 기술 스택

### 웹 프레임워크

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Uvicorn**: ASGI 서버

### AI/ML

- **LangChain**: LLM 애플리케이션 프레임워크
- **Azure OpenAI**: GPT-4o, Text Embedding 3 Large
- **FAISS**: 벡터 유사도 검색

### 프로토콜

- **Model Context Protocol (MCP)**: 도구 간 통신 프로토콜
- **FastMCP**: MCP 서버 구현

### 문서 처리

- **PyPDF**: PDF 문서 로딩 및 파싱
- **RecursiveCharacterTextSplitter**: 텍스트 청킹

## 📋 사전 요구사항

1. **Python 3.9+**
2. **Azure OpenAI 계정 및 API 키**
3. **환경 변수 설정**

## ⚙️ 설치 및 설정

### 1. 저장소 클론 및 의존성 설치

```bash
cd 4th_week
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
AOAI_API_KEY=your_azure_openai_api_key
AOAI_ENDPOINT=https://your-resource.openai.azure.com/
AOAI_API_VERSION=2024-02-15-preview
```

### 3. 문서 준비

`docs/` 폴더에 클라우드 거버넌스 관련 PDF 문서를 배치하세요.

## 🚀 실행 방법

### 방법 1: 개별 서버 실행 (개발용)

**터미널 1 - MCP 도구 서버 실행:**

```bash
python mcp.py
```

- 포트: 8001
- 제공 도구: search_documents, format_slide, get_tool_status

**터미널 2 - FastAPI 메인 서버 실행:**

```bash
python api_server.py
```

- 포트: 8000
- API 엔드포인트: /chat, /health, /system/status

### 방법 2: 프로덕션 실행

**MCP 서버:**

```bash
uvicorn mcp:mcp --host 0.0.0.0 --port 8001
```

**API 서버:**

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

## 📊 API 사용법

### 메인 채팅 엔드포인트

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "클라우드 보안 정책에 대해 알려주세요"}'
```

**응답 예시:**

```json
{
  "success": true,
  "data": {
    "final_answer": "클라우드 보안 정책은...",
    "mcp_context": {
      "orchestrator": {
        "processing_flow": ["Router: question", "Planner: QuestionAgent", "Agent: question", "Answer: completed"],
        "status": "success"
      }
    }
  },
  "message": "요청이 성공적으로 처리되었습니다.",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 시스템 상태 확인

```bash
curl "http://localhost:8000/health"
```

### 슬라이드 생성 요청

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "데이터 거버넌스 슬라이드 만들어주세요"}'
```

## 🔧 MCP 도구 API

MCP 도구 서버는 다음 도구들을 제공합니다:

### 1. search_documents

```python
# 문서 검색
result = mcp_client.search_documents(
    query="클라우드 보안",
    top_k=5
)
```

### 2. format_slide

```python
# 슬라이드 포맷팅
result = mcp_client.format_slide(
    content="슬라이드 내용",
    title="제목",
    slide_type="basic",  # basic, detailed, comparison
    format_type="json"   # json, markdown
)
```

### 3. get_tool_status

```python
# 도구 서버 상태 확인
status = mcp_client.get_tool_status()
```

## 🏗️ 시스템 구조

```
4th_week/
├── api_server.py          # FastAPI 메인 서버
├── mcp.py                 # FastMCP 도구 서버
├── mcp_client.py          # MCP 클라이언트
├── orchestrator.py        # 오케스트레이터
├── agents/                # 에이전트 모듈
│   ├── router_agent.py
│   ├── planner_agent.py
│   ├── question_agent.py
│   ├── slide_generator_agent.py
│   └── answer_agent.py
├── tools/                 # 도구 모듈
│   ├── rag_retriever.py
│   └── slide_formatter.py
├── core/                  # 핵심 모듈
│   ├── base_agent.py
│   ├── base_tool.py
│   └── settings.py
└── docs/                  # 문서 저장소
```

## 🔄 처리 플로우

1. **사용자 요청** → FastAPI 서버 (`/chat`)
2. **의도 분석** → Router Agent
3. **작업 계획** → Planner Agent
4. **전문 처리** → Question/SlideGenerator Agent
   - MCP 클라이언트를 통한 도구 호출
   - RAG 검색, 슬라이드 포맷팅 등
5. **응답 정제** → Answer Agent
6. **최종 응답** → 사용자

## 🛡️ 에러 처리

- **MCP 서버 연결 실패**: 도구 없이도 기본 응답 제공
- **RAG 검색 실패**: 일반 지식 기반 응답
- **LLM 호출 실패**: 적절한 에러 메시지 반환

## 📈 모니터링

### 로그 확인

```bash
# API 서버 로그
tail -f api_server.log

# MCP 서버 로그
tail -f mcp_server.log
```

### 헬스 체크

```bash
# API 서버
curl http://localhost:8000/health

# MCP 서버
curl http://localhost:8001/tools/get_tool_status
```

## 🔧 개발 및 디버깅

### 개발 모드 실행

```bash
# 자동 리로드 활성화
uvicorn api_server:app --reload --port 8000
uvicorn mcp:mcp --reload --port 8001
```

### 디버그 모드

환경 변수 `DEBUG=true` 설정 시 상세 로그 출력

## 🤝 기여 방법

1. 포크 생성
2. 기능 브랜치 생성 (`git checkout -b feature/새기능`)
3. 커밋 (`git commit -am '새 기능 추가'`)
4. 푸시 (`git push origin feature/새기능`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🆘 문제 해결

### 일반적인 문제들

1. **MCP 서버 연결 실패**

   - MCP 서버가 실행 중인지 확인 (포트 8001)
   - 방화벽 설정 확인

2. **Azure OpenAI 인증 실패**

   - `.env` 파일의 API 키와 엔드포인트 확인
   - API 사용량 한도 확인

3. **FAISS 인덱스 오류**

   - `docs/` 폴더에 PDF 파일 존재 확인
   - 인덱스 재생성: `faiss/` 폴더 삭제 후 재시작

4. **메모리 부족**
   - FAISS 인덱스 크기 조정
   - PDF 문서 수 제한

---

**📧 문의:** 시스템 관련 문의사항은 이슈를 통해 남겨주세요.

---

**개발자**: AI Master Project Team  
**버전**: 1.0.0  
**최종 업데이트**: 2024년
