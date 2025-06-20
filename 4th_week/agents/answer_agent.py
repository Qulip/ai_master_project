from typing import Dict, Any
from core import BaseAgent


class AnswerAgent(BaseAgent):
    """
    Answer Agent
    Question Agent 또는 SlideGenerator Agent의 결과를
    사용자 응답 형식으로 정제하여 반환하는 최종 에이전트
    """

    def __init__(self):
        super().__init__("AnswerAgent")
        self.mcp_context = {
            "role": "responder",
            "function": "final_response_formatting",
        }

    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        """
        최종 사용자 응답 생성을 위한 프롬프트 생성

        Args:
            inputs (Dict[str, Any]): Question/SlideGenerator Agent 결과

        Returns:
            str: LLM용 프롬프트
        """
        agent_type = inputs.get("agent_type", "unknown")
        answer_content = inputs.get("answer_content", "")
        confidence = inputs.get("confidence", "medium")
        source_type = inputs.get("source_type", "unknown")

        if agent_type == "question":
            prompt = f"""
당신은 클라우드 거버넌스 AI 어시스턴트입니다.
Question Agent가 생성한 답변을 사용자에게 친근하고 이해하기 쉽게 전달해야 합니다.

**Question Agent 답변:**
{answer_content}

**답변 신뢰도:** {confidence}
**정보 출처:** {source_type}

**응답 작성 지침:**
1. 친근하고 전문적인 어조 유지
2. 핵심 정보를 명확하게 전달
3. 필요시 추가 질문을 유도
4. 클라우드 거버넌스 전문성 어필
5. 실행 가능한 조언 포함

**출력 형식:**
자연스러운 한국어로 완성된 답변을 작성하세요.
답변 마지막에는 "추가 궁금한 점이 있으시면 언제든 말씀해 주세요!" 등의 친근한 마무리 문구를 포함하세요.
"""

        elif agent_type == "slide_generation":
            slide_data = inputs.get("slide_data", {})
            slide_markdown = inputs.get("slide_markdown", "")

            prompt = f"""
당신은 클라우드 거버넌스 AI 어시스턴트입니다.
SlideGenerator Agent가 생성한 슬라이드를 사용자에게 효과적으로 제시해야 합니다.

**SlideGenerator Agent 결과:**
{answer_content}

**생성된 슬라이드 데이터:**
{slide_data}

**마크다운 형식 슬라이드:**
{slide_markdown}

**응답 작성 지침:**
1. 슬라이드 생성 완료를 명확하게 알림
2. 슬라이드의 핵심 내용 요약 제시
3. 마크다운 형식으로 슬라이드 내용 표시
4. 추가 수정이나 다른 형식 요청 가능함을 안내
5. 전문적이면서도 친근한 어조 유지

**출력 형식:**
"📊 클라우드 거버넌스 슬라이드가 생성되었습니다!"로 시작하여,
마크다운 형식의 슬라이드 내용을 포함하고,
마지막에 "슬라이드 내용 수정이나 다른 형식을 원하시면 말씀해 주세요!" 등의 안내 문구를 포함하세요.
"""

        else:
            # 일반적인 대화나 오류 처리
            prompt = f"""
당신은 클라우드 거버넌스 AI 어시스턴트입니다.
사용자와 자연스럽게 대화하며 도움을 제공해야 합니다.

**처리 결과:**
{answer_content}

**상황:** {agent_type} 타입 처리

**응답 작성 지침:**
1. 친근하고 도움이 되는 어조
2. 클라우드 거버넌스 관련 도움 제공 의지 표현
3. 구체적인 질문이나 요청을 유도
4. 전문성을 바탕으로 한 신뢰감 조성

**출력 형식:**
자연스러운 한국어로 완성된 응답을 작성하세요.
"""

        return prompt

    def postprocess(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer Agent 최종 출력 후처리

        Args:
            outputs (Dict[str, Any]): LLM 응답

        Returns:
            Dict[str, Any]: 최종 사용자 응답
        """
        try:
            content = outputs.content if hasattr(outputs, "content") else str(outputs)

            # 최종 응답 형식 구성
            result = {
                "final_answer": content,
                "timestamp": self._get_timestamp(),
                "mcp_context": {
                    **self.mcp_context,
                    "status": "completed",
                    "response_ready": True,
                    "final_processing": True,
                },
            }

            return result

        except Exception as e:
            return {
                "final_answer": f"죄송합니다. 응답 처리 중 오류가 발생했습니다: {str(e)}\n\n다시 시도해 주시거나 다른 방식으로 질문해 주세요.",
                "timestamp": self._get_timestamp(),
                "mcp_context": {
                    **self.mcp_context,
                    "status": "error",
                    "message": str(e),
                },
            }

    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime

        return datetime.now().isoformat()
