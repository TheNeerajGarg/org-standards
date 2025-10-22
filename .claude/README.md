# Organization-wide Claude Documentation

**This is the source of truth for organization-wide Claude documentation.**

## Purpose

This directory contains documentation that applies to ALL repositories in the organization:
- fashion-extract (StyleGuru product)
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

These docs are **automatically synced** to all repos using:
```bash
./scripts/sync-claude-docs.sh
```

### Synced Copies (Git-tracked)
- `fashion-extract/.claude/` - Copies for StyleGuru bots/Claude
- `syra/.claude/` - Copies for Syra bots/Claude
- `syra-playground/.claude/` - Copies for playground bots/Claude

## Workflow

### Updating Documentation

1. **Edit here** (org-standards/.claude/):
   ```bash
   cd ~/NeerajDev/org-standards/.claude
   vim quality-standards.md  # Edit the source
   ```

2. **Sync to all repos**:
   ```bash
   cd ~/NeerajDev/org-standards
   ./scripts/sync-claude-docs.sh
   ```

3. **Commit everywhere**:
   ```bash
   # Commit source in org-standards
   cd ~/NeerajDev/org-standards
   git add .claude/
   git commit -m "docs: update quality standards"
   git push

   # Commit synced copies in each repo
   cd ~/NeerajDev/fashion-extract
   git add .claude/quality-standards.md
   git commit -m "docs: sync org-standards/.claude/ updates"
   git push

   # Repeat for syra, syra-playground
   ```

## Why This Approach?

### Why Not Symlinks?
- ❌ Symlinks don't work well in Git (tracked as symlinks, not content)
- ❌ Symlinks don't work on Windows
- ❌ Bots in containers can't traverse symlinks across repos

### Why Not Relative Paths?
- ❌ Bots run in individual repos, can't access `../org-standards/`
- ❌ Container mounts may not include all repos
- ❌ GitHub Actions checkouts are single-repo

### Why Synced Copies?
- ✅ Each repo has self-contained docs (bots work)
- ✅ Git tracks actual content (not pointers)
- ✅ Works in all environments (Mac, Windows, containers, CI)
- ✅ org-standards is single source of truth
- ✅ One command to sync everything

## Repo-Specific Documentation

Each repo also has its own `.claude/` directory for repo-specific docs:

- **fashion-extract/.claude/**
  - `architecture.md` - StyleGuru architecture
  - `CURRENT_STATE.md` - Deployment state
  - instance configs, worktree guides, etc.

- **syra/.claude/**
  - `INTROSPECTION-SETUP.md` - Introspection system setup
  - `PROMOTION-PROCESS.md` - How to promote changes
  - Syra-specific agents

## Questions?

See the main org-standards README or ask in team chat.
