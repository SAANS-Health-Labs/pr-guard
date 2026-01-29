from typing import TypedDict, Annotated, List
import operator

class PRReviewState(TypedDict):
    """State that flows through the LangGraph workflow"""
    
    # Input data
    pr_number: int
    repo_name: str
    pr_diff: str
    commit_messages: List[str]
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    
    # Analysis results
    has_tests: bool
    test_files: List[str]
    breaking_changes: List[str]
    commit_quality_score: int
    pr_size_category: str  # "small", "medium", "large"
    
    # Issues found (accumulates with operator.add)
    issues: Annotated[List[str], operator.add]
    
    # Final output
    merge_score: int
    recommendation: str
    detailed_report: str