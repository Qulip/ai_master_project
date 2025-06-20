from typing import Dict, Any
from agents import (
    RouterAgent,
    PlannerAgent,
    QuestionAgent,
    SlideGeneratorAgent,
    AnswerAgent,
)


class CloudGovernanceOrchestrator:
    """
    클라우드 거버넌스 AI 시스템 오케스트레이터
    모든 에이전트들을 조율하여 사용자 요청을 처리하는 메인 클래스
    """

    def __init__(self):
        self.router_agent = RouterAgent()
        self.planner_agent = PlannerAgent()
        self.question_agent = QuestionAgent()
        self.slide_generator_agent = SlideGeneratorAgent()
        self.answer_agent = AnswerAgent()

        self.mcp_context = {
            "role": "orchestrator",
            "function": "system_coordination",
            "agents_initialized": True,
        }

    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        사용자 요청을 처리하는 메인 메서드

        Args:
            user_input (str): 사용자 입력

        Returns:
            Dict[str, Any]: 최종 응답
        """
        try:
            print(f"🔄 사용자 입력 처리 시작: {user_input[:50]}...")

            # 1. Router Agent - 의도 분석
            print("📍 Router Agent: 의도 분석 중...")
            router_result = self.router_agent({"user_input": user_input})
            print(f"   └ Intent: {router_result.get('intent', 'unknown')}")

            # 2. Planner Agent - 작업 계획 수립
            print("📋 Planner Agent: 작업 계획 수립 중...")
            planner_input = {**router_result, "user_input": user_input}
            planner_result = self.planner_agent(planner_input)
            selected_agent = planner_result.get("selected_agent", "DirectAnswer")
            print(f"   └ Selected Agent: {selected_agent}")

            # 3. 선택된 Agent 실행
            agent_result = None
            if selected_agent == "QuestionAgent":
                print("❓ Question Agent: 질문 처리 중...")
                agent_input = {**planner_result, "user_input": user_input}
                agent_result = self.question_agent(agent_input)
                print("   └ 질문 처리 완료")

            elif selected_agent == "SlideGeneratorAgent":
                print("📊 SlideGenerator Agent: 슬라이드 생성 중...")
                agent_input = {**planner_result, "user_input": user_input}
                agent_result = self.slide_generator_agent(agent_input)
                print("   └ 슬라이드 생성 완료")

            else:  # DirectAnswer
                print("💬 Direct Answer: 직접 응답 처리 중...")
                agent_result = {
                    "agent_type": "direct",
                    "answer_content": self._generate_direct_answer(user_input),
                    "source_type": "direct",
                    "confidence": "medium",
                }
                print("   └ 직접 응답 완료")

            # 4. Answer Agent - 최종 응답 정제
            print("✨ Answer Agent: 최종 응답 정제 중...")
            final_result = self.answer_agent(agent_result)
            print("   └ 최종 응답 준비 완료")

            # 5. MCP Context 통합
            final_result["mcp_context"]["orchestrator"] = {
                **self.mcp_context,
                "processing_flow": [
                    f"Router: {router_result.get('intent', 'unknown')}",
                    f"Planner: {selected_agent}",
                    f"Agent: {agent_result.get('agent_type', 'unknown')}",
                    "Answer: completed",
                ],
                "status": "success",
            }

            print("✅ 요청 처리 완료")
            return final_result

        except Exception as e:
            print(f"❌ 오케스트레이터 오류: {str(e)}")
            return {
                "final_answer": f"시스템 처리 중 오류가 발생했습니다: {str(e)}\n\n다시 시도해 주세요.",
                "timestamp": self._get_timestamp(),
                "mcp_context": {
                    **self.mcp_context,
                    "status": "error",
                    "error_message": str(e),
                },
            }

    def _generate_direct_answer(self, user_input: str) -> str:
        """
        일반적인 대화를 위한 직접 응답 생성

        Args:
            user_input (str): 사용자 입력

        Returns:
            str: 직접 응답
        """
        # 간단한 인사나 일반 대화 처리
        user_input_lower = user_input.lower()

        if any(
            greeting in user_input_lower
            for greeting in ["안녕", "하이", "헬로", "시작"]
        ):
            return """
안녕하세요! 👋 

저는 클라우드 거버넌스 전문 AI 어시스턴트입니다.

**제가 도와드릴 수 있는 것들:**
• 클라우드 거버넌스 관련 질문 답변
• 정책 및 컴플라이언스 가이드
• 슬라이드 및 프레젠테이션 자료 생성
• 모니터링 및 관리 방안 제시

무엇을 도와드릴까요?
"""

        elif any(
            help_word in user_input_lower
            for help_word in ["도움", "help", "뭐 할 수", "기능"]
        ):
            return """
**클라우드 거버넌스 AI 어시스턴트 기능 안내** 📚

🔍 **질문 응답**
- 클라우드 거버넌스 정책
- 컴플라이언스 요구사항
- 보안 관리 방안
- 모니터링 전략

📊 **슬라이드 생성**
- 프레젠테이션 자료 작성
- 개념 정리 슬라이드
- 비교 분석 자료

예시: "클라우드 보안 정책에 대해 알려주세요" 또는 "데이터 거버넌스 슬라이드 만들어주세요"
"""

        else:
            return """
클라우드 거버넌스와 관련된 구체적인 질문이나 요청을 해주시면 더 도움이 될 것 같습니다.

예를 들어:
• "클라우드 보안 정책이 무엇인가요?"
• "컴플라이언스 관리 방안 슬라이드 만들어주세요"
• "데이터 거버넌스 모범 사례를 알려주세요"

어떤 도움이 필요하신지 말씀해 주세요! 😊
"""

    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime

        return datetime.now().isoformat()

    def get_system_status(self) -> Dict[str, Any]:
        """
        시스템 상태 확인

        Returns:
            Dict[str, Any]: 시스템 상태 정보
        """
        return {
            "orchestrator": "running",
            "agents": {
                "router": "initialized",
                "planner": "initialized",
                "question": "initialized",
                "slide_generator": "initialized",
                "answer": "initialized",
            },
            "tools": {"rag_retriever": "available", "slide_formatter": "available"},
            "mcp_context": self.mcp_context,
        }
