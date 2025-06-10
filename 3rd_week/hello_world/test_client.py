import logging  # 로깅 기능을 위한 모듈
from typing import Any  # 타입 힌팅을 위한 Any 타입
from uuid import uuid4  # 고유 식별자 생성을 위한 UUID 모듈

import httpx  # HTTP 클라이언트 라이브러리 (비동기 요청 지원)

from a2a.client import A2ACardResolver, A2AClient  # A2A 클라이언트 관련 클래스들
from a2a.types import (  # A2A 통신에 필요한 타입들
    AgentCard,  # 에이전트 카드 정보
    MessageSendParams,  # 메시지 전송 파라미터
    SendMessageRequest,  # 일반 메시지 요청 타입
    SendStreamingMessageRequest,  # 스트리밍 메시지 요청 타입
)


async def main() -> None:  # 비동기 메인 함수 정의
    PUBLIC_AGENT_CARD_PATH = "/.well-known/agent.json"  # 공개 에이전트 카드 경로
    EXTENDED_AGENT_CARD_PATH = (
        "/agent/authenticatedExtendedCard"  # 확장 에이전트 카드 경로
    )

    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)  # 로깅 레벨을 INFO로 설정
    logger = logging.getLogger(__name__)  # 현재 모듈의 로거 인스턴스 생성

    base_url = "http://localhost:9999"  # A2A 서버의 기본 URL

    async with httpx.AsyncClient() as httpx_client:  # HTTP 클라이언트 생성 (비동기 컨텍스트 매니저)
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(  # A2A 카드 해석기 초기화
            httpx_client=httpx_client,  # HTTP 클라이언트 전달
            base_url=base_url,  # 기본 URL 설정
            # agent_card_path uses default, extended_agent_card_path also uses default
        )

        final_agent_card_to_use: AgentCard | None = (
            None  # 최종 사용할 에이전트 카드 변수
        )

        try:
            logger.info(  # 공개 카드 요청 시도 로그
                f"Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}"
            )
            _public_card = (  # 공개 에이전트 카드 가져오기
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info("Successfully fetched public agent card:")  # 성공 로그
            logger.info(  # 가져온 카드 정보를 JSON 형태로 로그 출력
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card  # 공개 카드를 최종 사용 카드로 설정
            logger.info(
                "\nUsing PUBLIC agent card for client initialization (default)."
            )

            if (
                _public_card.supportsAuthenticatedExtendedCard
            ):  # 확장 카드 지원 여부 확인
                try:
                    logger.info(  # 확장 카드 요청 시도 로그
                        f"\nPublic card supports authenticated extended card. Attempting to fetch from: {base_url}{EXTENDED_AGENT_CARD_PATH}"
                    )
                    auth_headers_dict = {  # 인증 헤더 설정
                        "Authorization": "Bearer dummy-token-for-extended-card"
                    }
                    _extended_card = (
                        await resolver.get_agent_card(  # 확장 카드 가져오기
                            relative_card_path=EXTENDED_AGENT_CARD_PATH,
                            http_kwargs={"headers": auth_headers_dict},
                        )
                    )
                    logger.info(  # 확장 카드 획득 성공 로그
                        "Successfully fetched authenticated extended agent card:"
                    )
                    logger.info(  # 확장 카드 정보 JSON 출력
                        _extended_card.model_dump_json(indent=2, exclude_none=True)
                    )
                    final_agent_card_to_use = (  # 확장 카드를 최종 사용 카드로 업데이트
                        _extended_card  # Update to use the extended card
                    )
                    logger.info(
                        "\nUsing AUTHENTICATED EXTENDED agent card for client initialization."
                    )
                except Exception as e_extended:  # 확장 카드 가져오기 실패 시 처리
                    logger.warning(
                        f"Failed to fetch extended agent card: {e_extended}. Will proceed with public card.",
                        exc_info=True,
                    )
            elif (  # 확장 카드를 지원하지 않는 경우
                _public_card
            ):  # supportsAuthenticatedExtendedCard is False or None
                logger.info(
                    "\nPublic card does not indicate support for an extended card. Using public card."
                )

        except Exception as e:  # 공개 카드 가져오기 실패 시 처리
            logger.error(
                f"Critical error fetching public agent card: {e}", exc_info=True
            )
            raise RuntimeError(  # 치명적 오류로 프로그램 종료
                "Failed to fetch the public agent card. Cannot continue."
            ) from e

        client = A2AClient(  # A2A 클라이언트 초기화
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info("A2AClient initialized.")  # 클라이언트 초기화 완료 로그

        send_message_payload: dict[str, Any] = {  # 메시지 전송 페이로드 구성
            "message": {
                "role": "user",  # 사용자 역할
                "parts": [  # 메시지 구성 요소들
                    {
                        "kind": "text",
                        "text": "how much is 10 USD in INR?",
                    }  # 텍스트 메시지
                ],
                "messageId": uuid4().hex,  # 고유 메시지 ID 생성
            },
        }
        request = SendMessageRequest(  # 메시지 요청 객체 생성
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)  # 메시지 전송 및 응답 받기
        print(response.model_dump(mode="json", exclude_none=True))  # 응답 출력

        streaming_request = SendStreamingMessageRequest(  # 스트리밍 요청 객체 생성
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        stream_response = client.send_message_streaming(
            streaming_request
        )  # 스트리밍 응답 받기

        async for chunk in stream_response:  # 스트리밍 데이터를 청크 단위로 받기
            print(chunk.model_dump(mode="json", exclude_none=True))  # 각 청크 출력


if __name__ == "__main__":  # 스크립트가 직접 실행될 때만 실행
    import asyncio  # 비동기 이벤트 루프를 위한 모듈

    asyncio.run(main())  # 메인 함수를 비동기로 실행
