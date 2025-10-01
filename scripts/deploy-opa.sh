#!/bin/bash
# This script deploys Open Policy Agent (OPA) to the synapse-system namespace using Helm.

# Exit immediately if a command exits with a non-zero status.
set -e

# Add the OPA Helm repository
echo "Adding OPA Helm repository..."
helm repo add open-policy-agent https://open-policy-agent.github.io/opa-helm-charts
helm repo update

# Install OPA as a centralized policy service.
# We disable the admission controller as we are using OPA for application-level policy decisions,
# not as a Kubernetes admission controller.
echo "Installing/upgrading OPA in namespace synapse-system..."
helm upgrade --install opa open-policy-agent/opa \
    --namespace synapse-system \
    --create-namespace \
    --set admissionController.enabled=false

echo "OPA deployment complete."