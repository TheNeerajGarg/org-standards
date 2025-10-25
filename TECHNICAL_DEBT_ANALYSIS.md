# Technical Debt Analysis & Execution Plan
**Date:** 2025-10-25
**Goal:** Eliminate grandfather policy by bringing all existing code to org standards compliance

## Executive Summary

This document provides a comprehensive analysis of technical debt across all repositories and outlines prioritized execution plans to achieve 100% compliance with org standards, eliminating the need for grandfather policies.

### Current State Overview

| Repository | Tests | Coverage | Ruff Format | Ruff Lint | MyPy | Critical Issues |
|------------|-------|----------|-------------|-----------|------|-----------------|
| **StyleGuru** | ✅ 1507 passed | ✅ 80.40% | ⚠️ 1 file | ⚠️ 4 errors | ❌ 1 error | LOW |
| **syra** | ✅ 24 passed | ❌ 48.72% | ✅ Pass | ✅ Pass | ❌ 1 error | HIGH |
| **syra-lite-llm** | 🔄 Running | 🔄 Pending | ⚠️ 11 files | ✅ Pass | 🔄 Pending | MEDIUM |

---

## Repository-Specific Analysis

### 1. StyleGuru (Priority: LOW)

**Repository Path:** `/Users/neerajgarg/NeerajDev/StyleGuru`

#### Current Status
- ✅ **Tests:** 1507 passed, 6 skipped (skipped for valid reasons - cost money)
- ✅ **Coverage:** 80.40% (meets 80% threshold)
- ⚠️ **Ruff Format:** 1 file needs reformatting
  - `org-standards/python/quality_gates.py`
- ⚠️ **Ruff Lint:** 4 fixable errors
  - `org-standards/tests/test_quality_gates_stages.py` - Import sorting and unused imports
- ❌ **MyPy:** 1 error
  - `/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/mcp/client/sse.py:108` - Pattern matching syntax error (external dependency)

#### Technical Debt Breakdown

**HIGH Priority:**
- None

**MEDIUM Priority:**
- MyPy configuration needs update to handle Python 3.13 dependency issues
  - Estimated effort: 1 hour
  - Solution: Add `--python-version 3.11` to mypy config or upgrade mcp dependency

**LOW Priority:**
- Ruff formatting: 1 file
  - Estimated effort: 5 minutes
  - Solution: Run `ruff format org-standards/python/quality_gates.py`
- Ruff linting: 4 fixable errors
  - Estimated effort: 5 minutes
  - Solution: Run `ruff check --fix org-standards/tests/test_quality_gates_stages.py`

#### Files with Coverage Below 80%

Per the coverage report, these files have <80% coverage:

**Critical (Below 50%):**
- `src/crawler/domains/ecommerce/nordstrom/__init__.py` - 48.82%
- `src/crawler/domains/ecommerce/zappos/__init__.py` - 50.83%
- `src/crawler/main.py` - 10.45% (likely main entry point)
- `src/crawler/storage/__init__.py` - 61.70%

**Moderate (50-80%):**
- `src/crawler/config/__init__.py` - 75.20%
- `src/extractor/huggingface_provider.py` - 71.82%
- `src/crawler/observability/__init__.py` - 72.82%
- `src/extractor/image_extractor_config_spec.py` - 73.33%

**Note:** Overall coverage is 80.40%, so these files are grandfathered. New changes to these files must meet 80% coverage for the changed lines (differential coverage).

#### Execution Plan - StyleGuru

**Phase 1: Quick Fixes (15 minutes)**
1. Run `ruff format .` to fix formatting
2. Run `ruff check --fix .` to fix linting errors
3. Verify all checks pass

**Phase 2: MyPy Configuration (1 hour)**
1. Option A: Update `pyproject.toml` mypy config:
   ```toml
   [tool.mypy]
   python_version = "3.11"
   ```
2. Option B: Add mcp to mypy excludes
3. Verify `mypy src/` passes

**Phase 3: Coverage Improvements (Optional - 8-12 hours)**
- Add tests for low-coverage files if time permits
- Focus on critical files (<50% coverage)
- This is optional for grandfather policy removal but recommended for code quality

**Total Estimated Time:** 1.25 hours (mandatory) + 8-12 hours (optional coverage improvements)

---

### 2. Syra (Priority: HIGH)

**Repository Path:** `/Users/neerajgarg/NeerajDev/syra`

#### Current Status
- ✅ **Tests:** 24 passed
- ❌ **Coverage:** 48.72% (FAILS - needs 80%)
- ✅ **Ruff Format:** All files formatted
- ✅ **Ruff Lint:** All checks passed
- ❌ **MyPy:** 1 error
  - Duplicate module named "introspection" (conflict between `org-standards/claude-code/introspection` and `./introspection`)

#### Technical Debt Breakdown

**HIGH Priority:**
1. **Coverage Failure (48.72% vs 80% required)**
   - Estimated effort: 16-24 hours
   - Critical uncovered modules:
     - `introspection/core/introspection_generator.py` - 13% coverage
     - `introspection/core/pattern_detector.py` - 11% coverage
     - `introspection/core/failure_tracker.py` - 51% coverage
     - `introspection/hooks/*.py` - 0% coverage (4 files)
     - `setup.py` - 0% coverage
     - `test_lsp_timing.py` - 0% coverage

2. **MyPy Duplicate Module Error**
   - Estimated effort: 30 minutes
   - Solution: Use `--exclude` flag or adjust module structure

**MEDIUM Priority:**
- None

**LOW Priority:**
- None

#### Files Requiring Test Coverage

**Critical (0% coverage - must add tests):**
- `introspection/hooks/post_tool_use.py` - 0% (23 statements)
- `introspection/hooks/pre_tool_use.py` - 0% (54 statements)
- `introspection/hooks/session_end.py` - 0% (31 statements)
- `introspection/hooks/stop.py` - 0% (19 statements)
- `setup.py` - 0% (5 statements)
- `test_lsp_timing.py` - 0% (55 statements)

**Critical (Very low coverage <15%):**
- `introspection/core/introspection_generator.py` - 13% (61 statements, 53 missing)
- `introspection/core/pattern_detector.py` - 11% (157 statements, 140 missing)

**Moderate (50-60% coverage):**
- `introspection/core/failure_tracker.py` - 51% (392 statements, 191 missing)

#### Execution Plan - Syra

**Phase 1: MyPy Fix (30 minutes)**
1. Add to `pyproject.toml`:
   ```toml
   [tool.mypy]
   exclude = ["org-standards/"]
   ```
2. Verify `mypy .` passes

**Phase 2: Critical Test Coverage (16-20 hours)**
Priority order:
1. Add tests for `introspection/hooks/*.py` files (4-6 hours)
   - Focus on post_tool_use.py (54 statements)
   - Focus on pre_tool_use.py (54 statements)
   - Session lifecycle tests

2. Add tests for `introspection/core/introspection_generator.py` (4-6 hours)
   - Core functionality tests
   - Edge cases

3. Add tests for `introspection/core/pattern_detector.py` (4-6 hours)
   - Pattern matching tests
   - Detection algorithms

4. Improve `introspection/core/failure_tracker.py` from 51% to 80% (2-3 hours)
   - Focus on untested code paths
   - Error handling scenarios

**Phase 3: Cleanup (1 hour)**
1. Review and possibly remove or move `test_lsp_timing.py` if it's not a real test
2. Ensure `setup.py` coverage or mark as excluded

**Total Estimated Time:** 17.5-21.5 hours

---

### 3. syra-lite-llm (Priority: MEDIUM)

**Repository Path:** `/Users/neerajgarg/NeerajDev/syra-lite-llm`

#### Current Status
- 🔄 **Tests:** Running (analysis incomplete)
- 🔄 **Coverage:** Pending test completion
- ⚠️ **Ruff Format:** 11 files need reformatting
- ✅ **Ruff Lint:** All checks passed
- 🔄 **MyPy:** Pending analysis

#### Technical Debt Breakdown

**HIGH Priority:**
- TBD pending test completion

**MEDIUM Priority:**
1. **Ruff Formatting Issues**
   - Estimated effort: 15 minutes
   - 11 files need reformatting:
     - `.github/scripts/validate_pr_standards.py`
     - `bots/common/github_utils.py`
     - `bots/common/test_github_utils.py`
     - `bots/implementation-swarm/spike-tests/*.py` (4 files)
     - `introspection/tests/test_error_paths.py`
     - `introspection/tests/test_sustained_load.py`
     - `scripts/claude_cli_wrapper.py`
     - `tests/test_redaction.py`

**LOW Priority:**
- None

#### Execution Plan - syra-lite-llm

**Phase 1: Quick Fixes (15 minutes)**
1. Run `ruff format .` to fix all 11 files
2. Verify formatting passes

**Phase 2: Complete Analysis (Pending)**
1. Complete test run analysis
2. Complete coverage analysis
3. Complete MyPy analysis
4. Update this document with findings

**Phase 3: Remediation (TBD)**
- Based on Phase 2 findings

**Total Estimated Time:** 15 minutes + TBD

---

## Prioritized Execution Plan (All Repositories)

### Sprint 1: Critical Fixes (Week 1)
**Goal:** Fix all HIGH priority issues

1. **Syra Coverage Crisis** (Days 1-4)
   - Add tests for introspection hooks (0% → 80%)
   - Add tests for introspection_generator (13% → 80%)
   - Add tests for pattern_detector (11% → 80%)
   - Estimated: 16-20 hours

2. **Complete syra-lite-llm Analysis** (Day 5)
   - Finish test/coverage/mypy analysis
   - Identify all gaps
   - Estimated: 2-4 hours

3. **Fix All HIGH Priority Issues** (Day 5)
   - Based on findings from syra-lite-llm
   - Estimated: TBD

### Sprint 2: MEDIUM Priority (Week 2)
**Goal:** Fix all MEDIUM priority issues

1. **StyleGuru MyPy Configuration** (Day 1)
   - Update mypy config for Python version
   - Estimated: 1 hour

2. **Syra MyPy Duplicate Module** (Day 1)
   - Add exclude configuration
   - Estimated: 30 minutes

3. **syra-lite-llm Formatting** (Day 1)
   - Run ruff format on all 11 files
   - Estimated: 15 minutes

4. **Any MEDIUM Priority Issues from syra-lite-llm** (Days 2-5)
   - Based on completed analysis
   - Estimated: TBD

### Sprint 3: LOW Priority & Polish (Week 3)
**Goal:** Fix all LOW priority issues and verify compliance

1. **StyleGuru Quick Fixes** (Day 1)
   - Ruff formatting (1 file)
   - Ruff linting (4 errors)
   - Estimated: 15 minutes

2. **Any LOW Priority Issues from Other Repos** (Days 1-2)
   - Based on completed analysis
   - Estimated: TBD

3. **Full Compliance Verification** (Days 3-5)
   - Run all quality gates on all repos
   - Create test matrix showing 100% compliance
   - Document grandfather policy removal
   - Estimated: 4-8 hours

---

## Success Criteria

### Definition of "Grandfather Policy Removed"

All repositories must meet the following criteria:

**Required Quality Gates (Must Pass):**
- ✅ All tests pass
- ✅ Coverage ≥80% (overall project coverage)
- ✅ Ruff format check passes
- ✅ Ruff lint check passes
- ✅ MyPy type checking passes (no errors)

**Additional Standards:**
- ✅ Pre-commit hooks installed and configured
- ✅ GitHub Actions PR validation workflow in place
- ✅ All skipped tests have documented reasons
- ✅ No workarounds or temporary exceptions in CI/CD

### Verification Process

After all phases complete:

1. **Run Quality Gates on All Repos:**
   ```bash
   # StyleGuru
   cd /Users/neerajgarg/NeerajDev/StyleGuru
   ruff format --check .
   ruff check .
   mypy src/
   pytest --cov=src --cov-fail-under=80

   # syra
   cd /Users/neerajgarg/NeerajDev/syra
   ruff format --check .
   ruff check .
   mypy .
   pytest --cov=. --cov-fail-under=80

   # syra-lite-llm
   cd /Users/neerajgarg/NeerajDev/syra-lite-llm
   ruff format --check .
   ruff check .
   mypy .
   pytest --cov=. --cov-fail-under=80
   ```

2. **Document Results:**
   - Create compliance matrix
   - Screenshot all passing quality gates
   - Update org-standards README

3. **Remove Grandfather Policy:**
   - Update CI/CD configurations to remove exemptions
   - Update documentation to remove grandfather policy mentions
   - Announce to team

---

## Risk Assessment

### High Risk Items

1. **Syra Coverage** (High Impact, High Effort)
   - 48.72% → 80% requires significant test development
   - Risk: Introspection code may be difficult to test
   - Mitigation: Break down into smaller chunks, focus on unit tests first

2. **syra-lite-llm Unknown Scope** (Unknown Impact, Unknown Effort)
   - Analysis incomplete
   - Risk: May uncover significant technical debt
   - Mitigation: Complete analysis first before committing to timeline

### Medium Risk Items

1. **MyPy Dependency Issues**
   - May require dependency updates
   - Risk: Updates could introduce breaking changes
   - Mitigation: Test thoroughly after updates

### Low Risk Items

1. **Formatting/Linting Fixes**
   - Automated fixes available
   - Risk: Minimal
   - Mitigation: Review diffs before committing

---

## Next Steps

### Immediate Actions (Next Session)

1. **Complete syra-lite-llm analysis**
   - Finish running tests
   - Check coverage
   - Run mypy
   - Update this document

2. **Create GitHub Issues**
   - One issue per repository with full execution plan
   - Use this document as reference
   - Link issues together for tracking

3. **Begin Sprint 1**
   - Start with Syra coverage improvements
   - Focus on highest impact first

### Long-term Actions

1. **Weekly Progress Reviews**
   - Track completion against sprints
   - Adjust timelines as needed
   - Escalate blockers

2. **Team Communication**
   - Share progress weekly
   - Request help for difficult test scenarios
   - Celebrate milestones

3. **Process Improvement**
   - Document patterns learned
   - Update org-standards with lessons
   - Improve CI/CD based on findings

---

## Appendix

### Quality Gate Reference

From `/Users/neerajgarg/NeerajDev/org-standards/config/quality-gates.yaml`:

```yaml
gates:
  testing:
    enabled: true
    tool: pytest
    command: "pytest --tb=short -q"
    required: true

  coverage:
    enabled: true
    tool: diff-cover
    threshold: 80  # Percentage
    required: true

  type_checking:
    enabled: true
    tool: mypy
    required: true

  linting:
    enabled: true
    tool: ruff
    commands:
      format_check: "ruff format --check ."
      lint_check: "ruff check ."
    required: true
```

### Repository Details

**StyleGuru:**
- Main branch: `main`
- Python files: 246
- Test coverage: 80.40%
- Primary language: Python 3.11+

**syra:**
- Main branch: `main`
- Python files: 101
- Test coverage: 48.72% ❌
- Primary language: Python 3.11+

**syra-lite-llm:**
- Main branch: `fix/ruff-mypy-errors`
- Python files: 94
- Test coverage: Pending
- Primary language: Python 3.11+

### Contact & Resources

- **Org Standards:** `/Users/neerajgarg/NeerajDev/org-standards`
- **Documentation:** `/Users/neerajgarg/NeerajDev/org-standards/README.md`
- **Definition of Done:** `/Users/neerajgarg/NeerajDev/org-standards/workflow/DEFINITION_OF_DONE.md`
- **Quality Gates:** `/Users/neerajgarg/NeerajDev/org-standards/config/quality-gates.yaml`

---

**Document Status:** In Progress
**Last Updated:** 2025-10-25
**Next Review:** After syra-lite-llm analysis completion
