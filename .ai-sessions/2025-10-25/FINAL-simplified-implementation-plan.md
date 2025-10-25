# Final Implementation Plan: Stage-Aware Quality Gates (Simplified)

**Date**: 2025-10-25
**Status**: Ready to implement
**Approach**: **Keep it simple, learn from usage**

---

## User Feedback Incorporated

> "I do not want to make it too complicated to ensure relaxation are actually loosening. If they make it tighter, developers will complain and we will fix it"

**Philosophy**: Fast feedback from real usage > Complex upfront validation

---

## Simplified Implementation (3-4 hours)

### What We're Building

**Core Feature**: Stage-aware quality gates with highest standard by default

```yaml
gates:
  coverage:
    threshold: 85  # Base = highest standard (push-to-main)
    required: true

    stage_relaxations:
      pre-push:
        threshold: 70  # Relax for local speed
      pr:
        threshold: 80  # Relax slightly for PR
      # push-to-main: No entry = uses base (85%)
```

---

## What We're Keeping (SIMPLE)

### 1. Stage Name Validation (15 minutes)

```python
VALID_STAGES = {"pre-push", "pr", "push-to-main"}

def _apply_stage_relaxations(config, stage):
    if stage is not None and stage not in VALID_STAGES:
        raise ValueError(
            f"Unknown stage '{stage}'. Valid stages: {VALID_STAGES}.\n"
            f"Check for typos (e.g., 'pre_push' should be 'pre-push')."
        )
```

**Why Keep**: Catches typos → prevents silent failures → clear error message

**Example**:
```yaml
stage_relaxations:
  pre_push:  # Typo! Underscore instead of hyphen
    threshold: 70
```

**Error**: `Unknown stage 'pre_push'. Valid stages: {'pre-push', 'pr', 'push-to-main'}.`

---

### 2. Basic Implementation (2-3 hours)

```python
@dataclass
class GateConfig:
    # ... existing fields ...
    stage_relaxations: dict[str, dict[str, Any]] = field(default_factory=dict)

def _apply_stage_relaxations(config: QualityGatesConfig, stage: str | None) -> QualityGatesConfig:
    """Apply stage-specific relaxations.

    Base configuration = highest standard (push-to-main).
    Relaxations allow explicit opt-out for earlier stages.
    """
    if stage is None or stage == "push-to-main":
        return config  # No relaxations for push-to-main

    # Validate stage name
    if stage not in VALID_STAGES:
        raise ValueError(f"Unknown stage '{stage}'. Valid: {VALID_STAGES}")

    # Deep copy and apply relaxations
    config = copy.deepcopy(config)

    for gate_name, gate in config.gates.items():
        if stage in gate.stage_relaxations:
            relaxations = gate.stage_relaxations[stage]

            for key, value in relaxations.items():
                if hasattr(gate, key):
                    setattr(gate, key, value)
                else:
                    print(f"⚠️  Unknown key '{key}' for gate '{gate_name}' stage '{stage}'")

    return config

def execute_gates(config, phase=None, auto_detect=True):
    """Execute quality gates with stage-aware relaxations."""
    stage = phase or (_detect_stage() if auto_detect else None)

    if stage:
        print(f"🎯 Stage: {stage}")

    # Apply relaxations
    config = _apply_stage_relaxations(config, stage)

    # ... rest of execution logic ...
```

---

### 3. Documentation (30 minutes)

**Update quality-gates.yaml**:
```yaml
# Stage Relaxations (OPTIONAL)
#
# PHILOSOPHY: Base configuration = HIGHEST STANDARD (push-to-main)
#             Relaxations = Explicit opt-out for earlier stages
#
# Example:
# stage_relaxations:
#   pre-push:
#     threshold: 70  # Relax from base (e.g., 85)
#   pr:
#     threshold: 80  # Relax slightly
#   # push-to-main: No entry = uses base config
#
# Valid stages: pre-push, pr, push-to-main
```

---

### 4. Basic Tests (1 hour)

```python
def test_stage_relaxations_applied():
    """Test pre-push relaxations are applied."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")
    config = _apply_stage_relaxations(config, "pre-push")
    assert config.gates["coverage"].threshold == 70

def test_push_to_main_uses_base():
    """Test push-to-main uses base config (no relaxations)."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")
    config = _apply_stage_relaxations(config, "push-to-main")
    assert config.gates["coverage"].threshold == 85  # Base

def test_invalid_stage_name_rejected():
    """Test invalid stage names raise clear errors."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")
    with pytest.raises(ValueError, match="Unknown stage 'pre_push'"):
        _apply_stage_relaxations(config, "pre_push")  # Typo

def test_config_without_relaxations_works():
    """Test backward compatibility (configs without stage_relaxations)."""
    config = load_config("tests/fixtures/quality-gates-basic.yaml")
    config = _apply_stage_relaxations(config, "pre-push")
    # Should work without errors
```

---

## What We're NOT Building (Removed Complexity)

### ❌ Relaxation Tightening Validation

**Removed**: Complex validation that relaxations don't make requirements stricter

**Rationale** (user feedback):
- "If they make it tighter, developers will complain and we will fix it"
- Pragmatic: Fast feedback loop > complex validation
- YAGNI: Build when actually needed, not preemptively

**If Someone Misconfigures**:
```yaml
coverage:
  threshold: 70  # Base
  stage_relaxations:
    pre-push:
      threshold: 90  # Oops, tighter!
```

**What Happens**:
1. Developer runs pre-push → fails at 85% coverage
2. Developer confused: "Why is local stricter than CI?"
3. Developer reports issue
4. We fix the config: Lower base to 90 OR fix relaxation

**Learning**: Real feedback > hypothetical validation

---

### ❌ Push-to-Main Relaxation Blocking

**Removed**: Error if `stage_relaxations.push-to-main` exists

**Rationale**: Keep it simple, unusual configs are allowed

**If Someone Does This**:
```yaml
stage_relaxations:
  push-to-main:
    threshold: 70  # Unusual pattern
```

**What Happens**: Works as configured (push-to-main uses 70%)

**If Wrong**: Developer notices production has lower bar → reports → we fix

---

### ❌ Complex Conflict Resolution

**Removed**: Validation for conflicts between local overrides and stage relaxations

**Rationale**: Standard YAML merge behavior is sufficient

**If Conflict Occurs**: Last-wins precedence (standard behavior)

---

## Implementation Breakdown (3-4 hours)

### Hour 1-2: Core Implementation

1. Add `stage_relaxations` field to `GateConfig` (5 min)
2. Implement `_apply_stage_relaxations()` with stage validation (30 min)
3. Implement `_detect_stage()` (30 min)
4. Update `execute_gates()` to apply relaxations (30 min)

### Hour 3: Testing

5. Add unit tests (stage application, validation, backward compat) (45 min)
6. Add integration test (pre-push hook with relaxations) (15 min)

### Hour 4: Documentation & Rollout

7. Update quality-gates.yaml comments (15 min)
8. Update CLAUDE.md with stage examples (15 min)
9. Create example config with stage_relaxations (15 min)
10. Deploy to org-standards (push to main) (15 min)

---

## Rollout Plan (Phased)

### Phase 1: Deploy Code (Immediate)

- Push implementation to org-standards main
- No config changes yet (backward compatible)
- Update submodules in StyleGuru and syra
- Verify existing configs still work

**Success Criteria**: All repos' CI still green

---

### Phase 2: Canary (48 hours)

Add stage_relaxations to **syra only**:

```yaml
# org-standards/config/quality-gates.yaml (no changes)

# syra/quality-gates.local.yaml (NEW)
gates:
  coverage:
    stage_relaxations:
      pre-push:
        threshold: 45  # Relax from base (49%)
```

**Monitor**:
- Pre-push execution time (target: <90s)
- Emergency bypass rate (target: <10%)
- Developer feedback (any complaints?)

**Rollback**: Remove `quality-gates.local.yaml` if issues

---

### Phase 3: Full Rollout (After Canary Success)

Update base config in org-standards:

```yaml
# org-standards/config/quality-gates.yaml
gates:
  coverage:
    threshold: 85  # Raise base to 85%
    stage_relaxations:
      pre-push:
        threshold: 70
      pr:
        threshold: 80

  type_checking:
    enabled: true
    required: true
    stage_relaxations:
      pre-push:
        enabled: false  # Skip locally for speed
```

Update submodules in all repos → automatic propagation

---

## Success Metrics

### Must Have (Phase 1)

- ✅ Existing configs work without changes
- ✅ Stage name typos caught with clear errors
- ✅ Tests pass

### Should Have (Phase 2 - Canary)

- ✅ Pre-push execution time <90s (syra)
- ✅ No increase in bypass rate
- ✅ No developer complaints about unexpected behavior

### Nice to Have (Phase 3 - Full Rollout)

- ✅ Pre-push <90s across all repos
- ✅ CI failure rate <5% after passing pre-push
- ✅ Developer satisfaction (faster local development)

---

## What We'll Learn

**From Real Usage**:
1. Are relaxations configured correctly? (developers will tell us)
2. Do relaxations actually improve speed? (measure it)
3. Do developers accidentally tighten requirements? (they'll complain)
4. Are 3 stages enough or do we need more? (demand signal)

**Iterative Improvements**:
- If tightening is common → Add validation in Phase 2
- If push-to-main relaxations appear → Add warning/block
- If stage detection fails → Improve detection logic
- If performance doesn't improve → Adjust relaxations

---

## Decision Point

**Question**: Proceed with simplified implementation?

**What You're Approving**:
- ✅ Core feature: stage_relaxations with highest standard by default
- ✅ Minimal validation: Stage name typos only
- ✅ Implementation time: 3-4 hours
- ✅ Phased rollout: Code → Canary (syra) → Full

**What You're NOT Approving** (removed):
- ❌ Complex relaxation tightening validation
- ❌ Push-to-main relaxation blocking
- ❌ Conflict resolution validation

**User Philosophy Applied**: "Keep it simple, learn from usage"

---

**Ready to implement?**

If yes, I'll start with:
1. Update quality_gates.py (2-3 hours)
2. Add tests (1 hour)
3. Update documentation (30 min)
4. Deploy to org-standards main

**Estimated completion**: Today (3-4 hours work)
