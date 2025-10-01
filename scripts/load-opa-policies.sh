#!/bin/bash
# This script loads Rego policies into a Kubernetes ConfigMap for OPA to discover.

# Exit immediately if a command exits with a non-zero status.
set -e

NAMESPACE="synapse-system"
POLICY_DIR="policies"
CONFIGMAP_NAME="opa-policies-merge-control"
POLICY_FILE="merge_control.rego"

# Check if the policy file exists
if [ ! -f "${POLICY_DIR}/${POLICY_FILE}" ]; then
    echo "Error: Policy file not found at ${POLICY_DIR}/${POLICY_FILE}"
    exit 1
fi

echo "Creating ConfigMap ${CONFIGMAP_NAME} from ${POLICY_DIR}/${POLICY_FILE} in namespace ${NAMESPACE}..."

# Create the ConfigMap from the Rego file.
# Using --dry-run and kubectl apply is a robust way to create or update the resource.
kubectl create configmap ${CONFIGMAP_NAME} --namespace ${NAMESPACE} \
    --from-file=${POLICY_FILE}=${POLICY_DIR}/${POLICY_FILE} \
    --dry-run=client -o yaml | kubectl apply -f -

echo "Labeling ConfigMap for OPA discovery..."

# Label the ConfigMap for OPA discovery. This allows OPA to find and load the policy automatically.
kubectl label configmap ${CONFIGMAP_NAME} openpolicyagent.org/policy=rego \
    --namespace ${NAMESPACE} --overwrite

echo "Policy loading script complete."