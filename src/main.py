# import os
# from dotenv import load_dotenv
# from graph import create_prguard_workflow
# from state import PRReviewState

# # Load environment variables
# load_dotenv()

# def test_prguard():
#     """Test the PRGuard workflow with mock data"""
    
#     # Create mock PR data for testing
#     initial_state: PRReviewState = {
#         "pr_number": 123,
#         "repo_name": "myorg/myrepo",
#         "pr_diff": """
# diff --git a/src/api/users.py b/src/api/users.py
# -def get_user(user_id):
# +def get_user(user_id, include_details=False):
#      return User.query.get(user_id)
     
# -def delete_user(id):
# -    User.query.filter_by(id=id).delete()
#         """,
#         "commit_messages": [
#             "fix stuff",
#             "update code",
#             "feat: add user details parameter to get_user API"
#         ],
#         "files_changed": [
#             "src/api/users.py",
#             "src/models/user.py"
#         ],
#         "lines_added": 45,
#         "lines_deleted": 12,
        
#         # These will be filled by the workflow
#         "has_tests": False,
#         "test_files": [],
#         "breaking_changes": [],
#         "commit_quality_score": 0,
#         "pr_size_category": "",
#         "issues": [],
#         "suggestions": [],
#         "merge_score": 0,
#         "recommendation": "",
#         "detailed_report": ""
#     }
    
#     print("=" * 60)
#     print("🚀 Starting PRGuard AI Review")
#     print("=" * 60)
#     print()
    
#     # Create and run the workflow
#     app = create_prguard_workflow()
#     result = app.invoke(initial_state)
    
#     print()
#     print("=" * 60)
#     print("📊 FINAL REPORT")
#     print("=" * 60)
#     print()
#     print(result["detailed_report"])
    
#     return result


# if __name__ == "__main__":
#     test_prguard()

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


# def test_with_mock_data():
#     """Test PRGuard with mock PR data"""
    
#     print("\n" + "="*60)
#     print("🧪 Testing PRGuard with Mock Data")
#     print("="*60 + "\n")
    
#     state = {
#         "diff": """
# diff --git a/src/api/users.py b/src/api/users.py
# index 1234567..abcdefg 100644
# --- a/src/api/users.py
# +++ b/src/api/users.py
# @@ -10,8 +10,8 @@ class UserAPI:
# -    def get_user(self, user_id):
# -        return User.query.get(user_id)
# +    def get_user(self, user_id, include_details=False):
# +        return User.query.get(user_id)
     
# -    def delete_user(self, id):
# -        User.query.filter_by(id=id).delete()
# +    # Removed delete_user function
#         """,
#         "commits": """
# abc123 fix stuff
# def456 update code
# ghi789 feat: add user details parameter
#         """
#     }

#     graph = build_graph()
#     result = graph.invoke(state)

#     print("📝 SUMMARY:")
#     print(result["summary"])
#     print("\n⚠️ RISKS:")
#     for risk in result.get("risks", []):
#         print(f"  - {risk}")
#     print("\n🧪 MISSING TESTS:")
#     for test in result.get("missing_tests", []):
#         print(f"  - {test}")
#     print(f"\n📊 MERGE SCORE: {result['score']}/100")
    
#     if result["score"] >= 70:
#         print("\n✅ PR Guard PASSED")
#     else:
#         print("\n❌ PR Guard FAILED")


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
    # Test with mock data
    # test_with_mock_data()
    
    # Uncomment below when ready to use with real git
    main()