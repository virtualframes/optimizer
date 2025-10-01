# GitHub Issue Simulator

This script is designed to stress-test the Jules AGI agent by creating a configurable number of synthetic issues in a specified GitHub repository. It helps validate the entire task-handling pipeline, from ingestion to resolution.

## Setup

1.  **Install Dependencies:**
    Navigate to the `task_simulator` directory and install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the simulator from the command line, providing the necessary arguments.

```bash
python simulator.py --token YOUR_GITHUB_TOKEN --repo your-username/your-repo --count 50
```

### Arguments

*   `--token`: **(Required)** Your GitHub Personal Access Token. This is needed to authenticate with the GitHub API.
*   `--repo`: **(Required)** The target repository where the issues will be created (e.g., `virtualframes/optimizer`).
*   `--count`: (Optional) The number of synthetic issues to create. Defaults to `10`.

### Security

**Important:** Do not hardcode your GitHub token in the script or commit it to version control. Pass it as a command-line argument or use environment variables for better security.