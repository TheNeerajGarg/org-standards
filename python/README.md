# Python Organization Standards

Shared Python configuration for all projects in the organization.

## What's Included

- **pyproject.toml**: Project configuration with Ruff linting/formatting
- **.pre-commit-config.yaml**: Pre-commit hooks for code quality
- **requirements-dev.txt**: Standard development dependencies

## Technology Stack

- **Ruff**: Modern all-in-one linter and formatter (replaces black, flake8, isort, pylint)
- **pytest**: Testing framework with coverage
- **mypy**: Type checking
- **pre-commit**: Git hook management

## Usage in Your Project

### 1. Copy Configuration Files

```bash
# From your project root
cp /path/to/org-standards/python/pyproject.toml .
cp /path/to/org-standards/python/.pre-commit-config.yaml .
```

### 2. Customize pyproject.toml

Edit the `[project]` section with your project details:

```toml
[project]
name = "your-project-name"  # ⚠️ CHANGE THIS
version = "0.1.0"
description = "Your project description"  # ⚠️ CHANGE THIS
```

If needed, update `[tool.ruff.lint.isort]` with your package name:

```toml
[tool.ruff.lint.isort]
known-first-party = ["your_package_name"]  # ⚠️ CHANGE THIS
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

### 5. Run Quality Checks

```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check . --fix

# Type check
mypy src/

# Run tests
pytest

# Run all pre-commit hooks
pre-commit run --all-files
```

## Configuration Philosophy

### Ruff Settings

- **Line length**: 100 characters
- **Python version**: 3.11+
- **Selected rules**:
  - E/W: pycodestyle errors and warnings
  - F: pyflakes
  - I: isort (import sorting)
  - N: pep8-naming
  - UP: pyupgrade
  - B: flake8-bugbear
  - C4: flake8-comprehensions

### Test Configuration

- Tests in `tests/` directory
- 80% minimum coverage (configure in your custom config)
- Strict markers and config enforcement

### Type Checking

- Gradual typing approach (not strict)
- Third-party libraries can have missing type hints
- Test code has relaxed type requirements

## Shared Dependencies

All projects include:

**Production**:
- dynaconf (configuration management)
- click (CLI building)
- structlog + python-json-logger (structured logging)
- OpenTelemetry (observability)

**Development**:
- pytest + pytest-cov + pytest-mock
- ruff (linting and formatting)
- mypy (type checking)
- pre-commit (git hooks)

## Adding Project-Specific Hooks

Create `.pre-commit-config-custom.yaml` in your project with additional hooks:

```yaml
repos:
  - repo: local
    hooks:
      - id: my-custom-check
        name: My custom validation
        entry: python scripts/my_check.py
        language: python
        pass_filenames: false
```

Then merge with org standards in your workflow.

## Maintenance

This is the **single source of truth** for Python standards.

Updates to these files affect all projects, so:
1. Test changes thoroughly
2. Document breaking changes
3. Communicate updates to all teams
4. Version updates in commit messages

## Questions?

See the main [org-standards README](../../README.md) for more information.
