# Quickstart: Jules Mission Ω

This document provides a quick way to get started with the Jules Mission Ω Open Protocol.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/virtualframes/optimizer.git
    cd optimizer
    ```

2.  **Install in editable mode with development dependencies:**
    ```bash
    pip install -e .[dev]
    ```

## Running the API

To start the FastAPI server, run the following command:

```bash
uvicorn optimizer.api.main:app --reload
```

The API documentation will be available at `http://127.0.0.1:8000/docs`.

## Using the CLI

The protocol exposes several command-line tools for interacting with the system.

**Example: Run a risk scan**
```bash
jules-risk-scan
```

**Example: Inject entropy**
```bash
omega-inject
```

See `PROJECT_SUMMARY.md` for a full list of commands and their purposes.