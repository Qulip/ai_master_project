from typing import Dict, Any, List
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool


class BaseAgentTool(BaseTool):
    def __init__(self, name: str, description: str, func):
        super().__init__()
        self.name = name
        self.description = description
        self.func = func

    def _run(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class BaseAgent:
    def __init__(self, llm, tools: List[BaseTool], system_message: str):
        self.llm = llm
        self.tools = tools

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.agent_executor.ainvoke(input_data)
        return result
