from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
import json

# Initialize LLM - Using FREE Groq!
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def summarize_node(state):
    prompt = f"""
Summarize this pull request in 5 bullet points.
Focus on intent and impact.

DIFF:
{state['diff']}

COMMITS:
{state['commits']}
"""
    response = llm.invoke(prompt)
    state["summary"] = response.content
    return state


def risk_node(state):
    prompt = f"""
Analyze the PR diff and list potential risks or breaking changes.
Return ONLY a valid JSON array of strings, nothing else.
Example: ["Risk 1", "Risk 2"]

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        # Clean the response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        state["risks"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse risks: {e}")
        state["risks"] = ["Unable to parse risks"]
    return state


def test_node(state):
    prompt = f"""
Check if logic changes exist without corresponding tests.
Return ONLY a valid JSON array of missing test descriptions.
Example: ["Missing tests for user_api.py", "No tests for payment logic"]

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        # Clean the response
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        state["missing_tests"] = json.loads(content)
    except Exception as e:
        print(f"Warning: Could not parse test issues: {e}")
        state["missing_tests"] = ["Unable to parse test issues"]
    return state


def score_node(state):
    score = 100

    if state.get("risks"):
        score -= 20 * len(state["risks"])

    if state.get("missing_tests"):
        score -= 30

    # Make sure score doesn't go below 0
    state["score"] = max(0, score)
    return state