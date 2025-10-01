import asyncio
import click
from temporalio.client import Client

# Import the workflow from the orchestration layer
from services.synapse_cortex.workflows.orchestration_workflow import OrchestrationWorkflow

async def trigger_workflow(task: str):
    """
    Connects to Temporal and triggers the OrchestrationWorkflow.
    """
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        OrchestrationWorkflow.run,
        task,
        id="jules-orchestration-workflow",
        task_queue="syzygy-synapse-task-queue",
    )
    print(f"Workflow result: {result}")

@click.command()
@click.option("--task", default="Fix a bug in the login service", help="The task for Jules to work on.")
def main(task):
    """
    A CLI for triggering the Jules agent's orchestration workflow.
    """
    print(f"Triggering workflow for task: {task}")
    asyncio.run(trigger_workflow(task))

if __name__ == "__main__":
    main()