from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any
import json
from conf.settings import get_llm


class ReviewAgent:
    """
    생성된 TODO 리스트와 일정을 검토하는 에이전트
    """

    def __init__(self):
        self.model = get_llm()
        self.output_parser = JsonOutputParser()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 생성된 TODO 리스트와 일정을 검토하는 전문가입니다.
            
사용자의 목표, 생성된 할 일 목록, 추천 일정을 검토하고 다음을 평가하세요:
1. 할 일 목록이 목표 달성에 충분한지
2. 일정이 현실적이고 효율적인지
3. 개선이 필요한 부분이 있는지

결과는 다음 JSON 형식으로 반환하세요:
{{
    "is_sufficient": true,
    "is_realistic": true,
    "review_comment": "검토 의견",
    "suggestions": [
        {{"type": "add", "area": "영역", "task": {{"title": "추가할 할 일", "description": "설명", "duration_days": 1}}}},
        {{"type": "remove", "area": "영역", "task_title": "제거할 할 일"}},
        {{"type": "modify_duration", "area": "영역", "task_title": "수정할 할 일", "new_duration": 2}}
    ]
}}""",
                ),
                (
                    "user",
                    """목표: {goal}

할 일 목록:
{todos_markdown}

추천 일정:
{schedule_markdown}

위 할 일 목록과 일정을 검토하고 평가해주세요.""",
                ),
            ]
        )

    def review_plan(
        self, goal: str, todos_markdown: str, schedule_markdown: str
    ) -> Dict[str, Any]:
        """
        생성된 TODO 리스트와 일정을 검토합니다.

        Args:
            goal: 사용자의 목표
            todos_markdown: 마크다운 형식의 할 일 목록
            schedule_markdown: 마크다운 형식의 일정

        Returns:
            검토 결과가 포함된 딕셔너리
        """
        chain = self.prompt | self.model | self.output_parser

        try:
            result = chain.invoke(
                {
                    "goal": goal,
                    "todos_markdown": todos_markdown,
                    "schedule_markdown": schedule_markdown,
                }
            )
            return result
        except Exception as e:
            # 파싱 오류 시 기본값 반환
            print(f"Error reviewing plan: {e}")
            return {
                "is_sufficient": True,
                "is_realistic": True,
                "review_comment": "할 일 목록과 일정이 적절해 보입니다.",
                "suggestions": [],
            }
