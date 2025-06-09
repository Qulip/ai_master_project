import asyncio
from conf.settings import get_llm
from agents.requirement_agent import RequirementAnalysisAgent
from agents.requirement_validator import RequirementValidatorAgent
from agents.flow_creator import ServiceFlowCreatorAgent
from agents.api_creator import APISpecCreatorAgent
from agents.api_validator import APISpecValidatorAgent


async def main():
    llm = get_llm()

    # Agent 인스턴스 생성
    req_agent = RequirementAnalysisAgent(llm)
    req_validator = RequirementValidatorAgent(llm)
    flow_creator = ServiceFlowCreatorAgent(llm)
    api_creator = APISpecCreatorAgent(llm)
    api_validator = APISpecValidatorAgent(llm)

    # 초기 프로젝트 설명
    initial_input = {
        "input": """
        온라인 쇼핑몰 시스템 개발 프로젝트
        - 사용자 등록 및 인증
        - 상품 검색 및 조회
        - 장바구니 기능
        - 주문 및 결제
        - 배송 추적
        """
    }

    try:
        # Agent 순차 실행
        print("1. 요구사항 분석 중...")
        req_result = await req_agent.process(initial_input)

        print("2. 요구사항 검증 중...")
        val_result = await req_validator.process(
            {"input": req_result["requirement_spec"]}
        )

        print("3. 서비스 흐름도 작성 중...")
        flow_result = await flow_creator.process(
            {"input": val_result["requirement_spec"]}
        )

        print("4. API 명세서 작성 중...")
        api_result = await api_creator.process(
            {
                "input": f"""
            요구사항 명세서:
            {flow_result['requirement_spec']}
            
            서비스 흐름도:
            {flow_result['service_flow']}
            """
            }
        )

        print("5. API 명세서 검증 중...")
        final_result = await api_validator.process({"input": api_result["api_spec"]})

        # 결과 출력
        print("\n=== 최종 결과 ===")
        print("\n1. 요구사항 명세서:")
        print(req_result["requirement_spec"])

        print("\n2. 요구사항 검증 결과:")
        print(val_result["validator_feedback"])

        print("\n3. 서비스 흐름도:")
        print(flow_result["service_flow"])

        print("\n4. API 명세서:")
        print(api_result["api_spec"])

        print("\n5. API 검증 결과:")
        print(final_result["api_validation"])

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
