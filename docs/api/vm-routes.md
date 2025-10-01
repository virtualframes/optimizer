# VM Routes API Documentation

The VM Routes API provides endpoints for managing containerized agents in Jules Mission Ω. These routes enable deploying, listing, stopping, and health-checking Docker containers that run agent workloads.

## Base Path

All VM routes are prefixed with `/api/v1/vm`

## Authentication

(TBD - Add authentication requirements when implemented)

## Endpoints

### 1. Deploy Containerized Agent

**Endpoint:** `POST /api/v1/vm/deploy`

**Description:** Clone a Git repository, build a Docker image, and run a containerized agent.

**Request Body:**

```json
{
  "repo_url": "https://github.com/example/agent-repo",
  "branch": "main",
  "agent_name": "my-agent",
  "auth_token": "optional_github_token",
  "ssh_key_path": "/path/to/ssh/key",
  "python_version": "3.11",
  "expose_port": 8080,
  "startup_cmd": ["python", "main.py"],
  "environment": {
    "API_KEY": "value",
    "DEBUG": "true"
  }
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `repo_url` | string | Yes | - | Git repository URL (HTTPS or SSH) |
| `branch` | string | No | `"main"` | Git branch to clone |
| `agent_name` | string | Yes | - | Unique name for the agent container |
| `auth_token` | string | No | `null` | HTTPS authentication token for private repos |
| `ssh_key_path` | string | No | `null` | Path to SSH private key for private repos |
| `python_version` | string | No | `"3.11"` | Python base image version |
| `expose_port` | integer | No | `8080` | Service port exposed by the container |
| `startup_cmd` | array[string] | No | `["python", "main.py"]` | Container startup command |
| `environment` | object | No | `{}` | Environment variables for the container |

**Response (Success - 200):**

```json
{
  "container_id": "abc123...",
  "container_name": "jules-agent-my-agent-1234567890",
  "status": "running",
  "ports": {
    "8080/tcp": 32768
  }
}
```

**Response (Error - 502):**

```json
{
  "detail": "deployment_failed"
}
```

**Response (Not Implemented - 501):**

```json
{
  "detail": "VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
}
```

**Example cURL:**

```bash
curl -X POST http://localhost:8080/api/v1/vm/deploy \
  -H 'Content-Type: application/json' \
  -d '{
    "repo_url": "https://github.com/psf/black",
    "agent_name": "black-demo",
    "startup_cmd": ["python", "-c", "print(\"ok\")"]
  }'
```

### 2. List Deployments

**Endpoint:** `GET /api/v1/vm/list`

**Description:** List all active Jules-managed containers (identified by label).

**Request:** No parameters required.

**Response (Success - 200):**

```json
[
  {
    "container_id": "abc123...",
    "container_name": "jules-agent-my-agent-1234567890",
    "status": "running",
    "created": "2025-10-01T10:30:00Z",
    "ports": {
      "8080/tcp": 32768
    }
  }
]
```

**Response (Not Implemented - 501):**

```json
{
  "detail": "VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
}
```

**Example cURL:**

```bash
curl http://localhost:8080/api/v1/vm/list
```

### 3. Stop Deployment

**Endpoint:** `POST /api/v1/vm/stop`

**Description:** Stop and optionally remove a running container.

**Request Body:**

```json
{
  "container_name": "jules-agent-my-agent-1234567890",
  "remove": true
}
```

**Parameters:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `container_name` | string | Yes | - | Name of the container to stop |
| `remove` | boolean | No | `true` | Whether to remove the container after stopping |

**Response (Success - 200):**

```json
{
  "stopped": "jules-agent-my-agent-1234567890",
  "removed": true
}
```

**Response (Not Implemented - 501):**

```json
{
  "detail": "VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
}
```

**Example cURL:**

```bash
curl -X POST http://localhost:8080/api/v1/vm/stop \
  -H 'Content-Type: application/json' \
  -d '{
    "container_name": "jules-agent-my-agent-1234567890",
    "remove": true
  }'
```

### 4. Health Check

**Endpoint:** `GET /api/v1/vm/health/{container_name}`

**Description:** Check Docker container status and optionally perform an HTTP health probe.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `container_name` | string | Yes | Name of the container to check |

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | No | `"/health"` | HTTP endpoint path for health probe |

**Response (Success - 200):**

```json
{
  "container_status": "running",
  "health_status": "healthy",
  "http_probe": {
    "status_code": 200,
    "response": {"status": "ok"}
  }
}
```

**Response (Not Implemented - 501):**

```json
{
  "detail": "VM manager not yet implemented. Waiting for optimizer.vm_integration.enhanced_vm_manager module."
}
```

**Example cURL:**

```bash
curl "http://localhost:8080/api/v1/vm/health/jules-agent-my-agent-1234567890?path=/health"
```

## Implementation Status

⚠️ **Note:** These endpoints are currently placeholders that return HTTP 501 (Not Implemented). They will become functional once the `optimizer.vm_integration.enhanced_vm_manager` module is implemented.

The VM manager will provide:
- Git repository cloning with shallow clone (`--depth=1`)
- Automatic Dockerfile generation with HEALTHCHECK directives
- Docker image building using Python SDK
- Container lifecycle management (run, stop, remove)
- Health checking via Docker status and HTTP probes

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 501 | Not Implemented (VM manager module not yet available) |
| 502 | Bad Gateway (deployment failed) |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (container not found) |

## Future Enhancements

- Authentication and authorization
- Resource limits (CPU, memory)
- Volume mounting for persistent data
- Network configuration options
- Batch operations (deploy/stop multiple containers)
- Deployment rollback capabilities
- Metrics and monitoring integration
