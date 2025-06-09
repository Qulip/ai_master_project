import asyncio
import logging
from typing import Dict, Any, List
from google.cloud import pubsub_v1
from google.api_core.exceptions import AlreadyExists

from agents.a2a_communication import A2ACommunicationManager
from agents.requirement_agent import RequirementAnalysisAgent
from agents.requirement_validator import RequirementValidatorAgent
from agents.flow_creator import ServiceFlowCreatorAgent
from agents.api_creator import APISpecCreatorAgent
from agents.api_validator import APISpecValidatorAgent
from conf.settings import get_llm
from conf.cloud_config import cloud_config, validate_cloud_setup

logger = logging.getLogger(__name__)


class A2AOrchestrator:
    """A2A 통신 기반 에이전트 오케스트레이터"""

    def __init__(self, project_id: str = None):
        self.project_id = project_id or cloud_config.project_id
        self.llm = get_llm()
        self.comm_manager = A2ACommunicationManager(
            project_id=self.project_id, topic_prefix=cloud_config.topic_prefix
        )

        # 에이전트 초기화
        self.agents = {}
        self._initialize_agents()

        # 결과 저장소
        self.results_store = {}

    def _initialize_agents(self):
        """모든 에이전트 초기화"""
        self.agents = {
            "requirement-analysis": RequirementAnalysisAgent(
                self.llm, self.comm_manager
            ),
            "requirement-validator": RequirementValidatorAgent(
                self.llm, self.comm_manager
            ),
            "service-flow-creator": ServiceFlowCreatorAgent(
                self.llm, self.comm_manager
            ),
            "api-spec-creator": APISpecCreatorAgent(self.llm, self.comm_manager),
            "api-spec-validator": APISpecValidatorAgent(self.llm, self.comm_manager),
        }

        # 결과 수집 핸들러 등록
        self.comm_manager.register_message_handler(
            "collect_result", self._collect_result
        )

    async def _collect_result(self, message_data: Dict[str, Any]):
        """에이전트 결과 수집"""
        agent_name = message_data.get("agent")
        if agent_name:
            self.results_store[agent_name] = message_data
            logger.info(f"결과 수집됨: {agent_name}")

    async def setup_infrastructure(self):
        """Google Cloud Pub/Sub 인프라 설정"""
        publisher = pubsub_v1.PublisherClient()
        subscriber = pubsub_v1.SubscriberClient()

        # 각 에이전트별 토픽과 구독 생성
        for agent_name in self.agents.keys():
            try:
                # 토픽 생성
                topic_path = self.comm_manager.get_topic_path(agent_name)
                try:
                    publisher.create_topic(request={"name": topic_path})
                    logger.info(f"토픽 생성됨: {topic_path}")
                except AlreadyExists:
                    logger.info(f"토픽 이미 존재: {topic_path}")

                # 구독 생성
                subscription_path = self.comm_manager.get_subscription_path(agent_name)
                try:
                    subscriber.create_subscription(
                        request={
                            "name": subscription_path,
                            "topic": topic_path,
                            "ack_deadline_seconds": 600,
                        }
                    )
                    logger.info(f"구독 생성됨: {subscription_path}")
                except AlreadyExists:
                    logger.info(f"구독 이미 존재: {subscription_path}")

            except Exception as e:
                logger.error(f"인프라 설정 오류 ({agent_name}): {e}")

    async def start_all_agents(self):
        """모든 에이전트의 메시지 처리 시작"""
        tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(agent.start_processing())
            tasks.append(task)

        logger.info("모든 에이전트가 메시지 수신을 시작했습니다.")
        return tasks

    async def process_project(self, project_description: str) -> Dict[str, Any]:
        """프로젝트 전체 처리 워크플로우"""
        try:
            # 1. 요구사항 분석 시작
            req_agent = self.agents["requirement-analysis"]
            result = await req_agent.analyze_requirements(project_description)

            if result.get("status") == "failed":
                return {"error": "요구사항 분석 실패", "details": result}

            # 결과 수집을 위해 잠시 대기
            await asyncio.sleep(5)

            # A2A 체인 시작 (자동 전송 모드)
            await req_agent.send_to_agent(
                "requirement-validator",
                {
                    "input": result["requirement_spec"],
                    "message_id": "workflow-start",
                    "auto_forward": True,
                },
            )

            # 모든 에이전트가 처리 완료될 때까지 대기
            max_wait_time = 300  # 5분
            wait_time = 0

            while wait_time < max_wait_time:
                if len(self.results_store) >= 5:  # 모든 에이전트 완료
                    break
                await asyncio.sleep(5)
                wait_time += 5

            return self.results_store

        except Exception as e:
            logger.error(f"프로젝트 처리 오류: {e}")
            return {"error": str(e)}

    async def get_agent_status(self) -> Dict[str, str]:
        """모든 에이전트의 상태 확인"""
        status = {}
        for agent_name, agent in self.agents.items():
            status[agent_name] = {
                "queue_size": agent.processing_queue.qsize(),
                "status": "running" if not agent.processing_queue.empty() else "idle",
            }
        return status

    def cleanup_results(self):
        """결과 저장소 초기화"""
        self.results_store.clear()


async def main():
    """메인 실행 함수"""
    # Google Cloud 설정 검증
    if not validate_cloud_setup():
        print("Google Cloud 설정을 완료한 후 다시 시도해주세요.")
        return

    orchestrator = A2AOrchestrator()

    try:
        # 인프라 설정
        print("Google Cloud Pub/Sub 인프라 설정 중...")
        await orchestrator.setup_infrastructure()

        # 에이전트 시작
        print("에이전트들을 시작하는 중...")
        agent_tasks = await orchestrator.start_all_agents()

        # 프로젝트 처리
        project_description = """
        온라인 쇼핑몰 시스템 개발 프로젝트
        - 사용자 등록 및 인증
        - 상품 검색 및 조회
        - 장바구니 기능
        - 주문 및 결제
        - 배송 추적
        """

        print("프로젝트 처리 시작...")
        results = await orchestrator.process_project(project_description)

        # 결과 출력
        print("\n=== A2A 통신 기반 처리 결과 ===")
        for agent_name, result in results.items():
            print(f"\n{agent_name}: {result.get('status', 'unknown')}")
            if result.get("error"):
                print(f"오류: {result['error']}")

    except KeyboardInterrupt:
        print("\n프로세스가 중단되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        # 정리 작업
        for task in agent_tasks:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
