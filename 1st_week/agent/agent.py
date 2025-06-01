from core.state import State
from abc import ABC, abstractmethod
from conf.settings import get_llm


class Agent(ABC):

    def run(self, state: State) -> State:
        prompt = self._create_prompt(state)
        state["messages"].append(prompt)
        response = get_llm().invoke(prompt)
        state["response"] = response
        return state

    @abstractmethod
    def _create_prompt(self, state: State) -> str:
        pass
