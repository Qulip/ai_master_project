from agent.agent import Agent
from core.state import State


class PdfAgent(Agent):

    def _create_prompt(self, state: State) -> str:
        return f"""
        너는 데이터 분석가로 아래 PDF를 청킹 후 임베딩 결과를 보고 각각의 임베딩의 결과가 어떤 차이점이 있는지 정리해줘.
        아래 첨부한 청킹 결과를 보고 각각의 임베딩의 결과를 정리해주고, 두 청킹 결과에 어떤 차이점이 있는지 정리해줘.

        사용자 질의: {state['query']}
        similarity_search_results: {state['context']['similarity_search_results']}
        similarity_search_with_score_results: {state['context']['similarity_search_with_score_results']}

        """
