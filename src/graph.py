from langgraph.graph import StateGraph, END
from state import PRState
from nodes import summarize_node, risk_node, test_node, score_node


def build_graph():
    """Build the PRGuard LangGraph workflow"""
    workflow = StateGraph(PRState)
    # Add nodes
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("test", test_node)
    workflow.add_node("score", score_node)
    
    # Define flow
    workflow.set_entry_point("summarize")
    workflow.add_edge("summarize", "risk")
    workflow.add_edge("risk", "test")
    workflow.add_edge("test", "score")
    workflow.add_edge("score", END)
    
    return workflow.compile()