from typing import Dict, Any
from core import BaseAgent
from mcp_client import get_mcp_client


class QuestionAgent(BaseAgent):
    """
    Question Agent
    클라우드 거버넌스 질문 응답 전담 에이전트
    MCP 프로토콜을 통해 RAG 검색 도구를 사용하여 정보 검색 후 답변 생성
    """

    def __init__(self):
        super().__init__("QuestionAgent")
        self.mcp_client = get_mcp_client()
        self.mcp_context = {"role": "questioner", "function": "cloud_governance_qa"}

    def preprocess(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        질문 처리를 위한 전처리

        Args:
            inputs (Dict[str, Any]): Planner Agent 결과

        Returns:
            Dict[str, Any]: 전처리된 입력
        """
        # Planner Agent의 parameters에서 query 추출
        parameters = inputs.get("parameters", {})
        query = parameters.get("query", inputs.get("user_input", ""))

        # MCP 클라이언트를 통한 RAG 검색 실행
        try:
            rag_results = self.mcp_client.search_documents(query=query, top_k=5)
        except Exception as e:
            print(f"MCP 검색 실패: {str(e)}")
            rag_results = {
                "results": [],
                "mcp_context": {
                    "status": "error",
                    "message": f"MCP 검색 실패: {str(e)}",
                },
            }

        # 검색 결과를 입력에 포함
        inputs["rag_results"] = rag_results
        inputs["processed_query"] = query

        return inputs

    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        """
        클라우드 거버넌스 질문 답변을 위한 프롬프트 생성

        Args:
            inputs (Dict[str, Any]): RAG 결과 포함 입력

        Returns:
            str: LLM용 프롬프트
        """
        query = inputs.get("processed_query", "")
        rag_results = inputs.get("rag_results", {})
        search_results = rag_results.get("results", [])

        # 검색 결과를 컨텍스트로 구성
        context = ""
        if search_results:
            context = "**관련 문서 정보:**\n"
            for i, result in enumerate(search_results[:3], 1):  # 상위 3개만 사용
                context += f"{i}. {result['content'][:500]}...\n"
                context += f"   (출처: {result['source']}, 관련도: {result['relevance_score']:.2f})\n\n"
        else:
            context = "**관련 문서를 찾을 수 없어 일반적인 클라우드 거버넌스 지식으로 답변합니다.**\n\n"

        prompt = f"""
당신은 클라우드 거버넌스 전문가입니다.
사용자의 질문에 대해 검색된 문서 정보를 바탕으로 정확하고 유용한 답변을 제공해야 합니다.

**사용자 질문:**
{query}

{context}

**답변 작성 지침:**
1. 검색된 문서 정보를 우선적으로 활용하세요
2. 클라우드 거버넌스의 핵심 원칙에 맞게 답변하세요
3. 구체적이고 실행 가능한 정보를 포함하세요
4. 필요시 단계별 설명을 제공하세요
5. 관련 법규나 컴플라이언스 사항이 있다면 언급하세요

**출력 형식:**
답변 내용을 자연스러운 한국어로 작성하되, 마지막에 다음 정보를 포함하세요:

**요약:**
- 핵심 포인트 1
- 핵심 포인트 2
- 핵심 포인트 3

**참고 사항:**
검색된 문서에서 얻은 정보임을 명시하고, 추가적인 상세 정보가 필요한 경우를 안내하세요.
"""
        return prompt

    def postprocess(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Question Agent 출력 후처리

        Args:
            outputs (Dict[str, Any]): LLM 응답

        Returns:
            Dict[str, Any]: Answer Agent로 전달할 형식
        """
        try:
            content = outputs.content if hasattr(outputs, "content") else str(outputs)

            # 답변을 Answer Agent용 형식으로 구성
            result = {
                "agent_type": "question",
                "answer_content": content,
                "source_type": "rag_based",
                "confidence": "high",
                "mcp_context": {
                    **self.mcp_context,
                    "status": "success",
                    "processing_completed": True,
                    "rag_sources_used": True,
                    "mcp_enabled": True,
                },
            }

            return result

        except Exception as e:
            return {
                "agent_type": "question",
                "answer_content": f"질문 처리 중 오류가 발생했습니다: {str(e)}",
                "source_type": "error",
                "confidence": "low",
                "mcp_context": {
                    **self.mcp_context,
                    "status": "error",
                    "message": str(e),
                },
            }
