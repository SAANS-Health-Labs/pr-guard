# from langgraph.graph import StateGraph, END
# from state import PRReviewState
# from nodes import (
#     fetch_pr_data,
#     analyze_diff,
#     check_tests,
#     evaluate_commits,
#     generate_suggestions,  # ← ADD THIS
#     calculate_score
# )


# def create_prguard_workflow():
#     """Build and compile the PRGuard LangGraph workflow"""
    
#     workflow = StateGraph(PRReviewState)
    
#     # Add all nodes
#     workflow.add_node("fetch", fetch_pr_data)
#     workflow.add_node("analyze", analyze_diff)
#     workflow.add_node("tests", check_tests)
#     workflow.add_node("commits", evaluate_commits)
#     workflow.add_node("suggestions", generate_suggestions) 
#     workflow.add_node("score", calculate_score)


    
#     # Define the flow
#     workflow.set_entry_point("fetch")
#     workflow.add_edge("fetch", "analyze")
#     workflow.add_edge("analyze", "tests")
#     workflow.add_edge("tests", "commits")
#     workflow.add_edge("commits", "suggestions") 
#     workflow.add_edge("suggestions", "score")     
#     workflow.add_edge("score", END)
    
#     app = workflow.compile()
    
#     return app


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