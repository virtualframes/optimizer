import os
import argparse
import random
from github import Github
from faker import Faker

# --- Configuration ---
LABELS_PER_ISSUE = {
    "bug": ["bug", "needs-triage"],
    "feature": ["feature-request", "needs-discussion"],
    "test": ["testing", "needs-review"],
    "docs": ["documentation", "needs-clarification"],
}
TASK_TYPES = list(LABELS_PER_ISSUE.keys())

# --- Faker Initialization ---
fake = Faker()

def generate_issue(repo_name, task_type):
    """Generates a synthetic GitHub issue."""
    title = f"[{task_type.capitalize()}] {fake.bs().capitalize()}"
    body = f"**Description:**\n{fake.paragraph(nb_sentences=5)}\n\n"
    body += f"**Steps to Reproduce:**\n1. {fake.sentence()}\n2. {fake.sentence()}\n3. {fake.sentence()}\n\n"
    body += f"**Expected Behavior:**\n{fake.sentence()}\n\n"
    body += f"**Actual Behavior:**\n{fake.sentence()}\n\n"
    body += f"**Environment:**\n- OS: {fake.operating_system()}\n- Python: {random.choice(['3.8', '3.9', '3.10'])}\n"

    labels = LABELS_PER_ISSUE.get(task_type, [])

    return {"title": title, "body": body, "labels": labels}

def main():
    """Main function to run the simulator."""
    parser = argparse.ArgumentParser(description="GitHub Issue Simulator")
    parser.add_argument("--token", required=True, help="GitHub personal access token.")
    parser.add_argument("--repo", required=True, help="Target repository (e.g., 'virtualframes/optimizer').")
    parser.add_argument("--count", type=int, default=10, help="Number of issues to create.")
    args = parser.parse_args()

    g = Github(args.token)
    try:
        repo = g.get_repo(args.repo)
    except Exception as e:
        print(f"Error accessing repository {args.repo}: {e}")
        return

    print(f"Creating {args.count} issues in {args.repo}...")
    for i in range(args.count):
        task_type = random.choice(TASK_TYPES)
        issue_data = generate_issue(args.repo, task_type)

        try:
            repo.create_issue(
                title=issue_data["title"],
                body=issue_data["body"],
                labels=issue_data["labels"]
            )
            print(f"  ({i+1}/{args.count}) Created issue: {issue_data['title']}")
        except Exception as e:
            print(f"Error creating issue: {e}")

    print("Issue creation complete.")

if __name__ == "__main__":
    main()