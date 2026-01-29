# from state import PRReviewState
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# import json
# from dotenv import load_dotenv
# import os

# load_dotenv()
# # Initialize LLM (will use API key from .env)
# llm = ChatOpenAI(
#     model="gpt-4o-mini",  # Cheapest option
#     temperature=0
# )

# def fetch_pr_data(state: PRReviewState) -> PRReviewState:
#     """Node 1: Fetch PR data from GitHub"""
#     print("📥 Fetching PR data...")
    
#     # For now, using mock data - you'll replace with PyGithub later
#     # This lets you test the graph immediately
#     state["issues"] = []
    
#     # Calculate basic metrics
#     total_lines = state["lines_added"] + state["lines_deleted"]
#     if total_lines < 200:
#         state["pr_size_category"] = "small"
#     elif total_lines < 500:
#         state["pr_size_category"] = "medium"
#     else:
#         state["pr_size_category"] = "large"
    
#     print(f"✅ PR #{state['pr_number']} - {total_lines} lines changed")
#     return state


# def analyze_diff(state: PRReviewState) -> PRReviewState:
#     """Node 2: AI analyzes code changes for breaking changes"""
#     print("🔍 Analyzing code diff for breaking changes...")
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are an expert code reviewer. Analyze this git diff for breaking changes.
        
# Breaking changes include:
# - Renamed or removed public functions/methods
# - Changed function signatures (parameters added/removed/reordered)
# - Removed or renamed public classes
# - Database schema changes
# - Changed API endpoints

# Return ONLY valid JSON in this format:
# {
#   "breaking_changes": ["description1", "description2"],
#   "severity": "high" | "medium" | "low"
# }"""),
#         ("user", "Git Diff:\n```\n{diff}\n```")
#     ])
    
#     try:
#         response = llm.invoke(prompt.format(diff=state["pr_diff"][:3000]))  # Limit to 3k chars for demo
#         result = json.loads(response.content)
        
#         state["breaking_changes"] = result.get("breaking_changes", [])
        
#         if state["breaking_changes"]:
#             state["issues"].append(f"⚠️ Found {len(state['breaking_changes'])} potential breaking change(s)")
#             print(f"⚠️ Breaking changes detected: {len(state['breaking_changes'])}")
#         else:
#             print("✅ No breaking changes detected")
            
#     except Exception as e:
#         print(f"❌ Error analyzing diff: {e}")
#         state["breaking_changes"] = []
    
#     return state


# def check_tests(state: PRReviewState) -> PRReviewState:
#     """Node 3: Check if tests are present"""
#     print("🧪 Checking for test coverage...")
    
#     # Check if any test files were modified/added
#     test_patterns = ['test_', '_test.', 'spec.', '.test.', '.spec.']
#     test_files = [
#         f for f in state["files_changed"] 
#         if any(pattern in f.lower() for pattern in test_patterns)
#     ]
    
#     state["test_files"] = test_files
#     state["has_tests"] = len(test_files) > 0
    
#     # Check if logic files changed without tests
#     logic_files = [
#         f for f in state["files_changed"]
#         if f.endswith(('.py', '.js', '.ts', '.java', '.go'))
#         and not any(pattern in f.lower() for pattern in test_patterns)
#     ]
    
#     if logic_files and not state["has_tests"]:
#         state["issues"].append(f"❌ Code changes in {len(logic_files)} file(s) but no tests added")
#         print(f"❌ Missing tests for {len(logic_files)} logic file(s)")
#     elif state["has_tests"]:
#         print(f"✅ Found {len(test_files)} test file(s)")
#     else:
#         print("ℹ️ No logic files changed")
    
#     return state


# def evaluate_commits(state: PRReviewState) -> PRReviewState:
#     """Node 4: Evaluate commit message quality"""
#     print("📝 Evaluating commit messages...")
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """Rate these commit messages on a scale of 0-100.

# Good commits:
# - Clear, descriptive subject line
# - Explain WHY not just WHAT
# - Properly formatted (conventional commits is a plus)

# Bad commits:
# - "fix", "update", "changes" without context
# - Overly long or unclear
# - Multiple unrelated changes

# Return ONLY valid JSON:
# {
#   "score": 0-100,
#   "issues": ["issue1", "issue2"]
# }"""),
#         ("user", "Commits:\n" + "\n".join([f"- {msg}" for msg in state["commit_messages"]]))
#     ])
    
#     try:
#         response = llm.invoke(prompt.format())
#         result = json.loads(response.content)
        
#         state["commit_quality_score"] = result.get("score", 50)
        
#         if state["commit_quality_score"] < 60:
#             state["issues"].append(f"📝 Poor commit messages (score: {state['commit_quality_score']}/100)")
#             print(f"⚠️ Commit quality score: {state['commit_quality_score']}/100")
#         else:
#             print(f"✅ Good commit quality: {state['commit_quality_score']}/100")
            
#     except Exception as e:
#         print(f"❌ Error evaluating commits: {e}")
#         state["commit_quality_score"] = 50
    
#     return state

# def calculate_score(state: PRReviewState) -> PRReviewState:
#     """Node 5: Calculate final merge readiness score"""
#     print("🎯 Calculating merge readiness score...")
    
#     score = 0
    
#     # Test coverage (30 points)
#     if state["has_tests"]:
#         score += 30
    
#     # PR size (20 points)
#     size_scores = {"small": 20, "medium": 15, "large": 5}
#     score += size_scores.get(state["pr_size_category"], 0)
    
#     # Commit quality (20 points)
#     score += int(state["commit_quality_score"] * 0.2)
    
#     # No breaking changes (30 points)
#     if not state["breaking_changes"]:
#         score += 30
#     elif len(state["breaking_changes"]) == 1:
#         score += 15
    
#     state["merge_score"] = score
    
#     # Determine recommendation
#     if score >= 70:
#         state["recommendation"] = "✅ APPROVED - Ready to merge"
#     elif score >= 50:
#         state["recommendation"] = "⚠️ NEEDS REVIEW - Proceed with caution"
#     else:
#         state["recommendation"] = "❌ BLOCKED - Address issues before merging"
    
#     # Generate detailed report
#     report_lines = [
#         f"# PRGuard Review Report",
#         f"",
#         f"**PR #{state['pr_number']}** in `{state['repo_name']}`",
#         f"",
#         f"## Merge Readiness Score: {score}/100",
#         f"{state['recommendation']}",
#         f"",
#         f"## Analysis Details",
#         f"- **PR Size**: {state['pr_size_category'].upper()} ({state['lines_added']}+ / {state['lines_deleted']}- lines)",
#         f"- **Tests**: {'✅ Present' if state['has_tests'] else '❌ Missing'}",
#         f"- **Commit Quality**: {state['commit_quality_score']}/100",
#         f"- **Breaking Changes**: {len(state['breaking_changes'])} found",
#         f""
#     ]
    
#     if state["issues"]:
#         report_lines.append("## Issues Found")
#         for issue in state["issues"]:
#             report_lines.append(f"- {issue}")
#         report_lines.append("")
    
#     if state["breaking_changes"]:
#         report_lines.append("## Breaking Changes Detected")
#         for bc in state["breaking_changes"]:
#             report_lines.append(f"- {bc}")
#         report_lines.append("")
    
#     # ← ADD SUGGESTIONS SECTION
#     if state.get("suggestions"):
#         report_lines.append("## 💡 AI-Powered Improvement Suggestions")
#         report_lines.append("")
#         for i, suggestion in enumerate(state["suggestions"], 1):
#             report_lines.append(f"{i}. {suggestion}")
#             report_lines.append("")
    
#     state["detailed_report"] = "\n".join(report_lines)
    
#     print(f"✅ Final score: {score}/100")
#     print(f"Recommendation: {state['recommendation']}")
    
#     return state


# def generate_suggestions(state: PRReviewState) -> PRReviewState:
#     """Node 6: Generate actionable improvement suggestions"""
#     print("💡 Generating improvement suggestions...")
    
#     state["suggestions"] = []
    
#     # Analyze what needs improvement
#     needs_tests = not state["has_tests"] and any(
#         f.endswith(('.py', '.js', '.ts')) for f in state["files_changed"]
#     )
#     has_breaking_changes = len(state["breaking_changes"]) > 0
#     poor_commits = state["commit_quality_score"] < 60
#     large_pr = state["pr_size_category"] == "large"
    
#     # Generate AI-powered suggestions for each issue
#     if needs_tests:
#         suggestion = generate_test_suggestion(state)
#         if suggestion:
#             state["suggestions"].append(suggestion)
    
#     if has_breaking_changes:
#         suggestion = generate_breaking_change_suggestion(state)
#         if suggestion:
#             state["suggestions"].append(suggestion)
    
#     if poor_commits:
#         suggestion = generate_commit_suggestion(state)
#         if suggestion:
#             state["suggestions"].append(suggestion)
    
#     if large_pr:
#         suggestion = generate_pr_size_suggestion(state)
#         if suggestion:
#             state["suggestions"].append(suggestion)
    
#     # General code quality suggestions
#     code_suggestion = generate_code_quality_suggestion(state)
#     if code_suggestion:
#         state["suggestions"].append(code_suggestion)
    
#     print(f"✅ Generated {len(state['suggestions'])} suggestion(s)")
    
#     return state


# def generate_test_suggestion(state: PRReviewState) -> str:
#     """Generate specific test suggestions based on code changes"""
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are a senior developer reviewing code. Based on this diff, suggest specific tests that should be added.

# Be concrete and actionable:
# - Name specific test cases
# - Identify edge cases to test
# - Suggest test file names

# Return ONLY valid JSON:
# {"suggestion": "Concrete suggestion here"}"""),
#         ("user", "Code changes:\n```\n{diff}\n```\n\nWhat tests should be added?")
#     ])
    
#     try:
#         response = llm.invoke(prompt.format(diff=state["pr_diff"][:2000]))
#         content = clean_json_response(response.content)
#         result = json.loads(content)
#         return f"🧪 **Add Tests**: {result.get('suggestion', 'Add unit tests for changed logic')}"
#     except:
#         return "🧪 **Add Tests**: Consider adding unit tests for the modified functions"


# def generate_breaking_change_suggestion(state: PRReviewState) -> str:
#     """Suggest how to handle breaking changes"""
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are a senior developer. These breaking changes were detected. Suggest how to handle them properly.

# Options:
# - Deprecation strategy
# - Backward compatibility approach  
# - Version bump requirements
# - Migration guide needs

# Return ONLY valid JSON:
# {"suggestion": "Specific recommendation"}"""),
#         ("user", "Breaking changes:\n" + "\n".join(state["breaking_changes"]))
#     ])
    
#     try:
#         response = llm.invoke(prompt.format())
#         content = clean_json_response(response.content)
#         result = json.loads(content)
#         return f"⚠️ **Breaking Changes**: {result.get('suggestion', 'Add deprecation warnings and bump major version')}"
#     except:
#         return "⚠️ **Breaking Changes**: Consider adding deprecation warnings before removing functionality"


# def generate_commit_suggestion(state: PRReviewState) -> str:
#     """Suggest better commit messages"""
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """Analyze these commit messages and suggest improvements using conventional commits format.

# Show examples of better commit messages:
# - feat: Add user authentication
# - fix: Resolve null pointer in payment flow  
# - refactor: Extract validation logic to helper

# Return ONLY valid JSON:
# {"suggestion": "Suggestion with examples"}"""),
#         ("user", "Current commits:\n" + "\n".join(state["commit_messages"]))
#     ])
    
#     try:
#         response = llm.invoke(prompt.format())
#         content = clean_json_response(response.content)
#         result = json.loads(content)
#         return f"📝 **Improve Commits**: {result.get('suggestion', 'Use conventional commit format')}"
#     except:
#         return "📝 **Improve Commits**: Use conventional commit format (feat/fix/refactor/docs)"


# def generate_pr_size_suggestion(state: PRReviewState) -> str:
#     """Suggest how to split large PRs"""
    
#     total_lines = state["lines_added"] + state["lines_deleted"]
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """This PR is large ({lines} lines changed). Suggest how to split it into smaller, reviewable PRs.

# Be specific:
# - Identify logical boundaries
# - Suggest PR sequence
# - Maintain functionality

# Return ONLY valid JSON:
# {"suggestion": "Specific split strategy"}"""),
#         ("user", f"Files changed: {', '.join(state['files_changed'][:10])}\nTotal: {total_lines} lines")
#     ])
    
#     try:
#         response = llm.invoke(prompt.format(lines=total_lines))
#         content = clean_json_response(response.content)
#         result = json.loads(content)
#         return f"📦 **Split PR**: {result.get('suggestion', 'Consider splitting into multiple PRs')}"
#     except:
#         return "📦 **Split PR**: Consider breaking this into smaller, focused PRs (< 400 lines each)"


# def generate_code_quality_suggestion(state: PRReviewState) -> str:
#     """Generate general code quality suggestions"""
    
#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """Review this code diff and provide ONE specific, actionable code quality improvement.

# Focus on:
# - Error handling
# - Code duplication
# - Performance issues
# - Security concerns
# - Best practices

# Return ONLY valid JSON:
# {"suggestion": "One specific improvement"}"""),
#         ("user", "Code diff:\n```\n{diff}\n```")
#     ])
    
#     try:
#         response = llm.invoke(prompt.format(diff=state["pr_diff"][:2000]))
#         content = clean_json_response(response.content)
#         result = json.loads(content)
#         suggestion = result.get('suggestion', '')
#         if suggestion and len(suggestion) > 20:  # Only return substantial suggestions
#             return f"✨ **Code Quality**: {suggestion}"
#     except:
#         pass
    
#     return ""


# def clean_json_response(content: str) -> str:
#     """Clean LLM response to extract JSON"""
#     content = content.strip()
#     if content.startswith("```"):
#         content = content.split("```")[1]
#         if content.startswith("json"):
#             content = content[4:]
#     return content.strip()



from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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
Analyze the PR diff and list risks.
Return a JSON array of strings.

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        state["risks"] = eval(response.content)
    except:
        state["risks"] = ["Unable to parse risks"]
    return state


def test_node(state):
    prompt = f"""
Check if logic changes exist without corresponding tests.
Return a JSON array of issues.

DIFF:
{state['diff']}
"""
    response = llm.invoke(prompt)
    try:
        state["missing_tests"] = eval(response.content)
    except:
        state["missing_tests"] = ["Unable to parse test issues"]
    return state


def score_node(state):
    score = 100

    if state.get("risks"):
        score -= 20

    if state.get("missing_tests"):
        score -= 30

    state["score"] = score
    return state