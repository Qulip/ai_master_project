import json
import asyncio
from typing import Dict, Any, Optional, Callable
from google.cloud import pubsub_v1
from google.cloud import functions_v1
from google.auth import default
import logging
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class A2ACommunicationManager:
    """Google Cloud Pub/Sub을 통한 Agent-to-Agent 통신 매니저"""

    def __init__(self, project_id: str, topic_prefix: str = "agent-communication"):
        self.project_id = project_id
        self.topic_prefix = topic_prefix
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.message_handlers: Dict[str, Callable] = {}

    def get_topic_path(self, agent_name: str) -> str:
        """에이전트별 토픽 경로 생성"""
        topic_name = f"{self.topic_prefix}-{agent_name}"
        return self.publisher.topic_path(self.project_id, topic_name)

    def get_subscription_path(self, agent_name: str) -> str:
        """에이전트별 구독 경로 생성"""
        subscription_name = f"{self.topic_prefix}-{agent_name}-sub"
        return self.subscriber.subscription_path(self.project_id, subscription_name)

    async def publish_message(
        self, target_agent: str, message_data: Dict[str, Any]
    ) -> None:
        """메시지를 특정 에이전트에게 발송"""
        topic_path = self.get_topic_path(target_agent)
        message_json = json.dumps(message_data).encode("utf-8")

        try:
            future = self.publisher.publish(topic_path, message_json)
            message_id = future.result()
            logger.info(f"Message published to {target_agent}: {message_id}")
        except Exception as e:
            logger.error(f"Failed to publish message to {target_agent}: {e}")
            raise

    def register_message_handler(self, handler_name: str, handler_func: Callable):
        """메시지 핸들러 등록"""
        self.message_handlers[handler_name] = handler_func

    async def start_listening(self, agent_name: str):
        """특정 에이전트의 메시지 수신 시작"""
        subscription_path = self.get_subscription_path(agent_name)

        def callback(message):
            try:
                message_data = json.loads(message.data.decode("utf-8"))
                handler_name = message_data.get("handler", "default")

                if handler_name in self.message_handlers:
                    asyncio.create_task(
                        self.message_handlers[handler_name](message_data)
                    )

                message.ack()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                message.nack()

        flow_control = pubsub_v1.types.FlowControl(max_messages=100)
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path, callback=callback, flow_control=flow_control
        )

        logger.info(f"Listening for messages on {subscription_path}")

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()


class A2AAgent:
    """A2A 통신을 지원하는 기본 에이전트 클래스"""

    def __init__(
        self, agent_name: str, llm, communication_manager: A2ACommunicationManager
    ):
        self.agent_name = agent_name
        self.llm = llm
        self.comm_manager = communication_manager
        self.processing_queue = asyncio.Queue()

        # 메시지 핸들러 등록
        self.comm_manager.register_message_handler(
            f"{agent_name}_process", self._handle_incoming_message
        )

    async def _handle_incoming_message(self, message_data: Dict[str, Any]):
        """들어오는 메시지 처리"""
        await self.processing_queue.put(message_data)

    async def process_message(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """메시지 처리 - 서브클래스에서 구현"""
        raise NotImplementedError("Subclasses must implement process_message")

    async def send_to_agent(self, target_agent: str, message_data: Dict[str, Any]):
        """다른 에이전트에게 메시지 전송"""
        message_data["handler"] = f"{target_agent}_process"
        message_data["sender"] = self.agent_name
        await self.comm_manager.publish_message(target_agent, message_data)

    async def start_processing(self):
        """메시지 처리 루프 시작"""
        while True:
            try:
                message_data = await self.processing_queue.get()
                result = await self.process_message(message_data)

                # 응답이 필요한 경우 sender에게 결과 전송
                if "reply_to" in message_data and result:
                    await self.send_to_agent(
                        message_data["reply_to"],
                        {
                            "type": "response",
                            "original_message_id": message_data.get("message_id"),
                            "result": result,
                        },
                    )

                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing message in {self.agent_name}: {e}")

    async def process_with_llm(self, system_prompt: str, user_input: str) -> str:
        """LLM을 사용한 메시지 처리"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input),
        ]

        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            raise
