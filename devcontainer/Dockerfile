# Standard CI/Dev Container for All Projects
# Version: 2025-10-22
#
# CRITICAL: This Dockerfile defines the standard dev/CI environment for all projects.
# It ensures perfect parity between:
# - Local development (VS Code devcontainer)
# - CI/CD (GitHub Actions)
# - Production builds
#
# MUST MATCH: GitHub Actions runs-on: ubuntu-24.04

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install Python 3.11 (matching org-standards Python version)
# Reference: org-standards/python/README.md
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install system dependencies
# CRITICAL: These MUST match packages in .github/workflows/ci.yml
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # System dependencies for image processing (OpenCV, Pillow, etc.)
    libgl1 \
    libglib2.0-0 \
    # Development tools
    git \
    curl \
    wget \
    vim \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (gh) - used by bots for PR creation and GitHub operations
# Reference: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
# Note: pip 24.0 (system version) is sufficient - no upgrade needed
# GitHub Actions uses similar version

# Install Python development tools (core tools used by all projects)
# Note: ruff, mypy, pytest, pytest-cov are project-specific and installed via pip install -e .[dev]
RUN pip install --break-system-packages \
    pre-commit \
    build \
    twine \
    bandit \
    safety

# Install Node.js 18 (matching GitHub Actions setup-node@v4)
# This is needed for bot workflows that use Claude CLI
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Claude CLI globally (for local development and bot workflows)
# Note: GitHub Actions installs this on-demand, but we pre-install for convenience
RUN npm install -g @anthropic-ai/claude-code && \
    npm cache clean --force

# Set working directory (will be overridden by devcontainer.json)
WORKDIR /workspace

# Set up git for the container user
USER vscode
RUN git config --global user.name "Dev Container" \
    && git config --global user.email "dev@container.local"

# Default command
CMD ["/bin/bash"]
