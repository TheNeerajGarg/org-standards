# Grandfather Policy: Technical Debt Management

**Effective Date**: 2025-10-22
**Status**: ACTIVE

---

## Policy Statement

**Any file you touch, you must clean**. We grandfather existing technical debt but require all modified files to meet current quality standards.

---

## Principles

### 1. Boy Scout Rule
> "Always leave the campground cleaner than you found it."

When you modify a file, you must fix ALL quality issues in that file, not just the lines you changed.

### 2. No New Debt
New files and new code must meet all quality standards from day one. No exceptions.

### 3. Gradual Improvement
By requiring cleanup on touch, we gradually eliminate technical debt without blocking current work.

---

## How It Works

### CI/CD Checks Modified Files Only

**Before (blocking on all debt)**:
```yaml
extra_args: --all-files  # ❌ Checks entire codebase, fails on old debt
```

**After (grandfather existing, enforce on modified)**:
```yaml
extra_args: --from-ref origin/main --to-ref HEAD  # ✅ Only checks changed files
```

### What Gets Checked

**Modified files must pass ALL**:
- ✅ Linting (ruff, black, isort)
- ✅ Type checking (mypy)
- ✅ Test coverage (80% minimum)
- ✅ Pre-commit hooks (all of them)
- ✅ Import validation
- ✅ Test generation requirements
- ✅ Mock usage patterns
- ✅ Base test class usage

**Untouched files**:
- ⚠️ May have quality issues (grandfathered)
- 📝 Should be cleaned when next modified
- 🚫 Cannot add new issues

---

## Examples

### Example 1: Fix Bug in Old File

**Scenario**: Fix bug in `src/old_module.py` (has 50 linting warnings)

**Required**:
1. Fix the bug
2. Fix ALL 50 linting warnings
3. Add/update tests to 80% coverage
4. Ensure all pre-commit hooks pass

**Rationale**: You touched the file, you own cleaning it.

### Example 2: Add Feature to New File

**Scenario**: Create `src/new_feature.py`

**Required**:
1. Write the feature
2. Write comprehensive tests (80%+ coverage)
3. Pass all linting from the start
4. Document properly

**Rationale**: New code starts clean, no exceptions.

### Example 3: Refactor Across Multiple Files

**Scenario**: Rename function used in 10 files (5 clean, 5 dirty)

**Required**:
- Clean files: Just update the function call
- Dirty files: Update call + clean ALL issues in each file

**Rationale**: If you open a file to edit it, clean it fully.

---

## Benefits

### For Developers

**Predictable scope**:
- Know exactly what you need to clean (only files you touch)
- Not blocked by technical debt in unrelated files
- Freedom to choose which files to refactor

**Learning opportunity**:
- Fixing old issues teaches good patterns
- Understand why standards exist
- Build cleaner code habits

### For Codebase

**Guaranteed improvement**:
- Every PR makes at least some files cleaner
- High-churn files get cleaned quickly
- Low-touch files stay dirty longer (but they're low-risk)

**No regression**:
- Can't add new linting warnings
- Can't reduce test coverage
- Can't introduce bad patterns

---

## Exceptions

### When You Can Skip Cleanup

**Emergency hotfixes ONLY**:
- Production down
- Security vulnerability
- Data loss in progress

**Process**:
1. Get explicit approval from team lead
2. Use `--no-verify` if absolutely necessary
3. Create follow-up ticket to clean the file
4. Clean within 48 hours

### When You Must Clean Anyway

**No exceptions for**:
- "It's too much work" - Then don't touch the file
- "It's not my code" - You're touching it, you own it
- "I'm in a hurry" - Plan time for cleanup
- "The file is too big" - Break it down first

---

## Monitoring

### Tracking Debt Reduction

**Metrics**:
```bash
# Current quality debt
ruff check . --statistics
mypy src/ --report

# Track over time
git log --since="1 month ago" --name-only | sort -u | wc -l  # Files touched
# Compare to debt reduction in those files
```

### Success Criteria

**Good signals**:
- Linting warnings decrease month-over-month
- Test coverage increases steadily
- Pre-commit failures decrease
- CI/CD passes more often

**Bad signals**:
- Same files failing repeatedly (not getting cleaned)
- Developers avoiding touching dirty files
- --no-verify usage increasing

---

## FAQ

### "What if the file has 1000 issues?"

**Option 1**: Don't touch that file if you can avoid it

**Option 2**: Clean it in phases:
1. PR 1: Fix the critical issue + 20% of linting
2. PR 2: Add the feature + 20% more linting
3. Continue until file is clean

**Option 3**: Refactor the file completely (preferred)

### "What if I'm just updating a comment?"

**Yes, clean it**. Touching is touching. Comments count.

Exception: Documentation-only changes (README, .md files) don't require cleaning Python code.

### "How do I know what needs cleaning?"

```bash
# Check before you commit
pre-commit run --files path/to/your/file.py

# See all issues
ruff check path/to/your/file.py
mypy path/to/your/file.py
pytest --cov=src/module tests/test_module.py
```

### "What about generated files?"

Generated files are excluded from quality checks (e.g., `.ai-sessions/`, `build/`, `.venv/`).

See `.pre-commit-config.yaml` exclude patterns.

---

## Implementation

### CI/CD Changes

**Files modified**:
- `.github/workflows/ci.yml` - Changed `--all-files` to `--from-ref origin/main --to-ref HEAD`
- `.github/workflows/enhanced-ci.yml` - Same change

**Effect**:
- Pre-commit hooks only run on files changed in this PR
- Existing technical debt doesn't block CI/CD
- Any file you modify must be fully clean

### Local Development

**Pre-commit (on commit)**:
- Runs on staged files only (already worked this way)
- Fast, focused checks

**Pre-push**:
- Runs full test suite
- Linting warnings (informational)
- Doesn't block on warnings in untouched files

---

## Related Documents

- [Quality Standards](.claude/quality-standards.md) - What "clean" means
- [Testing Standards](.claude/testing.md) - Test coverage requirements
- [Technical Standards](.claude/technical.md) - Import patterns, sys.path rules

---

## History

**2025-10-22**: Policy created
- Trigger: CI/CD failing on pre-existing quality debt
- Decision: Grandfather existing debt, enforce on touch
- Implemented: Modified CI/CD workflows to check only changed files
