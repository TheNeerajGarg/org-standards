# Quality Gates Rollback Procedures

This document provides step-by-step procedures for rolling back quality gates configuration changes when issues are detected.

## Table of Contents

- [When to Rollback](#when-to-rollback)
- [Quick Rollback (Emergency)](#quick-rollback-emergency)
- [Rollback Scenarios](#rollback-scenarios)
- [Post-Rollback Actions](#post-rollback-actions)

---

## When to Rollback

### Rollback Triggers

**CRITICAL (Immediate Rollback)**:
- Hook crashes (exits with error on valid code)
- Hook execution time >2 minutes (blocks development)
- Configuration syntax error (breaks all repos)
- Data loss incident (code deleted, commits lost)

**HIGH (Rollback within 4 hours)**:
- Bypass rate >50% (developers avoiding system)
- False positive rate >20% (legitimate code blocked)
- Critical tool missing (pytest not installed)
- >5 developer complaints in 1 hour

**MEDIUM (Fix forward or rollback within 24 hours)**:
- Bypass rate 20-50% (too strict)
- False positive rate 10-20% (needs tuning)
- Negative developer feedback (annoying but functional)

**LOW (Fix forward)**:
- Bypass rate 5-20% (acceptable, monitor)
- False positive rate <10% (expected noise)
- Minor performance issues (p95 <90 seconds)

---

## Quick Rollback (Emergency)

**Target**: <30 minutes from detection to resolution

### Step 1: Revert Configuration (5 minutes)

```bash
# In org-standards repo
cd org-standards

# Find the bad commit
git log --oneline config/quality-gates.yaml | head -5

# Revert the problematic commit
git revert <bad-commit-hash>

# Or: Reset to last known good commit
git reset --hard <good-commit-hash>
git push --force origin main
```

### Step 2: Notify All Repos (2 minutes)

```bash
# Post in #dev-experience Slack
"🚨 URGENT: Quality gate config issue detected

Issue: [describe problem]
Action: Revert config to previous version
Impact: Previous behavior restored

Update your repo:
  cd your-repo
  git submodule update --remote org-standards

Status: Investigating root cause
ETA: Fix in [timeframe]

Questions: DM @Neeraj"
```

### Step 3: Verify Fix (10 minutes)

```bash
# Test in syra first
cd /path/to/syra
git submodule update --remote org-standards

# Verify config loads
python org-standards/scripts/validate-config.py

# Test real push
git push  # Should work now

# If verified: Notify team
"✅ Quality gate config rolled back successfully
You can resume development normally."
```

### Step 4: Document Incident (10 minutes)

Create `.ai-sessions/YYYY-MM-DD/incident-HHMMSS.md`:

```markdown
# Incident: Quality Gate Config Failure

**Date**: 2025-10-23 14:30 UTC
**Duration**: 30 minutes
**Impact**: All developers blocked from pushing

## Timeline

14:30 - Config change deployed (commit abc123)
14:35 - First developer report: "Hook crashes"
14:37 - Rollback initiated
14:42 - Rollback complete, repos notified
15:00 - All repos updated, issue resolved

## Root Cause

[What went wrong?]

## Fix

[What was the rollback action?]

## Prevention

[What will prevent this in the future?]
```

### Step 5: Root Cause Analysis (later)

After rollback is complete and systems restored:

1. Analyze what went wrong
2. Update validation to catch this issue
3. Add test case to prevent recurrence
4. Document lesson learned

---

## Rollback Scenarios

### Scenario 1: Invalid YAML Syntax

**Problem**: Typo in quality-gates.yaml breaks all repos

**Symptoms**:
- Hook fails with YAML parse error
- All pushes blocked
- Error: "could not parse quality-gates.yaml"

**Rollback**:

```bash
cd org-standards

# Revert last commit
git revert HEAD
git push origin main

# Notify repos
"Config syntax error fixed. Update submodule:
  git submodule update --remote org-standards"

# Verify
python scripts/validate-config.py
# Should show: ✅ Config is valid
```

**Prevention**:
- Pre-commit hook validates YAML syntax
- CI validates before merge
- Manual validation: `python -c "import yaml; yaml.safe_load(open('config/quality-gates.yaml'))"`

---

### Scenario 2: Hook Too Slow (>2 minutes)

**Problem**: New gate (e.g., security scan) takes 3 minutes

**Symptoms**:
- Bypass rate jumps from 5% to 30%
- Developers report "hook is too slow"
- Pre-push takes >2 minutes

**Rollback**:

```bash
cd org-standards

# Option A: Disable slow gate
# Edit config/quality-gates.yaml
gates:
  security_scan:
    enabled: false  # Temporarily disable

git add config/quality-gates.yaml
git commit -m "chore(config): disable security_scan (performance issue)"
git push origin main

# Option B: Revert entire change
git revert <commit-that-added-security-scan>
git push origin main
```

**Prevention**:
- Test gate performance in canary (48 hours)
- Measure p95 execution time before rollout
- Set timeout_seconds appropriately
- Consider moving slow gates to CI only

---

### Scenario 3: False Positives (Legitimate Code Blocked)

**Problem**: diff-cover reports low coverage on well-tested code

**Symptoms**:
- Bypass rate >20%
- Bypass reasons cite "false positive"
- Example: "Refactored code, tests exist but diff-cover says 0%"

**Rollback Options**:

**Option A: Add Omit Patterns** (fix forward)

```yaml
gates:
  coverage:
    omit_patterns:
      - "playground/*"
      - ".ai-sessions/*"
      - "*/migrations/*"  # Add this
      - "*/generated/*"   # Add this
```

**Option B: Lower Threshold Temporarily**

```yaml
gates:
  coverage:
    threshold: 70  # Was 80%, temporary reduction
```

**Option C: Make Coverage Optional**

```yaml
gates:
  coverage:
    required: false  # Allow bypassing temporarily
```

**Option D: Full Rollback**

```bash
git revert <commit-that-changed-coverage>
git push origin main
```

**Prevention**:
- Canary test with real refactoring PRs
- Review bypass reasons weekly
- Adjust omit patterns based on patterns

---

### Scenario 4: Missing Tool Dependency

**Problem**: Config requires tool not installed (e.g., bandit)

**Symptoms**:
- Hook fails with "bandit not found"
- Error: "Tool 'bandit' not installed"
- Pushes blocked

**Rollback**:

**Option A: Make Tool Optional**

```yaml
gates:
  security_scan:
    enabled: true
    tool: bandit
    required: false  # Allow missing tool
```

**Option B: Disable Gate**

```yaml
gates:
  security_scan:
    enabled: false
```

**Option C: Full Rollback**

```bash
git revert <commit-that-added-bandit>
git push origin main
```

**Prevention**:
- Document tool installation in README
- Check tool availability in hook (graceful failure)
- Start new gates as optional (required: false)

---

### Scenario 5: Circular Dependency

**Problem**: Gate A depends on Gate B, Gate B depends on Gate A

**Symptoms**:
- Hook crashes with recursion error
- Error: "Circular dependency detected"

**Rollback**:

```bash
cd org-standards
git revert HEAD
git push origin main
```

**Prevention**:
- Validation script checks for circular deps (scripts/validate-config.py)
- CI runs validation before merge
- Manual check: Review depends_on relationships

---

## Rollback Decision Tree

```
Issue Detected
  |
  ├─ Is development blocked? (all pushes fail)
  │   ├─ YES → IMMEDIATE ROLLBACK (<30 min)
  │   └─ NO → Continue investigation
  |
  ├─ Bypass rate >50%?
  │   ├─ YES → ROLLBACK (within 4 hours)
  │   └─ NO → Continue
  |
  ├─ False positive rate >20%?
  │   ├─ YES → ROLLBACK or FIX FORWARD (add omit patterns)
  │   └─ NO → Continue
  |
  ├─ Can we fix forward? (config tweak, no revert needed)
  │   ├─ YES → FIX FORWARD (faster than rollback)
  │   └─ NO → ROLLBACK
  |
  └─ Monitor and iterate
```

---

## Post-Rollback Actions

### Immediate (Within 1 hour)

1. **Verify Rollback Success**
   ```bash
   # Test in syra
   cd /path/to/syra
   git push  # Should succeed
   ```

2. **Notify Team**
   - Post in #dev-experience: "Issue resolved, resume work"
   - Explain what happened
   - Provide ETA for permanent fix

3. **Document Incident**
   - Create incident report
   - Timeline of events
   - Impact assessment

### Short-Term (Within 1 day)

1. **Root Cause Analysis**
   - What exactly failed?
   - Why did validation not catch it?
   - What was the trigger?

2. **Improve Validation**
   - Add test case for this failure
   - Update validate-config.py
   - Add CI check if missing

3. **Communication**
   - Post-mortem in #dev-experience
   - Lessons learned
   - Prevention plan

### Long-Term (Within 1 week)

1. **Implement Prevention**
   - Update validation scripts
   - Add integration tests
   - Improve canary testing

2. **Update Documentation**
   - Add scenario to this ROLLBACK.md
   - Update EVOLUTION.md with new best practice
   - Update README.md if needed

3. **Retrospective**
   - What went well in rollback?
   - What could be faster?
   - Process improvements?

---

## Rollback Checklist

**Before Rollback**:
- [ ] Identify problematic commit hash
- [ ] Confirm last known good configuration
- [ ] Notify team (rollback starting)

**During Rollback**:
- [ ] Revert or reset configuration
- [ ] Push to org-standards main branch
- [ ] Verify config validates (validate-config.py)
- [ ] Test in syra (one real push)

**After Rollback**:
- [ ] Notify all repos to update submodule
- [ ] Monitor #dev-experience for issues
- [ ] Create incident report
- [ ] Schedule root cause analysis
- [ ] Update validation to prevent recurrence

---

## Emergency Contacts

**Primary**: @Neeraj (Slack, email)
**Backup**: [Add backup contact]

**Escalation Path**:
1. Rollback config (30 min SLA)
2. Notify team
3. Root cause analysis (within 24 hours)
4. Implement prevention (within 1 week)

---

## Testing Rollback Procedures

**Quarterly Drill** (simulate rollback):

```bash
# 1. Introduce intentional error in dev branch
cd org-standards
git checkout -b test-rollback
echo "invalid: yaml: syntax: error:" > config/quality-gates.yaml
git add config/quality-gates.yaml
git commit -m "test: intentional config break"

# 2. Practice rollback
git revert HEAD
# Time yourself: How long did it take?

# 3. Verify
python scripts/validate-config.py

# 4. Clean up
git checkout main
git branch -D test-rollback
```

**Success Criteria**:
- Rollback completed in <30 minutes
- Config validates after rollback
- Team notified correctly
- Incident documented

---

## Related Documents

- [README.md](README.md) - Configuration overview
- [EVOLUTION.md](EVOLUTION.md) - How to evolve configuration
- [quality-gates.yaml](quality-gates.yaml) - Current configuration

---

**Last Updated**: 2025-10-23
**Version**: 1.0.0
