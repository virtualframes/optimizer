#!/usr/bin/env bash
# To install this hook, run the following command from the root of the repository:
# cp scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# .git/hooks/pre-commit (Syzygy Citation Tracker)

CITATIONS_FILE="docs/citations/citations.jsonl"
mkdir -p docs/citations

# Extract URLs, DOIs, arXiv IDs from staged changes
# We use git diff --cached to look at the content being committed.
STAGED_CONTENT=$(git diff --cached)
# Get the HEAD SHA if available, otherwise mark as initial
COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "initial")
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Function to log citations
log_citation() {
  local type=$1
  local ref=$2
  # Escape quotes in the reference for JSON compatibility
  local escaped_ref=$(echo "$ref" | sed 's/"/\\"/g')
  echo "{\"ts\":\"$TIMESTAMP\",\"commit\":\"$COMMIT_SHA\",\"type\":\"$type\",\"ref\":\"$escaped_ref\"}" >> "$CITATIONS_FILE"
}

# Extract URLs
echo "$STAGED_CONTENT" | grep -Eoh '\bhttps?://[^\s<>"]+' | sort -u | while read url; do
  log_citation "url" "$url"
done

# Extract DOIs
echo "$STAGED_CONTENT" | grep -Eoh '\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+' | sort -u | while read doi; do
  log_citation "doi" "$doi"
done

# Extract arXiv IDs
echo "$STAGED_CONTENT" | grep -Eoh 'arXiv:[0-9]{4}\.[0-9]{4,5}' | sort -u | while read arxiv; do
  log_citation "arxiv" "$arxiv"
done

# Deduplicate, sort, and stage the updated citations file
if [[ -f "$CITATIONS_FILE" ]]; then
  # Use a temporary file for sorting to ensure atomic update and avoid duplicates
  TMP_FILE=$(mktemp)
  sort -u "$CITATIONS_FILE" > "$TMP_FILE"
  mv "$TMP_FILE" "$CITATIONS_FILE"
  git add "$CITATIONS_FILE"
fi