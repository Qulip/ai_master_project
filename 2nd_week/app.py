import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from graph.task_graph import create_task_graph, initialize_state
from utils.mcp_context import MCPContext
from conf.settings import config

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키와 모델 설정
api_key = os.getenv("AOAI_API_KEY", "")
model_name = os.getenv("AOAI_DEPLOY_GPT4O")

# API 키가 설정되어 있으면 config에도 설정
if api_key:
    config.AOAI_API_KEY = api_key

# 페이지 설정
st.set_page_config(page_title="AI 기반 TODO 생성기", page_icon="✅", layout="wide")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "graph" not in st.session_state:
    st.session_state.graph = None

if "task_state" not in st.session_state:
    st.session_state.task_state = None

if "current_step" not in st.session_state:
    st.session_state.current_step = "goal_input"

if "goal" not in st.session_state:
    st.session_state.goal = ""

# 헤더 및 설명
st.title("✅ AI 기반 TODO 생성기")
st.markdown(
    """
이 앱은 사용자가 간단한 목표를 입력하면, AI가 이를 분석하여 구체적인 할 일 목록(TODO 리스트)과 
추천 일정(Time Plan)을 자동으로 생성해주는 서비스입니다.
"""
)

# 사이드바 - API 키 입력 부분 제거하고 사용 방법만 표시
with st.sidebar:
    st.header("설정")

    # API 키 상태 표시
    if api_key:
        st.success("✅ API 키가 설정되었습니다")
        st.info(f"사용 모델: {model_name}")
    else:
        st.error("❌ API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")

    st.markdown("---")
    st.markdown("### 사용 방법")
    st.markdown(
        """
    1. 목표를 입력하세요 (예: "2주 안에 포트폴리오 웹사이트 만들기")
    2. AI가 목표를 분석하고 할 일 목록을 생성합니다
    3. 일정을 추천받고 검토합니다
    4. 필요한 경우 수정을 요청할 수 있습니다
    """
    )

# 메인 화면
if st.session_state.current_step == "goal_input":
    st.header("목표 입력")

    goal_input = st.text_input(
        "달성하고자 하는 목표를 입력하세요",
        placeholder="예: 2주 안에 포트폴리오 웹사이트 만들기",
    )

    if st.button("분석 시작", type="primary", disabled=not api_key or not goal_input):
        with st.spinner("목표를 분석 중입니다..."):
            # 그래프 생성 - model_name 전달하지 않음 (singleton 패턴 활용)
            st.session_state.graph = create_task_graph()

            # 초기 상태 설정
            st.session_state.task_state = initialize_state(goal_input)
            st.session_state.goal = goal_input

            # 그래프 실행 - 초기 실행 (analyze_goal → generate_todos → recommend_schedule → review_plan)
            result = st.session_state.graph.invoke(st.session_state.task_state)

            # 결과에서 출력 메시지들을 추출
            if "output" in result and result["output"]:
                st.session_state.messages.append(
                    {"role": "assistant", "content": result["output"]}
                )

            # review_plan 단계로 이동
            st.session_state.current_step = "review"
            st.session_state.task_state = result

            st.rerun()

elif st.session_state.current_step == "review":
    st.header(f"목표: {st.session_state.goal}")

    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    user_input = st.chat_input(
        "수정이 필요하면 입력하세요 (예: '할일 목록을 수정해주세요', '일정을 더 여유있게 해주세요', '완료')"
    )

    if user_input:
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("처리 중..."):
            # 사용자 입력 처리
            st.session_state.task_state["human_input"] = user_input

            # 그래프 실행 - 사용자 입력 처리
            result = st.session_state.graph.invoke(st.session_state.task_state)

            # 결과에서 출력 메시지 추출
            if "output" in result and result["output"]:
                st.session_state.messages.append(
                    {"role": "assistant", "content": result["output"]}
                )

            # 최종 출력이면 결과 단계로 이동
            if result.get("current_node") == "final_output":
                st.session_state.current_step = "result"

            # 상태 업데이트
            st.session_state.task_state = result

            st.rerun()

elif st.session_state.current_step == "result":
    st.header(f"최종 결과: {st.session_state.goal}")

    # 최종 결과 표시
    final_output = (
        st.session_state.messages[-1]["content"] if st.session_state.messages else ""
    )
    st.markdown(final_output)

    # 다운로드 버튼
    if final_output:
        current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"todo_plan_{current_date}.md"

        st.download_button(
            label="마크다운 파일로 다운로드",
            data=final_output,
            file_name=filename,
            mime="text/markdown",
        )

    # 새로운 목표 시작 버튼
    if st.button("새로운 목표 시작", type="primary"):
        # 세션 상태 초기화
        st.session_state.messages = []
        st.session_state.graph = None
        st.session_state.task_state = None
        st.session_state.current_step = "goal_input"
        st.session_state.goal = ""
        st.rerun()

# 푸터
st.markdown("---")
st.markdown("AI 기반 TODO 생성기 | LangChain + LangGraph + MCP")
