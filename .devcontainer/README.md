# NeerajDev Unified Workspace - Devcontainer

This directory contains the **organization standard** devcontainer configuration for the NeerajDev multi-repository workspace.

## Purpose

Provides a unified development environment where all repositories (fashion-extract, syra, syra-playground, org-standards) are accessible within a single container.

## Directory Structure

```
org-standards/
├── .devcontainer/
│   ├── devcontainer.json              # Main devcontainer config (git-tracked)
│   ├── neerajdev.code-workspace.template  # VSCode workspace template
│   └── README.md                      # This file
├── devcontainer/
│   └── Dockerfile                     # Shared Dockerfile
└── scripts/
    └── setup-neerajdev-workspace.sh   # One-time setup script
```

## Initial Setup (New Developers)

### Prerequisites
- Docker Desktop installed and running
- VSCode with Dev Containers extension
- All repos cloned to `~/NeerajDev/`:
  ```
  ~/NeerajDev/
  ├── fashion-extract/
  ├── syra/
  ├── syra-playground/
  └── org-standards/    # This repo
  ```

### Setup Steps

1. **Run the setup script:**
   ```bash
   cd ~/NeerajDev/org-standards
   ./scripts/setup-neerajdev-workspace.sh
   ```

   This script:
   - Creates symlink: `NeerajDev/.devcontainer` → `org-standards/.devcontainer`
   - Copies workspace file: `neerajdev.code-workspace.template` → `neerajdev.code-workspace`
   - Verifies all repos are present

2. **Open the workspace in VSCode:**
   ```bash
   code ~/NeerajDev/neerajdev.code-workspace
   ```

3. **Reopen in Container:**
   - VSCode will prompt: "Reopen in Container"
   - Click it and wait for container build (~2-5 minutes first time)
   - Dependencies for all projects will be installed automatically

4. **Start developing:**
   - All 4 repos visible in sidebar
   - Unified Python environment
   - Cross-repo imports work
   - Git operations work in all repos

## How Automatic Sync Works

### The Symlink Strategy

```
~/NeerajDev/
├── .devcontainer/  → symlink to org-standards/.devcontainer/
└── org-standards/
    └── .devcontainer/  ← actual files (git-tracked)
        └── devcontainer.json
```

**When org-standards updates:**
```bash
cd ~/NeerajDev/org-standards
git pull  # Updates .devcontainer/devcontainer.json

# Your NeerajDev/.devcontainer automatically updates (it's a symlink!)
# Next time you rebuild container, you get the latest config
```

**Zero manual actions required!** Everyone stays in sync automatically.

## Container Features

### Repositories Accessible
- `/workspace/fashion-extract` - StyleGuru product
- `/workspace/syra` - Dev tools platform
- `/workspace/syra-playground` - Experiments
- `/workspace/org-standards` - Shared standards

### Environment Variables
- `ANTHROPIC_API_KEY` - Passed from host
- `OPENAI_API_KEY` - Passed from host
- `GOOGLE_API_KEY` - Passed from host
- `HONEYCOMB_API_KEY` - Passed from host
- `BOT_GITHUB_TOKEN` - Passed from host
- `NEERAJ_DEV=/workspace` - Set in container

### Ports Forwarded
- 3000 - Frontend/viewer
- 8000 - API services
- 8080 - Alternative services

### VSCode Extensions (Auto-installed)
- Python (Pylance, Black, isort, Ruff, MyPy)
- GitLens
- Error Lens
- Claude Code
- Continue

## Updating the Devcontainer (Maintainers)

### Making Changes

1. **Edit the config:**
   ```bash
   cd ~/NeerajDev/org-standards
   # Edit .devcontainer/devcontainer.json
   ```

2. **Test your changes:**
   - Rebuild container: `Cmd+Shift+P` → "Dev Containers: Rebuild Container"
   - Verify everything works

3. **Commit and push:**
   ```bash
   git add .devcontainer/
   git commit -m "feat: update devcontainer config - <what changed>"
   git push
   ```

4. **Notify team:**
   - Everyone will get the update on next `git pull` in org-standards
   - They may need to rebuild container to apply changes

### What to Update
- **devcontainer.json**: Extensions, settings, environment variables, ports
- **Dockerfile** (in devcontainer/): Base image, system dependencies
- **neerajdev.code-workspace.template**: Workspace folders, settings

## Troubleshooting

### Symlink Not Working
```bash
# Verify symlink exists
ls -la ~/NeerajDev/.devcontainer
# Should show: .devcontainer -> org-standards/.devcontainer

# Re-run setup script if missing
cd ~/NeerajDev/org-standards
./scripts/setup-neerajdev-workspace.sh
```

### Container Won't Start
```bash
# Check Docker is running
docker ps

# Rebuild from scratch
# In VSCode: Cmd+Shift+P → "Dev Containers: Rebuild Container Without Cache"
```

### Dependencies Not Installing
```bash
# Inside container, manually install:
cd /workspace/fashion-extract
pip install -e .[test,dev]

cd /workspace/syra
pip install -e .[test,dev]
```

### Git Operations Failing
```bash
# Inside container:
git config --global --add safe.directory /workspace/<repo-name>
```

### Outdated Devcontainer Config
```bash
# Update org-standards
cd ~/NeerajDev/org-standards
git pull

# Rebuild container to apply changes
# In VSCode: Cmd+Shift+P → "Dev Containers: Rebuild Container"
```

## Windows Support

The setup script supports Windows Subsystem for Linux (WSL2). Symlinks work in WSL2 but may not work in native Windows. Windows users should:

1. Use WSL2 for development
2. Clone repos to WSL filesystem (not /mnt/c/)
3. Run setup script from WSL

## GitHub Codespaces

The devcontainer also works in GitHub Codespaces:

1. Fork/clone repos to GitHub
2. Open workspace in Codespaces
3. Codespaces automatically uses `NeerajDev/.devcontainer` (via symlink)
4. Same environment as local development

## Benefits

✅ **Automatic sync** - Updates propagate via git pull
✅ **Zero manual actions** - Symlink handles everything
✅ **Single source of truth** - Config lives in org-standards
✅ **Version controlled** - All changes tracked in git
✅ **Team consistency** - Everyone uses identical environment
✅ **Cross-repo access** - All projects accessible
✅ **Unified dependencies** - Single Python environment

## Questions?

See the main org-standards documentation or ask in team chat.
