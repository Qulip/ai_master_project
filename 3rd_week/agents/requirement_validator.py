from .base_agent import BaseAgent, BaseAgentTool


class RequirementValidatorAgent(BaseAgent):
    def __init__(self, llm):
        tools = [
            BaseAgentTool(
                name="validate_requirements",
                description="Validate the requirements specification",
                func=self._validate_requirements,
            )
        ]

        system_message = """당신은 요구사항 검증 전문가입니다.
        주어진 요구사항 명세서를 다음 기준으로 검증하세요:
        1. 명확성
        2. 완전성
        3. 일관성
        4. 실현 가능성
        5. 검증 가능성"""

        super().__init__(llm, tools, system_message)

    def _validate_requirements(self, requirement_spec: str) -> dict:
        return {
            "requirement_spec": requirement_spec,
            "validator_feedback": "요구사항 검증 결과...",
        }
