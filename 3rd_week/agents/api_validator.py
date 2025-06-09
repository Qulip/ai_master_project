from .base_agent import BaseAgent, BaseAgentTool


class APISpecValidatorAgent(BaseAgent):
    def __init__(self, llm):
        tools = [
            BaseAgentTool(
                name="validate_api_spec",
                description="Validate the API specification",
                func=self._validate_api_spec,
            )
        ]

        system_message = """당신은 API 명세서 검증 전문가입니다.
        API 명세서를 다음 기준으로 검증하세요:
        1. RESTful 설계 원칙 준수
        2. 보안성
        3. 확장성
        4. 문서화 품질
        5. 에러 처리의 적절성"""

        super().__init__(llm, tools, system_message)

    def _validate_api_spec(self, api_spec: str) -> dict:
        return {"api_validation": "API 명세서 검증 결과..."}
