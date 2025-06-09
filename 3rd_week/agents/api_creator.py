from .a2a_communication import A2AAgent, A2ACommunicationManager
from typing import Dict, Any
import uuid


class APISpecCreatorAgent(A2AAgent):
    def __init__(self, llm, communication_manager: A2ACommunicationManager):
        super().__init__("api-spec-creator", llm, communication_manager)

        self.system_prompt = """당신은 API 명세서 작성 전문가입니다.
        요구사항과 서비스 흐름도를 바탕으로 다음 항목을 포함한 상세한 API 명세서를 작성해야 합니다:
        1. API 엔드포인트 목록 (RESTful 설계 원칙 적용)
        2. 요청/응답 스키마 (JSON 형식)
        3. HTTP 메서드와 상태 코드
        4. 인증 및 권한 관리
        5. 에러 처리 및 응답 형식
        6. API 버전 관리 전략
        7. 보안 고려사항
        
        OpenAPI 3.0 규격에 맞춰 작성해주세요."""

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """API 명세서 생성 메시지 처리"""
        try:
            requirement_spec = input_data.get("requirement_spec", "")
            service_flow = input_data.get("service_flow", "")

            user_input = f"""
            요구사항 명세서:
            {requirement_spec}
            
            서비스 흐름도:
            {service_flow}
            
            위 정보를 바탕으로 상세한 API 명세서를 OpenAPI 3.0 형식으로 작성해주세요.
            """

            # LLM을 사용하여 API 명세서 생성
            api_spec = await self.process_with_llm(self.system_prompt, user_input)

            result = {
                "requirement_spec": requirement_spec,
                "service_flow": service_flow,
                "api_spec": api_spec,
                "status": "completed",
                "agent": self.agent_name,
            }

            # 다음 에이전트에게 자동으로 전송
            if input_data.get("auto_forward", True):
                await self.send_to_agent(
                    "api-spec-validator",
                    {
                        "input": api_spec,
                        "requirement_spec": requirement_spec,
                        "service_flow": service_flow,
                        "message_id": str(uuid.uuid4()),
                        "auto_forward": True,
                    },
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "failed", "agent": self.agent_name}

    async def create_api_spec(
        self, requirement_spec: str, service_flow: str
    ) -> Dict[str, Any]:
        """외부에서 직접 호출 가능한 API 명세서 생성 메서드"""
        input_data = {
            "requirement_spec": requirement_spec,
            "service_flow": service_flow,
            "auto_forward": False,
        }
        return await self.process_message(input_data)
