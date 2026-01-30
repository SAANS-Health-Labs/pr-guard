from typing import TypedDict, List, Dict


class RiskBreakdown(TypedDict):
    high: List[str]
    medium: List[str]
    low: List[str]


class PRHygiene(TypedDict):
    is_valid: bool
    issues: List[str]


class PRState(TypedDict, total=False):
    # ── Inputs (required to start graph)
    diff: str
    commits: str
    pr_title: str

    # ── Metadata & summary
    summary: str
    pr_hygiene: PRHygiene

    # ── Analysis results
    risks: RiskBreakdown
    missing_tests: List[str]
    lint_issues: List[str]

    # ── Final evaluation
    score: int
