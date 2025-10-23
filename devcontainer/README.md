# Standard CI/Dev Container

**Version**: 2025-10-22
**Purpose**: Ensure perfect parity between local development and CI/CD environments

---

## Why This Matters

**Problem**: "Works on my machine" syndrome
- Local dev uses different OS/packages than CI
- CI failures that don't reproduce locally
- Time wasted debugging environment differences

**Solution**: Use identical container for dev and CI
- Local development → VS Code devcontainer
- CI/CD → GitHub Actions on ubuntu-24.04
- Production builds → Same base image

**Result**: What works locally WILL work in CI (and vice versa)

---

## What's Included

### Base Image
- `mcr.microsoft.com/devcontainers/base:ubuntu-24.04`
- Matches GitHub Actions `runs-on: ubuntu-24.04`

### Languages & Runtimes
- Python 3.11 (org-standards version)
- Node.js 18 (for Claude CLI and bot workflows)

### System Dependencies
- `libgl1`, `libglib2.0-0` - Image processing (OpenCV, Pillow)
- `git`, `curl`, `wget`, `vim` - Development tools

### Python Tools (Pre-installed)
- `ruff` - Linting and formatting (via pyproject.toml)
- `mypy` - Type checking (via pyproject.toml)
- `pytest` - Testing (via pyproject.toml)
- `pre-commit` - Git hooks
- `build`, `twine` - Package building
- `bandit`, `safety` - Security scanning

### GitHub & AI Tools
- `gh` - GitHub CLI (for bot workflows)
- `@anthropic-ai/claude-code` - Claude CLI (for AI workflows)

---

## Usage

### For New Projects (Simplest - Recommended)

**No need to copy Dockerfile!** Just reference it from org-standards:

1. **Create .devcontainer/devcontainer.json** in your project:
   ```json
   {
     "name": "YourProject - CI Container",
     "build": {
       "dockerfile": "../../org-standards/devcontainer/Dockerfile",
       "context": ".."
     },
     "workspaceFolder": "/workspace/yourproject",
     "remoteUser": "vscode",

     // Install project dependencies after container is created
     "postCreateCommand": "pip install -e .[test,dev] --break-system-packages",

     "postStartCommand": "git config --global --add safe.directory /workspace/yourproject && echo '✅ CI Container ready!'"
   }
   ```

2. **That's it!** No Dockerfile to maintain in your project.

**Benefits**:
- ✅ Single source of truth (org-standards Dockerfile)
- ✅ Automatic updates (all projects benefit when org-standards updates)
- ✅ No duplication
- ✅ Simpler maintenance

3. **Update CI workflow** to match:
   ```yaml
   # In .github/workflows/ci.yml
   jobs:
     test:
       runs-on: ubuntu-24.04  # MUST MATCH devcontainer base image
       steps:
         - uses: actions/setup-python@v4
           with:
             python-version: "3.11"  # MUST MATCH devcontainer Python version
   ```

4. **Open in VS Code**:
   - Install "Dev Containers" extension
   - Command Palette → "Dev Containers: Reopen in Container"

### For Existing Projects

1. **Check if CI already matches**:
   - CI uses `ubuntu-24.04`? ✅
   - CI uses Python 3.11? ✅
   - CI installs same system deps? ✅

2. **If yes**: Just add devcontainer (no CI changes needed)

3. **If no**: Update CI first, then add devcontainer

---

## Project-Specific Customizations

### Syra (AI Development Platform)
```json
{
  "name": "Syra - CI Container",
  "workspaceFolder": "/workspace/syra",
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "BOT_GITHUB_TOKEN": "${localEnv:BOT_GITHUB_TOKEN}"
  }
}
```

### StyleGuru/StyleGuru (Fashion AI)
```json
{
  "name": "Fashion Extract - CI Container",
  "workspaceFolder": "/workspace/StyleGuru",
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}",
    "GOOGLE_API_KEY": "${localEnv:GOOGLE_API_KEY}",
    "HONEYCOMB_API_KEY": "${localEnv:HONEYCOMB_API_KEY}"
  },
  "postStartCommand": "git config --global --add safe.directory /workspace/StyleGuru && . ~/.config/StyleGuru/tokens.env"
}
```

---

## Verification

### Test Dev/CI Parity

1. **In devcontainer** (local):
   ```bash
   python --version  # Should be 3.11
   ruff --version
   pytest --version
   gh --version
   ```

2. **In CI** (GitHub Actions):
   ```yaml
   - name: Verify environment parity
     run: |
       python --version  # Should match devcontainer
       ruff --version
       pytest --version
       gh --version
   ```

3. **Compare outputs** - should be identical!

---

## Maintenance

### When to Update

- ✅ Python version changes (e.g., 3.11 → 3.12)
- ✅ System dependencies change (new libs needed)
- ✅ Tool versions change (major version bumps)

### How to Update

1. Update `Dockerfile` in org-standards
2. Test in one project first
3. Roll out to all projects gradually
4. Document breaking changes

### Version History

- **2025-10-22**: Initial standard container
  - Base: ubuntu-24.04
  - Python: 3.11
  - Tools: Ruff, MyPy, pytest, gh CLI, Claude CLI

---

## Troubleshooting

### "Container fails to build"

**Check**:
- Docker daemon running?
- Enough disk space?
- Network connectivity (for apt-get, pip, npm)?

### "Tests pass locally but fail in CI"

**This shouldn't happen with devcontainer!**

If it does:
1. Verify devcontainer Dockerfile matches CI setup
2. Check for non-deterministic tests (time, random, network)
3. Check for local files not in git (.env, caches)

### "Container is slow to build"

**Normal on first build** (downloads base image, installs packages)

**Speed up**:
- Docker uses layer caching (subsequent builds faster)
- Pre-build and push to Docker Hub (for CI)
- Use GitHub Actions cache (for CI)

---

## Related Documents

- [org-standards/python/README.md](../python/README.md) - Python standards
- [org-standards/github/workflows/](../github/workflows/) - CI/CD templates
- [org-standards/CONFIG_PHILOSOPHY.md](../CONFIG_PHILOSOPHY.md) - Configuration approach

---

## Philosophy

**Dev/CI parity is non-negotiable**

- ✅ Same OS, same packages, same tools
- ✅ "Works locally" = "Works in CI"
- ✅ No surprises, no wasted time

**Container = Single Source of Truth**

- ✅ Devcontainer defines environment
- ✅ CI matches devcontainer
- ✅ Production builds from same base

**Keep it minimal**

- ✅ Only install what's needed
- ✅ Document why each tool is included
- ✅ Remove unused dependencies
