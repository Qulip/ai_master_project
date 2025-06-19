#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
클라우드 거버넌스 슬라이드 생성 AI 메인 실행 파일

이 시스템은 다음과 같은 구조로 동작합니다:
1. Router Agent: 사용자 의도 분석
2. Planner Agent: 작업 계획 수립
3. Question/SlideGenerator Agent: 실제 작업 수행
4. Answer Agent: 최종 응답 정제

기술 스택:
- LangChain
- MCP (Model Context Protocol)
- RAG (Retrieval-Augmented Generation)
- FAISS (Vector Database)
"""

import sys
import os

# 현재 디렉토리를 Python 패스에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import CloudGovernanceOrchestrator


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 클라우드 거버넌스 슬라이드 생성 AI 시스템")
    print("=" * 60)
    print()

    try:
        # 오케스트레이터 초기화
        print("🔧 시스템 초기화 중...")
        orchestrator = CloudGovernanceOrchestrator()

        # 시스템 상태 확인
        status = orchestrator.get_system_status()
        print("✅ 시스템 초기화 완료")
        print(f"   └ Orchestrator: {status['orchestrator']}")
        print(f"   └ Agents: {len(status['agents'])}개 준비됨")
        print(f"   └ Tools: {len(status['tools'])}개 준비됨")
        print()

        # 대화형 인터페이스
        print("💬 대화형 모드를 시작합니다. ('quit' 또는 'exit'으로 종료)")
        print("📌 예시 질문:")
        print("   • 클라우드 보안 정책에 대해 알려주세요")
        print("   • 데이터 거버넌스 슬라이드 만들어주세요")
        print("   • 컴플라이언스 관리 방안을 설명해주세요")
        print()

        while True:
            try:
                # 사용자 입력 받기
                user_input = input("💡 질문을 입력해주세요: ").strip()

                # 종료 명령어 체크
                if user_input.lower() in ["quit", "exit", "종료", "나가기"]:
                    print("👋 시스템을 종료합니다. 감사합니다!")
                    break

                # 빈 입력 체크
                if not user_input:
                    print("❓ 질문을 입력해주세요.")
                    continue

                print()

                # 요청 처리
                result = orchestrator.process_request(user_input)

                # 결과 출력
                print("\n" + "=" * 60)
                print("📝 응답:")
                print("=" * 60)
                print(result.get("final_answer", "응답을 생성할 수 없습니다."))
                print()

                # MCP Context 정보 (디버그용)
                if "--debug" in sys.argv:
                    print("🔍 MCP Context (Debug):")
                    mcp_context = result.get("mcp_context", {})
                    if "orchestrator" in mcp_context:
                        flow = mcp_context["orchestrator"].get("processing_flow", [])
                        print(f"   └ Processing Flow: {' → '.join(flow)}")
                    print()

            except KeyboardInterrupt:
                print("\n\n👋 시스템을 종료합니다.")
                break
            except Exception as e:
                print(f"\n❌ 오류가 발생했습니다: {str(e)}")
                print("🔄 다시 시도해주세요.\n")

    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {str(e)}")
        print("🔧 환경 설정을 확인해주세요.")
        return 1

    return 0


def test_mode():
    """테스트 모드 실행"""
    print("🧪 테스트 모드 실행")

    orchestrator = CloudGovernanceOrchestrator()

    test_cases = [
        "안녕하세요",
        "클라우드 보안 정책이 무엇인가요?",
        "데이터 거버넌스 슬라이드 만들어주세요",
        "컴플라이언스 관리 방안을 설명해주세요",
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📋 테스트 케이스 {i}: {test_input}")
        print("-" * 40)

        try:
            result = orchestrator.process_request(test_input)
            print("✅ 성공")
            print(f"응답 길이: {len(result.get('final_answer', ''))}")
        except Exception as e:
            print(f"❌ 실패: {str(e)}")

    print("\n🧪 테스트 완료")


if __name__ == "__main__":
    # 명령행 인수 확인
    if "--test" in sys.argv:
        test_mode()
    else:
        exit_code = main()
        sys.exit(exit_code)
