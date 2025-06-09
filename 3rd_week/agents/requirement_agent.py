from .a2a_communication import A2AAgent, A2ACommunicationManager
from typing import Dict, Any
import uuid


class RequirementAnalysisAgent(A2AAgent):
    def __init__(self, llm, communication_manager: A2ACommunicationManager):
        super().__init__("requirement-analysis", llm, communication_manager)

        self.system_prompt = """당신은 요구사항 분석 전문가입니다. 
        프로젝트 설명을 분석하여 상세한 요구사항 명세서를 작성해야 합니다.
        다음 형식으로 요구사항을 작성하세요:
        1. 프로젝트 개요
        2. 기능적 요구사항
        3. 비기능적 요구사항
        4. 제약사항
        5. 가정사항
        
        명확하고 구조화된 형태로 응답해주세요."""

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """요구사항 분석 메시지 처리"""
        try:
            project_description = input_data.get("input", "")

            # LLM을 사용하여 요구사항 분석
            requirement_spec = await self.process_with_llm(
                self.system_prompt,
                f"다음 프로젝트에 대한 상세한 요구사항 명세서를 작성해주세요:\n\n{project_description}",
            )

            result = {
                "requirement_spec": requirement_spec,
                "status": "completed",
                "agent": self.agent_name,
            }

            # 다음 에이전트에게 자동으로 전송
            if input_data.get("auto_forward", True):
                await self.send_to_agent(
                    "requirement-validator",
                    {
                        "input": requirement_spec,
                        "message_id": str(uuid.uuid4()),
                        "auto_forward": True,
                    },
                )

            return result

        except Exception as e:
            return {"error": str(e), "status": "failed", "agent": self.agent_name}

    async def analyze_requirements(self, project_description: str) -> Dict[str, Any]:
        """외부에서 직접 호출 가능한 요구사항 분석 메서드"""
        input_data = {"input": project_description, "auto_forward": False}
        return await self.process_message(input_data)
