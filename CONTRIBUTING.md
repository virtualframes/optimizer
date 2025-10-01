# Contributing to Jules Mission Ω

We welcome contributions to the Jules Mission Ω Open Protocol. Please follow these guidelines to ensure a smooth development process.

## Development Setup

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR_USERNAME/optimizer.git
    cd optimizer
    ```
3.  **Install the project in editable mode** with development dependencies. This will ensure that your changes are reflected immediately and that you have all the necessary tools for testing and linting.
    ```bash
    pip install -e .[dev]
    ```

## Running Tests

To ensure that your changes do not break existing functionality, please run the test suite before submitting a pull request.

```bash
pytest -q tests/
```

## Code Style

This project uses `black` for code formatting and `flake8` for linting. Please format your code before committing.

```bash
black .
flake8
```

## Pull Request Process

1.  Create a new branch for your feature or bug fix.
2.  Make your changes and commit them with a clear and descriptive commit message.
3.  Push your branch to your fork on GitHub.
4.  Open a pull request to the `main` branch of the `virtualframes/optimizer` repository.
5.  In your pull request, include a summary of the changes and link to any relevant issues.
6.  Jules will automatically benchmark your contribution and provide commentary. Address any feedback before the PR can be merged.