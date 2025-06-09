from .base_agent import BaseAgent, BaseAgentTool


class RequirementAnalysisAgent(BaseAgent):
    def __init__(self, llm):
        tools = [
            BaseAgentTool(
                name="analyze_requirements",
                description="Analyze project description and create detailed requirements specification",
                func=self._analyze_requirements,
            )
        ]

        system_message = """당신은 요구사항 분석 전문가입니다. 
        프로젝트 설명을 분석하여 상세한 요구사항 명세서를 작성해야 합니다.
        다음 형식으로 요구사항을 작성하세요:
        1. 프로젝트 개요
        2. 기능적 요구사항
        3. 비기능적 요구사항
        4. 제약사항
        5. 가정사항"""

        super().__init__(llm, tools, system_message)

    def _analyze_requirements(self, project_description: str) -> str:
        return {
            "requirement_spec": f"""
            프로젝트 분석 결과:
            {project_description}에 대한 상세 요구사항 분석...
            """
        }
