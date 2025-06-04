from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from conf.settings import get_llm


class SchedulerAgent:
    """
    할 일 목록을 바탕으로 일정을 추천하는 에이전트
    """

    def __init__(self):
        self.model = get_llm()
        self.output_parser = JsonOutputParser()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 할 일 목록을 바탕으로 효율적인 일정을 추천하는 전문가입니다.
            
사용자의 할 일 목록과 목표 기간을 바탕으로, 각 할 일에 대한 시작일과 종료일을 추천하세요.
일정은 현실적이고 효율적이어야 합니다. 작업 간의 의존성과 우선순위를 고려하세요.

결과는 다음 JSON 형식으로 반환하세요:
{{
    "start_date": "YYYY-MM-DD",
    "tasks": [
        {{
            "title": "할 일 제목",
            "area": "작업 영역",
            "duration_days": 1,
            "start_day_offset": 0
        }},
        ...
    ]
}}""",
                ),
                (
                    "user",
                    """목표: {goal}

목표 기간: {duration} 일

할 일 목록:
{todos_json}

위 할 일 목록을 바탕으로 {duration}일 이내에 완료할 수 있는 효율적인 일정을 추천해주세요.
오늘({today})부터 시작한다고 가정합니다.""",
                ),
            ]
        )

    def recommend_schedule(
        self, goal: str, todos: Dict[str, List[Dict[str, Any]]], duration: int = None
    ) -> Dict[str, Any]:
        """
        할 일 목록을 바탕으로 일정을 추천합니다.

        Args:
            goal: 사용자의 목표
            todos: 영역별 할 일 목록
            duration: 목표 기간(일). None인 경우 할 일의 총 소요 시간을 사용

        Returns:
            추천 일정이 포함된 딕셔너리
        """
        # 총 소요 시간 계산
        total_days = 0
        flattened_todos = []

        for area, tasks in todos.items():
            for task in tasks:
                total_days += task.get("duration_days", 0)
                flattened_todos.append(
                    {
                        "title": task["title"],
                        "area": area,
                        "duration_days": task.get("duration_days", 0),
                    }
                )

        # 목표 기간이 지정되지 않은 경우, 총 소요 시간의 1.2배로 설정
        if duration is None:
            duration = int(total_days * 1.2)

        chain = self.prompt | self.model | self.output_parser

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            result = chain.invoke(
                {
                    "goal": goal,
                    "duration": duration,
                    "todos_json": json.dumps(todos, ensure_ascii=False, indent=2),
                    "today": today,
                }
            )

            # 날짜 문자열을 datetime 객체로 변환
            start_date = datetime.strptime(result["start_date"], "%Y-%m-%d")

            # 태스크 정렬 및 시작일 계산
            sorted_tasks = sorted(result["tasks"], key=lambda x: x["start_day_offset"])

            return {"start_date": start_date, "tasks": sorted_tasks}
        except Exception as e:
            # 파싱 오류 시 기본 일정 생성
            print(f"Error recommending schedule: {e}")

            start_date = datetime.now()
            tasks = []
            day_offset = 0

            for area, area_tasks in todos.items():
                for task in area_tasks:
                    tasks.append(
                        {
                            "title": task["title"],
                            "area": area,
                            "duration_days": task.get("duration_days", 1),
                            "start_day_offset": day_offset,
                        }
                    )
                    day_offset += task.get("duration_days", 1)

            return {"start_date": start_date, "tasks": tasks}
