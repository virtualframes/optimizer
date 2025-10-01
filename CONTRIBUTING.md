# Contributing to Optimizer

Thank you for your interest in contributing to Optimizer! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/virtualframes/optimizer.git
   cd optimizer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Code Style

- Follow PEP 8 guidelines
- Maximum line length: 127 characters
- Use type hints where appropriate
- Write docstrings for all public functions and classes

## Linting

Before committing, run:

```bash
flake8 optimizer --max-line-length=127 --max-complexity=10
```

## Testing

1. **Run all tests**
   ```bash
   pytest tests/ -v
   ```

2. **Run tests with coverage**
   ```bash
   pytest tests/ -v --cov=optimizer --cov-report=term-missing
   ```

3. **Write tests for new features**
   - Add unit tests in the appropriate `test_*.py` file
   - Aim for at least 80% code coverage for new code
   - Test both success and failure cases

## Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise commit messages
   - Keep commits focused and atomic
   - Update documentation if needed

3. **Test your changes**
   ```bash
   pytest tests/ -v
   flake8 optimizer --max-line-length=127
   ```

4. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **PR Guidelines**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI checks pass
   - Request review from maintainers

## Project Structure

```
optimizer/
├── optimizer/              # Main package
│   ├── core/              # Core node implementation
│   ├── engine/            # Physics engine adapter
│   ├── auth/              # Authentication matrix
│   ├── api/               # FastAPI application
│   ├── config/            # Configuration and logging
│   └── cli.py             # CLI entrypoint
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD workflows
└── docs/                  # Documentation (future)
```

## Adding New Features

### Adding a New Core Module

1. Create module in appropriate package directory
2. Add `__init__.py` exports
3. Write comprehensive tests
4. Update documentation

### Adding API Endpoints

1. Add route functions in `optimizer/api/routes/`
2. Define Pydantic models for request/response
3. Add tests in `tests/test_api.py`
4. Update API documentation

### Adding CLI Commands

1. Add command function in `optimizer/cli.py`
2. Use Click decorators for options
3. Add tests for the command
4. Update README and QUICKSTART

## Documentation

- Keep README.md up to date
- Document all public APIs
- Add examples for new features
- Update QUICKSTART.md if workflow changes

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for questions or discussions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
