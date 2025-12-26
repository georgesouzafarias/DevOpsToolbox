# Contributing to DevOpsToolbox

Thank you for your interest in contributing to DevOpsToolbox! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Access to a Kubernetes cluster (for testing k8s commands)

### Development Setup

1. Fork the repository on GitHub

2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DevOpsToolbox.git
   cd DevOpsToolbox
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install the pre-push hook:
   ```bash
   ./scripts/install-hooks.sh
   ```

## Development Workflow

### 1. Create a Branch

Create a branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code patterns in the project
- Add tests for new functionality
- Update documentation if needed

### 3. Code Quality

Before committing, ensure your code passes all checks:

```bash
# Run linting
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .

# Run tests
pytest

# Run tests with coverage
pytest --cov=devopstoolbox
```

### 4. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git commit -m "Add deployment list command with replica status"
```

Commit message guidelines:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues when applicable ("Fix #123")

### 5. Push and Create a Pull Request

```bash
git push origin your-branch-name
```

Then create a Pull Request on GitHub. Fill out the PR template completely.

## Code Style

### Python Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names

### CLI Commands

When adding new CLI commands:

1. Follow the existing pattern in `src/devopstoolbox/k8s/`
2. Use Rich tables for output formatting
3. Support `--namespace` and `--all-namespaces` flags where applicable
4. Add comprehensive help text to commands

Example structure:
```python
@app.command()
def list(
    namespace: str = typer.Option("default", "--namespace", "-n", help="Kubernetes namespace"),
    all_namespaces: bool = typer.Option(False, "--all-namespaces", "-A", help="List across all namespaces"),
):
    """List resources with status information."""
    # Implementation
```

### Testing

- Write tests for all new functionality
- Place tests in the `tests/` directory
- Follow the existing test patterns
- Mock Kubernetes client calls

Example test structure:
```python
class TestYourCommand:
    def test_command_default_namespace(self, mock_k8s):
        # Test implementation
        pass

    def test_command_all_namespaces(self, mock_k8s):
        # Test implementation
        pass
```

## Adding New Features

### Adding a New K8s Command

1. Create a new file in `src/devopstoolbox/k8s/` or add to an existing one
2. Create a Typer app and register it in `main.py`
3. Add tests in `tests/`
4. Update README.md with usage examples
5. Update the roadmap if applicable

### Project Structure

```
DevOpsToolbox/
├── src/devopstoolbox/
│   ├── main.py           # CLI entry point
│   └── k8s/              # Kubernetes commands
├── tests/                # Test suite
├── scripts/              # Utility scripts
└── docs/                 # Documentation (if needed)
```

## Reporting Issues

### Bug Reports

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs

### Feature Requests

Use the feature request template and include:
- Description of the feature
- Use case and problem it solves
- Proposed command syntax
- Acceptance criteria

## Pull Request Guidelines

- Fill out the PR template completely
- Link related issues
- Ensure all checks pass
- Keep PRs focused on a single change
- Respond to review feedback promptly

## Getting Help

- Open an issue for questions
- Check existing issues before creating new ones
- Be respectful and constructive in discussions

## License

By contributing to DevOpsToolbox, you agree that your contributions will be licensed under the same license as the project.
