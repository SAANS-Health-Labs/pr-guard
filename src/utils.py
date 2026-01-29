def format_pr_comment(result, threshold):
    status = "❌ FAILED" if result["score"] < threshold else "✅ PASSED"

    return f"""
## 🛡️ PR Guard Report

### {status}
**Score:** {result["score"]} / 100  
**Threshold:** {threshold}

---

### 🔍 Summary
{result["summary"]}

---

### ⚠️ Risks
{result.get("risks", "None")}

---

### 🧪 Missing Tests
{result.get("missing_tests", "None")}

---

_This comment was generated automatically by PR Guard_
"""
