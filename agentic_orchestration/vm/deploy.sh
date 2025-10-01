#!/bin/bash
gcloud compute instances create agentic-orchestrator \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --tags=http-server \
  --metadata-from-file startup-script=vm/startup.sh