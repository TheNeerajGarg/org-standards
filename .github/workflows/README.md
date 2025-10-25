# org-standards Workflows

This directory contains GitHub Actions workflows for org-standards automation.

## Workflows

### 1. `propagate-to-repos.yml` - Automatic Submodule Updates

**Purpose**: Automatically create PRs in all dependent repos when org-standards is updated.

**When it runs**:
- Automatically on every push to `main` branch
- Manually via "Run workflow" button

**What it does**:
1. Detects when org-standards `main` branch is updated
2. For each dependent repo (syra, StyleGuru, syra-playground):
   - Checks out the repo
   - Updates org-standards submodule to latest main
   - Creates a PR if changes exist
   - PR includes org-standards commit message and review checklist

**How to add a new repo**:
```yaml
# In propagate-to-repos.yml, add to matrix:
strategy:
  matrix:
    repo:
      - StyleGuru/syra
      - StyleGuru/your-new-repo  # Add here
```

**Manual trigger**:
```bash
# Update specific repos only
gh workflow run propagate-to-repos.yml -f repos="StyleGuru/syra"

# Update all repos (default)
gh workflow run propagate-to-repos.yml
```

**Requirements**:
- `BOT_GITHUB_TOKEN` secret must be set in org-standards repo
  - Token needs `repo` and `workflow` permissions
  - Token should be a PAT (Personal Access Token) or GitHub App token

**Troubleshooting**:
- If PR creation fails: Check BOT_GITHUB_TOKEN has correct permissions
- If no PR created: No changes to propagate (submodule already up to date)
- To disable for a repo: Remove from matrix or add to skip list

---

### 2. `ci.yml` - Continuous Integration

**Purpose**: Run tests and quality checks on org-standards code.

**When it runs**: On every push and PR

---

### 3. `reusable-quality-gates.yml` - Reusable Quality Gates

**Purpose**: Shared quality gate workflow that other repos can use.

**How to use in other repos**:
```yaml
# In .github/workflows/quality-gates.yml
jobs:
  quality-gates:
    uses: TheNeerajGarg/org-standards/.github/workflows/reusable-quality-gates.yml@main
```

---

### 4. `validate-config.yml` - Configuration Validation

**Purpose**: Validate quality-gates.yaml changes before merge.

**When it runs**: On PRs that modify `config/quality-gates.yaml`

---

## Secrets Required

| Secret | Purpose | Scope |
|--------|---------|-------|
| `BOT_GITHUB_TOKEN` | Create PRs in dependent repos | org-standards repo |

**Setting up BOT_GITHUB_TOKEN**:
1. Create a GitHub PAT with `repo` and `workflow` scopes
2. Add to org-standards repo secrets: Settings → Secrets → Actions → New repository secret
3. Name: `BOT_GITHUB_TOKEN`, Value: `ghp_...`

---

## Workflow Permissions

All workflows use `BOT_GITHUB_TOKEN` for cross-repo operations to avoid permission issues.

Default `GITHUB_TOKEN` only has permissions within the current repo, so we use a dedicated bot token for propagation.

---

## Monitoring

**View workflow runs**: https://github.com/TheNeerajGarg/org-standards/actions

**Check propagation status**:
```bash
# List recent workflow runs
gh run list --workflow=propagate-to-repos.yml --limit 5

# View specific run
gh run view <run-id>
```

**Check if repos are up to date**:
```bash
# In each dependent repo
cd syra && git submodule status
```

---

## Adding New Automation

When adding new workflows:
1. Use descriptive names (`verb-noun.yml`)
2. Add documentation to this README
3. Use `BOT_GITHUB_TOKEN` for cross-repo operations
4. Add `fail-fast: false` for matrix jobs
5. Include clear error messages and troubleshooting steps
