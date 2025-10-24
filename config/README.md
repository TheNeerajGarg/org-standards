# Quality Gates Configuration

This directory contains the quality gate configuration system for all repositories using org-standards.

## Files

- **quality-gates.yaml** - Base configuration (org-wide defaults)
- **quality-gates.schema.json** - JSON Schema for validation
- **quality-gates.local.yaml.example** - Example repository-specific overrides

## Usage

### For Repository Users

The quality gates are automatically enforced via pre-push hooks. No action required.

**Emergency bypass** (production incidents only):
```bash
EMERGENCY_PUSH=1 EMERGENCY_REASON="Production down, fix urgent" git push
```

### Repository-Specific Overrides

Create `quality-gates.local.yaml` in your repo root (NOT in org-standards/):

```yaml
# Lower coverage threshold for this repo
gates:
  coverage:
    threshold: 60  # Override org-wide 80%
```

See `quality-gates.local.yaml.example` for more examples.

## Validation

All config changes are validated automatically via pre-commit hooks.

**Manual validation**:
```bash
cd org-standards
python scripts/validate-config.py
```

**What's validated**:
- ✅ JSON Schema (structure, types, required fields)
- ✅ Semantic rules (no circular deps, undefined gates, execution order)
- ✅ Version format (semver: X.Y.Z)

## Evolution

### Adding a New Quality Gate

1. **Update config** (`config/quality-gates.yaml`):
```yaml
gates:
  security:
    enabled: true
    tool: bandit
    command: "bandit -r ."
    description: "Security vulnerability scanning"
    required: false  # Optional for now
    timeout_seconds: 60
```

2. **Add to execution order**:
```yaml
execution_order:
  - testing
  - coverage
  - type_checking
  - linting
  - security  # New gate
```

3. **Validate**:
```bash
python scripts/validate-config.py
```

4. **Commit and propagate**:
```bash
git add config/
git commit -m "feat(config): add security scanning gate"
git push origin main
```

5. **Update repos** (users run):
```bash
git submodule update --remote org-standards
```

### Changing Existing Gate

1. **Update threshold/command** in `quality-gates.yaml`
2. **Validate**: `python scripts/validate-config.py`
3. **Commit with clear rationale**
4. **Announce in Slack** (if breaking change)

### Removing a Gate

1. **Set `enabled: false`** (don't delete - preserve for overrides)
2. **Remove from execution_order**
3. **Update docs**
4. **Wait 1 sprint before deleting** (grace period)

## Rollback

If a config change breaks repositories:

```bash
cd org-standards
git revert <commit-hash>
git push origin main

# Notify repos to update
# Slack: "Reverted quality-gates change. Run: git submodule update --remote org-standards"
```

## Testing Config Changes

Before pushing config changes:

1. **Validate**: `python scripts/validate-config.py`
2. **Test locally**: Update submodule in test repo, run git push
3. **Check execution**: Verify gates run in correct order
4. **Monitor first repo**: Watch for issues during rollout

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-23 | Initial release - 4 gates (testing, coverage, type_checking, linting) |

## Support

- **Issues**: [org-standards GitHub issues](https://github.com/TheNeerajGarg/org-standards/issues)
- **Docs**: See `.claude/` for full org standards
- **Slack**: #dev-experience

## Related Documentation

- [Config Evolution Guide](EVOLUTION.md) - Detailed evolution procedures
- [Rollback Procedures](ROLLBACK.md) - Emergency rollback guide
- [Git Hooks Documentation](../git-hooks/README.md) - How pre-push hook works
