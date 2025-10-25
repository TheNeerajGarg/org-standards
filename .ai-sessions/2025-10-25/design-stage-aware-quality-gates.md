# Design: Stage-Aware Quality Gates Configuration

**Date**: 2025-10-25
**Author**: Claude
**Status**: Proposal (awaiting user approval)
**Related**: ERD-progressive-quality-phase1.md, quality-gates.yaml

## Abstract

This document proposes a stage-aware configuration system for quality gates that enforces **highest standards by default** with explicit relaxation for earlier stages. The design ensures new gates are automatically enforced at all stages unless explicitly relaxed for local development speed.

**Key Philosophy:** **Strictest by default, relax as needed** (opt-out, not opt-in)

**Key Changes:**
- Base configuration = highest standard (push-to-main requirements)
- `stage_relaxations` section allows explicit opt-out for pre-push/PR stages
- Modify `execute_gates()` to apply relaxations
- Maintain single source of truth (one YAML file)

**Impact**:
- New gates are enforced everywhere by default (safety)
- Local development can be faster via explicit relaxation (convenience)
- Prevents accidental quality regressions from opt-in model

---

## 1. Problem Statement

**Current State**: All quality gates use the same configuration regardless of where they run:
- Pre-push hook (local) runs same checks as CI
- No way to have stricter requirements for main branch
- No way to optimize for speed locally vs comprehensiveness in CI

**User Question**: "Where do we store the configuration of what is the bar for various stages, e.g. merge to main vs. push to origin?"

**User Confirmation**: "Configuration driven seems correct to me."

**User Design Principle**: "We want to use the highest standard by default, and then configure relaxation. So, if the push to main adds a new gate, that is by default enforced at stages. If it is too hard, then appropriate relaxation can be configured."

---

## 2. Requirements

### 2.1 Functional Requirements

**FR1**: Support different quality bars for different stages:
- **Stage: `pre-push`** - Local enforcement before sharing code
- **Stage: `pr`** - CI enforcement for pull requests
- **Stage: `push-to-main`** - Highest bar for direct pushes to main

**FR2**: Allow per-gate, per-stage overrides for:
- `enabled` (run gate or skip)
- `threshold` (e.g., coverage percentage)
- `required` (block or warn)
- `timeout_seconds` (faster locally, comprehensive in CI)

**FR3**: Maintain backward compatibility - gates without stage overrides work as before

**FR4**: Single source of truth - one configuration file (not multiple files per stage)

### 2.2 Non-Functional Requirements

**NFR1**: Configuration changes propagate automatically via org-standards submodule
**NFR2**: Clear error messages when stage configuration is invalid
**NFR3**: Documentation shows how to add new stages or modify existing ones

---

## 3. Design Options Considered

### Option A: Stages Section (Separate)
```yaml
stages:
  pre-push:
    gates: [linting, testing]
    overrides:
      coverage:
        threshold: 70
  pr:
    gates: [linting, testing, coverage, type_checking]
    overrides:
      coverage:
        threshold: 80
```

**Pros**: Clear separation of stages
**Cons**: Configuration duplicated across stages, harder to see all stages for a gate

---

### Option B: Per-Gate Stage Relaxations (RECOMMENDED)
```yaml
gates:
  coverage:
    enabled: true
    threshold: 85  # HIGHEST STANDARD (push-to-main requirement)
    required: true

    # Explicit relaxation for earlier stages (opt-out)
    stage_relaxations:
      pre-push:
        threshold: 70  # Relaxed for fast feedback
        # required: still true (inherited from base)
      pr:
        threshold: 80  # Relaxed slightly for PR
        # required: still true (inherited from base)
      # push-to-main: No relaxation = uses base config (85%)
```

**Philosophy**:
- **Base config = strictest requirement** (push-to-main)
- **Relaxations = explicit opt-out** for earlier stages
- **New gates auto-enforced everywhere** unless explicitly relaxed

**Pros**:
- Safety by default (new gates enforced everywhere)
- Single source of truth per gate
- Easy to see all stage variations
- Prevents accidental quality regressions
- Aligns with existing override pattern (quality-gates.local.yaml)

**Cons**: Stage configuration spread across multiple gate definitions

---

### Option C: Separate Files Per Stage
```
config/
  quality-gates.yaml
  quality-gates-pre-push.yaml
  quality-gates-pr.yaml
```

**Pros**: Clear separation
**Cons**: Multiple files to maintain, easy to get out of sync, violates single source of truth

---

**Decision**: **Option B** (Per-Gate Stage Relaxations)

**Rationale**:
1. **Safety by default**: New gates enforced everywhere automatically
2. **User design principle**: "Use highest standard by default, configure relaxation"
3. Aligns with ERD preference for YAML (not JSON-LD or separate configs)
4. Single source of truth reduces maintenance burden
5. Easy to add new stages without restructuring
6. Backward compatible (existing configs work without changes)

---

## 4. Proposed Configuration Structure

### 4.1 Updated quality-gates.yaml Schema

```yaml
version: "1.0.0"

gates:
  # Testing: All tests must pass
  # BASE CONFIG = STRICTEST (push-to-main requirements)
  testing:
    enabled: true
    tool: pytest
    command: "pytest --tb=short"  # Full traceback (strictest)
    description: "Run full test suite"
    required: true
    timeout_seconds: 600  # Generous timeout for comprehensive tests

    # RELAXATIONS for earlier stages (explicit opt-out)
    stage_relaxations:
      pre-push:
        # Fast smoke tests locally
        command: "pytest tests/unit --tb=short -q -x"  # Unit only, exit on first failure
        timeout_seconds: 60  # Faster timeout for local dev
      pr:
        # Full test suite but quieter output
        command: "pytest --tb=short -q"
        timeout_seconds: 300
      # push-to-main: No relaxation = uses base config (full suite, 600s timeout)

  # Coverage: New code must meet threshold
  # BASE CONFIG = HIGHEST STANDARD
  coverage:
    enabled: true
    tool: diff-cover
    threshold: 85  # Strictest threshold (push-to-main requirement)
    command: "diff-cover coverage.xml --compare-branch=origin/main --fail-under={threshold}"
    description: "Differential coverage on new/modified lines"
    required: true
    depends_on: [testing]
    timeout_seconds: 60

    # RELAXATIONS for fast local feedback
    stage_relaxations:
      pre-push:
        threshold: 70  # Relaxed for fast feedback
      pr:
        threshold: 80  # Standard bar for PRs
      # push-to-main: No relaxation = uses base (85%)

  # Type Checking: Type hints validated
  # BASE CONFIG = REQUIRED EVERYWHERE
  type_checking:
    enabled: true
    tool: mypy
    command: "mypy ."
    description: "Static type checking"
    required: true
    timeout_seconds: 120

    # OPTIONAL RELAXATION for local speed
    stage_relaxations:
      pre-push:
        enabled: false  # Skip locally for speed (developer can enable if desired)
      # pr: No relaxation = uses base (enabled: true, required: true)
      # push-to-main: No relaxation = uses base (enabled: true, required: true)

  # Linting: Code style enforced
  # BASE CONFIG = SAME FOR ALL STAGES (fast check, no need to relax)
  linting:
    enabled: true
    tool: ruff
    commands:
      format_check: "ruff format --check ."
      lint_check: "ruff check ."
    description: "Code formatting and linting"
    required: true
    timeout_seconds: 60

    # No relaxations - linting is fast enough for all stages

execution_order:
  - testing
  - coverage
  - type_checking
  - linting

emergency_bypass:
  enabled: true
  env_var: "EMERGENCY_PUSH"
  log_dir: ".emergency-bypasses"
  log_format: "json"
  reason_env_var: "EMERGENCY_REASON"

override_file: "quality-gates.local.yaml"
```

---

### 4.2 Stage Detection

**How stages are determined:**

| Context | Stage | Detection Method |
|---------|-------|-----------------|
| Local pre-push hook | `pre-push` | Passed explicitly in hook script |
| GitHub Actions PR | `pr` | Detect from `GITHUB_EVENT_NAME=pull_request` |
| GitHub Actions push to main | `push-to-main` | Detect from `GITHUB_REF=refs/heads/main` |
| Manual execution | Default (no overrides) | No stage specified |

**Implementation in execute_gates()**:
```python
def execute_gates(
    config: QualityGatesConfig,
    phase: str | None = None,  # Explicit stage
    auto_detect: bool = True,  # Auto-detect from environment
) -> ExecutionResults:
    # Determine stage
    stage = phase or (_detect_stage() if auto_detect else None)

    # Apply stage overrides
    config = _apply_stage_overrides(config, stage)

    # Execute gates with overridden config
    ...
```

---

## 5. Implementation Changes

### 5.1 Configuration Loader (quality_gates.py)

**Add Stage Override Logic:**

```python
@dataclass
class GateConfig:
    """Configuration for a single quality gate.

    Base configuration represents the HIGHEST STANDARD (push-to-main requirements).
    Stage relaxations allow explicit opt-out for earlier stages.
    """
    name: str
    enabled: bool
    tool: str
    command: str | None = None
    commands: dict[str, str] | None = None
    threshold: int | None = None
    description: str = ""
    required: bool = True
    depends_on: list[str] = field(default_factory=list)
    omit_patterns: list[str] = field(default_factory=list)
    fail_message: str = ""
    timeout_seconds: int = 300
    stage_relaxations: dict[str, dict[str, Any]] = field(default_factory=dict)  # NEW


def _apply_stage_relaxations(
    config: QualityGatesConfig,
    stage: str | None
) -> QualityGatesConfig:
    """Apply stage-specific relaxations to gate configurations.

    Base configuration = HIGHEST STANDARD (push-to-main requirements).
    Relaxations allow explicit opt-out for earlier stages.

    Args:
        config: Base quality gates configuration (strictest requirements)
        stage: Stage to apply (e.g., "pre-push", "pr")
                "push-to-main" uses base config (no relaxations)

    Returns:
        Configuration with stage relaxations applied
    """
    if stage is None or stage == "push-to-main":
        return config  # No relaxations for push-to-main (uses highest standard)

    # Deep copy config
    import copy
    config = copy.deepcopy(config)

    # Apply relaxations for each gate
    for gate_name, gate in config.gates.items():
        if stage in gate.stage_relaxations:
            relaxations = gate.stage_relaxations[stage]

            # Apply each relaxation (always loosening, never tightening)
            for key, value in relaxations.items():
                if hasattr(gate, key):
                    setattr(gate, key, value)
                else:
                    # Log warning for unknown relaxation
                    print(f"⚠️  Unknown relaxation key '{key}' for gate '{gate_name}' stage '{stage}'")

    return config


def _detect_stage() -> str | None:
    """Auto-detect stage from environment.

    Returns:
        Stage name or None if cannot detect
    """
    import os

    # GitHub Actions detection
    if os.getenv("GITHUB_ACTIONS") == "true":
        event_name = os.getenv("GITHUB_EVENT_NAME")
        ref = os.getenv("GITHUB_REF")

        if event_name == "pull_request":
            return "pr"
        elif ref in ("refs/heads/main", "refs/heads/master"):
            return "push-to-main"

    # Default: assume pre-push if not in CI
    return None


def execute_gates(
    config: QualityGatesConfig,
    phase: str | None = None,
    auto_detect: bool = True,
) -> ExecutionResults:
    """Execute quality gates in configured order.

    Base configuration = HIGHEST STANDARD (push-to-main requirements).
    Relaxations applied for pre-push/pr stages for development speed.

    Args:
        config: Quality gates configuration (base = strictest)
        phase: Explicit stage name (overrides auto-detection)
               "pre-push", "pr", or "push-to-main"
        auto_detect: Auto-detect stage from environment if phase not provided

    Returns:
        Execution results with pass/fail status
    """
    # Determine stage
    stage = phase or (_detect_stage() if auto_detect else None)

    if stage:
        print(f"🎯 Stage: {stage}")
        if stage == "push-to-main":
            print("   Using HIGHEST STANDARD (no relaxations)")
        else:
            print(f"   Applying relaxations for '{stage}' stage")

    # Apply stage relaxations (base config = strictest)
    config = _apply_stage_relaxations(config, stage)

    # [Rest of existing execute_gates logic...]
    ...
```

---

### 5.2 Pre-Push Hook (No Changes Required)

The pre-push hook already passes `phase="pre-push"`:
```python
results = execute_gates(config, phase="pre-push")  # Line 128
```

**No changes needed** - hook will automatically use pre-push overrides.

---

### 5.3 GitHub Actions Workflow (Auto-Detection)

**Current workflow** (.github/workflows/reusable-quality-gates.yml):
```yaml
- name: Run quality gates
  run: |
    python3 << 'PYTHON_SCRIPT'
    import sys
    sys.path.insert(0, "org-standards/python")
    from quality_gates import load_config, execute_gates

    config = load_config()
    results = execute_gates(config)  # Will auto-detect stage

    sys.exit(0 if results.passed else 1)
    PYTHON_SCRIPT
```

**With stage override** (optional explicit):
```yaml
- name: Run quality gates
  run: |
    python3 << 'PYTHON_SCRIPT'
    import sys
    sys.path.insert(0, "org-standards/python")
    from quality_gates import load_config, execute_gates

    config = load_config()

    # Explicit stage (alternative to auto-detect)
    stage = "pr" if "${{ github.event_name }}" == "pull_request" else "push-to-main"
    results = execute_gates(config, phase=stage)

    sys.exit(0 if results.passed else 1)
    PYTHON_SCRIPT
```

---

## 6. Migration Path

### 6.1 Phase 1: Add Stage Support (Backward Compatible)

**Changes:**
1. Update `GateConfig` dataclass to include `stage_overrides` field
2. Add `_apply_stage_overrides()` and `_detect_stage()` functions
3. Update `execute_gates()` to apply overrides
4. No changes to existing quality-gates.yaml (works as-is)

**Result**: Existing configs work without changes, new stage overrides optional.

---

### 6.2 Phase 2: Add Stage Overrides (Selective Rollout)

**Candidates for stage overrides** (based on ERD Section 8.2):

**Testing gate:**
- Pre-push: Unit tests only (`pytest tests/unit -x`)
- PR: Full test suite (`pytest`)
- Push-to-main: Full suite with strict mode

**Coverage gate:**
- Pre-push: 70% threshold (fast feedback)
- PR: 80% threshold (standard)
- Push-to-main: 85% threshold (highest bar)

**Type checking:**
- Pre-push: Skip (optional, for speed)
- PR: Required
- Push-to-main: Required

---

### 6.3 Phase 3: Monitor and Adjust

**Metrics to track:**
1. Pre-push hook execution time (target: <60s)
2. Bypass rate by stage (if >10%, thresholds too strict)
3. CI failure rate (if high, pre-push not catching issues)

**Adjustment criteria:**
- If pre-push >90s → Lower pre-push requirements further
- If CI failures >5% → Increase pre-push requirements
- If bypasses >10% → Lower thresholds

---

## 7. Example: Workflow Comparison

### 7.1 Before (Current State)

**Pre-push** (local):
```
✅ Testing: pytest --tb=short -q (300s timeout)
✅ Coverage: 80% threshold
✅ Type checking: mypy .
✅ Linting: ruff

Total time: ~5 minutes (too slow for local development)
```

**CI** (pull request):
```
✅ Testing: pytest --tb=short -q (300s timeout)
✅ Coverage: 80% threshold
✅ Type checking: mypy .
✅ Linting: ruff

Total time: ~5 minutes (same as local)
```

**Problem**: Local development slowed by comprehensive checks.

---

### 7.2 After (Stage-Aware with Highest Standard by Default)

**Base Configuration** (represents push-to-main requirements):
```yaml
# This is the DEFAULT - enforced everywhere unless relaxed
testing: pytest --tb=short (600s timeout, full suite, full traceback)
coverage: 85% threshold
type_checking: mypy . (required)
linting: ruff (required)
```

**Pre-push** (local with relaxations applied):
```
✅ Testing: pytest tests/unit -x (60s timeout, unit only)  [RELAXED from base]
✅ Coverage: 70% threshold  [RELAXED from 85%]
❌ Type checking: skipped  [RELAXED - disabled locally]
✅ Linting: ruff  [NO RELAXATION - same as base]

Total time: ~90 seconds (fast feedback)
```

**CI - Pull Request** (moderate relaxations):
```
✅ Testing: pytest --tb=short -q (300s timeout, full suite)  [RELAXED from base]
✅ Coverage: 80% threshold  [RELAXED from 85%]
✅ Type checking: mypy .  [NO RELAXATION - same as base]
✅ Linting: ruff  [NO RELAXATION - same as base]

Total time: ~5 minutes (comprehensive)
```

**CI - Push to Main** (NO relaxations = uses base):
```
✅ Testing: pytest --tb=short (600s timeout, full traceback)  [BASE = STRICTEST]
✅ Coverage: 85% threshold  [BASE = HIGHEST]
✅ Type checking: mypy .  [BASE = REQUIRED]
✅ Linting: ruff  [BASE = REQUIRED]

Total time: ~6 minutes (strictest enforcement)
```

**Key Benefit**:
- **Fast local feedback** (90s) via explicit relaxations
- **Comprehensive CI checks** (5-6min) enforced by default
- **Safety guarantee**: New gates auto-enforced everywhere (can't forget to enable)

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Test stage relaxation application:**
```python
def test_apply_stage_relaxations_pre_push():
    """Test pre-push stage relaxes coverage threshold from base."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")

    # Apply pre-push relaxations
    config = _apply_stage_relaxations(config, "pre-push")

    # Verify relaxations applied (base = 85%, relaxed to 70%)
    assert config.gates["coverage"].threshold == 70
    assert config.gates["type_checking"].enabled is False  # Relaxed (base = True)


def test_apply_stage_relaxations_pr():
    """Test PR stage applies moderate relaxations."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")

    config = _apply_stage_relaxations(config, "pr")

    # Verify relaxations (base = 85%, relaxed to 80%)
    assert config.gates["coverage"].threshold == 80
    assert config.gates["type_checking"].enabled is True  # Not relaxed


def test_apply_stage_relaxations_push_to_main():
    """Test push-to-main uses base config (NO relaxations)."""
    config = load_config("tests/fixtures/quality-gates-with-stages.yaml")

    config = _apply_stage_relaxations(config, "push-to-main")

    # Verify NO relaxations (uses base = strictest)
    assert config.gates["coverage"].threshold == 85  # Base threshold
    assert config.gates["testing"].timeout_seconds == 600  # Base timeout


def test_new_gate_enforced_everywhere():
    """Test that new gates without relaxations are enforced at all stages."""
    config = load_config("tests/fixtures/quality-gates-with-new-gate.yaml")

    # New gate has no relaxations configured
    assert "security_scan" in config.gates
    assert config.gates["security_scan"].required is True

    # Apply pre-push relaxations
    config_pre_push = _apply_stage_relaxations(config, "pre-push")

    # New gate still required (no relaxation configured)
    assert config_pre_push.gates["security_scan"].required is True  # Safety by default!
```

---

### 8.2 Integration Tests

**Test pre-push hook with stage relaxations:**
```bash
# Setup
git init /tmp/test-repo
cd /tmp/test-repo
ln -s $PWD/org-standards/git-hooks/pre-push .git/hooks/pre-push

# Add quality-gates.yaml with stage relaxations
# Base config = 85% coverage (strictest)
# Pre-push relaxation = 70%
# PR relaxation = 80%
cp tests/fixtures/quality-gates-with-stages.yaml org-standards/config/quality-gates.yaml

# Test: Pre-push should use 70% threshold (relaxed from base 85%)
git add .
git commit -m "test"
git push  # Should succeed with 70% coverage

# Test: CI (PR) should use 80% threshold (relaxed from base 85%)
export GITHUB_ACTIONS=true
export GITHUB_EVENT_NAME=pull_request
python3 -c "from quality_gates import load_config, execute_gates; ..."
# Should require 80% coverage

# Test: CI (push-to-main) should use 85% threshold (base = strictest)
export GITHUB_REF=refs/heads/main
python3 -c "from quality_gates import load_config, execute_gates; ..."
# Should require 85% coverage (NO relaxation)
```

---

## 9. Documentation Updates

### 9.1 Update quality-gates.yaml Comments

Add section explaining stage overrides:
```yaml
# Stage Relaxations (OPTIONAL)
#
# PHILOSOPHY: Base configuration = HIGHEST STANDARD (push-to-main requirements)
#             Stage relaxations = Explicit opt-out for earlier stages
#
# Example: Configure relaxations for local development speed
#
# stage_relaxations:
#   pre-push:        # Local enforcement before push
#     threshold: 70  # RELAXED from base (e.g., 85%)
#     enabled: false # SKIP locally (base requires it)
#   pr:              # CI enforcement for pull requests
#     threshold: 80  # RELAXED slightly from base (e.g., 85%)
#   # push-to-main: NO RELAXATION = uses base config (strictest)
#
# KEY PRINCIPLE:
#   - If you add a new gate, it's enforced EVERYWHERE by default
#   - If local dev is too slow, you configure explicit relaxation
#   - Safety by default, convenience by configuration
#
# Available stages:
#   - pre-push: Pre-push hook (local)
#   - pr: Pull request CI checks
#   - push-to-main: Direct push to main branch (uses base config, no relaxation)
#
# Relaxable fields:
#   - enabled: true/false (can disable for earlier stages)
#   - threshold: integer (can lower for earlier stages)
#   - required: true/false (can make optional for earlier stages)
#   - timeout_seconds: integer (can shorten for earlier stages)
#   - command: string (can simplify for earlier stages)
```

---

### 9.2 Update CLAUDE.md

Add section on stage-aware gates:
```markdown
## Quality Gates - Stage-Aware Configuration

Quality gates run different checks at different stages:

**Pre-push** (local, fast feedback ~90s):
- Unit tests only
- 70% coverage threshold
- Skip type checking (optional)

**Pull Request** (CI, comprehensive ~5min):
- Full test suite
- 80% coverage threshold
- Type checking required

**Push to Main** (CI, strictest ~6min):
- Full test suite with detailed output
- 85% coverage threshold
- All checks required

Configure via `org-standards/config/quality-gates.yaml` → `stage_overrides` section.
```

---

## 10. Risks and Mitigations

### Risk 1: Stage Overrides Too Permissive

**Risk**: Pre-push stage set too low → Issues slip through to CI

**Mitigation**:
1. Monitor CI failure rate (target: <5%)
2. If CI failures >5% for 2 weeks → Raise pre-push requirements
3. Emergency bypass logs show if developers bypass frequently

---

### Risk 2: Stage Detection Fails

**Risk**: Auto-detection picks wrong stage → Wrong thresholds applied

**Mitigation**:
1. Explicit `phase` parameter overrides auto-detection
2. Log detected stage: `print(f"🎯 Stage: {stage}")`
3. Integration tests verify detection in CI environment

---

### Risk 3: Configuration Complexity

**Risk**: Too many stage overrides → Config hard to understand

**Mitigation**:
1. Only override what varies (keep defaults for common values)
2. Clear comments in quality-gates.yaml
3. Example configurations in docs

---

## 11. Success Criteria

**Must Have** (Phase 1):
- ✅ Pre-push hook execution time <90s (median)
- ✅ CI enforcement remains comprehensive (no gaps)
- ✅ Backward compatibility (existing configs work)

**Should Have** (Phase 2):
- ✅ Developer bypass rate <10%
- ✅ CI failure rate <5% (pre-push catching issues)
- ✅ Documentation updated with examples

**Nice to Have** (Phase 3):
- ✅ Auto-adjust thresholds based on bypass rate
- ✅ Stage-specific failure messages
- ✅ Dashboards showing stage performance

---

## 12. Open Questions

**Q1**: Should we support custom stage names (e.g., `canary`, `staging`)?
- **Recommendation**: Start with 3 stages (pre-push, pr, push-to-main), add more if needed

**Q2**: Should stage overrides apply to `execution_order`?
- **Recommendation**: No, keep execution order consistent. Use `enabled: false` to skip gates.

**Q3**: Should we validate stage names (reject unknown stages)?
- **Recommendation**: Yes, fail-fast if typo in stage name. Prevents silent failures.

---

## 13. Next Steps

### 13.1 Implementation Tasks (3-4 hours)

1. **Update quality_gates.py** (2h):
   - Add `stage_overrides` field to `GateConfig`
   - Implement `_apply_stage_overrides()`
   - Implement `_detect_stage()`
   - Update `execute_gates()` to apply overrides

2. **Add tests** (1h):
   - Unit tests for override application
   - Integration test for pre-push hook
   - Integration test for CI detection

3. **Update quality-gates.yaml** (30min):
   - Add example stage overrides (commented out)
   - Add documentation section

4. **Update docs** (30min):
   - Update CLAUDE.md with stage-aware examples
   - Update README with new configuration options

---

### 13.2 Rollout Plan

**Phase 1** (Canary - 48 hours):
1. Implement stage override support (backward compatible)
2. Deploy to org-standards repo only
3. Verify pre-push hook still works (no overrides yet)

**Phase 2** (Limited - 1 week):
1. Add stage overrides to quality-gates.yaml
2. Test in org-standards + syra repos
3. Monitor execution times and bypass rates

**Phase 3** (Full Rollout):
1. Update org-standards submodule in all repos
2. All repos automatically get stage-aware behavior
3. Monitor metrics, adjust thresholds as needed

---

## 14. Conclusion

**Proposed Solution**: Add `stage_relaxations` section to each gate in quality-gates.yaml, with base configuration representing the **highest standard** (push-to-main requirements) and explicit relaxations for earlier stages.

**Key Philosophy**: **Strictest by default, relax as needed** (opt-out, not opt-in)

**Benefits**:
- **Safety by default**: New gates auto-enforced everywhere
- Fast local feedback (~90s pre-push) via explicit relaxations
- Comprehensive CI checks (~5min PR, ~6min push-to-main)
- Single source of truth (one config file)
- Backward compatible (no breaking changes)
- Prevents accidental quality regressions

**Alignment with User Requirements**:
- ✅ "Use highest standard by default"
- ✅ "Configure relaxation" for local speed
- ✅ "New gate enforced at all stages" unless explicitly relaxed
- ✅ Implements ERD "Tiered Gates" pattern (Section 8.2)

**User Confirmation Needed**:
1. Approve overall design approach (highest standard by default with relaxations)
2. Approve terminology ("stage_relaxations" not "stage_overrides")
3. Approve initial thresholds (base=85%, PR relaxed to 80%, pre-push relaxed to 70%)
4. Approve implementation plan (3-4 hours)

---

**Ready to proceed with implementation?**
