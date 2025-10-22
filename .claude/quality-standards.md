# Code Quality Standards

## MANDATORY: Pre-commit Requirements
All code must pass pre-commit hooks before commit:
- Maximum line length: 100 characters
- All imports properly sorted at top of file
- No unused imports, variables, or f-strings
- All functions have type hints
- No hardcoded secrets or unsafe functions
- Follow PEP 8 naming conventions

## MANDATORY: Formatting
- Run `black . --line-length=100` before committing
- Run `isort . --profile=black` before committing
- Use `pre-commit run --all-files` to check all files

## MANDATORY: Naming Conventions
- **Variables and functions**: snake_case
- **Classes**: PascalCase
- **Constants**: SCREAMING_SNAKE_CASE
- **Configuration keys**: SCREAMING_SNAKE_CASE
- **JSON keys**: snake_case
- **Module names**: snake_case
- **Package names**: snake_case

## MANDATORY: Type Hints
- All function parameters must have type hints
- All function return values must have type hints
- Use `Optional[Type]` instead of `Type | None` for Python < 3.10
- Use `Dict[str, Any]` instead of `dict` for older Python
- Use `List[Type]` instead of `list[Type]` for older Python

## MANDATORY: Documentation
- All public functions must have docstrings
- Use Google-style docstrings
- Include parameter types and return types
- Document exceptions that may be raised

## MANDATORY: Error Handling
- Always handle exceptions explicitly
- Use specific exception types when possible
- Log errors with context
- Never use bare `except:` clauses
- Use `try/except/finally` blocks appropriately

## MyPy Type Checking Standards

### MANDATORY: MyPy Configuration Compliance
- All new code MUST pass MyPy type checking without errors
- MyPy runs as warning-only pre-commit hook
- Test files excluded from strict type checking
- External libraries excluded from missing import checks

### Common MyPy Patterns

**Function return type annotations:**
```python
# ✅ CORRECT
def process_data(data: List[str]) -> Dict[str, Any]:
    """Process input data and return results."""
    return {"processed": data}

def main() -> None:
    """Main function that doesn't return a value."""
    print("Starting application")

# ❌ INCORRECT
def process_data(data):  # Missing type hints
    return {"processed": data}
```

**Variable definition and scope:**
```python
# ✅ CORRECT
def process_file(file_path: Path) -> int:
    """Process file and return count."""
    processed_count = 0  # Define before use
    with open(file_path) as f:
        for line in f:
            processed_count += 1
    return processed_count

# ❌ INCORRECT
def process_file(file_path: Path) -> int:
    with open(file_path) as f:
        for line in f:
            processed_count += 1  # Used before definition
    processed_count = 0
    return processed_count
```

**Path and file operations:**
```python
# ✅ CORRECT
from pathlib import Path

def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory."""
    return list(directory.rglob("*.py"))

# ❌ INCORRECT
def find_python_files(directory: Path) -> List[Path]:
    files = []
    for root, dirs, files in directory.walk():  # .walk() doesn't exist
        for file in files:
            if file.endswith(".py"):
                files.append(Path(root) / file)
    return files
```

## CRITICAL: Adding Dependencies (AIVC Pattern)

**When adding ANY new dependency, ALWAYS follow the AIVC pattern:**

### The AIVC Workflow (Add → Install → Verify → Commit)

```bash
# 1. ADD to requirements.txt
echo "huggingface-hub>=0.20.0" >> requirements.txt

# 2. INSTALL immediately (don't wait!)
pip install 'huggingface-hub>=0.20.0'

# 3. VERIFY import works
python -c "from huggingface_hub import InferenceClient; print('✅ Import successful')"

# 4. COMMIT atomically (requirement + code that uses it)
git add requirements.txt src/extractor/huggingface_provider.py
git commit -m "feat: add HuggingFace provider with huggingface-hub dependency"
```

### Why This Matters

**Single missing dependency = 100% test failure**

When a dependency is in requirements.txt but not installed:
- Python import fails → Module can't load → ALL tests that import it fail
- Result: 50+ test collection errors that look like code bugs but are just missing `pip install`

**Example from 2025-10-18**:
- Added `huggingface-hub>=0.20.0` to requirements.txt
- Didn't run `pip install huggingface-hub`
- Result: 50+ test collection errors, 0 tests could run
- Fix: `pip install huggingface-hub` → 1162 tests collected, 1083 passing

### Anti-Patterns to Avoid

❌ **"I'll install it later"**
```bash
echo "package>=1.0.0" >> requirements.txt
git commit -m "add dependency"  # Without installing!
# Later: Oops, forgot to install. Tests fail.
```

❌ **"Tests will catch it"**
```python
from new_package import Module  # Import fails → tests can't even run
```

❌ **"Someone else will set it up"**
- CI/CD will fail identically
- Other developers will waste time debugging
- You're blocking everyone downstream

### Correct Pattern

✅ **Atomic dependency addition**
```bash
# 1. Add + Install + Verify (BEFORE writing code)
echo "anthropic>=0.70.0" >> requirements.txt
pip install 'anthropic>=0.70.0'
python -c "from anthropic import Anthropic; print('✅ Works')"

# 2. NOW write code that uses it
vim src/extractor/anthropic_provider.py

# 3. Write tests
vim tests/unit/extractor/test_anthropic_provider.py

# 4. Verify everything works
pytest --collect-only  # Check tests can collect (no import errors)
pytest                  # Run tests

# 5. Commit BOTH together
git add requirements.txt src/extractor/anthropic_provider.py tests/
git commit -m "feat: add Anthropic provider with anthropic SDK dependency"
```

### Verification Before Commit

**ALWAYS verify these before committing dependency changes:**

```bash
# 1. Dependency is installed
pip list | grep package-name

# 2. Import works
python -c "import package_name"

# 3. Tests can collect (no import errors)
pytest --collect-only

# 4. Tests pass
pytest
```

### Optional Dependencies (Future Enhancement)

For provider/plugin systems, consider making dependencies optional:

```python
# provider_factory.py
try:
    from .anthropic_provider import AnthropicProvider
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    AnthropicProvider = None

def create_provider(provider_type: str):
    if provider_type == "anthropic":
        if not HAS_ANTHROPIC:
            raise ImportError(
                "Anthropic SDK not installed. "
                "Install with: pip install anthropic>=0.70.0"
            )
        return AnthropicProvider()
```

**Benefits**:
- Adding new provider doesn't break existing functionality
- Users only install SDKs they use
- Clear error messages when trying to use unavailable provider

### Related Documentation

**Full introspection**: `.ai-sessions/2025-10-18/introspection-missing-dependency-installation.md`

**Key insight**: Dependencies are **environment contracts**, not documentation. Adding to requirements.txt without installing is like calling a function you haven't defined yet.

---

## Key Technical Constraints

### Never Do These:
1. **No sys.path manipulation** in production code (conftest.py only)
2. **No automated code modification scripts** (except Black, isort)
3. **No warning suppression** (`--disable-warnings`, `# noqa` without justification)
4. **No skipping tests** without documented reason and deadline
5. **No bare except clauses** - use specific exceptions
6. **No overriding base class attributes** with context managers
7. **No workarounds without fixing root cause** (see below)
8. **No adding dependencies without immediate installation** (see AIVC pattern above)

### Always Do These:
1. **Add type hints** to all functions (parameters and returns)
2. **Write tests** for every new function/class
3. **Use absolute imports** for cross-component imports
4. **Follow naming conventions**: snake_case (vars/functions), PascalCase (classes), SCREAMING_SNAKE_CASE (constants)
5. **Document with Google-style docstrings**
6. **Run pre-commit hooks** before pushing
7. **Apply 5 whys before suggesting solutions** (see below)

## MANDATORY: Root Cause Fixes Over Workarounds

**Organization Mission**: Learn what blocks 10× productivity → **Workarounds hide problems** → Can't learn from them

### When You Encounter a Problem

**If you think of a workaround**:

1. **STOP**: Recognize you're considering a workaround
2. **Apply 5 Whys**: Find root cause
   - Why does this problem exist?
   - Why did that cause the problem?
   - Why did that happen?
   - Why is that the case?
   - What's the root cause?
3. **Propose root cause fix**: "Let me fix X instead"
4. **Ask human**: "Should I fix root cause now or use workaround temporarily?"

### Examples of Workaround Thinking to AVOID

- ❌ "Use `--no-verify` to bypass hook" → ✅ **Fix the hook**
- ❌ "Add exception to rule" → ✅ **Fix why rule doesn't work**
- ❌ "Work around the bug" → ✅ **Fix the bug**
- ❌ "Skip this check" → ✅ **Make check work correctly**
- ❌ "Mock this to make test pass" → ✅ **Fix the architecture**
- ❌ "Hardcode this value" → ✅ **Make it configurable**
- ❌ "Comment out failing test" → ✅ **Fix what the test found**

### When Workarounds Are Acceptable (Rare)

Only in these scenarios:

1. **Emergency hotfix** (production down)
   - MUST file follow-up issue immediately
   - MUST include deadline for root cause fix
   - MUST document workaround clearly

2. **Deliberate technical debt** (conscious trade-off)
   - MUST document trade-off analysis
   - MUST file issue for future fix
   - MUST get human approval

3. **External dependency you can't fix**
   - MUST file issue upstream
   - MUST document limitation
   - MUST revisit when upstream fixes

**In ALL cases**: Workaround MUST be explicitly approved by human and documented with follow-up issue.

### Why This Matters

**This session example**:
- Problem: Pre-commit hook blocks commit (hash chicken-and-egg)
- Workaround suggested: Use `--no-verify`
- Why it's bad: Bypasses safety mechanism, doesn't fix root cause
- Root cause fix: Update hook to auto-stage introspection file after validation

**Historical examples** (from Problem Registry):
- P-001: Excessive mocking = workaround for bad architecture
- P-002: No integration tests = workaround hiding integration bugs
- Both caused 3-4 days wasted per incident

**Pattern**: When facing friction → I suggest workarounds → Problems remain hidden → Can't improve system

**Fix**: When facing friction → Apply 5 whys → Fix root cause → System improves

## MANDATORY: Investigation Before Implementation

**CRITICAL**: Before writing ANY code, you MUST investigate first. Jumping to implementation without investigation is the #1 cause of wasted effort and rework.

### Behavioral Trigger #1: "Before Code, Read Code" (5-10 Minutes MANDATORY)

**When**: Before modifying, migrating, or refactoring ANY code
**Action**: Read BOTH old and new implementations thoroughly
**Time**: Minimum 5-10 minutes of reading BEFORE any coding
**Verification**: Can explain what both do and how they differ

**Example**:
```
❌ WRONG: "Let's migrate these tests!" [starts editing imports]
✅ RIGHT: "Let me first read old tests AND new provider to see if migration is possible" [spends 5-10 min reading]
```

**Why This Matters**:
- 5 minutes of investigation prevents 30+ minutes of futile implementation
- Understanding the problem is 80% of the work; implementation is 20%
- Most "simple" tasks hide architectural mismatches that only investigation reveals

### Behavioral Trigger #2: "Assume Incompatibility" (Default Mindset)

**When**: Dealing with refactored, migrated, or rewritten code
**Action**: Default assumption is OLD and NEW are incompatible until PROVEN otherwise
**Verification**: Must explicitly verify compatibility before attempting migration

**Things to Check for Incompatibility**:
1. **Config systems**: Dict-based vs Dynaconf vs other?
2. **Method signatures**: Same names? Same parameters? Same return types?
3. **Error messages**: Same format? Different text?
4. **Initialization**: Same constructor parameters?
5. **Dependencies**: Same imports? Same external libraries?

**Example**:
```
❌ WRONG: "Just update the imports and it'll work"
✅ RIGHT: "New architecture likely has breaking changes. Let me verify compatibility first."
```

**Why This Matters**:
- Major refactorings (like config system changes) almost always break compatibility
- Assuming compatibility wastes time on migration that won't work
- Better to rewrite from scratch than waste time on failed migration

### Behavioral Trigger #3: "5-Minute Investigation Tax" (MANDATORY Overhead)

**When**: Any task that seems "simple," "obvious," or "quick"
**Action**: MANDATORY 5-minute investigation before ANY implementation
**What to Document**:
1. What does the current code do? (read it)
2. What does the new/target code need to do?
3. Are they compatible? (prove it)
4. What could go wrong? (list 3 non-obvious failure modes)

**Example**:
```
❌ WRONG: [See task] → [Start coding]
✅ RIGHT: [See task] → [5-min investigation] → [Document findings] → [Then code]
```

**Why This Matters**:
- "Simple" tasks often hide complexity that only investigation reveals
- Investigation upfront prevents discovery of blockers mid-implementation
- Prevents the "oops, this won't work" moment after 30 minutes of coding

### Behavioral Trigger #4: "What Could Go Wrong?" (Pre-Completion Check)

**When**: Before declaring anything "done" or "ready"
**Action**: List 3 ways this could fail that aren't immediately obvious
**Verification**: Test or verify each potential failure mode

**Example**:
```
Before: "Import updates done, let's run tests"
After: "What if: (1) Config system changed? (2) Method signatures changed? (3) Error messages changed? Let me check these first."
```

**Why This Matters**:
- Proactive failure identification prevents "ship and discover bug" pattern
- Forces thinking about edge cases and architectural assumptions
- Catches issues before they become blockers

### Metrics for Behavioral Change Success

Track these to verify behavior is changing:

**Metric 1: Investigation Time Ratio**
- Formula: `(Investigation time) / (Total task time)`
- Target: ≥30% for any new task
- How to measure: Document investigation start/end times

**Metric 2: Discovery Point of Issues**
- Metric: % of issues discovered DURING investigation vs AFTER implementation starts
- Target: 80% discovered during investigation
- How to measure: Note when each issue was discovered

**Metric 3: Rework Rate**
- Formula: `(Tasks requiring rework) / (Total tasks completed)`
- Target: <10%
- How to measure: Count tasks that needed significant changes after "done"

### When to Skip Investigation (Rare)

**Only skip investigation if ALL of these are true**:
1. ✅ You wrote the original code recently (<1 week ago)
2. ✅ No one else has modified it since
3. ✅ Change is purely additive (no modifications to existing code)
4. ✅ No architecture or pattern changes involved

**In ALL other cases**: Investigation is MANDATORY.

## MANDATORY: Definition of Done (DoD)

**Full DoD Reference**: [org-standards/workflow/DEFINITION_OF_DONE.md](https://github.com/TheNeerajGarg/org-standards/blob/main/workflow/DEFINITION_OF_DONE.md)

### DoD for Coding Tasks (Quick Reference)

**Before claiming ANY coding task is complete, you MUST verify ALL of these**:

1. ✅ **All existing tests pass** - No regressions (`pytest`)
2. ✅ **New unit tests added** - For all new functions/classes (70% of test effort)
3. ✅ **Integration tests added** - Real API/DB calls when applicable (20% of test effort)
4. ✅ **System tests identified** - End-to-end scenarios (10% of test effort)
5. ✅ **Coverage ≥80%** - Or maintains existing (`pytest --cov=src --cov-fail-under=80`)
6. ✅ **Test pyramid verified** - 70% unit / 20% integration / 10% system
7. ✅ **Ruff format/check pass** - Linting compliant (`ruff format . && ruff check .`)
8. ✅ **MyPy no errors** - Type safety (`mypy src/`)
9. ✅ **Pre-commit hooks pass** - All hooks green (`pre-commit run --all-files`)
10. ✅ **Type hints present** - All function parameters and returns
11. ✅ **Docstrings present** - All public functions (Google style)
12. ✅ **Documentation updated** - If interfaces changed
13. ✅ **Dead code removed** - For refactoring: old code deleted, references migrated (see below)

### DoD for Refactoring/Architecture Changes (ADDITIONAL REQUIREMENTS)

**When refactoring or changing architecture, you MUST ALSO verify**:

14. ✅ **Old code identified** - List all files being replaced/superseded
15. ✅ **References migrated** - ALL imports, tests, docs updated to new code
16. ✅ **Old files removed** - Dead code deleted (or marked deprecated with timeline)
17. ✅ **No broken imports** - Linting/type checking passes after removal
18. ✅ **Tests target new code** - Coverage measured against ACTIVE codebase only
19. ✅ **Architecture docs updated** - Document the new architecture

**Why This Matters**:
- Dead code with tests creates FALSE confidence
- Tests passing on dead code masks real coverage gaps
- Refactoring is incomplete without: Add New + Migrate References + Remove Old

**Verification Commands** (run these before claiming "done"):
```bash
# Run ALL of these - ALL must pass
ruff format . && ruff check .                    # Linting
mypy src/                                        # Type checking
pytest                                           # All tests
pytest --cov=src --cov-fail-under=80            # Coverage ≥80%
pre-commit run --all-files                       # Pre-commit hooks
```

**DO NOT claim task is "done" until ALL checks pass.**

**If ANY check fails**:
1. Fix the issue immediately
2. Re-run ALL verification commands
3. Only when ALL pass → claim "done" and create PR

**Expected Bot Behavior**:
```
After writing code:
Bot: "Let me verify DoD before marking this complete..."
Bot: [Runs ruff format . && ruff check .]
Bot: [Runs mypy src/]
Bot: [Runs pytest]
Bot: [Runs pytest --cov=src --cov-fail-under=80]
Bot: [Runs pre-commit run --all-files]

If any check fails:
Bot: "DoD check: ❌ Coverage 73% (need 80%). Adding more tests..."
Bot: [Adds tests]
Bot: [Re-runs ALL verification commands]

When all checks pass:
Bot: "✅ DoD Verification Complete:
- Tests: 142 passed, 0 failed
- Coverage: 84% (meets 80% requirement)
- Ruff: Passing
- MyPy: No errors
- Pre-commit: All hooks green

Ready to create PR?"
```

**GitHub CI Enforcement**: All these checks run in CI and BLOCK merge if they fail. No bypass, even for bots.

### CRITICAL: Implementation Plan Template

**When creating ANY implementation plan for a coding task, you MUST include DoD verification as explicit tasks.**

**Template** ([full reference](https://github.com/TheNeerajGarg/org-standards/blob/main/workflow/DEFINITION_OF_DONE.md#critical-implementation-plan-template)):

```
## Implementation Plan

### Feature Tasks
1. [Your feature-specific tasks]
2. ...

### Definition of Done Verification (MANDATORY - Always Include)
N. Run linting: ruff format . && ruff check .
N+1. Run type checking: mypy src/
N+2. Run all tests: pytest
N+3. Verify coverage ≥80%: pytest --cov=src --cov-fail-under=80
N+4. Run pre-commit hooks: pre-commit run --all-files
N+5. Verify type hints present (all new functions)
N+6. Verify docstrings present (all new functions)
N+7. Identify integration tests needed
N+8. Update documentation if needed

### Completion (CRITICAL - Task NOT Done Until This Step)
N+9. Create PR with verification results
N+10. Get PR approved (if required)
N+11. Merge PR to main
N+12. **Verify merged code pushed to main** (git pull origin main shows your changes)

**CRITICAL**: A feature is NOT "done" until it is merged and pushed to main. Code that exists only in a PR or local branch is NOT done.
```

**Example**:

User: "Add data export feature"

Your plan MUST be:
```
1. Design export data structure
2. Implement CSV export
3. Implement JSON export
4. Write unit tests
5. Run linting: ruff format . && ruff check .    ← DoD verification starts
6. Run type checking: mypy src/
7. Run all tests: pytest
8. Verify coverage ≥80%
9. Run pre-commit hooks
10. Verify type hints present
11. Verify docstrings present
12. Identify integration tests needed
13. Update documentation
14. Create PR                                     ← Only create PR after ALL DoD tasks pass
15. Get PR approved
16. Merge PR to main
17. Verify code pushed to main                    ← Task is DONE when merged and pushed
```

**CRITICAL**: Do NOT create implementation plans without DoD verification tasks (5-17 in example above).

**Use TodoWrite**: Add all tasks (including DoD) to todo list so human can track your progress.

## Security and Performance Standards

### MANDATORY: Security Practices
- Never commit secrets or API keys
- Use environment variables for sensitive data
- Validate all input data
- Use parameterized queries for database operations
- Sanitize user input
- Use HTTPS for external API calls

### MANDATORY: Performance Considerations
- Use appropriate data structures
- Avoid unnecessary loops and iterations
- Use generators for large datasets
- Cache expensive operations
- Use connection pooling for databases
- Profile code for bottlenecks

### Memory Management
- Use context managers for resources
- Close files and connections properly
- Avoid memory leaks in long-running processes

## CRITICAL: Commit Best Practices - Never Use --no-verify

**NEVER use `git commit --no-verify` or `git push --no-verify`**. Quality gates exist to prevent bugs in production.

### Pre-Commit Workflow (Zero Bypasses)

**Follow this workflow to ensure commits always pass without bypasses:**

```bash
# 1. BEFORE writing code - Create introspection document (for significant changes)
cat > .ai-sessions/$(date +%Y-%m-%d)/feature-name.md <<'EOF'
# Feature Name

## What Changed?
[Describe the change]

## Why This Change?
[Explain the business/technical need]

## How to Prevent Similar Issues?
[If fixing a bug, explain prevention]
EOF

# 2. Write tests ALONGSIDE your code (not after)
# - Write unit test first (TDD approach)
# - Implement feature
# - Run tests continuously: pytest --cov=src --cov-fail-under=80

# 3. Run quality checks BEFORE committing
ruff format . && ruff check .              # Fix formatting/linting
mypy src/                                  # Fix type errors
pytest --cov=src --cov-fail-under=80      # Ensure coverage ≥80%
pre-commit run --all-files                 # Verify all hooks pass

# 4. Keep commits small and focused (<10 files when possible)
git add specific-file1.py specific-file2.py
git status  # Verify only intended files staged

# 5. Commit - hooks run automatically
git commit -m "feat: descriptive message"
# If hooks fail, fix issues and try again
# DO NOT use --no-verify

# 6. Push - safety checks run automatically
git push origin main
# If push fails, fix issues or rebase
# DO NOT use --no-verify or force push
```

### Avoiding Common Bypass Scenarios

#### Scenario 1: "Bulk Modification" (>10 files)

**❌ WRONG**:
```bash
git add .  # 25 files staged
git commit --no-verify -m "big update"  # NEVER DO THIS
```

**✅ RIGHT**:
```bash
# Split into logical commits
git add src/feature/*.py tests/feature/*.py
git commit -m "feat: add feature X"

git add src/utils/*.py tests/utils/*.py
git commit -m "refactor: update utilities"

git add .coveragerc pyproject.toml
git commit -m "chore: update configuration"
```

**When bulk changes are truly necessary** (like auto-formatting):
- Ensure ALL quality checks pass first
- Document in introspection why bulk change is safe
- Get code review approval
- The pre-commit hook allows bulk changes if justified in introspection

#### Scenario 2: "Missing Introspection Document"

**❌ WRONG**:
```bash
git commit --no-verify -m "quick fix"  # NEVER DO THIS
```

**✅ RIGHT**:
```bash
# Pre-commit hook tells you the exact filename needed
# Example: "Missing: .ai-sessions/2025-10-16/commit-abc123.md"

# Create the document (hook provides template path)
cp .ai-session-template.md .ai-sessions/2025-10-16/commit-abc123.md

# Fill in: What? Why? How to prevent?
vim .ai-sessions/2025-10-16/commit-abc123.md

# Stage and commit
git add .ai-sessions/2025-10-16/commit-abc123.md
git commit -m "your message"  # Will pass now
```

**For small commits**, introspection may not be required. The hook is smart about what needs documentation.

#### Scenario 3: "Coverage Drops Below 80%"

**❌ WRONG**:
```bash
# Coverage: 78%
git commit --no-verify -m "ship it anyway"  # NEVER DO THIS
```

**✅ RIGHT**:
```bash
# Add tests BEFORE committing
# 1. Identify uncovered code
pytest --cov=src --cov-report=term-missing

# 2. Write tests for uncovered lines
# Example: src/feature.py:42-50 not covered
vim tests/test_feature.py  # Add test for lines 42-50

# 3. Verify coverage now ≥80%
pytest --cov=src --cov-fail-under=80

# 4. Commit with confidence
git commit -m "feat: add feature with tests"
```

#### Scenario 4: "Tests Are Failing"

**❌ WRONG**:
```bash
# 5 tests failing
git commit --no-verify -m "will fix later"  # NEVER DO THIS
```

**✅ RIGHT**:
```bash
# Fix tests BEFORE committing
# 1. Identify failures
pytest -v

# 2. Fix the failing tests
# Either fix the code or update the test expectations

# 3. Verify all tests pass
pytest  # All green

# 4. Commit
git commit -m "feat: properly tested feature"
```

#### Scenario 5: "Linting Errors"

**❌ WRONG**:
```bash
# Ruff: 15 errors found
git commit --no-verify -m "ignore linting"  # NEVER DO THIS
```

**✅ RIGHT**:
```bash
# Auto-fix most issues
ruff format .        # Fixes formatting
ruff check . --fix   # Auto-fixes some linting issues

# Manually fix remaining issues
ruff check .         # See remaining errors
# Fix each error

# Verify clean
ruff check .  # Should show "All checks passed!"

# Commit
git commit -m "feat: lint-compliant code"
```

### Pre-Commit Hook Behavior

**What hooks check automatically:**
1. **Python syntax** - Files must parse
2. **Bulk modifications** - Warns if >10 files (allows with justification)
3. **Dangerous commands** - Blocks `rm -rf`, `DROP TABLE`, etc.
4. **Introspection document** - Required for significant changes
5. **Infrastructure patterns** - Warns about anti-patterns (non-blocking)
6. **Full test suite** - All tests must pass
7. **Coverage check** - Must be ≥80%
8. **Code formatting** - Auto-formats and amends commit
9. **Linting** - All ruff checks must pass
10. **Mock patterns** - Validates proper mocking

**Post-commit auto-formatting:**
- Hooks may auto-format code after commit
- Commit is automatically amended with formatting
- This is SAFE and expected behavior

### Emergency Bypass (Last Resort Only)

**If you absolutely must bypass** (e.g., reverting a breaking production change):

1. **Document why** in commit message:
   ```bash
   git commit --no-verify -m "EMERGENCY: revert breaking change

   Production is down. Reverting commit abc123.
   Bypassing hooks because immediate fix needed.
   Will address properly in follow-up PR #123."
   ```

2. **Create follow-up issue** immediately to fix properly

3. **Get approval** from team lead/manager

**Reasons that are NOT emergencies:**
- "I'm in a hurry" - NO
- "Tests take too long" - NO
- "I'll fix it later" - NO
- "It's just a small change" - NO

### Benefits of Zero-Bypass Policy

**Why hooks exist:**
- 🐛 **Prevent bugs** - Catch issues before they reach production
- 📊 **Maintain quality** - Keep codebase at 80%+ coverage
- 🔒 **Enforce standards** - Consistent code style
- 📚 **Documentation** - Introspection creates learning artifacts
- 🚀 **CI/CD confidence** - If it passes locally, it passes in CI

**Time saved:**
- No "fix it later" debt that never gets fixed
- No production hotfixes for preventable bugs
- No debugging undocumented changes
- No coverage decay over time

### Quick Reference Commands

```bash
# Before every commit - run these
ruff format . && ruff check .              # Linting
pytest --cov=src --cov-fail-under=80      # Tests + coverage
pre-commit run --all-files                 # All hooks

# If any fail, fix and re-run
# When all pass, commit:
git commit -m "your message"

# Push will auto-check quality
git push origin main
```

**Remember**: Hooks are your friends. They catch bugs before they reach production. Never bypass them.
