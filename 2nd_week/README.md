# AI 기반 TODO 생성기

이 프로젝트는 사용자가 간단한 목표나 작업 요청을 입력하면, AI가 이를 분석하여 구체적인 할 일 목록(TODO 리스트)과 추천 일정(Time Plan)을 자동으로 생성해주는 서비스입니다.

## 기능

- 목표 분석: 사용자의 목표에서 핵심 작업 영역 추출
- TODO 생성: 각 영역별로 세부 태스크 생성
- 일정 추천: 각 태스크별 소요 시간 추정 및 전체 일정 구성
- 최종 검토: TODO 및 일정 검토 및 수정 요청 가능

## 설치 방법

1. 저장소 클론

```
git clone [repository-url]
cd ai-todo-generator
```

2. 가상환경 생성 및 활성화

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치

```
pip install -r requirements.txt
```

4. 환경 변수 설정

```
cp .env.example .env
```

`.env` 파일을 열고 OpenAI API 키를 입력하세요.

## 실행 방법

```
streamlit run app.py
```

## 기술 스택

- LangChain: 태스크 분해 및 일정 추천을 위한 체인 구성
- LangGraph: 에이전트 흐름 정의
- MCP (Model Context Protocol): 대화 흐름 중 사용자의 컨텍스트 유지
- Streamlit: 웹 인터페이스
