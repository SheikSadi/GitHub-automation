import os
import sys
import json
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai.types import GenerateContentConfig
from github import Github  # pip install PyGithub


GEMINI_MODEL = "gemini-2.5-flash"
RESERVED_LABELS = ["P1 - High", "P2 - Medium", "P3 - Low", "ShowStopper"]


class Response(BaseModel):
    labels: List[str] = Field(
        description="List of labels suggested for the issue or comment."
    )


def label_issues(issue, description):
    client = genai.Client(vertexai=True)

    print(f"Sending request to Google GenAI ({GEMINI_MODEL}) for labeling...")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=(
            "Find appropiate labels for the GitHub issue or comment based on the provided description and labels. "
            "The labels are provided in the format: label_name: description. "
            "The description is a brief summary of the issue or comment. "
            "Return a JSON array of label names that are relevant to the issue or comment. "
            "Your labels should be taken directly from the provided ones, "
            "Example: ['bug', 'enhancement', 'question']"
            f"\n\nLabels:\n{REPO_LABELS}"
            f"\n\nIssue or Comment Description:\n{description}"
        ),
        config=GenerateContentConfig(
            system_instruction=[
                (
                    "You are an expert Github project manager. Given the description of an issue or comment, "
                    "and a set of labels with descriptions, your task is to suggest appropriate labels for the issue."
                )
            ],
            temperature=0,
            response_mime_type="application/json",
            response_schema=Response,
        ),
    )

    suggested_labels = response.parsed.labels
    all_labels = [label["name"] for label in REPO_LABELS]
    assert set(suggested_labels).issubset(
        all_labels
    ), "Labels must be a subset of the available labels"

    print(f"Received labels from Google GenAI: {suggested_labels}")

    already = set(l.name for l in issue.get_labels())
    to_add = set(suggested_labels).difference(already)
    if to_add:
        issue.add_to_labels(*to_add)
        print(f"Labels added to issue #{issue.number}: {', '.join(to_add)}")

    return to_add


def extract_description(event):
    if "issue" in event:
        title = event["issue"].get("title") or ""
        body = event["issue"].get("body") or ""
        text = title + "\n" + body
    if "comment" in event:
        body = event["comment"].get("body") or ""
        text += "\n" + body
    return text.lower()


if __name__ == "__main__":
    gh_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]
    event_path = os.environ.get("GITHUB_EVENT_PATH", "github_event.json")
    event_name = os.environ["GITHUB_EVENT_NAME"]

    print("Reading event payload...")
    if os.path.exists(event_path):
        with open(event_path) as f:
            event = json.load(f)
    else:
        print("No event payload found, skipping.")
        sys.exit(0)

    print("Initializing Github client...")
    g = Github(gh_token)

    print(f"Fetching repository {repo_name=}...")
    repo = g.get_repo(repo_name)

    print("Fetching repository labels...")
    REPO_LABELS = [
        {"name": label.name, "description": label.description}
        for label in repo.get_labels()
        if label.name not in RESERVED_LABELS
    ]

    print("Fetching issue...")
    issue = repo.get_issue(number=event["issue"]["number"])

    print("Extracting description from event...")
    description = extract_description(event)

    print("Labeling issue based on description with Google GenAI...")
    new_labels = label_issues(issue, description)
    if not new_labels:
        print("No new labels added.")
