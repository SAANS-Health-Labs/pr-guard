import os
import subprocess
import argparse
from graph import build_graph


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


def test_vulnerable_code():
    """Test with VULNERABLE/BAD code examples"""
    
    print("\n" + "="*60)
    print("🚨 Testing VULNERABLE CODE")
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
+# Hardcoded credentials (SECURITY RISK!)
+ADMIN_PASSWORD = "admin123"
+API_KEY = "sk-1234567890abcdef"
+
+def authenticate_user(username, password):
+    # SQL Injection vulnerability!
+    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
+    return db.execute(query)
+
+def hash_password(password):
+    # Using weak MD5 hashing (SECURITY RISK!)
+    return hashlib.md5(password.encode()).hexdigest()
+
+def process_payment(amount, card_number):
+    # No input validation!
+    total = amount * 100  # No overflow check
+    print(f"Processing payment: {card_number}")  # Logging sensitive data!
+    return total
+
+def delete_user(user_id):
+    # No authorization check!
+    query = f"DELETE FROM users WHERE id={user_id}"
+    return db.execute(query)

diff --git a/src/api.py b/src/api.py
index abc123..def456 100644
--- a/src/api.py
+++ b/src/api.py
@@ -5,10 +5,8 @@
 
-def get_user_data(user_id):
-    if not is_authorized(user_id):
-        raise PermissionError()
+def get_user_data(user_id):
+    # Removed authorization check (BREAKING CHANGE!)
     return database.get(user_id)
 
-def upload_file(file):
-    allowed_types = ['.jpg', '.png']
-    if file.ext not in allowed_types:
-        raise ValueError("Invalid file type")
+def upload_file(file):
+    # Removed file type validation (SECURITY RISK!)
     return save_to_disk(file)
        """,
        "commits": """
a1b2c3d fix auth
e4f5g6h update api
i7j8k9l remove checks
        """
    }

    graph = build_graph()
    result = graph.invoke(state)

    print("📝 SUMMARY:")
    print(result["summary"])
    print("\n⚠️ RISKS DETECTED:")
    for risk in result.get("risks", []):
        print(f"  🔴 {risk}")
    print("\n🧪 MISSING TESTS:")
    for test in result.get("missing_tests", []):
        print(f"  ⚪ {test}")
    print(f"\n📊 MERGE SCORE: {result['score']}/100")
    
    if result["score"] >= 70:
        print("\n✅ PR Guard PASSED")
    else:
        print("\n❌ PR Guard FAILED - DO NOT MERGE!")


def test_good_code():
    """Test with GOOD, secure code"""
    
    print("\n" + "="*60)
    print("✅ Testing GOOD CODE")
    print("="*60 + "\n")
    
    state = {
        "diff": """
diff --git a/src/auth.py b/src/auth.py
new file mode 100644
--- /dev/null
+++ b/src/auth.py
@@ -0,0 +1,30 @@
+import bcrypt
+from typing import Optional
+
+def authenticate_user(username: str, password: str) -> Optional[dict]:
+    '''Authenticate user with parameterized query'''
+    query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
+    user = db.execute_safe(query, (username, hash_password(password)))
+    return user
+
+def hash_password(password: str) -> str:
+    '''Hash password using bcrypt'''
+    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
+
+def verify_password(password: str, hash: str) -> bool:
+    '''Verify password against hash'''
+    return bcrypt.checkpw(password.encode(), hash.encode())
+
+@require_permission('admin')
+def delete_user(user_id: int) -> bool:
+    '''Delete user with authorization check'''
+    if not user_id or user_id < 0:
+        raise ValueError("Invalid user_id")
+    query = "DELETE FROM users WHERE id = ?"
+    return db.execute_safe(query, (user_id,))

diff --git a/tests/test_auth.py b/tests/test_auth.py
new file mode 100644
--- /dev/null
+++ b/tests/test_auth.py
@@ -0,0 +1,20 @@
+import pytest
+from auth import authenticate_user, hash_password, verify_password
+
+def test_hash_password():
+    password = "test123"
+    hash1 = hash_password(password)
+    hash2 = hash_password(password)
+    assert hash1 != hash2  # Different salts
+    assert verify_password(password, hash1)
+
+def test_authenticate_user():
+    result = authenticate_user("test_user", "test_pass")
+    assert result is not None
+
+def test_delete_user_requires_auth():
+    with pytest.raises(PermissionError):
+        delete_user(123)  # Without auth should fail
        """,
        "commits": """
feat(auth): implement secure authentication with bcrypt
test(auth): add comprehensive security tests
docs(auth): add security documentation
refactor(auth): use parameterized queries to prevent SQL injection
        """
    }

    graph = build_graph()
    result = graph.invoke(state)

    print("📝 SUMMARY:")
    print(result["summary"])
    print("\n⚠️ RISKS DETECTED:")
    risks = result.get("risks", [])
    if risks:
        for risk in risks:
            print(f"  🟡 {risk}")
    else:
        print("  ✅ No security risks detected!")
    print("\n🧪 MISSING TESTS:")
    tests = result.get("missing_tests", [])
    if tests:
        for test in tests:
            print(f"  ⚪ {test}")
    else:
        print("  ✅ All code has test coverage!")
    print(f"\n📊 MERGE SCORE: {result['score']}/100")
    
    if result["score"] >= 70:
        print("\n✅ PR Guard PASSED - Safe to merge!")
    else:
        print("\n❌ PR Guard FAILED")


def main():
    """Run PR Guard on actual git repository"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    state = {
        "diff": get_pr_diff(),
        "commits": get_commits(),
    }

    graph = build_graph()
    result = graph.invoke(state)

    print("\n🤖 PR GUARD REPORT\n")
    print("SUMMARY:\n", result["summary"])
    print("\nRISKS:\n", result.get("risks"))
    print("\nMISSING TESTS:\n", result.get("missing_tests"))
    print("\nMERGE SCORE:", result["score"])

    if result["score"] < args.threshold:
        print("\n❌ PR Guard failed quality gate")
        exit(1)

    print("\n✅ PR Guard passed")


if __name__ == "__main__":
    # Demo Mode: Show both vulnerable and good code
    print("🎯 PRGuard Demo - Testing AI Security Analysis\n")
    
    test_vulnerable_code()  # Should FAIL with low score
    print("\n" + "="*60 + "\n")
    test_good_code()        # Should PASS with high score
    
    # Uncomment to use with real git repo
    # main()