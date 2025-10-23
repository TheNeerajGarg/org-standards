# Organization-wide Claude Documentation

**This is the source of truth for organization-wide Claude documentation.**

## Purpose

This directory contains documentation that applies to ALL repositories in the organization:
- StyleGuru (StyleGuru product)
- syra (dev tools platform)
- syra-playground (experiments)

## Documentation Files

### Process & Workflow
- **workflow.md** - BRD→PRD→ERD→Execution Plan process
- **planning-checklist.md** - Problem validation, outline-first approach
- **execution-plan-standards.md** - Granular task breakdown, time estimates

### Code Quality
- **quality-standards.md** - Code quality, DoD checklist, root cause fixes
- **testing.md** - Test strategy (70/20/10), mocking guidelines
- **technical.md** - Import architecture, path resolution

### Documentation Standards
- **brd-prd-erd-standards.md** - Document anti-patterns, 40-item ERD checklist

### AI & Context
- **introspection.md** - AI learning protocols, auto-detection of corrections
- **memory-sync-workflow.md** - How Claude memory syncs with Git
- **context-management.md** - When/how to update context

### Organization
- **org-context.md** - Development model, repository map, global philosophy
- **schema-standards.md** - JSON-LD architecture, A2A protocol
- **grandfather-policy.md** - How to handle pre-existing issues

## Distribution

These docs are distributed via **Git submodules** with branch-based versioning:
- **stable** branch → Production repos (StyleGuru)
- **main** branch → Development repos (Syra, Syra-playground)

### How Repos Access These Docs

Repos include org-standards as a Git submodule:
```bash
# In StyleGuru (uses stable)
git submodule add -b stable https://github.com/TheNeerajGarg/org-standards.git org-standards

# In syra (uses main/development)
git submodule add -b main https://github.com/TheNeerajGarg/org-standards.git org-standards
```

Docs are then available at `org-standards/.claude/` in each repo.

## Workflow

### Updating Documentation

1. **Edit standards** (org-standards repo):
   ```bash
   cd ~/NeerajDev/org-standards
   git checkout main  # Always edit on main
   vim .claude/quality-standards.md
   git add . && git commit -m "docs: update quality standards"
   git push origin main
   ```

2. **Test in Syra** (uses main automatically):
   ```bash
   cd ~/NeerajDev/syra
   git submodule update --remote org-standards  # Pull latest main
   # Use for 1-2 weeks, verify no issues
   ```

3. **Promote to stable** (when ready):
   ```bash
   cd ~/NeerajDev/org-standards
   git checkout stable
   git merge main --no-ff -m "promote: quality standards updates"
   git tag v1.x.x
   git push origin stable --tags
   ```

4. **StyleGuru adopts** (when ready):
   ```bash
   cd ~/NeerajDev/StyleGuru
   git submodule update --remote org-standards  # Pull latest stable
   git commit -am "chore: update org-standards to v1.x.x"
   ```

## Why Git Submodules?

### Advantages
- ✅ **Versioning built-in**: stable vs main branches, git tags
- ✅ **Standard Git tooling**: No custom scripts
- ✅ **Explicit control**: Repos update when ready (not auto)
- ✅ **Branch tracking**: Syra follows main, StyleGuru follows stable
- ✅ **Works everywhere**: Local, CI, containers
- ✅ **Single source**: org-standards repo is the truth

### What About Alternatives?

**Symlinks**: Don't work in Git, Windows, containers
**Relative paths**: Fragile directory structure dependencies
**Package (npm/pip)**: Over-engineered for markdown files
**Synced copies**: Manual sync, drift risk, 4 commits per change

Git submodules leverage existing version control for versioning.

## Repo-Specific Documentation

Each repo also has its own `.claude/` directory for repo-specific docs:

- **StyleGuru/.claude/**
  - `architecture.md` - StyleGuru architecture
  - `CURRENT_STATE.md` - Deployment state
  - instance configs, worktree guides, etc.

- **syra/.claude/**
  - `INTROSPECTION-SETUP.md` - Introspection system setup
  - `PROMOTION-PROCESS.md` - How to promote changes
  - Syra-specific agents

## Questions?

See the main org-standards README or ask in team chat.
