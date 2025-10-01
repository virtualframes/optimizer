import asyncio
import click
from temporalio.client import Client

# Import the workflow
from .workflows.debugandpatch import DebugAndPatchWorkflow

@click.command()
@click.option("--task-id", required=True, help="A unique ID for the task.")
@click.option("--repo", required=True, help="The full repository name (e.g., 'user/repo').")
@click.option("--branch", default="main", help="The base branch to work from.")
@click.option("--body", required=True, help="The body of the issue or task description.")
@click.option("--file-path", required=True, help="The path to the file to be patched.")
async def run_workflow(task_id, repo, branch, body, file_path):
    """
    Triggers the DebugAndPatchWorkflow with the provided task details.
    """
    client = await Client.connect("localhost:7233")

    task = {
        "id": task_id,
        "repo": repo,
        "branch": branch,
        "body": body,
        "file_path": file_path, # Add file_path to the task dictionary
    }

    print(f"Starting workflow {DebugAndPatchWorkflow.run.__name__} with task ID: {task_id}")
    result = await client.execute_workflow(
        DebugAndPatchWorkflow.run,
        task,
        id=f"jules-patch-workflow-{task_id}",
        task_queue="jules-patch-queue",
    )

    print(f"\nWorkflow completed. Result: {result}")


if __name__ == "__main__":
    # Click's async support requires running the command this way
    run_workflow(_anyio_backend="asyncio")