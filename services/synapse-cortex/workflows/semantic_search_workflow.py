import asyncio
from datetime import timedelta

from temporalio import workflow

# Import activity stubs. The actual implementations will be in the activities file.
# The `with` block is necessary for the Temporal runtime to correctly handle imports.
with workflow.unsafe.imports_passed_through():
    from services.synapse_cortex.activities.embedding_activities import (
        fetch_note_points,
        fetch_citations,
        fetch_audit_events,
        generate_embeddings,
        index_to_milvus,
        prune_stale_vectors,
        publish_metrics,
    )


def _chunk_array(arr: list, size: int) -> list[list]:
    """Helper function to break a list into smaller chunks."""
    return [arr[i : i + size] for i in range(0, len(arr), size)]


@workflow.defn
class SemanticSearchWorkflow:
    """The main workflow for the semantic search pipeline."""

    @workflow.run
    async def run(self, since: str) -> dict:
        """
        Workflow execution entry point.

        Args:
            since: A string representing the timestamp from which to fetch new data.

        Returns:
            A dictionary containing the total number of items indexed.
        """
        total_indexed = 0

        # 1. Fetch data from all sources in parallel
        notes_future = workflow.start_activity(
            fetch_note_points, since, start_to_close_timeout=timedelta(minutes=15)
        )
        citations_future = workflow.start_activity(
            fetch_citations, since, start_to_close_timeout=timedelta(minutes=15)
        )
        audit_future = workflow.start_activity(
            fetch_audit_events, since, start_to_close_timeout=timedelta(minutes=15)
        )

        # Wait for all data fetching activities to complete
        notes, citations, audit = await asyncio.gather(
            notes_future, citations_future, audit_future
        )

        batches = [
            {"source": "notes", "items": notes},
            {"source": "citations", "items": citations},
            {"source": "audit", "items": audit},
        ]

        # 2. Process each batch of data
        for batch in batches:
            if not batch["items"]:
                continue

            # Break items into chunks to avoid overwhelming the embedding service
            chunks = _chunk_array(batch["items"], 100)
            for chunk in chunks:
                embeddings = await workflow.start_activity(
                    generate_embeddings, chunk, start_to_close_timeout=timedelta(minutes=10)
                )
                indexed_count = await workflow.start_activity(
                    index_to_milvus,
                    batch["source"],
                    embeddings,
                    start_to_close_timeout=timedelta(minutes=10),
                )
                total_indexed += indexed_count

        # 3. Perform cleanup and reporting
        await workflow.start_activity(
            prune_stale_vectors, start_to_close_timeout=timedelta(minutes=5)
        )

        await workflow.start_activity(
            publish_metrics,
            {
                "workflow": "semantic-search",
                "indexed": total_indexed,
                "timestamp": workflow.now().isoformat(),
            },
            start_to_close_timeout=timedelta(minutes=1),
        )

        workflow.logger.info(f"SemanticSearchWorkflow completed. Indexed {total_indexed} items.")
        return {"indexed": total_indexed}