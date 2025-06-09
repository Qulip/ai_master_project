from .a2a_communication import A2AAgent, A2ACommunicationManager
from typing import Dict, Any
import uuid


class ServiceFlowCreatorAgent(A2AAgent):
    def __init__(self, llm, communication_manager: A2ACommunicationManager):
        super().__init__("service-flow-creator", llm, communication_manager)

        self.system_prompt = """당신은 서비스 흐름도 설계 전문가입니다.
        요구사항 명세서를 바탕으로 다음을 포함한 서비스 흐름도를 작성해야 합니다:
        1. 사용자 여정 (User Journey)
        2. 시스템 간 상호작용
        3. 데이터 흐름
        4. 비즈니스 프로세스 흐름
        5. 예외 처리 흐름
        
        명확하고 논리적인 순서로 서비스 흐름을 설계해주세요."""

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """서비스 흐름도 생성 메시지 처리"""
        try:
            requirement_spec = input_data.get("input", "")
            validation_feedback = input_data.get("validation_feedback", "")

            user_input = f"""
            요구사항 명세서:
            {requirement_spec}
            
            검증 피드백:
            {validation_feedback}
            
            위 정보를 바탕으로 상세한 서비스 흐름도를 작성해주세요.
            """

            # LLM을 사용하여 서비스 흐름도 생성
            service_flow = await self.process_with_llm(self.system_prompt, user_input)

            result = {
                "requirement_spec": requirement_spec,
                "service_flow": service_flow,
                "status": "completed",
                "agent": self.agent_name,
            }

            # 다음 에이전트에게 자동으로 전송
            if input_data.get("auto_forward", True):
                await self.send_to_agent(
                    "api-spec-creator",
                    {
                        "requirement_spec": requirement_spec,
                        "service_flow": service_flow,
                        "message_id": str(uuid.uuid4()),
                        "auto_forward": True,
                    },
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "failed", "agent": self.agent_name}

    async def create_service_flow(self, requirement_spec: str) -> Dict[str, Any]:
        """외부에서 직접 호출 가능한 서비스 흐름도 생성 메서드"""
        input_data = {"input": requirement_spec, "auto_forward": False}
        return await self.process_message(input_data)
