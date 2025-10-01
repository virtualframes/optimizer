import { proxyActivities, workflow } from '@temporalio/workflow';
import type * as activities from 'services/synapse_cortex/activities/embedding_activities';

const {
  fetch_note_points,
  fetch_citations,
  // fetch_audit_events,
  generate_embeddings,
  index_to_milvus,
} = proxyActivities<typeof activities>({
  startToCloseTimeout: '45 minutes', // Extended timeout for large batches
  retry: { initialInterval: '30s', maximumAttempts: 5 },
});

// ... (Interface definitions for EmbeddingBatch and EmbeddingItem) ...

export async function semanticSearchWorkflow() {
  // Determine the time window based on the last successful scheduled run provided by Temporal
  const workflowInfo = workflow.getInfo();
  // Note: Accessing previous run details requires enhanced visibility enabled on the Temporal cluster.
  const previousSuccessfulRun = workflowInfo.searchAttributes?.TemporalScheduledStartTime?.[0];

  let sinceTimestamp: string;
  if (previousSuccessfulRun) {
    sinceTimestamp = new Date(previousSuccessfulRun).toISOString();
  } else {
    // Fallback for the very first run (e.g., last 7 days)
    const fallbackDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    sinceTimestamp = fallbackDate.toISOString();
  }

  workflow.logger.info(`Starting SemanticSearchWorkflow, indexing data since ${sinceTimestamp}`);

  // 1. Parallel Fetch (Fan-out)
  const [notes, citations] = await Promise.all([
    fetch_note_points(sinceTimestamp),
    fetch_citations(sinceTimestamp),
  ]);

  const batches = [
      { source: 'notes', items: notes },
      { source: 'citations', items: citations },
  ].filter(batch => batch.items && batch.items.length > 0);

  let totalIndexed = 0;

  // 2. Process Batches (Embedding and Indexing)
  for (const batch of batches) {
    // Chunking (e.g., 100 items per API call)
    const chunks = chunkArray(batch.items, 100);

    for (const chunk of chunks) {
      const embeddings = await generate_embeddings(chunk);
      const indexed = await index_to_milvus(batch.source, embeddings);
      totalIndexed += indexed;
    }
  }

  return { indexed: totalIndexed };
}

// Utility function
function chunkArray<T>(arr: T[], size: number): T[][] {
  return Array.from({ length: Math.ceil(arr.length / size) },
    (_, i) => arr.slice(i * size, i * size + size));
}