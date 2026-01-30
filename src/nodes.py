from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
import json
from utils import _clean_json

# Initialize LLM - Using FREE Groq!
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


#PR title hygiene check
def pr_metadata_node(state):
    prompt = f"""
Evaluate the pull request title for hygiene and clarity.

Check for:
- Clear intent
- Action-oriented wording
- No vague titles like "fix", "update", "changes"

Return ONLY valid JSON:
{{
  "is_valid": true | false,
  "issues": []
}}

PR TITLE:
{state.get("pr_title", "")}
"""
    response = llm.invoke(prompt)
    try:
        content = _clean_json(response.content)
        state["pr_hygiene"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse PR title hygiene: {e}")
        state["pr_hygiene"] = {"is_valid": True, "issues": []}
    return state   


# Summarization node
def summary_node(state):
    prompt = f"""
Summarize this pull request in 4 bullet points.
Focus on intent and impact.

DIFF:
{state['diff']}

COMMITS:
{state['commits']}
"""
    response = llm.invoke(prompt)
    state["summary"] = response.content
    return state


# Risk analysis node
def risk_analysis_node(state):
    prompt = f"""
You are a senior reviewer analyzing a pull request diff.

Classify ONLY REAL risks into severity levels:
- HIGH: security issues, secrets exposure, breaking runtime changes, permission escalation
- MEDIUM: dependency upgrades, CI instability, backward compatibility concerns
- LOW: non-breaking refactors, config changes with minimal impact

DO NOT report trivial or informational changes as risks.
If no risks exist for a severity, return an empty array for it.

Return ONLY valid JSON in this exact format:
{{
  "high": [],
  "medium": [],
  "low": []
}}

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        content = _clean_json(response.content)
        state["risks"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse risks: {e}")
        state["risks"] = {"high": [], "medium": [], "low": []}
    return state


def test_coverage_node(state):
    prompt = f"""
You are reviewing a pull request to determine whether NEW OR MODIFIED LOGIC
requires corresponding test updates.

Only flag missing tests if ALL of the following are true:
1. The diff introduces or modifies executable logic (functions, conditionals, APIs).
2. The change affects runtime behavior.
3. No related test changes are present.

DO NOT flag missing tests for:
- Configuration files (YAML, JSON, ENV)
- CI/CD workflows
- Dependency version changes
- Refactors without behavior change
- Comments or formatting changes

If no test gaps exist, return an empty array: [].

Return ONLY a valid JSON array of strings describing missing tests.

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)

    try:
        content = _clean_json(response.content)
        state["missing_tests"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse test coverage issues: {e}")
        state["missing_tests"] = []

    return state


def static_quality_node(state):
    prompt = f"""
Review the diff and identify potential lint, static analysis, or code quality issues.
Focus on:
- Unused variables
- Dead code
- Complexity
- Formatting that violates common conventions

Ignore stylistic preferences unless they clearly reduce readability.

Return ONLY a valid JSON array of strings.
If none, return [].

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        content = _clean_json(response.content)
        state["lint_issues"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse lint issues: {e}")
        state["lint_issues"] = []
    return state



def maintainability_node(state):
    prompt = f"""
Analyze the code changes for adherence to common coding conventions:
- Naming consistency
- File organization
- Function responsibility
- Readability

Do NOT report personal style preferences.

Return ONLY a valid JSON array of findings.
If none, return [].

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        content = _clean_json(response.content)
        state["convention_issues"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse convention issues: {e}")
        state["convention_issues"] = []
    return state

def scoring_node(state):
    score = 100

    risks = state.get("risks", {})
    score -= 40 * len(risks.get("high", []))
    score -= 20 * len(risks.get("medium", []))
    score -= 5 * len(risks.get("low", []))

    if state.get("missing_tests"):
        score -= 20

    score -= min(10, len(state.get("lint_issues", [])) * 2)
    score -= min(10, len(state.get("convention_issues", [])) * 2)

    if not state.get("pr_hygiene", {}).get("is_valid", True):
        score -= 5

    state["score"] = max(0, score)
    return state
