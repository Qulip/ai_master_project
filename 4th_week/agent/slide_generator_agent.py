from core import BaseAgent


class SlideGeneratorAgent(BaseAgent):
    """
    슬라이드 생성 Agent
    """

    def __init__(self):
        super().__init__("slide_agent")

    def _create_prompt(self, inputs: dict) -> str:
        return inputs
