from typing import Dict, Any
from core import BaseAgent
from mcp_client import get_mcp_client


class SlideGeneratorAgent(BaseAgent):
    """
    SlideGenerator Agent
    클라우드 거버넌스 슬라이드 생성 전담 에이전트
    MCP 프로토콜을 통해 RAG 검색 및 슬라이드 포맷팅 도구를 사용하여 시각화 가능한 슬라이드 생성
    """

    def __init__(self):
        super().__init__("SlideGeneratorAgent")
        self.mcp_client = get_mcp_client()
        self.mcp_context = {
            "role": "slide_generator",
            "function": "presentation_creation",
        }

    def preprocess(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        슬라이드 생성을 위한 전처리

        Args:
            inputs (Dict[str, Any]): Planner Agent 결과

        Returns:
            Dict[str, Any]: 전처리된 입력
        """
        # Planner Agent의 parameters에서 정보 추출
        parameters = inputs.get("parameters", {})
        query = parameters.get("query", inputs.get("user_input", ""))
        slide_type = parameters.get("slide_type", "basic")

        # MCP 클라이언트를 통한 RAG 검색 실행 (슬라이드용으로 더 많은 결과 수집)
        try:
            rag_results = self.mcp_client.search_documents(
                query=query, top_k=8  # 슬라이드 생성용으로 더 많은 자료 수집
            )
        except Exception as e:
            print(f"MCP 검색 실패: {str(e)}")
            rag_results = {
                "results": [],
                "mcp_context": {
                    "status": "error",
                    "message": f"MCP 검색 실패: {str(e)}",
                },
            }

        # 전처리된 정보 저장
        inputs["rag_results"] = rag_results
        inputs["processed_query"] = query
        inputs["slide_type"] = slide_type

        # slide_type 저장 (postprocess에서 사용)
        self._current_slide_type = slide_type

        return inputs

    def _create_prompt(self, inputs: Dict[str, Any]) -> str:
        """
        슬라이드 내용 생성을 위한 프롬프트 생성

        Args:
            inputs (Dict[str, Any]): RAG 결과 포함 입력

        Returns:
            str: LLM용 프롬프트
        """
        query = inputs.get("processed_query", "")
        slide_type = inputs.get("slide_type", "basic")
        rag_results = inputs.get("rag_results", {})
        search_results = rag_results.get("results", [])

        # 검색 결과를 슬라이드 컨텍스트로 구성
        context = ""
        if search_results:
            context = "**참고 문서 내용:**\n"
            for i, result in enumerate(search_results[:5], 1):  # 상위 5개 사용
                context += f"{i}. {result['content'][:400]}...\n"
                context += f"   (출처: {result['source']})\n\n"
        else:
            context = "**일반적인 클라우드 거버넌스 지식을 바탕으로 슬라이드를 구성합니다.**\n\n"

        prompt = f"""
당신은 클라우드 거버넌스 전문가이며 효과적인 프레젠테이션 슬라이드를 제작해야 합니다.
주어진 주제에 대해 {slide_type} 형식의 슬라이드 내용을 구성하세요.

**슬라이드 주제:**
{query}

**슬라이드 타입:** {slide_type}

{context}

**슬라이드 작성 지침:**
1. 명확하고 이해하기 쉬운 제목 설정
2. 핵심 내용을 bullet point로 정리
3. 각 포인트는 간결하면서도 구체적으로 작성
4. 클라우드 거버넌스의 실무적 관점 반영
5. 청중이 실행할 수 있는 구체적인 가이드라인 포함

**출력 형식:**
다음 정보를 포함한 구조화된 텍스트로 작성하세요:

제목: [슬라이드 제목]

핵심 내용:
- [포인트 1: 구체적이고 실행 가능한 내용]
- [포인트 2: 관련 정책이나 절차]
- [포인트 3: 모니터링 및 관리 방안]
- [포인트 4: 컴플라이언스 고려사항]
- [포인트 5: 최적화 방안]

상세 설명:
[각 포인트에 대한 추가 설명이나 예시]

결론:
[핵심 메시지나 실행 방안 요약]

이 내용을 바탕으로 SlideFormatter Tool이 적절한 형식으로 변환할 예정입니다.
"""
        return prompt

    def postprocess(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        SlideGenerator Agent 출력 후처리 및 MCP를 통한 SlideFormatter Tool 호출

        Args:
            outputs (Dict[str, Any]): LLM 응답

        Returns:
            Dict[str, Any]: Answer Agent로 전달할 형식
        """
        try:
            content = outputs.content if hasattr(outputs, "content") else str(outputs)
            slide_type = getattr(self, "_current_slide_type", "basic")

            # 제목 추출
            title = "클라우드 거버넌스"
            if "제목:" in content:
                title_line = content.split("제목:")[1].split("\n")[0].strip()
                if title_line:
                    title = title_line

            # MCP 클라이언트를 통한 SlideFormatter Tool 호출
            try:
                slide_result = self.mcp_client.format_slide(
                    content=content,
                    title=title,
                    slide_type=slide_type,
                    format_type="json",
                )
            except Exception as e:
                print(f"MCP 슬라이드 포맷팅 실패: {str(e)}")
                slide_result = {
                    "slide": {},
                    "markdown": "",
                    "mcp_context": {
                        "status": "error",
                        "message": f"MCP 슬라이드 포맷팅 실패: {str(e)}",
                    },
                }

            # Answer Agent용 형식으로 구성
            result = {
                "agent_type": "slide_generation",
                "answer_content": content,
                "slide_data": slide_result.get("slide", {}),
                "slide_markdown": slide_result.get("markdown", ""),
                "source_type": "rag_based_slide",
                "confidence": "high",
                "mcp_context": {
                    **self.mcp_context,
                    "status": "success",
                    "slide_generated": True,
                    "slide_type": slide_type,
                    "formatter_status": slide_result.get("mcp_context", {}).get(
                        "status", "unknown"
                    ),
                    "mcp_enabled": True,
                },
            }

            return result

        except Exception as e:
            return {
                "agent_type": "slide_generation",
                "answer_content": f"슬라이드 생성 중 오류가 발생했습니다: {str(e)}",
                "slide_data": {},
                "slide_markdown": "",
                "source_type": "error",
                "confidence": "low",
                "mcp_context": {
                    **self.mcp_context,
                    "status": "error",
                    "message": str(e),
                },
            }
