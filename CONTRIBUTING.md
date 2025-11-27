# Contributing to Peircean Abduction

Thank you for your interest in contributing to Peircean Abduction! This document provides guidelines for contributing to the project.

## Ways to Contribute

- 🐛 **Bug Reports**: Open an issue describing the bug
- 💡 **Feature Requests**: Open an issue describing the feature
- 📝 **Documentation**: Improve docs, add examples, fix typos
- 🧪 **Tests**: Add test coverage, fix failing tests
- 🔧 **Code**: Fix bugs, implement features, improve performance

## Development Setup

### Prerequisites

- Python 3.10+
- `uv` (recommended) or `pip`

### Setup

```bash
# Clone the repository
git clone https://github.com/Hmbown/peircean-abduction.git
cd peircean-abduction

# Create virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy peircean

# Run linting
ruff check peircean
```

## Code Style

We use:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing

### Guidelines

1. **Type Hints**: All public functions should have type hints
2. **Docstrings**: Use Google-style docstrings
3. **Tests**: Add tests for new functionality
4. **Commits**: Use conventional commit messages

### Example

```python
def analyze_observation(
    observation: str,
    context: dict[str, Any] | None = None,
) -> Observation:
    """
    Analyze an observation to determine surprise level.
    
    Args:
        observation: The fact or phenomenon to analyze
        context: Optional background information
        
    Returns:
        Observation object with surprise classification
        
    Raises:
        ValueError: If observation is empty
    """
    if not observation:
        raise ValueError("Observation cannot be empty")
    ...
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Make** your changes
4. **Test** your changes: `pytest`
5. **Commit** with a descriptive message
6. **Push** to your fork
7. **Open** a Pull Request

### PR Checklist

- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Type hints added
- [ ] Documentation updated
- [ ] No linting errors

## Issues

### Bug Reports

Include:
- Python version
- `peircean-abduction` version
- Minimal reproduction case
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed solution
- Alternatives considered

## Questions?

Open a discussion or reach out to the maintainers.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, inclusive, and constructive. We're all here to learn and build something useful.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
