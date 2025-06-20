#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
클라우드 거버넌스 AI 서비스 FastMCP 서버

RAG 검색 및 슬라이드 포맷팅 도구들을 MCP 프로토콜로 제공합니다.
"""

import sys
import os
from typing import Dict, Any
import logging

# 현재 디렉토리를 Python 패스에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from tools import RAGRetrieverTool, SlideFormatterTool

# FastMCP 서버 초기화
mcp = FastMCP(name="cloud-governance-tools")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 도구 인스턴스들
rag_retriever = None
slide_formatter = None


def startup():
    """MCP 서버 시작 시 도구들 초기화"""
    global rag_retriever, slide_formatter
    try:
        logger.info("🔧 MCP 도구 서버 초기화 중...")

        # RAG Retriever 초기화
        rag_retriever = RAGRetrieverTool()
        logger.info("✅ RAG Retriever 도구 초기화 완료")

        # Slide Formatter 초기화
        slide_formatter = SlideFormatterTool()
        logger.info("✅ Slide Formatter 도구 초기화 완료")

        logger.info("🎉 모든 MCP 도구 초기화 완료")

    except Exception as e:
        logger.error(f"❌ MCP 도구 초기화 실패: {str(e)}")
        raise


startup()


@mcp.tool()
def search_documents(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    RAG 기반 문서 검색 도구

    Args:
        query: 검색할 질문이나 키워드
        top_k: 반환할 최대 결과 개수 (기본값: 5)

    Returns:
        검색 결과 및 관련 메타데이터
    """
    try:
        logger.info(f"📄 문서 검색 요청: {query[:50]}...")

        if not rag_retriever:
            return {
                "results": [],
                "mcp_context": {
                    "role": "retriever",
                    "status": "error",
                    "message": "RAG Retriever가 초기화되지 않았습니다.",
                },
            }

        # RAG 검색 실행
        result = rag_retriever.run({"query": query, "top_k": top_k})

        logger.info(f"✅ 문서 검색 완료: {len(result.get('results', []))}개 결과")
        return result

    except Exception as e:
        logger.error(f"❌ 문서 검색 실패: {str(e)}")
        return {
            "results": [],
            "mcp_context": {
                "role": "retriever",
                "status": "error",
                "message": f"문서 검색 중 오류: {str(e)}",
            },
        }


@mcp.tool()
def format_slide(
    content: str,
    title: str = "클라우드 거버넌스",
    slide_type: str = "basic",
    subtitle: str = "",
    format_type: str = "json",
) -> Dict[str, Any]:
    """
    슬라이드 포맷팅 도구

    Args:
        content: 슬라이드로 변환할 텍스트 내용
        title: 슬라이드 제목 (기본값: "클라우드 거버넌스")
        slide_type: 슬라이드 유형 ("basic", "detailed", "comparison")
        subtitle: 슬라이드 부제목 (detailed 타입에서 사용)
        format_type: 출력 형식 ("json", "markdown")

    Returns:
        포맷팅된 슬라이드 데이터
    """
    try:
        logger.info(f"📊 슬라이드 포맷팅 요청: {slide_type} 타입")

        if not slide_formatter:
            return {
                "slide": {},
                "markdown": "",
                "mcp_context": {
                    "role": "formatter",
                    "status": "error",
                    "message": "Slide Formatter가 초기화되지 않았습니다.",
                },
            }

        # 슬라이드 포맷팅 실행
        result = slide_formatter.run(
            {
                "content": content,
                "title": title,
                "slide_type": slide_type,
                "subtitle": subtitle,
                "format": format_type,
            }
        )

        logger.info(f"✅ 슬라이드 포맷팅 완료: {slide_type} 타입")
        return result

    except Exception as e:
        logger.error(f"❌ 슬라이드 포맷팅 실패: {str(e)}")
        return {
            "slide": {},
            "markdown": "",
            "mcp_context": {
                "role": "formatter",
                "status": "error",
                "message": f"슬라이드 포맷팅 중 오류: {str(e)}",
            },
        }


@mcp.tool()
def get_tool_status() -> Dict[str, Any]:
    """
    MCP 도구 서버 상태 확인

    Returns:
        도구 서버의 현재 상태 정보
    """
    try:
        status = {
            "server_name": "cloud-governance-tools",
            "version": "1.0.0",
            "status": "running",
            "tools": {
                "rag_retriever": "available" if rag_retriever else "unavailable",
                "slide_formatter": "available" if slide_formatter else "unavailable",
            },
            "timestamp": get_timestamp(),
        }

        logger.info("📊 도구 상태 조회 완료")
        return status

    except Exception as e:
        logger.error(f"❌ 도구 상태 조회 실패: {str(e)}")
        return {
            "status": "error",
            "message": f"상태 조회 중 오류: {str(e)}",
            "timestamp": get_timestamp(),
        }


def get_timestamp() -> str:
    """현재 타임스탬프 반환"""
    from datetime import datetime

    return datetime.now().isoformat()


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🛠️  클라우드 거버넌스 MCP 도구 서버 시작")
    print("=" * 60)
    print("📄 사용 가능한 도구:")
    print("   • search_documents: RAG 기반 문서 검색")
    print("   • format_slide: 슬라이드 포맷팅")
    print("   • get_tool_status: 도구 상태 확인")
    print("=" * 60)

    # MCP 서버 실행
    uvicorn.run(
        "mcp_server:mcp", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
