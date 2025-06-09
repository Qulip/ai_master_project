from .a2a_communication import A2AAgent, A2ACommunicationManager
from typing import Dict, Any
import uuid


class RequirementValidatorAgent(A2AAgent):
    def __init__(self, llm, communication_manager: A2ACommunicationManager):
        super().__init__("requirement-validator", llm, communication_manager)

        self.system_prompt = """당신은 요구사항 검증 전문가입니다.
        제공된 요구사항 명세서를 검토하고 다음 사항을 확인해야 합니다:
        1. 완성도 - 모든 필수 항목이 포함되어 있는가?
        2. 명확성 - 요구사항이 명확하고 이해하기 쉬운가?
        3. 일관성 - 요구사항들 간에 모순이 없는가?
        4. 실현가능성 - 기술적으로 구현 가능한가?
        5. 측정가능성 - 성공 기준이 명확한가?
        
        검증 결과와 개선 제안사항을 포함하여 응답해주세요."""

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """요구사항 검증 메시지 처리"""
        try:
            requirement_spec = input_data.get("input", "")

            # LLM을 사용하여 요구사항 검증
            validator_feedback = await self.process_with_llm(
                self.system_prompt,
                f"다음 요구사항 명세서를 검증해주세요:\n\n{requirement_spec}",
            )

            result = {
                "requirement_spec": requirement_spec,
                "validator_feedback": validator_feedback,
                "status": "completed",
                "agent": self.agent_name,
            }

            # 다음 에이전트에게 자동으로 전송
            if input_data.get("auto_forward", True):
                await self.send_to_agent(
                    "service-flow-creator",
                    {
                        "input": requirement_spec,
                        "validation_feedback": validator_feedback,
                        "message_id": str(uuid.uuid4()),
                        "auto_forward": True,
                    },
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "failed", "agent": self.agent_name}

    async def validate_requirements(self, requirement_spec: str) -> Dict[str, Any]:
        """외부에서 직접 호출 가능한 요구사항 검증 메서드"""
        input_data = {"input": requirement_spec, "auto_forward": False}
        return await self.process_message(input_data)
