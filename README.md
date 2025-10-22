# Organization Standards

**Shared configuration and standards for all Neeraj Garg projects**

---

## Purpose

This repository contains battle-tested configurations, coding standards, and workflows that are shared across all projects in the organization.

**Don't copy. Reference.**

---

## What's Included

### Python Standards
- Code formatting and linting (Ruff - replaces black, isort, flake8)
- Type checking (mypy)
- Testing (pytest with coverage)
- Pre-commit hooks

### CI/Dev Container
- **NEW (2025-10-22)**: Standard devcontainer for dev/CI parity
- Ubuntu 24.04 base image
- Python 3.11 + all dev tools pre-installed
- Ensures "works locally" = "works in CI"

### GitHub Workflows
- PR validation
- CI/CD templates
- Branch protection configs

### Logging & Observability
- Structured logging (structlog)
- OpenTelemetry setup

### Configuration Management
- Dynaconf patterns
- Environment configs

---

## Usage

### For New Projects

```bash
# Copy standard configs
curl -o pyproject.toml \
  https://raw.githubusercontent.com/neerajgarg/org-standards/main/python/pyproject.toml

curl -o .github/workflows/pr-validation.yml \
  https://raw.githubusercontent.com/neerajgarg/org-standards/main/github/workflows/python-pr-validation.yml
```

### For Existing Projects

Run sync script:
```bash
./scripts/sync-org-standards.sh
```

---

## Projects Using These Standards

- [fashion-extract](https://github.com/neerajgarg/fashion-extract) - StyleGuru product
- [syra](https://github.com/neerajgarg/syra) - AI development platform
- [syra-playground](https://github.com/neerajgarg/syra-playground) - Syra testing ground

---

## Structure

```
org-standards/
├── devcontainer/                # NEW: Standard CI/Dev container
│   ├── Dockerfile               # Ubuntu 24.04 + Python 3.11 + tools
│   ├── devcontainer.json        # VS Code devcontainer config
│   └── README.md                # Dev/CI parity guide
│
├── python/
│   ├── pyproject.toml           # Ruff, mypy, pytest config
│   ├── .pre-commit-config.yaml  # Pre-commit hooks
│   ├── requirements-dev.txt     # Dev dependencies
│   └── README.md                # Usage guide
│
├── github/
│   ├── workflows/
│   │   ├── python-pr-validation.yml
│   │   └── python-ci.yml
│   ├── CODEOWNERS.template
│   └── PULL_REQUEST_TEMPLATE.md
│
├── logging/
│   ├── structlog_setup.py
│   └── opentelemetry_setup.py
│
├── config/
│   ├── default.toml.template
│   └── dynaconf_setup.md
│
└── scripts/
    └── sync-to-project.sh      # Sync script for projects
```

---

## Philosophy

**Standards should be**:
- ✅ Battle-tested (proven in real projects)
- ✅ Minimal (only what's needed)
- ✅ Documented (with reasoning)
- ✅ Evolving (improved based on learnings)

**Not**:
- ❌ Dogmatic (rules for rules' sake)
- ❌ Comprehensive (covering every edge case)
- ❌ Static (never updated)

---

## Contributing

Standards come from real project needs. When you discover a better pattern:

1. Validate in a real project first
2. Document the improvement
3. PR to org-standards
4. Update projects gradually

**Don't standardize theoretical best practices. Only proven ones.**

---

## Versioning

We use simple date-based versioning:
- `2025-10-10` - Initial extraction from fashion-extract, migrated to Ruff

Projects reference specific versions in comments.

---

## Recent Changes

### 2025-10-22: Standard CI/Dev Container
- **NEW**: Standard devcontainer for all projects
- Ensures perfect dev/CI parity (no more "works on my machine")
- Based on ubuntu-24.04 + Python 3.11
- All tools pre-installed: ruff, mypy, pytest, gh CLI, Claude CLI
- See [devcontainer/README.md](devcontainer/README.md) for usage

### 2025-10-10: Migration to Ruff
- **BREAKING**: Replaced black + isort + flake8 with Ruff
- Update your projects:
  ```bash
  pip uninstall black isort flake8
  pip install ruff
  ruff format .  # replaces: black .
  ruff check . --fix  # replaces: isort . && flake8
  ```
- See [python/README.md](python/README.md) for migration guide
