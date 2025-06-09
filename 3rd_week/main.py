import asyncio
import logging
from services.a2a_orchestrator import A2AOrchestrator
from conf.cloud_config import validate_cloud_setup

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """A2A 통신 기반 메인 실행 함수"""

    print("=== LangChain + Google Cloud A2A 통신 시스템 ===")
    print("Azure OpenAI와 Google Cloud Pub/Sub을 활용한 Agent-to-Agent 통신")

    # Google Cloud 설정 검증
    print("\n1. Google Cloud 설정 검증 중...")
    if not validate_cloud_setup():
        print("❌ Google Cloud 설정이 필요합니다.")
        print("\n다음 단계를 수행하세요:")
        print("1. gcloud auth application-default login")
        print("2. 환경변수 GCP_PROJECT_ID 설정")
        print("3. Pub/Sub API 활성화")
        return

    print("✅ Google Cloud 설정 완료")

    # 오케스트레이터 초기화
    print("\n2. A2A 오케스트레이터 초기화 중...")
    orchestrator = A2AOrchestrator()

    try:
        # 인프라 설정
        print("\n3. Google Cloud Pub/Sub 인프라 설정 중...")
        await orchestrator.setup_infrastructure()
        print("✅ 인프라 설정 완료")

        # 에이전트 시작
        print("\n4. 에이전트들 시작 중...")
        agent_tasks = await orchestrator.start_all_agents()
        print("✅ 모든 에이전트가 시작되었습니다")

        # 프로젝트 설명
        initial_input = """
        온라인 쇼핑몰 시스템 개발 프로젝트
        
        주요 기능:
        - 사용자 등록 및 인증 (OAuth 2.0, JWT)
        - 상품 카탈로그 관리 (검색, 필터링, 카테고리)
        - 장바구니 기능 (임시 저장, 수량 조절)
        - 주문 및 결제 (PG 연동, 다양한 결제 수단)
        - 배송 추적 (실시간 위치, 상태 업데이트)
        - 고객 서비스 (Q&A, 리뷰, 평점)
        
        비기능적 요구사항:
        - 동시 사용자 10,000명 처리
        - 99.9% 가용성
        - 모바일 최적화
        - 보안 강화 (개인정보 보호)
        """

        print("\n5. 프로젝트 처리 시작...")
        print("💡 각 에이전트가 A2A 통신으로 순차적으로 작업을 수행합니다")

        # A2A 워크플로우 실행
        results = await orchestrator.process_project(initial_input)

        # 결과 출력
        print("\n" + "=" * 60)
        print("📋 A2A 통신 기반 프로젝트 분석 결과")
        print("=" * 60)

        if "error" in results:
            print(f"❌ 오류 발생: {results['error']}")
            return

        # 각 에이전트 결과 출력
        agent_names = {
            "requirement-analysis": "1. 요구사항 분석",
            "requirement-validator": "2. 요구사항 검증",
            "service-flow-creator": "3. 서비스 흐름도 설계",
            "api-spec-creator": "4. API 명세서 작성",
            "api-spec-validator": "5. API 명세서 검증",
        }

        for agent_key, agent_title in agent_names.items():
            if agent_key in results:
                result = results[agent_key]
                print(f"\n{agent_title}")
                print("-" * 50)

                if result.get("status") == "completed":
                    print("✅ 완료")

                    # 요구사항 분석 결과
                    if "requirement_spec" in result:
                        print("\n📝 요구사항 명세서:")
                        print(
                            result["requirement_spec"][:500] + "..."
                            if len(result["requirement_spec"]) > 500
                            else result["requirement_spec"]
                        )

                    # 검증 피드백
                    if "validator_feedback" in result:
                        print("\n🔍 검증 피드백:")
                        print(
                            result["validator_feedback"][:500] + "..."
                            if len(result["validator_feedback"]) > 500
                            else result["validator_feedback"]
                        )

                    # 서비스 흐름도
                    if "service_flow" in result:
                        print("\n🔄 서비스 흐름도:")
                        print(
                            result["service_flow"][:500] + "..."
                            if len(result["service_flow"]) > 500
                            else result["service_flow"]
                        )

                    # API 명세서
                    if "api_spec" in result:
                        print("\n🌐 API 명세서:")
                        print(
                            result["api_spec"][:500] + "..."
                            if len(result["api_spec"]) > 500
                            else result["api_spec"]
                        )

                    # API 검증 결과
                    if "api_validation" in result:
                        print("\n✅ API 검증 결과:")
                        print(
                            result["api_validation"][:500] + "..."
                            if len(result["api_validation"]) > 500
                            else result["api_validation"]
                        )

                else:
                    print(f"❌ 실패: {result.get('error', '알 수 없는 오류')}")
            else:
                print(f"\n{agent_title}")
                print("-" * 50)
                print("⏳ 처리되지 않음")

        # 에이전트 상태 확인
        print(f"\n📊 에이전트 상태:")
        status = await orchestrator.get_agent_status()
        for agent_name, agent_status in status.items():
            print(
                f"  {agent_name}: {agent_status['status']} (큐 크기: {agent_status['queue_size']})"
            )

        print(f"\n🎉 A2A 통신 기반 프로젝트 분석이 완료되었습니다!")
        print(f"총 {len(results)}개 에이전트가 처리를 완료했습니다.")

    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        print(f"❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 정리 작업
        print("\n🧹 정리 작업 중...")
        try:
            for task in agent_tasks:
                task.cancel()
        except:
            pass
        print("✅ 정리 완료")


if __name__ == "__main__":
    asyncio.run(main())
