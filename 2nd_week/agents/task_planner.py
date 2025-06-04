from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, List, Any
import json
from conf.settings import get_llm


class TaskPlannerAgent:
    """
    사용자의 목표를 분석하여 핵심 작업 영역을 추출하는 에이전트
    """

    def __init__(self):
        self.model = get_llm()
        self.output_parser = JsonOutputParser()

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """당신은 사용자의 목표를 분석하여 핵심 작업 영역을 추출하는 전문가입니다.
            
사용자가 제공한 목표를 분석하고, 이를 달성하기 위해 필요한 주요 작업 영역을 식별하세요.
작업 영역은 3-6개 정도로 구성하며, 목표 달성을 위한 주요 카테고리여야 합니다.

예를 들어:
- "포트폴리오 웹사이트 만들기" → ["기획", "디자인", "개발", "콘텐츠 작성", "배포"]
- "책 출판하기" → ["기획", "집필", "편집", "디자인", "출판", "마케팅"]

결과는 다음 JSON 형식으로 반환하세요:
{{
    "task_areas": ["영역1", "영역2", "영역3", ...],
    "goal_analysis": "목표에 대한 간략한 분석"
}}""",
                ),
                ("user", "{goal}"),
            ]
        )

    def analyze_goal(self, goal: str) -> Dict[str, Any]:
        """
        사용자의 목표를 분석하여 핵심 작업 영역을 추출합니다.

        Args:
            goal: 사용자가 입력한 목표

        Returns:
            작업 영역과 목표 분석 결과가 포함된 딕셔너리
        """
        chain = self.prompt | self.model | self.output_parser

        try:
            result = chain.invoke({"goal": goal})
            return result
        except Exception as e:
            # 파싱 오류 시 기본값 반환
            print(f"Error analyzing goal: {e}")
            return {
                "task_areas": ["기획", "실행", "검토"],
                "goal_analysis": f"목표 분석 중 오류 발생: {goal}",
            }
