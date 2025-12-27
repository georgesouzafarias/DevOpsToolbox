# DevOpsToolbox

[![CI](https://github.com/georgesouzafarias/DevOpsToolbox/actions/workflows/ci.yml/badge.svg)](https://github.com/georgesouzafarias/DevOpsToolbox/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/georgesouzafarias/DevOpsToolbox/branch/main/graph/badge.svg)](https://codecov.io/gh/georgesouzafarias/DevOpsToolbox)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/georgesouzafarias/DevOpsToolbox)](LICENSE)

A Python-based CLI toolkit for automating daily DevOps operations.

## Features

- **Kubernetes Management**: Manage pods, services, and certificates from the command line
- **Human-readable Output**: Formatted tables with Rich for clear visualization
- **Metrics Support**: View CPU and memory usage for pods (requires Metrics Server)
- **Certificate Management**: List and monitor cert-manager certificates

## Requirements

- Python 3.9+
- Access to a Kubernetes cluster (kubeconfig configured)
- Metrics Server (optional, for pod metrics)
- cert-manager (optional, for certificate management)

## Installation

```bash
# Clone the repository
git clone https://github.com/georgesouzafarias/DevOpsToolbox.git
cd DevOpsToolbox

# Install in development mode
pip install -e .
```

## Usage

### General Commands

```bash
# Show version
devopstoolbox version

# Show help
devopstoolbox --help
```

### Short Aliases

All Kubernetes commands support short aliases for common options, matching kubectl conventions:

| Long Form          | Short | Description                    |
| ------------------ | ----- | ------------------------------ |
| `--namespace`      | `-n`  | Specify the namespace          |
| `--all-namespaces` | `-A`  | List resources across all namespaces |

### Pods Management

```bash
# List all pods in default namespace
devopstoolbox k8s pods list

# List all pods in a specific namespace
devopstoolbox k8s pods list -n monitoring

# List all pods across all namespaces
devopstoolbox k8s pods list -A

# List unhealthy pods (not Running or Succeeded)
devopstoolbox k8s pods unhealthy -A

# Show pod metrics (CPU and memory usage)
devopstoolbox k8s pods metrics -n default
```

### Services Management

```bash
# List services in default namespace
devopstoolbox k8s services list

# List services in a specific namespace
devopstoolbox k8s services list -n kube-system

# List all services across all namespaces
devopstoolbox k8s services list -A
```

### Certificates Management

```bash
# List certificates in default namespace
devopstoolbox k8s certificates list

# List certificates in a specific namespace
devopstoolbox k8s certificates list -n cert-manager

# List certificates that are not ready
devopstoolbox k8s certificates not-ready -n default
```

## Command Reference

| Command                                    | Description                                |
| ------------------------------------------ | ------------------------------------------ |
| `devopstoolbox version`                    | Show tool version                          |
| `devopstoolbox k8s pods list`              | List pods with status and restart count    |
| `devopstoolbox k8s pods metrics`           | Show CPU and memory usage per container    |
| `devopstoolbox k8s pods unhealthy`         | List pods not in Running/Succeeded state   |
| `devopstoolbox k8s services list`          | List services with type and traffic policy |
| `devopstoolbox k8s certificates list`      | List cert-manager certificates             |
| `devopstoolbox k8s certificates not-ready` | List certificates not in Ready state       |

## Dependencies

- boto3
- kubernetes
- typer
- rich

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install the pre-push git hook
./scripts/install-hooks.sh
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=devopstoolbox --cov-report=html

# Run specific test file
pytest tests/test_pods.py

# Run specific test class
pytest tests/test_pods.py::TestPodsListCommand

# Run specific test
pytest tests/test_pods.py::TestPodsListCommand::test_list_pods_default_namespace
```

### Code Quality

The project uses Ruff for linting and formatting, and pytest for testing.

```bash
# Check for linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

All tests must pass before pushing code.

### Git Hooks

A pre-push hook automatically runs tests before each push to ensure code quality:

```bash
# Install the hook (one-time setup)
./scripts/install-hooks.sh

# The hook will run automatically on git push
# If tests fail, the push will be rejected
```

To bypass the hook (not recommended):

```bash
git push --no-verify
```

## License

See LICENSE file for details.

## Author

George Farias (georgesouzafarias@gmail.com)
