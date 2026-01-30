from langgraph.graph import StateGraph, END
from state import PRState
from nodes import pr_metadata_node, summary_node, risk_analysis_node, test_coverage_node, static_quality_node, maintainability_node, scoring_node


def build_graph():
    """Build the PRGuard LangGraph workflow"""
    workflow = StateGraph(PRState)
    # Add nodes
    workflow.add_node("pr_metadata", pr_metadata_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("test_coverage", test_coverage_node)
    workflow.add_node("static_quality", static_quality_node)
    workflow.add_node("scoring", scoring_node)
    
    # Entry point
    workflow.set_entry_point("pr_metadata")

    # Define flow
    workflow.add_edge("pr_metadata", "summary")
    workflow.add_edge("summary", "risk_analysis")
    workflow.add_edge("risk_analysis", "test_coverage")
    workflow.add_edge("test_coverage", "static_quality")
    workflow.add_edge("static_quality", "scoring")
    workflow.add_edge("scoring", END)
    
    return workflow.compile()