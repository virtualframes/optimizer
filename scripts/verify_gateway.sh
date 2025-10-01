#!/bin/bash

# This script verifies the physixiology_api/gateway service.
# It builds the Docker image, runs the container, checks the health endpoint,
# and then cleans up.

set -e

GATEWAY_DIR="physixiology_api/gateway"
IMAGE_NAME="physixiology-gateway"
CONTAINER_NAME="physixiology-gateway-container"
HOST_PORT=8000

echo "--- Starting Gateway Verification ---"

# 1. Build the Docker image
echo "Building Docker image: $IMAGE_NAME"
sudo docker build -t $IMAGE_NAME $GATEWAY_DIR

# 2. Run the Docker container in detached mode
echo "Running Docker container: $CONTAINER_NAME on port $HOST_PORT"
sudo docker run -d --name $CONTAINER_NAME -p $HOST_PORT:80 $IMAGE_NAME

# 3. Wait for the service to start
echo "Waiting for service to start..."
sleep 5

# 4. Check the health endpoint
echo "Pinging health endpoint..."
response=$(curl -s http://localhost:$HOST_PORT/health)

# 5. Stop and remove the container
echo "Cleaning up container..."
sudo docker stop $CONTAINER_NAME > /dev/null
sudo docker rm $CONTAINER_NAME > /dev/null

# 6. Verify the response
if [[ "$response" == *"\"status\":\"healthy\""* ]]; then
  echo "✅ Verification successful: Gateway is healthy."
  exit 0
else
  echo "❌ Verification failed: Did not receive healthy status."
  echo "Received response: $response"
  exit 1
fi