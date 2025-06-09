# LangChain + Google Cloud A2A 통신 시스템

Azure OpenAI와 Google Cloud Pub/Sub을 활용한 Agent-to-Agent 통신 기반 프로젝트 분석 시스템입니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Requirement     │    │ Requirement     │    │ Service Flow    │
│ Analysis Agent  │───▶│ Validator Agent │───▶│ Creator Agent   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Google Cloud    │    │ Google Cloud    │    │ Google Cloud    │
│ Pub/Sub Topic   │    │ Pub/Sub Topic   │    │ Pub/Sub Topic   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ API Spec        │    │ API Spec        │
│ Creator Agent   │───▶│ Validator Agent │
└─────────────────┘    └─────────────────┘
```

## 📋 주요 구성요소

### 1. A2A 통신 매니저 (`a2a_communication.py`)

- Google Cloud Pub/Sub 기반 메시지 라우팅
- 에이전트 간 비동기 통신 관리
- 메시지 핸들러 등록 및 처리

### 2. 에이전트들

- **RequirementAnalysisAgent**: 프로젝트 요구사항 분석
- **RequirementValidatorAgent**: 요구사항 검증 및 피드백
- **ServiceFlowCreatorAgent**: 서비스 흐름도 설계
- **APISpecCreatorAgent**: API 명세서 작성
- **APISpecValidatorAgent**: API 명세서 검증

### 3. 오케스트레이터 (`a2a_orchestrator.py`)

- 전체 워크플로우 관리
- 인프라 설정 및 에이전트 생명주기 관리
- 결과 수집 및 상태 모니터링

## 🚀 설치 및 설정

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Google Cloud 설정

#### Google Cloud CLI 설치 및 로그인

```bash
# Google Cloud CLI 설치 (Windows)
# https://cloud.google.com/sdk/docs/install 참조

# 인증 설정
gcloud auth application-default login
```

#### 프로젝트 설정

```bash
# 프로젝트 ID 설정
gcloud config set project YOUR_PROJECT_ID

# Pub/Sub API 활성화
gcloud services enable pubsub.googleapis.com
```

### 3. 환경변수 설정

`env_template.txt`를 참조하여 `.env` 파일 생성:

```bash
# .env 파일 생성
cp env_template.txt .env
```

`.env` 파일 내용 수정:

```
# Azure OpenAI 설정
AOAI_API_KEY=실제_Azure_OpenAI_API_키
AOAI_ENDPOINT=https://실제-엔드포인트.openai.azure.com/
AOAI_API_VERSION=2024-02-15-preview

# Google Cloud 설정
GCP_PROJECT_ID=실제-구글클라우드-프로젝트-ID
GCP_TOPIC_PREFIX=agent-communication
GCP_REGION=asia-northeast3
```

## 🎯 사용법

### 기본 실행

```bash
cd 3rd_week
python main.py
```

### 개별 에이전트 테스트

```python
import asyncio
from conf.settings import get_llm
from conf.cloud_config import cloud_config
from agents.a2a_communication import A2ACommunicationManager
from agents.requirement_agent import RequirementAnalysisAgent

async def test_agent():
    llm = get_llm()
    comm_manager = A2ACommunicationManager(cloud_config.project_id)
    agent = RequirementAnalysisAgent(llm, comm_manager)

    result = await agent.analyze_requirements("테스트 프로젝트 설명")
    print(result)

asyncio.run(test_agent())
```

## 🔧 주요 기능

### 1. A2A 통신 플로우

1. **요구사항 분석** → Pub/Sub → **요구사항 검증**
2. **요구사항 검증** → Pub/Sub → **서비스 흐름도 설계**
3. **서비스 흐름도 설계** → Pub/Sub → **API 명세서 작성**
4. **API 명세서 작성** → Pub/Sub → **API 명세서 검증**

### 2. 비동기 처리

- 각 에이전트는 독립적인 처리 큐 운영
- 논블로킹 메시지 전송 및 수신
- 확장 가능한 아키텍처

### 3. 에러 처리

- 메시지 전송 실패 시 재시도 로직
- 타임아웃 처리
- 로깅 및 모니터링

## 📊 모니터링

### 에이전트 상태 확인

```python
status = await orchestrator.get_agent_status()
print(status)
```

### 로그 확인

- 콘솔에서 실시간 로그 확인
- 각 에이전트의 처리 상태 모니터링
- 에러 발생 시 상세 로그 제공

## 🔍 트러블슈팅

### 1. Google Cloud 인증 오류

```
DefaultCredentialsError: Could not automatically determine credentials.
```

**해결책**: `gcloud auth application-default login` 실행

### 2. Pub/Sub API 비활성화 오류

```
google.api_core.exceptions.Forbidden: 403 Pub/Sub API has not been used
```

**해결책**: `gcloud services enable pubsub.googleapis.com` 실행

### 3. 권한 오류

```
Permission denied on resource project
```

**해결책**:

- Google Cloud IAM에서 Pub/Sub Editor 권한 부여
- 서비스 계정 키 파일 사용 시 올바른 경로 설정

### 4. 에이전트 응답 없음

**확인사항**:

- 토픽과 구독이 올바르게 생성되었는지 확인
- 네트워크 연결 상태 확인
- LLM API 키 유효성 확인

## 🚧 확장 가능성

### 새로운 에이전트 추가

1. `A2AAgent` 클래스 상속
2. `process_message` 메서드 구현
3. 오케스트레이터에 에이전트 등록

### 다른 클라우드 서비스 연동

- AWS SQS/SNS
- Azure Service Bus
- Apache Kafka

### 실시간 웹 인터페이스

- WebSocket 기반 실시간 업데이트
- React/Vue.js 프론트엔드
- 진행상황 시각화

## 📝 주의사항

1. **비용**: Google Cloud Pub/Sub 사용 시 메시지 전송량에 따른 과금
2. **레이턴시**: 네트워크 통신으로 인한 지연 시간 고려
3. **순서**: 메시지 순서 보장이 필요한 경우 추가 설정 필요
4. **보안**: 민감한 정보는 암호화하여 전송 권장

## 🤝 기여

버그 리포트나 기능 개선 제안은 Issues를 통해 제출해주세요.

## 📄 라이선스

MIT License
