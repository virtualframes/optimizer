# Syzygy Synapse: A Flaw-First Optimization Engine

This repository contains the source code for **Syzygy Synapse**, a multi-agent, self-healing software development framework. It is designed to autonomously detect, diagnose, and patch flaws in its own codebase and in target applications. The system leverages a "Flaw-First" philosophy, treating every potential error as an opportunity for mutation, learning, and evolution.

At its core, Syzygy Synapse is powered by **Jules**, an advanced AI agent responsible for the hands-on tasks of debugging, patch generation, and code verification. The entire process is orchestrated by a durable, fault-tolerant cortex built on Temporal.io, ensuring that complex, long-running development and repair tasks can execute reliably.

## Key Architectural Pillars

1.  **Flaw-First Optimization Engine**: The high-level control system that governs the agentic processes. It identifies potential flaws, schedules diagnostic tasks, and manages the lifecycle of automated software development.

2.  **Jules Agent**: A specialized AI agent with a suite of tools for interacting with codebases, running tests, and collaborating with other AI models. Jules is the primary actor in the system's automated debugging and development workflows.

3.  **Syzygy Synapse Cortex**: The orchestration layer, built on Temporal, that manages the complex workflows of the Jules agent. It provides the durability and scalability required for autonomous, long-running software engineering tasks.

4.  **Unified Memory and Provenance**: A hybrid memory system using Neo4j for structured data and provenance and Milvus for vector-based semantic search. Every action taken by the system is recorded, creating an auditable history of all mutations, decisions, and outcomes.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Temporal CLI (`tctl`)
- Kubernetes (`kubectl`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/virtualframes/optimizer.git
    cd optimizer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the environment:**
    - Copy the `.env.example` to `.env` and populate it with the necessary credentials for services like OpenAI, GitHub, and Neo4j.

4.  **Start the local development environment:**
    ```bash
    docker-compose up -d
    ```

## Running the System

The system is composed of several services that can be run locally for development and testing.

-   **Start the Temporal worker:**
    ```bash
    python -m jules.worker
    ```

-   **Trigger a workflow:**
    ```bash
    python -m jules.workflow --task "Fix a bug in the authentication service"
    ```

## Testing

To run the test suite, use `pytest`:
```bash
pytest
```

## Contributing

This project is an exploration into the future of autonomous software development. Contributions, ideas, and feedback are welcome. Please open an issue to discuss any proposed changes.