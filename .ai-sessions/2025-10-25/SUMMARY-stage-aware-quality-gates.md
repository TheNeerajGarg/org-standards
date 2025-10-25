# Summary: Stage-Aware Quality Gates Design & Reviews

**Date**: 2025-10-25
**Status**: Ready for user decision
**Related Files**:
- `design-stage-aware-quality-gates.md` - Full design (26K)
- `review-principal-engineer.md` - Architecture review
- `review-test-architect.md` - Testing review

---

## Executive Summary

**Proposed Feature**: Stage-aware quality gates with **highest standard by default**, explicit relaxations for earlier stages

**Key Philosophy**: **Strictest by default, relax as needed** (opt-out, not opt-in)

**Motivation**:
- Current state: Pre-push hook takes ~5 minutes (too slow for local development)
- Desired state: Pre-push ~90s (fast feedback), CI comprehensive (~5-6min), main strictest

**User Requirement Met**:
> "We want to use the highest standard by default, and then configure relaxation. So, if the push to main adds a new gate, that is by default enforced at stages."

---

## Design Highlights

### Configuration Structure

```yaml
gates:
  coverage:
    # BASE CONFIG = HIGHEST STANDARD (push-to-main requirements)
    threshold: 85
    required: true

    # RELAXATIONS for earlier stages (explicit opt-out)
    stage_relaxations:
      pre-push:
        threshold: 70  # Relaxed for fast local feedback
      pr:
        threshold: 80  # Relaxed slightly for PRs
      # push-to-main: No entry = uses base (85%, strictest)
```

###Benefits

1. **Safety by default**: New gates auto-enforced everywhere
2. **Fast local development**: Pre-push ~90s via relaxations
3. **Comprehensive CI**: PR/main use higher standards
4. **Single source of truth**: One YAML file
5. **Backward compatible**: Existing configs work unchanged

---

## Review Results

### Principal Engineer Review: **CONDITIONAL APPROVE**

**Verdict**: Architecture is sound, but implementation needs validation

**Critical Blockers** (must fix before implementation):

1. **Add validation that relaxations don't tighten requirements**
   - Prevent: `threshold: 85` base → `threshold: 90` relaxation (tightening!)
   - Prevent: `stage_relaxations.push-to-main` anti-pattern
   - Prevent: Making optional gates required via relaxation

2. **Add stage name validation**
   - Catch typos: `pre_push` (underscore) → should be `pre-push` (hyphen)
   - Fail-fast with clear error instead of silent failure

3. **Clarify stage=None behavior**
   - Fix misleading code comment
   - Document that manual execution uses strictest standard (safe default)

**Estimated Impact**: +2 hours implementation time (total 5-6 hours)

---

### Test Architect Review: **INSUFFICIENT**

**Verdict**: Current test coverage ~30% - Major gaps in critical areas

**Current Gaps** (0% test coverage):
- ❌ Validation logic (most critical)
- ❌ Error handling
- ❌ Regression testing
- ❌ Performance validation
- ❌ End-to-end workflow

**Critical Test Cases Missing**:

```python
# MUST ADD (blockers):
def test_relaxation_cannot_tighten_threshold()
def test_relaxation_cannot_require_optional_gate()
def test_invalid_stage_name_rejected()
def test_push_to_main_relaxations_rejected()
def test_stage_none_uses_base_config()

# SHOULD ADD (high priority):
def test_pre_push_execution_time_under_90_seconds()
def test_relaxations_actually_improve_speed()
def test_full_developer_workflow()
```

**Estimated Impact**: +1-2 hours test implementation (included in 5-6 hour estimate)

---

## Consolidated Recommendations

### CRITICAL (Must Fix - Blockers)

1. **Implement Validation Logic** (Principal Engineer #1)
   ```python
   def _apply_stage_relaxations(config, stage):
       # Validate no push-to-main relaxations
       if "push-to-main" in gate.stage_relaxations:
           raise ValueError("push-to-main cannot have relaxations")

       # Validate relaxations don't tighten
       if key == "threshold" and value > base_value:
           raise ValueError("Relaxation tightens requirement")

       # Validate stage names
       if stage not in VALID_STAGES:
           raise ValueError(f"Unknown stage '{stage}'")
   ```

2. **Add Validation Tests** (Test Architect)
   - Test that relaxations cannot tighten requirements
   - Test that invalid stage names are rejected
   - Test that push-to-main relaxations are rejected
   - Test that stage=None uses base config

3. **Update Documentation** (Principal Engineer #3)
   - Fix misleading comment about stage=None behavior
   - Document validation rules in quality-gates.yaml
   - Add examples of invalid configurations

### HIGH PRIORITY (Should Fix)

4. **Add Error Handling Tests**
   - Malformed stage_relaxations structure
   - Circular dependencies when gate disabled
   - Conflicting local override + stage relaxation

5. **Add Integration Tests**
   - Full workflow: commit → pre-push → PR → merge
   - Stage detection in different environments
   - Hook execution with relaxations

6. **Add Performance Tests**
   - Verify pre-push <90s target
   - Verify relaxations actually improve speed

### MEDIUM PRIORITY (Nice to Have)

7. **Add Stage Summary Tool**
   ```bash
   python -m quality_gates.summarize
   # Shows what runs at each stage
   ```

8. **Make Branch Names Configurable**
   ```yaml
   stage_detection:
     protected_branches: [main, master, production]
   ```

---

## Implementation Plan (Revised)

### Phase 1: Implementation with Validation (3-4 hours)

1. **Update quality_gates.py** (2-3h):
   - Add `stage_relaxations` field to `GateConfig`
   - Implement `_apply_stage_relaxations()` with validation
   - Implement `_detect_stage()`
   - Update `execute_gates()` to apply relaxations

2. **Add validation logic** (1h):
   - Validate relaxations don't tighten
   - Validate stage names against allowlist
   - Validate no push-to-main relaxations
   - Clear error messages

### Phase 2: Testing (2 hours)

3. **Add unit tests** (1h):
   - Validation tests (tightening, stage names, push-to-main)
   - Relaxation application tests
   - Regression tests

4. **Add integration tests** (1h):
   - Stage detection tests
   - Hook execution tests
   - Full workflow test

### Phase 3: Documentation & Rollout (1 hour)

5. **Update documentation** (30min):
   - quality-gates.yaml comments
   - CLAUDE.md examples
   - Validation error examples

6. **Canary rollout** (48 hours):
   - Deploy to org-standards only
   - Add stage_relaxations to syra (canary)
   - Monitor execution times and bypass rates

**Total Estimated Time**: 5-6 hours implementation + 48 hours canary monitoring

---

## Risk Assessment

**Blast Radius**: MEDIUM-HIGH
- Affects all repos using org-standards
- Changes core quality gate execution
- Validation errors could block legitimate workflows

**Reversibility**: MODERATE
- Can revert code changes (git revert)
- Can rollback org-standards submodule
- Configuration changes backward compatible

**Mitigation Strategy**:
1. Implement validation to prevent misconfigurations
2. Comprehensive testing (validation, regression, integration)
3. Phased rollout (org-standards → syra canary → all repos)
4. Monitoring (execution times, bypass rates, CI failure rates)

---

## Decision Points for User

### 1. Approve Overall Design?

**Question**: Approve "highest standard by default with stage_relaxations" approach?

**Options**:
- ✅ **Approve** - Proceed with implementation (with validation fixes)
- ⚠️ **Revise** - Request changes to design
- ❌ **Reject** - Different approach needed

**Recommendation**: **APPROVE** (architecture is sound, validation fixes address concerns)

---

### 2. Approve Terminology?

**Question**: Use "stage_relaxations" (current) or alternative term?

**Options**:
- ✅ **"stage_relaxations"** - Clear intent, matches semantics (WITH validation)
- ⏸️ **"stage_overrides"** - Neutral term, matches implementation
- ⏸️ **"stage_adjustments"** - Generic term

**Recommendation**: **"stage_relaxations"** with validation enforcement

---

### 3. Approve Initial Thresholds?

**Question**: Approve proposed thresholds for coverage gate?

**Current Proposal**:
- Base (push-to-main): 85%
- PR relaxation: 80%
- Pre-push relaxation: 70%

**Options**:
- ✅ **Approve** - Use proposed thresholds
- ⏸️ **Adjust** - Specify different thresholds
- ⏸️ **Defer** - Start without relaxations, add based on data

**Recommendation**: **Approve** and adjust based on canary monitoring

---

### 4. Approve Implementation Priority?

**Question**: Implement now or defer?

**Options**:
- ✅ **Implement now** - With validation fixes (5-6 hours)
- ⏸️ **Defer** - Gather more data on current pain points
- ⏸️ **Partial** - Implement validation only, no relaxations yet

**Recommendation**: **Implement now** (pain point is real, design is sound with fixes)

---

## Success Criteria

**Must Have** (Phase 1):
- ✅ Pre-push hook execution time <90s (median)
- ✅ CI enforcement remains comprehensive (no gaps)
- ✅ Backward compatibility (existing configs work)
- ✅ Validation prevents misconfigurations

**Should Have** (Phase 2):
- ✅ Developer bypass rate <10%
- ✅ CI failure rate <5% (pre-push catching issues)
- ✅ Documentation updated with examples

**Nice to Have** (Phase 3):
- ✅ Auto-adjust thresholds based on bypass rate
- ✅ Stage-specific failure messages
- ✅ Dashboards showing stage performance

---

## Next Steps

**If Approved**:

1. **User confirms**:
   - Approve overall design
   - Approve "stage_relaxations" terminology
   - Approve initial thresholds
   - Approve implementation priority

2. **Implementation** (5-6 hours):
   - Update quality_gates.py with validation
   - Add comprehensive test suite
   - Update documentation

3. **Canary Rollout** (48 hours):
   - Deploy to org-standards
   - Add stage_relaxations to syra
   - Monitor metrics

4. **Full Rollout** (1 week):
   - Update org-standards submodule in all repos
   - Monitor across all repos
   - Adjust thresholds based on data

---

## Files Reference

1. **Main Design**: `design-stage-aware-quality-gates.md` (26K)
   - Full technical specification
   - Configuration examples
   - Implementation details

2. **Principal Engineer Review**: `review-principal-engineer.md` (3.2K)
   - Architecture assessment
   - Critical concerns
   - Validation requirements

3. **Test Architect Review**: `review-test-architect.md` (4.9K)
   - Testing strategy assessment
   - Missing test cases
   - Test coverage gaps

---

**Ready for user decision on proceeding with implementation.**
