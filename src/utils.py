def format_pr_comment(result, threshold):
    score = result.get("score", 0)
    status = "❌ FAILED" if score < threshold else "✅ PASSED"

    risks = result.get("risks") or {}
    missing_tests = result.get("missing_tests") or []
    lint_issues = result.get("lint_issues") or []
    maintainability_issues = result.get("maintainability_issues") or []
    pr_hygiene = result.get("pr_hygiene") or {"is_valid": True, "issues": []}

    def render_bullets(items):
        if not items:
            return "- None"
        return "\n".join(f"- {str(item)}" for item in items)

    return f"""
## 🛡️ PR Guard Report

### {status}
**Score:** {score} / 100  
**Threshold:** {threshold}

---

### 🧾 PR Metadata
{"✅ Title and commits look good"
 if pr_hygiene.get("is_valid", True)
 else render_bullets(pr_hygiene.get("issues", []))}

---

### 🔍 Summary
{result.get("summary", "No summary available.")}

---

### 🔐 Risk Analysis

**🔴 High Risk**
{render_bullets(risks.get("high", []))}

**🟡 Medium Risk**
{render_bullets(risks.get("medium", []))}

**🟢 Low Risk**
{render_bullets(risks.get("low", []))}

---

### 🧪 Test Coverage
{render_bullets(missing_tests)}

---

### 🧹 Static Quality
{render_bullets(lint_issues)}

---

_🤖 This review was generated automatically by **PR Guard**_
"""



def _clean_json(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return content.strip()