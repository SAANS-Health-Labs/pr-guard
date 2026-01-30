import os
import subprocess
import argparse
from graph import build_graph
from utils import format_pr_comment
from gith.client import post_pr_comment, is_ci


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

def get_pr_title():
    """Get PR title from GitHub event payload (CI only)"""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return ""
    try:
        import json
        with open(event_path) as f:
            event = json.load(f)
        return event.get("pull_request", {}).get("title", "")
    except Exception:
        return ""


def main():
    """Run PR Guard on actual git repository"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=70)
    args = parser.parse_args()

    state = {
        "diff": get_pr_diff(),
        "commits": get_commits(),
        "pr_title": get_pr_title(),
    }

    graph = build_graph()
    result = graph.invoke(state)

    print("\n🤖 PR GUARD REPORT\n")
    print("\n🔐 RISKS:\n", result.get("risks"))
    print("\n🧪 MISSING TESTS:\n", result.get("missing_tests"))
    print("\n🧹 LINT ISSUES:\n", result.get("lint_issues"))
    print("\nMERGE SCORE:", result["score"])

    # Generate PR comment
    markdown_comment = format_pr_comment(result, args.threshold)

    # Post comment ONLY in GitHub Actions
    if is_ci():
        post_pr_comment(markdown_comment)

    if result["score"] < args.threshold:
        print("\n❌ PR Guard failed quality gate")
        exit(1)

    print("\n✅ PR Guard passed")


if __name__ == "__main__":
    print("🎯 PRGuard: AI-powered security analysis in progress.\n")
    print("\n" + "="*60 + "\n")
    main()