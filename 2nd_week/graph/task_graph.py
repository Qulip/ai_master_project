from langgraph.graph import StateGraph, END
from typing import Dict, List, Any, TypedDict, Annotated, Literal
from agents.task_planner import TaskPlannerAgent
from agents.todo_generator import TodoGeneratorAgent
from agents.scheduler import SchedulerAgent
from agents.review_agent import ReviewAgent
from utils.mcp_context import MCPContext
import json


class TaskState(TypedDict):
    """LangGraph 상태를 정의하는 클래스"""

    goal: str
    task_areas: List[str]
    todos: Dict[str, List[Dict[str, Any]]]
    schedule: Dict[str, Any]
    review_result: Dict[str, Any]
    context: MCPContext
    current_node: str
    human_input: str
    output: str
    next: str


def create_task_graph():
    """
    TODO 생성 및 일정 추천을 위한 LangGraph 흐름을 생성합니다.

    Returns:
        컴파일된 LangGraph 실행 그래프
    """
    # 에이전트 초기화 - 싱글톤 패턴 활용
    task_planner = TaskPlannerAgent()
    todo_generator = TodoGeneratorAgent()
    scheduler = SchedulerAgent()
    reviewer = ReviewAgent()

    # 그래프 생성
    graph = StateGraph(TaskState)

    # 노드 정의

    # 1. 목표 분석 노드
    def analyze_goal(state: TaskState) -> TaskState:
        goal = state["goal"]
        context = state["context"]

        # 목표 분석
        result = task_planner.analyze_goal(goal)
        task_areas = result["task_areas"]

        # 컨텍스트 업데이트
        context.set_goal(goal)
        context.set_task_areas(task_areas)

        # 상태 업데이트
        state["task_areas"] = task_areas
        state["current_node"] = "analyze_goal"
        state["output"] = (
            f"목표를 분석했습니다: {result['goal_analysis']}\n\n작업 영역: {', '.join(task_areas)}"
        )

        return state

    # 2. TODO 생성 노드
    def generate_todos(state: TaskState) -> TaskState:
        goal = state["goal"]
        task_areas = state["task_areas"]
        context = state["context"]

        # TODO 생성
        todos = todo_generator.generate_todos(goal, task_areas)

        # 컨텍스트 업데이트
        for area, tasks in todos.items():
            for task in tasks:
                context.add_todo(area, task)

        # 상태 업데이트
        state["todos"] = todos
        state["current_node"] = "generate_todos"
        state["output"] = (
            f"할 일 목록을 생성했습니다:\n\n{context.get_formatted_todos()}"
        )

        return state

    # 3. 일정 추천 노드
    def recommend_schedule(state: TaskState) -> TaskState:
        goal = state["goal"]
        todos = state["todos"]
        context = state["context"]

        # 일정 추천
        schedule_result = scheduler.recommend_schedule(goal, todos)

        # 컨텍스트 업데이트
        context.set_schedule(schedule_result["start_date"], schedule_result["tasks"])

        # 상태 업데이트
        state["schedule"] = schedule_result
        state["current_node"] = "recommend_schedule"
        state["output"] = f"일정을 추천했습니다:\n\n{context.get_formatted_schedule()}"

        return state

    # 4. 검토 노드
    def review_plan(state: TaskState) -> TaskState:
        goal = state["goal"]
        context = state["context"]

        # 검토
        todos_markdown = context.get_formatted_todos()
        schedule_markdown = context.get_formatted_schedule()
        review_result = reviewer.review_plan(goal, todos_markdown, schedule_markdown)

        # 상태 업데이트
        state["review_result"] = review_result
        state["current_node"] = "review_plan"

        # 출력 생성
        output = f"검토 결과:\n\n{review_result['review_comment']}\n\n"

        if review_result["suggestions"]:
            output += "개선 제안:\n"
            for suggestion in review_result["suggestions"]:
                if suggestion["type"] == "add":
                    output += f"- 추가: {suggestion['area']}에 '{suggestion['task']['title']}' 추가 ({suggestion['task'].get('duration_days', 0)}일)\n"
                elif suggestion["type"] == "remove":
                    output += f"- 제거: {suggestion['area']}에서 '{suggestion['task_title']}' 제거\n"
                elif suggestion["type"] == "modify_duration":
                    output += f"- 수정: {suggestion['area']}의 '{suggestion['task_title']}'의 소요 시간을 {suggestion['new_duration']}일로 변경\n"

        state["output"] = output

        return state

    # 5. 최종 결과 노드
    def generate_final_output(state: TaskState) -> TaskState:
        context = state["context"]

        # 최종 출력 생성
        output = f"### 목표: {context.goal}\n\n"
        output += context.get_formatted_todos() + "\n\n"
        output += context.get_formatted_schedule()

        state["output"] = output
        state["current_node"] = "final_output"

        return state

    # 6. 사용자 입력 처리 노드
    def process_human_input(state: TaskState) -> TaskState:
        human_input = state["human_input"].lower()
        context = state["context"]

        # 사용자 입력을 컨텍스트에 추가
        context.add_to_history("user", human_input)

        # 사용자 입력에 따른 다음 노드 결정
        if "수정" in human_input or "변경" in human_input:
            if "할일" in human_input or "todo" in human_input:
                state["next"] = "generate_todos"
            elif "일정" in human_input or "스케줄" in human_input:
                state["next"] = "recommend_schedule"
        elif "검토" in human_input:
            state["next"] = "review_plan"
        elif "완료" in human_input or "종료" in human_input:
            state["next"] = "final_output"
        else:
            # 기본적으로 검토 단계로 이동
            state["next"] = "review_plan"

        state["current_node"] = "process_human_input"
        return state

    # 노드 추가
    graph.add_node("analyze_goal", analyze_goal)
    graph.add_node("generate_todos", generate_todos)
    graph.add_node("recommend_schedule", recommend_schedule)
    graph.add_node("review_plan", review_plan)
    graph.add_node("final_output", generate_final_output)
    graph.add_node("process_human_input", process_human_input)

    # 엣지 추가
    graph.add_edge("analyze_goal", "generate_todos")
    graph.add_edge("generate_todos", "recommend_schedule")
    graph.add_edge("recommend_schedule", "review_plan")

    # 초기 실행에서는 review_plan에서 종료
    # 사용자 입력이 있을 때만 process_human_input으로 이동
    def should_process_human_input(state: TaskState) -> str:
        """사용자 입력이 있는지 확인하여 다음 노드 결정"""
        if state.get("human_input", "").strip():
            return "process_human_input"
        else:
            return "END"

    graph.add_conditional_edges(
        "review_plan",
        should_process_human_input,
        {"process_human_input": "process_human_input", "END": END},
    )

    # 조건부 엣지 추가
    def route_after_human_input(state: TaskState) -> str:
        """사용자 입력 후 다음 노드를 결정하는 라우팅 함수"""
        return state.get("next", "review_plan")

    graph.add_conditional_edges(
        "process_human_input",
        route_after_human_input,
        {
            "generate_todos": "generate_todos",
            "recommend_schedule": "recommend_schedule",
            "review_plan": "review_plan",
            "final_output": "final_output",
        },
    )

    graph.add_edge("final_output", END)

    # 시작 노드 설정
    graph.set_entry_point("analyze_goal")

    # 그래프 컴파일
    return graph.compile()


def initialize_state(goal: str) -> TaskState:
    """
    초기 상태를 생성합니다.

    Args:
        goal: 사용자의 목표

    Returns:
        초기 상태
    """
    context = MCPContext()

    return {
        "goal": goal,
        "task_areas": [],
        "todos": {},
        "schedule": {},
        "review_result": {},
        "context": context,
        "current_node": "",
        "human_input": "",
        "output": "",
        "next": "",
    }
