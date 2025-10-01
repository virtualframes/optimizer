# Memory Tags

This file contains tags and metadata associated with the agent's memory artifacts. Each entry links a specific memory (e.g., a diff receipt, a benchmark result, a knowledge summary) to a set of descriptive tags.

## Tagging Convention

- **type:** The type of artifact (e.g., `diff_receipt`, `benchmark`, `api_trace`).
- **cycle_id:** A unique identifier for the agent cycle that produced the artifact.
- **outcome:** The result of the action (e.g., `success`, `failure`, `test_pass`, `test_fail`).
- **domain:** The area of focus (e.g., `repo_rewrite`, `db_schema`, `knowledge_acquisition`).
- **tags:** Free-form tags for semantic search (e.g., `refactor`, `bugfix`, `performance`).

## Example

```json
{
  "artifact_path": "receipts/20251001_123456.diff",
  "cycle_id": "cycle_abc123",
  "type": "diff_receipt",
  "outcome": "success",
  "domain": "repo_rewrite",
  "tags": ["refactor", "logging", "daemon"]
}
```