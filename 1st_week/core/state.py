from typing import List, Dict, TypedDict
from langchain_core.messages import BaseMessage


class State(TypedDict):
    """
    상태 정의 클래스

    - query: 검색할 질의
    - context: 검색된 컨텍스트
    - messages: LLM에 전달할 메시지
    - response: LLM 응답
    """

    query: str
    context: dict[str]
    messages: List[BaseMessage]
    response: str
