import os
from dotenv import load_dotenv
from graph import create_prguard_workflow
from state import PRReviewState

# Load environment variables
load_dotenv()

def test_prguard():
    """Test the PRGuard workflow with mock data"""
    
    # Create mock PR data for testing
    initial_state: PRReviewState = {
        "pr_number": 123,
        "repo_name": "myorg/myrepo",
        "pr_diff": """
diff --git a/src/api/users.py b/src/api/users.py
-def get_user(user_id):
+def get_user(user_id, include_details=False):
     return User.query.get(user_id)
     
-def delete_user(id):
-    User.query.filter_by(id=id).delete()
        """,
        "commit_messages": [
            "fix stuff",
            "update code",
            "feat: add user details parameter to get_user API"
        ],
        "files_changed": [
            "src/api/users.py",
            "src/models/user.py"
        ],
        "lines_added": 45,
        "lines_deleted": 12,
        
        # These will be filled by the workflow
        "has_tests": False,
        "test_files": [],
        "breaking_changes": [],
        "commit_quality_score": 0,
        "pr_size_category": "",
        "issues": [],
        "suggestions": [],
        "merge_score": 0,
        "recommendation": "",
        "detailed_report": ""
    }
    
    print("=" * 60)
    print("🚀 Starting PRGuard AI Review")
    print("=" * 60)
    print()
    
    # Create and run the workflow
    app = create_prguard_workflow()
    result = app.invoke(initial_state)
    
    print()
    print("=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print()
    print(result["detailed_report"])
    
    return result


if __name__ == "__main__":
    test_prguard()