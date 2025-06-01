from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any
import json
from conf.settings import get_llm


class TodoGeneratorAgent:
    """
    작업 영역별로 세부 할 일 목록을 생성하는 에이전트
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model = get_llm()
        self.output_parser = JsonOutputParser()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            당신은 목표 달성을 위한 세부 할 일 목록을 생성하는 전문가입니다.
            
            사용자의 목표와 작업 영역을 바탕으로, 각 영역별 구체적인 할 일 목록을 생성하세요.
            각 할 일은 명확하고 실행 가능해야 하며, 각 작업 영역에 대해 3-5개의 할 일을 생성하세요.
            
            각 할 일에는 다음 정보를 포함하세요:
            1. 제목: 간결하고 명확한 할 일 제목
            2. 설명: 필요한 경우 간략한 설명
            3. 소요 시간(일): 예상 소요 시간(일 단위)
            
            결과는 다음 JSON 형식으로 반환하세요:
            {
                "영역1": [
                    {"title": "할 일 제목", "description": "설명", "duration_days": 1},
                    ...
                ],
                "영역2": [
                    {"title": "할 일 제목", "description": "설명", "duration_days": 2},
                    ...
                ],
                ...
            }
            """,
                ),
                (
                    "user",
                    """
            목표: {goal}
            
            작업 영역:
            {task_areas}
            
            각 영역별로 구체적인 할 일 목록을 생성해주세요.
            """,
                ),
            ]
        )

    def generate_todos(
        self, goal: str, task_areas: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        작업 영역별로 세부 할 일 목록을 생성합니다.

        Args:
            goal: 사용자의 목표
            task_areas: 작업 영역 목록

        Returns:
            영역별 할 일 목록이 포함된 딕셔너리
        """
        chain = self.prompt | self.model | self.output_parser

        try:
            task_areas_str = "\n".join([f"- {area}" for area in task_areas])
            result = chain.invoke({"goal": goal, "task_areas": task_areas_str})
            return result
        except Exception as e:
            # 파싱 오류 시 기본값 반환
            print(f"Error generating todos: {e}")
            default_todos = {}
            for area in task_areas:
                default_todos[area] = [
                    {
                        "title": f"{area} 계획 수립",
                        "description": "기본 계획 수립",
                        "duration_days": 1,
                    },
                    {
                        "title": f"{area} 실행",
                        "description": "계획 실행",
                        "duration_days": 2,
                    },
                    {
                        "title": f"{area} 검토",
                        "description": "결과 검토",
                        "duration_days": 1,
                    },
                ]
            return default_todos
