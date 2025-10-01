import os
from github import Github, GithubException

class GitHubAdapter:
    def __init__(self):
        """
        Initializes the GitHub adapter with a token from environment variables.
        """
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable not set.")
        self.g = Github(self.token)

    def commit_patch(self, repo_full_name: str, base_branch: str, patch: dict):
        """
        Commits a patch to a new branch.

        Args:
            repo_full_name: The full name of the repository (e.g., 'user/repo').
            base_branch: The branch to base the new branch on (e.g., 'main').
            patch: A dictionary containing the patch details, including
                   'file_path', 'diff', and 'message'.

        Returns:
            The name of the new branch if successful, otherwise None.
        """
        try:
            repo = self.g.get_repo(repo_full_name)
            source = repo.get_branch(base_branch)
            new_branch_name = f"jules-patch-{patch.get('id', 'temp')}"

            # Create new branch from the source branch
            repo.create_git_ref(ref=f'refs/heads/{new_branch_name}', sha=source.commit.sha)

            # Get the file and update it
            file_path = patch['file_path']
            contents = repo.get_contents(file_path, ref=new_branch_name)
            repo.update_file(
                path=contents.path,
                message=patch['message'],
                content=patch['diff'], # In a real scenario, you'd apply a diff. Here we overwrite.
                sha=contents.sha,
                branch=new_branch_name
            )
            return new_branch_name
        except GithubException as e:
            print(f"GitHub API error during commit: {e}")
            return None

    def create_pr(self, repo_full_name: str, base_branch: str, head_branch: str, title: str, body: str):
        """
        Creates a pull request.
        """
        try:
            repo = self.g.get_repo(repo_full_name)
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            return pr
        except GithubException as e:
            print(f"GitHub API error during PR creation: {e}")
            return None

    def check_ci_status(self, pr_url: str):
        print(f"Simulating check of CI status for PR {pr_url}")
        # In a real implementation, you would parse the PR URL to get the repo and PR number
        # and then use the API to check the status of the latest commit.
        return "success"

    def revert_pr(self, pr_url: str):
        print(f"Simulating revert of PR {pr_url}")
        # In a real implementation, you would parse the PR URL and use the API to revert the PR.
        return True