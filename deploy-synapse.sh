#!/usr/bin/env bash
# deploy-synapse.sh - Syzygy Synapse Unified Deployment

set -euo pipefail

echo "=== Syzygy Synapse Deployment ==="
NAMESPACE="synapse-system"
COCKROACHDB_HOST="cockroachdb-public.syzygy.svc.cluster.local" # Adjust if necessary

# Prerequisites check
command -v kubectl >/dev/null || { echo "ERROR: kubectl required"; exit 1; }
command -v helm >/dev/null || { echo "ERROR: helm required"; exit 1; }

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Add Helm Repositories
helm repo add temporalio https://helm.temporal.io
helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo add milvus https://milvus-io.github.io/milvus-helm/
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update

# 1. Deploy Temporal (Cortex - Durable Execution)
echo "[1/6] Deploying Temporal Cluster..."

# NOTE: This configuration assumes CockroachDB is already deployed and accessible.
# Ensure the 'temporal_synapse' database exists in CockroachDB.
helm upgrade --install temporal temporalio/temporal \
  --namespace $NAMESPACE \
  --set server.replicaCount=3 \
  --set cassandra.enabled=false \
  --set postgresql.enabled=false \
  --set mysql.enabled=false \
  --set elasticsearch.enabled=false \
  --set prometheus.enabled=true \
  --set grafana.enabled=true \
  --set externalSQL.enabled=true \
  --set externalSQL.dialect=cockroachdb \
  --set externalSQL.connection.host=$COCKROACHDB_HOST \
  --set externalSQL.connection.port=26257 \
  --set externalSQL.connection.database="temporal_synapse"
  # CRITICAL: Add --set flags for user/password/tls configuration via secrets as required by your DB.

# 2. Deploy NATS JetStream (Event Bus)
echo "[2/6] Deploying NATS JetStream..."
helm upgrade --install nats nats/nats \
  --namespace $NAMESPACE \
  --set cluster.replicas=3 \
  --set nats.jetstream.enabled=true \
  --set nats.jetstream.memStorage.enabled=false \
  --set nats.jetstream.fileStorage.enabled=true \
  --set nats.jetstream.fileStorage.size=10Gi

# 3. Deploy Milvus (Memory Core - Vector DB)
echo "[3/6] Deploying Milvus Cluster..."
# Note: The service endpoint for clients will be 'milvus-proxy'
helm upgrade --install milvus milvus/milvus \
  --namespace $NAMESPACE \
  --set cluster.enabled=true \
  --set persistence.enabled=true

# 4. Deploy Neo4j (Memory Core - Graph DB)
echo "[4/6] Deploying Neo4j..."
# CRITICAL: Set a strong, secure password for production use.
NEO4J_PASSWORD="CHANGE_THIS_SECURE_PASSWORD"
helm upgrade --install neo4j neo4j/neo4j \
  --namespace $NAMESPACE \
  --set neo4j.password=$NEO4J_PASSWORD

# 5. Deploy Application Services
echo "[5/6] Deploying Application Services..."
# Assuming the manifests are saved in the k8s/ directory
if [ -f "k8s/monday-sync-deployment.yaml" ] && [ -f "k8s/intel-harvester-cronjob.yaml" ]; then
    kubectl apply -f k8s/monday-sync-deployment.yaml
    kubectl apply -f k8s/intel-harvester-cronjob.yaml
else
    echo "ERROR: Kubernetes manifests not found in k8s/ directory."
    exit 1
fi

echo "✓ Deployment sequence initiated."
echo "Monitor rollout: kubectl get pods -n $NAMESPACE -w"
echo "Neo4j Password (if default used): $NEO4J_PASSWORD"