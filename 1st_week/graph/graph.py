from langgraph.graph import StateGraph, END
from core.state import State
from agent.pdf_agent import PdfAgent


def create_graph():
    workflow = StateGraph(State)

    pdf_agent = PdfAgent()

    workflow.add_node("agent", pdf_agent.run)

    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    return workflow.compile()
