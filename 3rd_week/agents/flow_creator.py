from .base_agent import BaseAgent, BaseAgentTool


class ServiceFlowCreatorAgent(BaseAgent):
    def __init__(self, llm):
        tools = [
            BaseAgentTool(
                name="create_service_flow",
                description="Create service flow diagram based on requirements",
                func=self._create_service_flow,
            )
        ]

        system_message = """당신은 서비스 흐름도 작성 전문가입니다.
        요구사항 명세서를 바탕으로 다음 항목을 포함한 서비스 흐름도를 작성하세요:
        1. 주요 컴포넌트 정의
        2. 컴포넌트 간 상호작용
        3. 데이터 흐름
        4. 주요 프로세스 흐름"""

        super().__init__(llm, tools, system_message)

    def _create_service_flow(self, requirement_spec: str) -> dict:
        return {
            "requirement_spec": requirement_spec,
            "service_flow": "서비스 흐름도 작성 결과...",
        }
