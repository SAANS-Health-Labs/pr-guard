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
    print("\n" + "="*60 + "\n")
    # Uncomment to use with real git repo
    main()