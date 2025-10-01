import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

# Import the workflow and activities to register them with the worker
from services.synapse_cortex.activities import embedding_activities, jules_activities
from services.synapse_cortex.workflows.semantic_search_workflow import (
    SemanticSearchWorkflow,
)


async def main():
    """The main entry point for the Temporal worker."""
    # Connect to the Temporal cluster.
    # The address is read from an environment variable for flexibility.
    temporal_address = os.getenv("TEMPORAL_ADDRESS", "temporal-frontend.temporal.svc.cluster.local:7233")
    client = await Client.connect(temporal_address)

    # Define the task queue name. This worker will only poll for tasks on this queue.
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "cortex-workflows")

    # Create a worker that will host and run the workflow and activities.
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[SemanticSearchWorkflow],
        activities=[
            embedding_activities.generate_embeddings,
            embedding_activities.index_to_milvus,
            embedding_activities.fetch_note_points,
            embedding_activities.fetch_citations,
            embedding_activities.fetch_audit_events,
            embedding_activities.prune_stale_vectors,
            embedding_activities.publish_metrics,
            jules_activities.auto_debug_and_patch,
        ],
    )

    print(f"Worker started. Listening on task queue: {task_queue}")
    # Start the worker and keep it running until interrupted.
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())