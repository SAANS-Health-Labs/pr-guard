import os
import json
from github import Github


def _get_pr_number():
    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    return event["pull_request"]["number"]


def post_pr_comment(body: str):
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

    pr_number = _get_pr_number()
    pr = repo.get_pull(pr_number)

    pr.create_issue_comment(body)

def is_ci():
    return os.getenv("GITHUB_ACTIONS") == "true"