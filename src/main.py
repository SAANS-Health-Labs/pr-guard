import os
import subprocess
import argparse
from graph import build_graph
from github import Github


def get_pr_diff():
    """Get PR diff from git"""
    subprocess.run(
        ["git", "fetch", "origin", os.environ.get("GITHUB_BASE_REF", "main")],
        check=False
    )

    try:
        diff = subprocess.check_output(
            ["git", "diff", f"origin/{os.environ.get('GITHUB_BASE_REF', 'main')}"],
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return diff
    except subprocess.CalledProcessError:
        return ""


def get_commits(n=5):
    """Get recent commit messages"""
    try:
        return subprocess.check_output(
            ["git", "log", "--oneline", f"-n{n}"],
            text=True,
            encoding='utf-8',
            errors='replace'
        )
    except subprocess.CalledProcessError:
        return ""


def format_pr_comment(result):
    """Format the analysis results as a beautiful GitHub PR comment"""
    
    score = result['score']
    
    # Determine status
    if score >= 80:
        status_emoji = "✅"
        status_text = "APPROVED"
        status_color = "brightgreen"
        recommendation = "**✅ READY TO MERGE** - This PR meets all quality standards!"
    elif score >= 50:
        status_emoji = "⚠️"
        status_text = "NEEDS_REVIEW"
        status_color = "yellow"
        recommendation = "**⚠️ NEEDS ATTENTION** - Address the issues below before merging."
    else:
        status_emoji = "❌"
        status_text = "BLOCKED"
        status_color = "red"
        recommendation = "**🚫 DO NOT MERGE** - Critical issues must be resolved first."
    
    # Build the comment
    comment = f"""
<div align="center">

# 🛡️ PRGuard AI Review

![Score](https://img.shields.io/badge/Score-{score}%25-{status_color}?style=for-the-badge&logo=shield&logoColor=white)
![Status](https://img.shields.io/badge/Status-{status_text}-{status_color}?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/Powered_by-LangGraph-purple?style=for-the-badge)

</div>

---

## 📝 AI Analysis Summary

{result['summary']}

---

## ⚠️ Security & Quality Risks

"""
    
    risks = result.get('risks', [])
    if risks and len(risks) > 0:
        comment += "| # | Risk Description |\n"
        comment += "|---|------------------|\n"
        for i, risk in enumerate(risks, 1):
            comment += f"| 🔴 **{i}** | {risk} |\n"
    else:
        comment += "> ### ✅ No security or quality risks detected!\n"
    
    comment += "\n---\n\n## 🧪 Test Coverage\n\n"
    
    tests = result.get('missing_tests', [])
    if tests and len(tests) > 0:
        comment += "| # | Missing Test |\n"
        comment += "|---|-------------|\n"
        for i, test in enumerate(tests, 1):
            comment += f"| ⚪ **{i}** | {test} |\n"
    else:
        comment += "> ### ✅ All code changes have proper test coverage!\n"
    
    # Scoring breakdown
    risk_deduction = len(risks) * 20 if risks else 0
    test_deduction = 30 if tests else 0
    
    comment += f"""
---

## 📊 Score Breakdown
```
Base Score:           100 points
Risk Deductions:      -{risk_deduction} points  ({len(risks)} risks found)
Test Coverage:        -{test_deduction} points  ({'missing tests' if tests else 'all covered'})
─────────────────────────────────
Final Score:          {score}/100
```

---

<div align="center">

## {status_emoji} Final Recommendation

{recommendation}

---

<sub>🤖 Analyzed by **PRGuard** • Powered by LangGraph + Groq (Llama 3.3 70B)</sub>

<sub>⭐ [Star us on GitHub](https://github.com/SAANS-Health-Labs/pr-guard) • 📖 [Documentation](https://github.com/SAANS-Health-Labs/pr-guard) • 🐛 [Report Issues](https://github.com/SAANS-Health-Labs/pr-guard/issues)</sub>

</div>
"""
    
    return comment


def post_github_comment(comment_body):
    """Post formatted comment to GitHub PR"""
    
    github_token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")
    
    if not all([github_token, repo_name, pr_number]):
        print("\n⚠️  Missing GitHub environment variables")
        print(f"   GITHUB_TOKEN: {'✓' if github_token else '✗'}")
        print(f"   GITHUB_REPOSITORY: {'✓' if repo_name else '✗'}")
        print(f"   PR_NUMBER: {'✓' if pr_number else '✗'}")
        print("\n📋 Comment preview (would be posted to PR):")
        print("="*60)
        print(comment_body)
        return False
    
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_number))
        
        # Post the comment
        pr.create_issue_comment(comment_body)
        
        print(f"\n✅ Comment successfully posted to PR #{pr_number}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error posting comment: {e}")
        print("\n📋 Comment that would be posted:")
        print("="*60)
        print(comment_body)
        return False


def test_mode():
    """Demo mode with vulnerable code example"""
    
    print("🧪 DEMO MODE: Testing PRGuard with Vulnerable Code\n")
    print("="*60)
    print("🚨 Analyzing INSECURE CODE")
    print("="*60 + "\n")
    
    state = {
        "diff": """
diff --git a/src/auth.py b/src/auth.py
new file mode 100644
--- /dev/null
+++ b/src/auth.py
@@ -0,0 +1,25 @@
+import hashlib
+
+# SECURITY RISK: Hardcoded credentials
+ADMIN_PASSWORD = "admin123"
+API_KEY = "sk-1234567890abcdef"
+DATABASE_URL = "mysql://root:password@localhost"
+
+def authenticate_user(username, password):
+    # SQL Injection vulnerability!
+    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
+    return db.execute(query)
+
+def hash_password(password):
+    # Using weak MD5 hashing
+    return hashlib.md5(password.encode()).hexdigest()
+
+def process_payment(amount, card_number):
+    # Logging sensitive data!
+    print(f"Processing card: {card_number}")
+    return amount * 100
+
+def delete_user(user_id):
+    # No authorization check!
+    query = f"DELETE FROM users WHERE id={user_id}"
+    return db.execute(query)
        """,
        "commits": """
abc123 fix stuff
def456 update code
ghi789 changes
        """
    }

    print("⏳ Running AI analysis with LangGraph...\n")
    
    graph = build_graph()
    result = graph.invoke(state)

    # Format as GitHub comment
    comment = format_pr_comment(result)
    
    # Print beautiful preview
    print("\n" + "="*60)
    print("📋 GITHUB PR COMMENT PREVIEW")
    print("="*60 + "\n")
    print(comment)
    print("\n" + "="*60)
    
    # Show console summary
    print("\n📊 CONSOLE SUMMARY:")
    print(f"   Score: {result['score']}/100")
    print(f"   Risks Found: {len(result.get('risks', []))}")
    print(f"   Missing Tests: {len(result.get('missing_tests', []))}")
    
    if result['score'] < 70:
        print("\n   Status: ❌ BLOCKED")
    else:
        print("\n   Status: ✅ APPROVED")
    
    print("\n💡 TIP: In GitHub Actions, this comment would be posted to the PR automatically")


def main():
    """Run PR Guard on actual git repository"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    print("⏳ Fetching PR changes from git...\n")

    state = {
        "diff": get_pr_diff(),
        "commits": get_commits(),
    }

    print("⏳ Running AI analysis with LangGraph...\n")

    graph = build_graph()
    result = graph.invoke(state)

    # Format as GitHub comment
    comment = format_pr_comment(result)
    
    # Try to post to GitHub PR
    posted = post_github_comment(comment)
    
    # Console output
    print("\n" + "="*60)
    print("🤖 PR GUARD ANALYSIS COMPLETE")
    print("="*60)
    print(f"\n📊 Score: {result['score']}/100")
    print(f"⚠️  Risks: {len(result.get('risks', []))} found")
    print(f"🧪 Tests: {len(result.get('missing_tests', []))} missing")

    if result["score"] < args.threshold:
        print(f"\n❌ PR Guard FAILED (threshold: {args.threshold})")
        exit(1)

    print(f"\n✅ PR Guard PASSED (threshold: {args.threshold})")


if __name__ == "__main__":
    import sys
    
    print("🎯 PRGuard: AI-Powered Code Review Agent")
    print("   Built with LangGraph + Groq (Llama 3.3 70B)\n")
    
    # Check for demo/test flag
    if "--demo" in sys.argv or "--test" in sys.argv:
        test_mode()
    else:
        print("="*60 + "\n")
        main()