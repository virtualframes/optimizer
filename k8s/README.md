# Kubernetes Manifests

This directory contains the Kubernetes manifests for the Syzygy Synapse application services.

## Prerequisites

Before applying these manifests or running the `deploy-synapse.sh` script, you **must** build the container images for the `monday-sync` and `intel-harvester` services and push them to your container registry.

The placeholder image names in the manifest files (`your-registry/monday-sync:latest` and `your-registry/intel-harvester:latest`) must be updated to point to the images you have built and pushed. Failure to do so will result in the deployment failing.