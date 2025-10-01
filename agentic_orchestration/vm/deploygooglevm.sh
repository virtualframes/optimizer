#!/bin/bash

# This script provisions a Google Cloud VM to run the agentic orchestration system.
# Prerequisites:
# 1. Google Cloud SDK (gcloud) installed and configured.
# 2. You must be authenticated with gcloud (`gcloud auth login`).
# 3. You must have a project set up (`gcloud config set project YOUR_PROJECT_ID`).

# Note: The startup script assumes the repository is public.
# For a private repository, you would need to handle authentication (e.g., via SSH keys or tokens).

gcloud compute instances create agentic-orchestrator \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=http-server,https-server \
  --metadata-from-file startup-script=startup_config.yaml