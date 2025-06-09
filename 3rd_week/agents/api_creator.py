from .base_agent import BaseAgent, BaseAgentTool


class APISpecCreatorAgent(BaseAgent):
    def __init__(self, llm):
        tools = [
            BaseAgentTool(
                name="create_api_spec",
                description="Create API specification based on requirements and service flow",
                func=self._create_api_spec,
            )
        ]

        system_message = """당신은 API 명세서 작성 전문가입니다.
        요구사항과 서비스 흐름도를 바탕으로 다음 항목을 포함한 API 명세서를 작성하세요:
        1. API 엔드포인트 목록
        2. 요청/응답 형식
        3. 인증 방식
        4. 에러 처리
        5. API 버전 관리"""

        super().__init__(llm, tools, system_message)

    def _create_api_spec(self, requirement_spec: str, service_flow: str) -> dict:
        return {
            "requirement_spec": requirement_spec,
            "service_flow": service_flow,
            "api_spec": "API 명세서 작성 결과...",
        }
