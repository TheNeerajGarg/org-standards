# Quality Gates Configuration Evolution Guide

This document explains how to evolve the quality gates configuration over time as organizational needs change.

## Table of Contents

- [Adding a New Quality Gate](#adding-a-new-quality-gate)
- [Changing an Existing Tool](#changing-an-existing-tool)
- [Adjusting Thresholds](#adjusting-thresholds)
- [Repository-Specific Overrides](#repository-specific-overrides)
- [Rollback Procedures](#rollback-procedures)

---

## Adding a New Quality Gate

### Example: Add Security Scanning (Bandit)

**Step 1: Update quality-gates.yaml**

```yaml
gates:
  # ... existing gates ...

  security_scan:
    enabled: true
    tool: bandit
    command: "bandit -r . -f json"
    description: "Security vulnerability scanning"
    required: false  # Start optional
    fail_message: |
      Security issues detected. Fix:
      1. Review bandit output
      2. Fix vulnerabilities or add # nosec comments
    timeout_seconds: 120

execution_order:
  - testing
  - coverage
  - type_checking
  - linting
  - security_scan  # Add to end
```

**Step 2: Validate Configuration**

```bash
cd org-standards
python scripts/validate-config.py
```

**Step 3: Test in Canary Repo**

```bash
# Deploy to syra first
cd /path/to/syra
git submodule update --remote org-standards
git push  # Trigger pre-push hook
```

**Step 4: Monitor for 48 Hours**

- Check bypass rate (should be <5%)
- Review error messages (are they clear?)
- Collect developer feedback

**Step 5: Gradual Rollout**

- **Week 1-2**: Optional (required: false) - collect data
- **Week 3-4**: Show warnings (non-blocking)
- **Week 5+**: Enforce (required: true)

**Timeline**: 1 week config + test, 4 weeks validation = 5 weeks total

---

## Changing an Existing Tool

### Example: Replace Ruff with New-Linter

**Phase 1: Run Both in Parallel (2-4 weeks)**

```yaml
gates:
  linting_ruff:
    enabled: true
    tool: ruff
    commands:
      format_check: "ruff format --check ."
      lint_check: "ruff check ."
    required: true  # Still enforced

  linting_new:
    enabled: true
    tool: new-linter
    command: "new-linter check ."
    required: false  # Parallel run, not blocking
```

**Phase 2: Collect Agreement Data**

```bash
# Track: How often do both tools agree?
# If agreement >95%, proceed to cutover
# If <95%, investigate discrepancies
```

**Phase 3: Cutover**

```yaml
gates:
  linting_ruff:
    enabled: false  # Deprecated

  linting_new:
    enabled: true
    required: true  # Now enforced
```

**Phase 4: Remove Old Gate (after 1 month)**

```yaml
# Delete linting_ruff entirely
gates:
  linting:
    enabled: true
    tool: new-linter
    # ...
```

**Timeline**: 6 weeks (2 prep, 4 parallel, instant cutover)

---

## Adjusting Thresholds

### Option 1: Repository-Specific (Recommended)

For a single repo that needs different threshold:

```bash
# In repo root
cat > quality-gates.local.yaml <<EOF
gates:
  coverage:
    threshold: 75  # Override org-wide 80%
EOF
```

**Use Cases**:
- CLI wrapper code (simple, doesn't need 80%)
- Data pipelines (different testing approach)
- Legacy repos (gradual improvement)

### Option 2: Org-Wide Change

For changing threshold across all repos:

**Step 1: Document Rationale**

```bash
# In commit message, explain:
# - Why changing threshold?
# - What data supports this?
# - What's the expected impact?
```

**Step 2: Update Config**

```yaml
gates:
  coverage:
    threshold: 75  # Was 80%, lowered due to [reason]
```

**Step 3: Communicate**

```bash
# Post in #dev-experience Slack:
"📢 Quality gate threshold changing: 80% → 75%
Reason: [explain]
Effective: [date]
Questions: Reply or DM @Neeraj"
```

**Step 4: Monitor**

- Track bypass rate (should decrease)
- Check overall coverage trend (should not drop)

**Timeline**: 1 day config change, 1 week monitoring

---

## Repository-Specific Overrides

### When to Use Overrides

**Good Reasons**:
- Code type has different testing needs (CLI vs API)
- Legacy repo with gradual improvement plan
- Experimental repo (research, prototypes)

**Bad Reasons**:
- "Tests are hard to write" (improve testing skills instead)
- "Deadline pressure" (use EMERGENCY_PUSH for true emergencies)
- "I don't like the threshold" (discuss with team)

### Override File Format

**Location**: `quality-gates.local.yaml` (repo root, NOT committed)

```yaml
# Override coverage threshold
gates:
  coverage:
    threshold: 60

# Disable optional gates
gates:
  type_checking:
    enabled: false

# Add repo-specific gate
gates:
  custom_check:
    enabled: true
    tool: custom-tool
    command: "./scripts/custom-check.sh"
    required: true
```

### Override Merge Behavior

```yaml
# Base (org-standards/config/quality-gates.yaml)
gates:
  coverage:
    threshold: 80
    tool: diff-cover
    required: true

# Override (repo/quality-gates.local.yaml)
gates:
  coverage:
    threshold: 70  # Only override threshold

# Result (deep merge)
gates:
  coverage:
    threshold: 70       # Overridden
    tool: diff-cover    # Inherited
    required: true      # Inherited
```

---

## Configuration Validation

**Before Committing Config Changes**:

```bash
# 1. Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/quality-gates.yaml'))"

# 2. Validate schema
python scripts/validate-config.py

# 3. Test config loading
cd python
python -c "
from quality_gates import load_config
config = load_config(base_config='../config/quality-gates.yaml')
print(f'✅ Config version {config.version} loaded successfully')
"
```

**CI Validation**:

CI automatically validates on every PR:
- `.github/workflows/validate-config.yml`
- Runs schema + semantic validation
- PRs blocked if validation fails

---

## Best Practices

### 1. Start Optional, Graduate to Required

```yaml
# Week 1: Optional (required: false)
# Collect data, refine errors

# Week 3: Required (required: true)
# Only after validating low false positive rate
```

### 2. Canary Test in syra First

```bash
# Deploy to syra (48 hours minimum)
# 5+ real pushes, monitor metrics
# Only then deploy org-wide
```

### 3. Document Every Change

```bash
# Commit message should explain:
git commit -m "
chore(config): lower coverage threshold 80% → 75%

Reason: CLI wrapper code doesn't need 80% (simple arg parsing)
Data: 15% of bypasses cite 'CLI code doesn't need high coverage'
Impact: Expected 10% reduction in bypass rate

Canary tested in syra for 1 week (no issues)
"
```

### 4. Version Config

```yaml
# Bump version on breaking changes
version: "2.0.0"  # Was 1.0.0

# Breaking: Changed tool from ruff to new-linter
# Repos must: pip install new-linter
```

### 5. Communicate Changes

```bash
# For org-wide changes:
# 1. Announce 1 week in advance (#dev-experience Slack)
# 2. Provide migration guide
# 3. Monitor support channels for issues
```

---

## Common Evolution Scenarios

### Scenario 1: Coverage Too Strict

**Problem**: 20% bypass rate, many cite "threshold too high"

**Solution**:
1. Review bypass reasons (are they legitimate?)
2. If yes: Lower threshold 80% → 75% org-wide
3. If no: Improve error messages, add more omit patterns

### Scenario 2: New Tool Available

**Problem**: Better tool released (e.g., faster linter)

**Solution**:
1. Run both tools in parallel (4 weeks)
2. Compare results (>95% agreement?)
3. Cutover to new tool
4. Remove old tool after 1 month

### Scenario 3: Repo-Specific Needs

**Problem**: CLI repo needs 60% (not 80%)

**Solution**:
1. Create quality-gates.local.yaml in repo
2. Override threshold: 60
3. Document rationale in repo README

### Scenario 4: Emergency Bypass Overuse

**Problem**: >3 emergency bypasses per month

**Solution**:
1. Review bypass reasons
2. Identify patterns (same gate failing? specific code type?)
3. Adjust config (lower threshold, add omit pattern)
4. If abuse: Add approval requirement (Phase 2)

---

## Related Documents

- [README.md](README.md) - Configuration overview
- [ROLLBACK.md](ROLLBACK.md) - Rollback procedures
- [quality-gates.yaml](quality-gates.yaml) - Current configuration
- [quality-gates.schema.json](quality-gates.schema.json) - JSON Schema

---

**Last Updated**: 2025-10-23
**Version**: 1.0.0
