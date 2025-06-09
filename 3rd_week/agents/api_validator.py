from .a2a_communication import A2AAgent, A2ACommunicationManager
from typing import Dict, Any
import uuid


class APISpecValidatorAgent(A2AAgent):
    def __init__(self, llm, communication_manager: A2ACommunicationManager):
        super().__init__("api-spec-validator", llm, communication_manager)

        self.system_prompt = """당신은 API 명세서 검증 전문가입니다.
        제공된 API 명세서를 검토하고 다음 사항을 확인해야 합니다:
        1. RESTful 설계 원칙 준수
        2. OpenAPI 3.0 규격 준수
        3. 보안 고려사항 (인증, 권한, 데이터 보호)
        4. 에러 처리의 일관성
        5. API 성능 및 확장성
        6. 문서화의 완성도
        7. 요구사항과의 일치성
        
        검증 결과와 개선 제안사항을 포함하여 응답해주세요."""

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """API 명세서 검증 메시지 처리"""
        try:
            api_spec = input_data.get("input", "")
            requirement_spec = input_data.get("requirement_spec", "")
            service_flow = input_data.get("service_flow", "")

            user_input = f"""
            API 명세서:
            {api_spec}
            
            원본 요구사항:
            {requirement_spec}
            
            서비스 흐름도:
            {service_flow}
            
            위 API 명세서를 상세히 검증하고 개선 제안사항을 제공해주세요.
            """

            # LLM을 사용하여 API 명세서 검증
            api_validation = await self.process_with_llm(self.system_prompt, user_input)

            result = {
                "api_spec": api_spec,
                "api_validation": api_validation,
                "requirement_spec": requirement_spec,
                "service_flow": service_flow,
                "status": "completed",
                "agent": self.agent_name,
            }

            return result

        except Exception as e:
            return {"error": str(e), "status": "failed", "agent": self.agent_name}

    async def validate_api_spec(self, api_spec: str) -> Dict[str, Any]:
        """외부에서 직접 호출 가능한 API 명세서 검증 메서드"""
        input_data = {"input": api_spec, "auto_forward": False}
        return await self.process_message(input_data)
