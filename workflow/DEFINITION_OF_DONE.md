# Definition of Done (DoD) Standards

**Purpose**: Ensure tasks meet quality standards before being marked complete

**Applies to**: All projects (fashion-extract, syra, playground, etc.)

**Date**: 2025-01-13

---

## Overview

Definition of Done provides clear completion criteria for different task types. DoD must be:
1. **Documented** - Explicit criteria, not implicit
2. **Enforced** - CI blocks merge if not met
3. **Verified Early** - Check during work, not at merge
4. **Task-Specific** - Different DoD for different tasks

---

## DoD Framework

### Three-Layer Enforcement

**Layer 1: Documentation** (This file)
- Clear completion criteria
- Task-specific checklists
- Verification commands

**Layer 2: Bot Awareness** (CLAUDE.md)
- Bots read DoD before starting
- Bots verify DoD before claiming "done"
- Bots prompt human when complete

**Layer 3: CI Enforcement** (GitHub Actions)
- Required checks block merge
- Branch protection (no bypass)
- Clear error messages

---

## DoD by Task Type

### Coding Tasks

**Completion Criteria**:
- [ ] **All existing tests pass** (no regressions)
- [ ] **New unit tests added** (for all new functions/classes)
- [ ] **Integration tests identified** (document which needed)
- [ ] **Integration tests added** (if in scope, or create issue)
- [ ] **Code coverage ≥80%** (or maintains existing)
- [ ] **Type hints present** (all function parameters/returns)
- [ ] **Docstrings present** (all public functions, Google style)
- [ ] **Linting passes** (Ruff format + check)
- [ ] **Type checking passes** (MyPy no errors)
- [ ] **Pre-commit hooks pass** (all hooks green)
- [ ] **No skipped tests** (without documented reason)
- [ ] **Standards compliant** (follows project CLAUDE.md)
- [ ] **Imports resolve** (no sys.path manipulation)
- [ ] **No excessive mocking** (only external dependencies)
- [ ] **Documentation updated** (if interfaces changed)

**Verification Commands**:
```bash
# Run these before claiming "done"
ruff format . && ruff check .        # Linting
mypy src/                             # Type checking
pytest                                # All tests
pytest --cov=src --cov-fail-under=80 # Coverage
pre-commit run --all-files            # Pre-commit hooks
```

**CI Enforcement** (Required Checks):
```yaml
required_checks:
  - ruff-format-check
  - ruff-lint-check
  - mypy-type-check
  - pytest-all
  - pytest-coverage-80
  - pre-commit-hooks
  - no-skipped-tests
```

**Bot Behavior**:
```
1. After writing code:
   Bot: "Verifying DoD before marking complete..."
   Bot: [Runs verification commands]

2. If DoD fails:
   Bot: "DoD check: ❌ Coverage 73% (need 80%). Adding more tests..."
   Bot: [Fixes issue]
   Bot: [Re-runs verification]

3. When DoD passes:
   Bot: "✅ DoD Complete:
   - All tests pass (142 passed)
   - Coverage: 84%
   - Ruff: Passing
   - MyPy: No errors
   - Pre-commit: All hooks green

   Ready to create PR?"
```

---

### BRD Tasks

**Completion Criteria**:
- [ ] **Problem statement** includes 5-level root cause analysis
- [ ] **Business requirements** have measurable success criteria
- [ ] **Scope** clearly defines in-scope vs. out-of-scope
- [ ] **Risks identified** with mitigation strategies
- [ ] **Timeline** includes phases with milestones
- [ ] **Stakeholders** identified
- [ ] **Open questions** documented
- [ ] **Appendix** includes comprehensive issue inventory
- [ ] **Template structure** followed
- [ ] **Human approval** (signature)

**CI Enforcement**:
```yaml
required_checks:
  - markdown-lint
  - required-sections-present
  - links-valid
```

**Bot Behavior**:
```
Bot: "BRD checklist complete. Ready for your approval?"
```

---

### PRD Tasks

**Completion Criteria**:
- [ ] **Solution architecture** defined
- [ ] **Requirements** link back to BRD business requirements
- [ ] **User stories** have acceptance criteria
- [ ] **Technical constraints** documented
- [ ] **Dependencies** identified
- [ ] **Success metrics** defined
- [ ] **References BRD** (by link)
- [ ] **Template structure** followed
- [ ] **Human approval**

**CI Enforcement**:
```yaml
required_checks:
  - markdown-lint
  - required-sections-present
  - links-to-brd-valid
```

**Bot Behavior**:
```
Bot: "PRD addresses all BRD requirements. Ready for approval?"
```

---

### ERD Tasks

**Completion Criteria**:
- [ ] **Technical design** specified (components, interfaces, data flow)
- [ ] **Implementation plan** with tasks
- [ ] **Testing strategy** defined
- [ ] **Migration strategy** defined (if applicable)
- [ ] **Performance considerations** addressed
- [ ] **Security considerations** addressed
- [ ] **References PRD and BRD** (by link)
- [ ] **Template structure** followed
- [ ] **Human approval**

**CI Enforcement**:
```yaml
required_checks:
  - markdown-lint
  - required-sections-present
  - links-to-prd-brd-valid
  - diagrams-render
```

**Bot Behavior**:
```
Bot: "ERD covers all PRD requirements. Ready for implementation approval?"
```

---

## Implementation Guide

### Step 1: Add to Project CLAUDE.md

**In project/CLAUDE.md**:
```markdown
## MANDATORY: Definition of Done

See [org-standards/workflow/DEFINITION_OF_DONE.md](/path/to/org-standards/workflow/DEFINITION_OF_DONE.md)

**Quick Reference for Coding Tasks**:

Before claiming ANY coding task is complete:
1. ✅ All tests pass
2. ✅ Coverage ≥80%
3. ✅ Ruff format/check pass
4. ✅ MyPy no errors
5. ✅ Pre-commit hooks pass
6. ✅ New tests added
7. ✅ Integration tests identified
8. ✅ Documentation updated

**Verification**:
\`\`\`bash
ruff format . && ruff check .
mypy src/
pytest --cov=src --cov-fail-under=80
pre-commit run --all-files
\`\`\`

**DO NOT claim "done" until ALL checks pass.**
```

### Step 2: Create GitHub Issue Templates

**.github/ISSUE_TEMPLATE/coding-task.md**:
```markdown
---
name: Coding Task
about: Task involving code changes
---

## Task Description
[What needs to be done]

## Definition of Done
- [ ] All existing tests pass
- [ ] New unit tests added
- [ ] Integration tests identified/added
- [ ] Coverage ≥80%
- [ ] Ruff format/check pass
- [ ] MyPy no errors
- [ ] Pre-commit hooks pass
- [ ] Type hints present
- [ ] Docstrings present
- [ ] Documentation updated

## Verification
\`\`\`bash
ruff format . && ruff check .
mypy src/
pytest --cov=src --cov-fail-under=80
pre-commit run --all-files
\`\`\`

Check off each item as you complete it.
```

### Step 3: Configure Branch Protection

**Repository Settings → Branches → Add Rule**:
- Branch name pattern: `main`
- Require pull request reviews: ✅
- Require status checks: ✅
  - ruff-format-check
  - ruff-lint-check
  - mypy-type-check
  - pytest-all
  - pytest-coverage-80
  - pre-commit-hooks
- Do not allow bypassing: ✅
- Require linear history: ✅

### Step 4: Update CI Workflows

**.github/workflows/pr-validation.yml**:
```yaml
name: PR Validation (DoD Enforcement)

on: [pull_request]

jobs:
  definition-of-done:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install ruff mypy pytest pytest-cov pre-commit
          pip install -e .

      - name: Ruff Format Check
        run: ruff format --check .

      - name: Ruff Lint Check
        run: ruff check .

      - name: MyPy Type Check
        run: mypy src/

      - name: Run All Tests
        run: pytest

      - name: Check Coverage ≥80%
        run: pytest --cov=src --cov-fail-under=80 --cov-report=term-missing

      - name: Pre-commit Hooks
        run: pre-commit run --all-files

      - name: Check No Skipped Tests
        run: |
          skipped=$(pytest --collect-only -q | grep "skipped" | wc -l)
          if [ $skipped -gt 0 ]; then
            echo "ERROR: $skipped skipped tests found"
            exit 1
          fi
```

---

## Anti-Patterns to Avoid

❌ **Claiming "done" without verification**
```
# BAD
Bot: "I've written the code. Task complete!"
[Hasn't run tests, linting, or type checking]
```

✅ **Verify DoD before claiming done**
```
# GOOD
Bot: "Code written. Verifying DoD..."
Bot: [Runs all verification commands]
Bot: "✅ All DoD criteria met. Ready for PR?"
```

❌ **Skipping tests without reason**
```python
# BAD
@pytest.skip("TODO: Fix later")
def test_important_feature():
    ...
```

✅ **Document reason and deadline for skipped tests**
```python
# GOOD
@pytest.skip("Blocked by Issue #123, will fix by 2025-01-20")
def test_important_feature():
    ...
```

❌ **Adding tests that don't run or assert**
```python
# BAD - Test doesn't actually test anything
def test_process_data():
    process_data()  # No assertions!
```

✅ **Tests have clear assertions**
```python
# GOOD
def test_process_data():
    result = process_data([1, 2, 3])
    assert result == [2, 4, 6]
    assert len(result) == 3
```

---

## FAQs

**Q: Can I skip DoD for trivial changes (<5 lines)?**
A: Most DoD still applies. At minimum: tests pass, linting passes, no regressions.

**Q: What if coverage drops below 80% due to untestable code?**
A: Document why it's untestable, add `# pragma: no cover` with justification, maintain existing coverage.

**Q: Can I merge if CI fails but I know it's a flake?**
A: No. Fix the flaky test or document why it's flaky. Never bypass CI.

**Q: Who approves exemptions to DoD?**
A: Tech lead or repository owner only. Must be documented with reason and deadline.

**Q: How do I know which integration tests to add?**
A: Identify component boundaries. Test interactions across boundaries. If unsure, create issue: "Identify integration tests for [feature]"

---

## Metrics

Track these to measure DoD effectiveness:

- **CI Pass Rate**: Should be >95% (excluding legitimate failures)
- **Time to Fix CI Failures**: Should be <1 hour
- **Rework Rate**: Tasks marked "done" but reopened should be <10%
- **Coverage Trend**: Should maintain or increase, never decrease
- **Skipped Tests**: Should be <5% of total tests

---

## Version History

- **2025-01-13**: Initial version (DoD for coding, BRD, PRD, ERD tasks)

---

## Related Documents

- [org-standards/python/README.md](../python/README.md) - Python standards
- [org-standards/CONFIG_PHILOSOPHY.md](../CONFIG_PHILOSOPHY.md) - Configuration standards
- fashion-extract/.ai-sessions/2025-01-13/learning-definition-of-done.md - Detailed learning log
