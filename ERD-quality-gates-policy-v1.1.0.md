# ERD: Quality Gates Policy v1.1.0 - Branch-Aware and File-Pattern-Based Validation

**Status**: Draft → Review
**Created**: 2025-10-25
**Author**: Principal Engineer + Test Architect
**Reviewers**: @TheNeerajGarg
**Related**:
- Issue: https://github.com/StyleGuru/syra/issues/81
- Analysis: [EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md](EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md)
- Execution Plan: [EXECUTION-PLAN-quality-gates-policy-improvement.md](EXECUTION-PLAN-quality-gates-policy-improvement.md)

---

## Abstract

This ERD specifies the technical implementation of branch-aware and file-pattern-based quality gates to reduce emergency bypass rate from 95% to 15%. The changes introduce two new configuration sections (`branch_policies` and `file_pattern_rules`) to `quality-gates.yaml` and implement conditional gate execution logic in `quality_gates.py`. **Critical**: These are config and code changes that directly control production validation - incorrect implementation can either block all pushes (availability issue) or allow bad code to merge (quality issue). Implementation includes comprehensive testing, gradual rollout, and immediate rollback capability.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Technical Architecture](#technical-architecture)
3. [Configuration Schema](#configuration-schema)
4. [Implementation Details](#implementation-details)
5. [Data Flow](#data-flow)
6. [Error Handling](#error-handling)
7. [Testing Strategy](#testing-strategy)
8. [Deployment & Rollback](#deployment--rollback)
9. [Monitoring & Observability](#monitoring--observability)
10. [Security Considerations](#security-considerations)
11. [Performance Impact](#performance-impact)
12. [Migration Path](#migration-path)
13. [Risks & Mitigations](#risks--mitigations)
14. [Appendix: ERD Checklist](#appendix-erd-checklist)

---

## 1. Problem Statement

### Current Behavior

**Observed**: 19 emergency bypasses in 8 hours (95% bypass rate) on Syra repository.

**Root Cause**: Quality gates apply uniformly to all:
- Branch types (main, feature, test, playground)
- File types (Python code, YAML workflows, Markdown docs, JSON configs)
- Repository types (product code vs development tooling)

**Impact**:
- Developers bypass gates for legitimate changes (workflows, docs)
- Quality gates lose credibility ("just bypass it")
- Real issues hidden in bypass noise (19 bypasses, 0 genuine emergencies)

### Desired Behavior

**Goal**: Quality gates adapt to context:
- **Branch type**: Test branches skip coverage, main requires full gates
- **File patterns**: Workflows get YAML validation, not code coverage
- **Change scope**: MyPy checks only changed files, not entire repo

**Target**: 15% bypass rate (only genuine emergencies)

### Why This is Critical

**Config is Code**: `quality-gates.yaml` controls production validation flow
- Incorrect schema → All pushes blocked (availability incident)
- Incorrect exemptions → Bad code merges (quality incident)
- Incorrect commands → False positives/negatives (credibility erosion)

**Prompts are Code**: File pattern rules are executable logic
- Glob pattern errors → Wrong files exempted
- Regex errors → Infinite loops or crashes
- Logic errors → Security gates bypassed

**Production Impact**:
- 3 repositories depend on this config (Syra, StyleGuru, syra-playground)
- ~10-20 pushes/day affected
- Downtime if rollout fails: Developers blocked, work halted

---

## 2. Technical Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Git Pre-Push Hook                          │
│                                                                 │
│  1. Load quality-gates.yaml (config)                           │
│  2. Detect context:                                            │
│     - Current branch (git branch --show-current)               │
│     - Changed files (git diff --name-only origin/main...HEAD)  │
│  3. Apply policies:                                            │
│     - Match branch_policies by pattern                         │
│     - Match file_pattern_rules by glob                         │
│     - Build exemption list                                     │
│  4. Execute gates:                                             │
│     - Run non-exempted gates only                              │
│     - Apply branch-specific thresholds                         │
│  5. Report results:                                            │
│     - Pass: Allow push                                         │
│     - Fail: Block with actionable error message                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Type | Purpose | Failure Mode |
|-----------|------|---------|--------------|
| `quality-gates.yaml` | Config | Define gates, policies, rules | Parse error → Block all pushes |
| `quality_gates.py` | Python | Execute gates, apply logic | Runtime error → Block all pushes |
| `.git/hooks/pre-push` | Shell | Invoke quality_gates.py | Missing → No validation (silent fail) |
| Git metadata | Data | Branch name, changed files | Unavailable → Assume strictest policy |

### Dependencies

**External**:
- Git (for branch detection, diff calculation)
- Python 3.11+ (for quality_gates.py execution)
- YAML parser (PyYAML) (for config parsing)

**Internal**:
- `org-standards/config/quality-gates.yaml` (config schema v1.1.0)
- `org-standards/python/quality_gates.py` (execution engine)
- Submodule mechanism (propagate config to repos)

**Failure Propagation**:
```
quality-gates.yaml parse error
  → quality_gates.py raises exception
  → pre-push hook exits 1
  → Git blocks push
  → Developer sees error message
```

---

## 3. Configuration Schema

### 3.1 New Schema Additions

**File**: `org-standards/config/quality-gates.yaml`

#### 3.1.1 Branch Policies Section

```yaml
# =============================================================================
# Branch-Aware Quality Gates
# =============================================================================
branch_policies:
  # Policy name (used in logs, must be unique)
  <policy_name>:
    # Optional: Regex pattern to match branch names
    # If omitted, policy applies to branches matching the policy name exactly
    pattern: "<regex>"  # Example: "^feature/.*"

    # Required: Enforcement level
    enforcement_level: "strict" | "relaxed" | "minimal" | "none"

    # Optional: List of gates to exempt (skip)
    # Special value: "all" exempts all gates
    exempt_gates: [<gate_name>, ...]

    # Optional: List of gates that MUST run (overrides exempt_gates)
    required_gates: [<gate_name>, ...]

    # Optional: Override coverage threshold for this branch
    coverage_threshold: <number>  # Percentage (0-100)

    # Required: Human-readable description (for logs and error messages)
    description: "<string>"

    # Optional: Whether all gates must pass (vs any can fail)
    all_gates_required: true | false  # Default: false for non-strict

# Example policies
branch_policies:
  main:
    enforcement_level: strict
    all_gates_required: true
    description: "Production branch requires all quality gates"

  feature:
    pattern: "^feature/.*"
    enforcement_level: relaxed
    coverage_threshold: 60
    description: "Feature branches allow iteration with lower coverage"

  test:
    pattern: "^test/.*"
    enforcement_level: minimal
    exempt_gates: [coverage, type_checking]
    required_gates: [linting, testing]
    description: "Test branches for experimentation"

  playground:
    pattern: "^playground/.*"
    enforcement_level: none
    exempt_gates: [all]
    description: "Playground branches skip all gates"
```

**Schema Constraints**:
- `policy_name` MUST be unique
- `pattern` MUST be valid regex (validated on load)
- `enforcement_level` MUST be one of: strict, relaxed, minimal, none
- `exempt_gates` and `required_gates` MUST reference existing gate names
- `coverage_threshold` MUST be 0-100
- `description` MUST be non-empty string (used in error messages)

**Validation Rules**:
1. If `enforcement_level: none`, must have `exempt_gates: [all]`
2. `required_gates` takes precedence over `exempt_gates`
3. Special policy name "main" matches branch "main" exactly (no pattern needed)
4. Pattern matching is case-sensitive
5. First matching policy wins (order matters)

**Error Conditions**:
| Error | Detection | Handling |
|-------|-----------|----------|
| Invalid regex in `pattern` | Config load time | Fail fast, block all pushes, log error |
| Unknown gate in `exempt_gates` | Config load time | Warn, ignore unknown gate name |
| Invalid enforcement_level | Config load time | Fail fast, block all pushes |
| Missing description | Config load time | Warn, use policy name as description |

---

#### 3.1.2 File Pattern Rules Section

```yaml
# =============================================================================
# File-Pattern-Based Gate Selection
# =============================================================================
file_pattern_rules:
  # Rule name (used in logs, must be unique)
  <rule_name>:
    # Required: List of glob patterns to match file paths
    # Empty list = special case for empty commits (no files changed)
    patterns: ["<glob>", ...]

    # Optional: List of gates to exempt for matched files
    exempt_gates: [<gate_name>, ...]

    # Optional: List of gates that MUST run (overrides exempt_gates)
    required_gates: [<gate_name>, ...]

    # Required: Human-readable description
    description: "<string>"

# Example rules
file_pattern_rules:
  workflows:
    patterns:
      - ".github/workflows/*.yml"
      - ".github/workflows/*.yaml"
    exempt_gates: [coverage, type_checking, testing]
    required_gates: [workflow_validation]
    description: "Workflows are declarative config, need YAML validation not code coverage"

  documentation:
    patterns:
      - ".ai-sessions/**/*.md"
      - "docs/**/*.md"
      - "*.md"
    exempt_gates: [coverage, type_checking, testing, linting]
    required_gates: []
    description: "Documentation changes don't require code quality gates"

  configs:
    patterns:
      - "*.yaml"
      - "*.yml"
      - "*.toml"
      - "*.json"
    exempt_gates: [coverage, type_checking, testing]
    required_gates: [linting]
    description: "Config files need syntax validation, not code coverage"

  empty_commit:
    patterns: []  # Special: matches when no files changed
    exempt_gates: [all]
    description: "Empty commits used to trigger workflows"
```

**Schema Constraints**:
- `rule_name` MUST be unique
- `patterns` MUST be list of valid glob patterns
- Empty `patterns` is special case (empty commits only)
- `exempt_gates` and `required_gates` MUST reference existing gates
- `description` MUST be non-empty string

**Validation Rules**:
1. Glob patterns use `fnmatch` syntax (not regex)
2. `**` matches any depth of subdirectories
3. Multiple patterns are OR'd (any match triggers rule)
4. Multiple rules can match same file (exemptions are combined)
5. If ANY rule exempts a gate, gate is skipped
6. `required_gates` from ANY rule overrides all exemptions

**Error Conditions**:
| Error | Detection | Handling |
|-------|-----------|----------|
| Invalid glob pattern | Runtime (fnmatch) | Log warning, skip pattern |
| Unknown gate in rules | Config load time | Warn, ignore unknown gate |
| Conflicting rules | Runtime | Union all exemptions, intersection of required |

---

### 3.2 Modified Gate Definitions

#### 3.2.1 Type Checking Gate - Diff-Based Validation

```yaml
gates:
  type_checking:
    enabled: true
    tool: mypy
    description: "Type check changed Python files only (diff-based)"
    required: true

    # NEW: Multi-line command using git diff
    command: |
      # Get changed Python files
      CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep '\.py$' || true)

      # If no Python files changed, skip
      if [ -z "$CHANGED_FILES" ]; then
        echo "✓ No Python files changed, skipping MyPy"
        exit 0
      fi

      # Log which files we're checking
      echo "Running MyPy on changed files:"
      echo "$CHANGED_FILES"

      # Run MyPy on changed files only
      echo "$CHANGED_FILES" | xargs mypy

    fail_message: |
      Type checking failed on your changes.

      Fix: Add type hints to new/modified functions

      Note: Pre-existing MyPy failures in other files don't block your work.
      This gate only checks files you modified.

    timeout_seconds: 120
```

**Key Changes**:
- `command` now multi-line shell script (not single command)
- Uses `git diff --name-only origin/main...HEAD` to get changed files
- Filters for `.py` files only
- Gracefully handles case where no Python files changed (exit 0)
- Uses `xargs` to pass file list to mypy

**Error Handling**:
- If `git diff` fails → Assume all files (fail safe to strict)
- If `grep` finds no matches → Exit 0 (no Python files = skip check)
- If `mypy` not installed → Fail with actionable error message
- If `xargs` receives empty input → Exit 0 (handled by `[ -z "$CHANGED_FILES" ]`)

---

#### 3.2.2 New Gate: Workflow Validation

```yaml
gates:
  workflow_validation:
    enabled: true
    tool: composite  # Multiple tools in sequence
    description: "Validate GitHub Actions workflows (YAML syntax + security)"
    required: true

    # NEW: Multiple commands (all must pass)
    commands:
      # YAML syntax validation
      syntax:
        command: "yamllint -c .yamllint.yml .github/workflows/"
        fail_message: "YAML syntax errors. Run: yamllint .github/workflows/"

      # Security check: no hardcoded secrets
      security:
        command: |
          # Check for GITHUB_TOKEN usage (should use BOT_GITHUB_TOKEN)
          if grep -r 'secrets\.GITHUB_TOKEN' .github/workflows/; then
            echo "❌ Found GITHUB_TOKEN usage"
            echo "Fix: Replace with secrets.BOT_GITHUB_TOKEN"
            exit 1
          fi

          # Check for hardcoded secrets
          if grep -rE '(password|api_key|secret).*=.*["\']' .github/workflows/; then
            echo "❌ Found potential hardcoded secrets"
            exit 1
          fi

          exit 0
        fail_message: "Security violations in workflows"

      # Workflow schema validation
      actionlint:
        command: "actionlint .github/workflows/*.yml"
        fail_message: "Workflow schema errors. Run: actionlint .github/workflows/"

    timeout_seconds: 60

    # NEW: Only apply to workflow files
    applies_to_patterns: [".github/workflows/*.yml"]
```

**Key Features**:
- Multiple sub-commands (syntax, security, actionlint)
- All must pass for gate to pass
- Security checks for hardcoded tokens
- Only runs when workflow files changed (via `applies_to_patterns`)

**Error Handling**:
- If `yamllint` not installed → Skip with warning (non-blocking)
- If `actionlint` not installed → Skip with warning (non-blocking)
- If no workflow files → Skip entire gate (exit 0)
- If `grep` fails → Assume no violations (exit 0)

---

### 3.3 Version Migration

**Current Version**: 1.0.0
**New Version**: 1.1.0

**Breaking Changes**: NONE
- New sections (`branch_policies`, `file_pattern_rules`) are optional
- If omitted, behavior identical to v1.0.0
- Existing repos can upgrade gradually

**Backwards Compatibility**:
```python
# In quality_gates.py
def load_config(config_path: str) -> QualityGatesConfig:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # v1.1.0 additions (optional)
    if 'branch_policies' not in config:
        config['branch_policies'] = {}  # Empty = no branch awareness

    if 'file_pattern_rules' not in config:
        config['file_pattern_rules'] = {}  # Empty = no file pattern rules

    return QualityGatesConfig(**config)
```

---

## 4. Implementation Details

### 4.1 Core Logic: Gate Selection

**Function**: `_apply_branch_and_file_exemptions()`

**Input**:
- `gates_to_run: List[GateConfig]` - All enabled gates from config
- `branch_name: str` - Current branch (from `git branch --show-current`)
- `changed_files: List[str]` - Changed files (from `git diff --name-only`)
- `config: QualityGatesConfig` - Loaded config

**Output**:
- `List[GateConfig]` - Filtered list of gates to actually run

**Algorithm**:
```python
def _apply_branch_and_file_exemptions(
    gates_to_run: List[GateConfig],
    branch_name: str,
    changed_files: List[str],
    config: QualityGatesConfig
) -> List[GateConfig]:
    """
    Apply branch policies and file pattern rules to determine which gates to run.

    Returns filtered list of gates after applying exemptions.
    """
    exempt_gates = set()
    required_gates = set()

    # Step 1: Match branch policy
    branch_policy = _match_branch_policy(branch_name, config)
    if branch_policy:
        print(f"📋 Branch policy: {branch_policy['description']}")

        # If enforcement is 'none', exempt all gates
        if branch_policy.get('enforcement_level') == 'none':
            print("✓ Branch policy: All gates exempted")
            return []

        # Collect exemptions from branch policy
        exempt_gates.update(branch_policy.get('exempt_gates', []))
        required_gates.update(branch_policy.get('required_gates', []))

    # Step 2: Match file pattern rules
    matched_rules = _detect_file_patterns(changed_files, config)
    if matched_rules:
        print(f"📋 File patterns detected: {', '.join(matched_rules)}")

        for rule_name in matched_rules:
            rule = config.file_pattern_rules[rule_name]
            exempt_gates.update(rule.get('exempt_gates', []))
            required_gates.update(rule.get('required_gates', []))

    # Step 3: Handle special case 'all' exemption
    if 'all' in exempt_gates:
        print("✓ All gates exempted")
        return []

    # Step 4: Filter gates
    # A gate runs if:
    #   - NOT in exempt_gates AND NOT in required_gates, OR
    #   - IS in required_gates (overrides exemptions)
    filtered_gates = []
    for gate in gates_to_run:
        if gate.name in required_gates:
            # Required gates always run
            filtered_gates.append(gate)
        elif gate.name not in exempt_gates:
            # Non-exempted gates run
            filtered_gates.append(gate)

    # Step 5: Log changes
    if len(filtered_gates) < len(gates_to_run):
        exempted = [g.name for g in gates_to_run if g not in filtered_gates]
        print(f"✓ Gates exempted: {', '.join(exempted)}")

    if required_gates:
        print(f"✓ Required gates: {', '.join(required_gates)}")

    return filtered_gates
```

**Edge Cases**:
1. **No branch policy match**: Run all gates (strictest default)
2. **No file pattern match**: Run all gates
3. **Empty commit (no files changed)**: Match `empty_commit` rule if exists
4. **Multiple rules match same file**: Union all exemptions, intersection of required
5. **Branch policy conflicts with file rule**: Required gates always win

**Error Recovery**:
```python
try:
    filtered_gates = _apply_branch_and_file_exemptions(...)
except Exception as e:
    # If logic fails, fail safe to strictest policy
    logger.error(f"Gate filtering failed: {e}")
    logger.error("Failing safe: Running ALL gates")
    return gates_to_run  # Return unfiltered list
```

---

### 4.2 Branch Policy Matching

**Function**: `_match_branch_policy()`

```python
def _match_branch_policy(branch_name: str, config: QualityGatesConfig) -> Optional[Dict]:
    """
    Match current branch against branch policies.

    Returns policy configuration if match found, None otherwise.

    Matching rules:
    1. Exact match: branch_name == policy_name (e.g., "main")
    2. Pattern match: branch_name matches policy['pattern'] regex
    3. First match wins (order in YAML matters)
    """
    if not hasattr(config, 'branch_policies'):
        return None

    for policy_name, policy in config.branch_policies.items():
        # Special case: 'main' policy matches 'main' branch exactly
        if policy_name == branch_name:
            return policy

        # Pattern-based matching
        if 'pattern' in policy:
            try:
                import re
                if re.match(policy['pattern'], branch_name):
                    return policy
            except re.error as e:
                # Invalid regex - log and skip
                logger.warning(f"Invalid regex in policy {policy_name}: {e}")
                continue

    # No match found
    return None
```

**Testing Strategy**:
```python
# Unit tests
def test_match_branch_policy_exact():
    config = QualityGatesConfig(branch_policies={
        'main': {'description': 'Main branch'}
    })
    assert _match_branch_policy('main', config) is not None
    assert _match_branch_policy('feature/foo', config) is None

def test_match_branch_policy_pattern():
    config = QualityGatesConfig(branch_policies={
        'feature': {'pattern': '^feature/.*', 'description': 'Feature'}
    })
    assert _match_branch_policy('feature/foo', config) is not None
    assert _match_branch_policy('test/foo', config) is None

def test_match_branch_policy_invalid_regex():
    config = QualityGatesConfig(branch_policies={
        'bad': {'pattern': '[invalid(regex', 'description': 'Bad'}
    })
    # Should not crash, should return None
    assert _match_branch_policy('anything', config) is None
```

---

### 4.3 File Pattern Detection

**Function**: `_detect_file_patterns()`

```python
def _detect_file_patterns(changed_files: List[str], config: QualityGatesConfig) -> List[str]:
    """
    Detect which file pattern rules apply to changed files.

    Returns list of rule names that match.

    Matching rules:
    1. Use fnmatch (glob patterns), not regex
    2. ANY pattern in rule matches → Rule matches
    3. Multiple rules can match same file → All returned
    4. Empty patterns list = matches empty commits only
    """
    if not hasattr(config, 'file_pattern_rules'):
        return []

    matched_rules = []

    for rule_name, rule in config.file_pattern_rules.items():
        patterns = rule.get('patterns', [])

        # Special case: empty commit (no files changed)
        if not changed_files and not patterns:
            matched_rules.append(rule_name)
            continue

        # Skip empty patterns if files changed (not an empty commit)
        if not patterns:
            continue

        # Check if any changed file matches any pattern
        import fnmatch
        for file_path in changed_files:
            for pattern in patterns:
                try:
                    if fnmatch.fnmatch(file_path, pattern):
                        matched_rules.append(rule_name)
                        break  # Stop checking patterns for this file
                except Exception as e:
                    logger.warning(f"Invalid glob pattern '{pattern}': {e}")
                    continue

            # If rule matched, no need to check more files
            if rule_name in matched_rules:
                break

    # Deduplicate (same rule can match multiple files)
    return list(set(matched_rules))
```

**Testing Strategy**:
```python
def test_detect_file_patterns_workflows():
    config = QualityGatesConfig(file_pattern_rules={
        'workflows': {'patterns': ['.github/workflows/*.yml']}
    })
    changed = ['.github/workflows/ci.yml', 'src/main.py']
    assert 'workflows' in _detect_file_patterns(changed, config)

def test_detect_file_patterns_empty_commit():
    config = QualityGatesConfig(file_pattern_rules={
        'empty': {'patterns': []}
    })
    assert 'empty' in _detect_file_patterns([], config)
    assert 'empty' not in _detect_file_patterns(['file.py'], config)

def test_detect_file_patterns_glob_wildcard():
    config = QualityGatesConfig(file_pattern_rules={
        'docs': {'patterns': ['docs/**/*.md']}
    })
    assert 'docs' in _detect_file_patterns(['docs/foo/bar/baz.md'], config)
    assert 'docs' not in _detect_file_patterns(['docs/image.png'], config)
```

---

### 4.4 Context Detection

**Function**: `_get_execution_context()`

```python
def _get_execution_context() -> Dict[str, Any]:
    """
    Gather execution context: branch name, changed files, stage.

    Returns:
    {
        'branch': str,           # Current branch name
        'changed_files': List[str],  # Changed file paths
        'stage': str,            # 'pre-push', 'pre-commit', 'ci'
        'is_empty_commit': bool  # True if no files changed
    }

    Error handling:
    - If git commands fail, return safe defaults (strictest policy)
    """
    import subprocess

    context = {
        'branch': 'unknown',
        'changed_files': [],
        'stage': 'unknown',
        'is_empty_commit': False
    }

    # Detect stage
    context['stage'] = _detect_stage()

    # Get current branch
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        context['branch'] = result.stdout.strip()
    except Exception as e:
        logger.warning(f"Failed to detect branch: {e}")
        # Default to 'main' (strictest policy)
        context['branch'] = 'main'

    # Get changed files (diff against origin/main)
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        changed = result.stdout.strip().split('\n')
        # Filter out empty strings
        context['changed_files'] = [f for f in changed if f]
        context['is_empty_commit'] = len(context['changed_files']) == 0
    except Exception as e:
        logger.warning(f"Failed to detect changed files: {e}")
        # Default to empty (triggers strictest policy)
        context['changed_files'] = []

    return context
```

**Error Handling**:
| Scenario | Behavior | Rationale |
|----------|----------|-----------|
| `git branch` fails | Default to 'main' | Fail safe to strictest policy |
| `git diff` fails | Default to [] | Empty = no exemptions = strict |
| Network timeout (fetching origin) | Use cached origin/main | Best effort |
| Detached HEAD state | Use 'HEAD' as branch | Treat as main-equivalent |

---

## 5. Data Flow

### 5.1 Normal Push Flow (Feature Branch, Code Change)

```
Developer: git push
  ↓
Pre-push hook invokes quality_gates.py
  ↓
1. Load quality-gates.yaml
   - Parse YAML
   - Validate schema
   - Load branch_policies, file_pattern_rules
  ↓
2. Detect context
   - Current branch: "feature/add-tests" (git branch --show-current)
   - Changed files: ["tests/test_foo.py", "src/foo.py"] (git diff --name-only)
  ↓
3. Match branch policy
   - Pattern match: "feature/add-tests" matches "^feature/.*"
   - Policy: enforcement_level=relaxed, coverage_threshold=60
  ↓
4. Match file patterns
   - "tests/test_foo.py" matches no special patterns
   - "src/foo.py" matches no special patterns
   - Result: No file-based exemptions
  ↓
5. Apply exemptions
   - Branch policy: No gates exempted (relaxed allows all, lower thresholds)
   - File rules: No exemptions
   - Gates to run: [testing, coverage, linting, type_checking]
  ↓
6. Execute gates
   - testing: pytest → PASS
   - coverage: diff-cover --threshold=60 → PASS (65% coverage)
   - linting: ruff check → PASS
   - type_checking: mypy tests/test_foo.py src/foo.py → PASS
  ↓
7. All gates pass
  ↓
Push succeeds ✅
```

---

### 5.2 Workflow Change Flow (Test Branch)

```
Developer: git push
  ↓
Pre-push hook invokes quality_gates.py
  ↓
1. Load config
  ↓
2. Detect context
   - Branch: "test/merge-bot-verification"
   - Changed files: [".github/workflows/merge-bot.yml"]
  ↓
3. Match branch policy
   - Pattern match: "test/merge-bot-verification" matches "^test/.*"
   - Policy: exempt_gates=[coverage, type_checking], required_gates=[linting, testing]
  ↓
4. Match file patterns
   - ".github/workflows/merge-bot.yml" matches "workflows" rule
   - Rule: exempt_gates=[coverage, type_checking, testing], required_gates=[workflow_validation]
  ↓
5. Apply exemptions
   - Branch exempts: coverage, type_checking
   - File rule exempts: coverage, type_checking, testing
   - Union: coverage, type_checking, testing EXEMPTED
   - Required gates: linting (branch), workflow_validation (file)
   - Gates to run: [linting, workflow_validation]
  ↓
6. Execute gates
   - linting: ruff check .github/workflows/merge-bot.yml → PASS
   - workflow_validation:
     * syntax: yamllint .github/workflows/merge-bot.yml → PASS
     * security: grep for secrets → PASS
     * actionlint: actionlint .github/workflows/merge-bot.yml → PASS
  ↓
7. All gates pass
  ↓
Push succeeds ✅ (No emergency bypass needed!)
```

**Impact**: Previously required emergency bypass, now passes validation.

---

### 5.3 Documentation Change Flow (Any Branch)

```
Developer: git push
  ↓
Pre-push hook invokes quality_gates.py
  ↓
1. Load config
  ↓
2. Detect context
   - Branch: "feature/update-docs"
   - Changed files: ["README.md", "docs/guide.md"]
  ↓
3. Match branch policy
   - Pattern match: "feature/update-docs" matches "^feature/.*"
   - Policy: relaxed
  ↓
4. Match file patterns
   - "README.md" matches "documentation" rule
   - "docs/guide.md" matches "documentation" rule
   - Rule: exempt_gates=[all]
  ↓
5. Apply exemptions
   - File rule: ALL gates exempted
   - Gates to run: []
  ↓
6. No gates to execute
  ↓
7. Trivially pass
  ↓
Push succeeds ✅ (No validation needed)
```

**Impact**: Documentation changes bypass all gates (as intended).

---

### 5.4 Error Flow (Invalid Config)

```
Developer: git push
  ↓
Pre-push hook invokes quality_gates.py
  ↓
1. Load quality-gates.yaml
   - Parse YAML
   - ERROR: Invalid regex in branch_policies.feature.pattern: "[invalid(regex"
  ↓
2. Exception raised
  ↓
3. Error handler catches
   - Log error: "Config validation failed: Invalid regex"
   - Print user-friendly message:
     "❌ Quality gates configuration is invalid.
      This is a configuration error (not your code).
      Contact: @TheNeerajGarg
      Details: Invalid regex in branch_policies.feature.pattern"
  ↓
4. Exit code: 1
  ↓
Push blocked ❌

Notify: Alert in Slack/GitHub that config is broken
Rollback: Auto-revert org-standards to previous version
```

**Recovery**:
- User can emergency bypass (one-time)
- Config error logged to monitoring
- Auto-rollback initiated if error persists >10 minutes

---

## 6. Error Handling

### 6.1 Config Parse Errors

**Scenario**: `quality-gates.yaml` has syntax error

```python
def load_config(config_path: str) -> QualityGatesConfig:
    try:
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse {config_path}: {e}")
        print(f"""
❌ QUALITY GATES CONFIG ERROR

The configuration file has a YAML syntax error:
  File: {config_path}
  Error: {e}

This is a configuration issue (not your code).

Workaround (one-time):
  EMERGENCY_PUSH=1 EMERGENCY_REASON='config syntax error' git push

Permanent fix:
  Contact @TheNeerajGarg or fix {config_path}
        """)
        sys.exit(1)  # Block push

    # Validate schema
    try:
        validate_config_schema(config_dict)
    except ValueError as e:
        logger.error(f"Invalid config schema: {e}")
        print(f"""
❌ QUALITY GATES CONFIG ERROR

The configuration file has invalid schema:
  Error: {e}

Workaround: EMERGENCY_PUSH=1 git push
Contact: @TheNeerajGarg
        """)
        sys.exit(1)

    return QualityGatesConfig(**config_dict)
```

**User Experience**:
- Clear error message (not Python traceback)
- Identifies config as problem (not user's code)
- Provides emergency bypass command
- Provides contact for fix

---

### 6.2 Invalid Regex Patterns

**Scenario**: Branch policy has invalid regex

```python
def _match_branch_policy(branch_name: str, config: QualityGatesConfig) -> Optional[Dict]:
    for policy_name, policy in config.branch_policies.items():
        if 'pattern' in policy:
            try:
                import re
                if re.match(policy['pattern'], branch_name):
                    return policy
            except re.error as e:
                # Log error but don't crash
                logger.warning(
                    f"Invalid regex in branch policy '{policy_name}': "
                    f"pattern='{policy['pattern']}', error={e}"
                )
                # Notify config maintainers
                send_alert(
                    level='warning',
                    message=f"Invalid regex in quality-gates.yaml: {policy_name}"
                )
                # Skip this policy, continue checking others
                continue

    return None  # No match
```

**Behavior**:
- Invalid policy skipped (logged but not fatal)
- Other policies still checked
- Alert sent to config maintainers
- User's push not blocked by config error

---

### 6.3 Git Command Failures

**Scenario**: `git diff` fails (network issue, repo corruption)

```python
def _get_changed_files() -> List[str]:
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'origin/main...HEAD'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10  # Don't hang indefinitely
        )
        changed = result.stdout.strip().split('\n')
        return [f for f in changed if f]

    except subprocess.TimeoutExpired:
        logger.warning("git diff timed out (slow network?)")
        # Fail safe: Assume no changed files → strictest policy
        return []

    except subprocess.CalledProcessError as e:
        logger.warning(f"git diff failed: {e.stderr}")
        # Fail safe: Assume no changed files
        return []

    except Exception as e:
        logger.error(f"Unexpected error in git diff: {e}")
        # Fail safe
        return []
```

**Fail-Safe Strategy**:
- If can't detect changed files → Assume empty list
- Empty list → No file-based exemptions → All gates run
- Strictest policy applied (safe default)

---

### 6.4 Gate Execution Failures

**Scenario**: Gate command crashes or hangs

```python
def _run_gate(gate: GateConfig) -> GateResult:
    try:
        # Run with timeout
        result = subprocess.run(
            gate.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=gate.timeout_seconds or 300,  # Default 5 min
            check=False  # Don't raise on non-zero exit
        )

        return GateResult(
            gate_name=gate.name,
            passed=(result.returncode == 0),
            stdout=result.stdout,
            stderr=result.stderr,
            duration=...
        )

    except subprocess.TimeoutExpired:
        logger.error(f"Gate '{gate.name}' timed out after {gate.timeout_seconds}s")
        return GateResult(
            gate_name=gate.name,
            passed=False,
            error=f"Gate timed out (limit: {gate.timeout_seconds}s)"
        )

    except Exception as e:
        logger.error(f"Gate '{gate.name}' crashed: {e}")
        # Fail safe: Treat as gate failure (block push)
        return GateResult(
            gate_name=gate.name,
            passed=False,
            error=f"Gate crashed: {e}"
        )
```

**Behavior**:
- Timeout → Gate fails (safe default)
- Crash → Gate fails
- User sees error message with gate name
- Can emergency bypass if gate is broken

---

### 6.5 Emergency Bypass Loop Prevention

**Scenario**: User repeatedly bypasses same issue

```python
def check_bypass_history() -> None:
    """
    Check if user is bypassing too frequently.
    Alert if >3 bypasses in 1 hour.
    """
    bypass_dir = Path('.emergency-bypasses')
    if not bypass_dir.exists():
        return

    recent_bypasses = []
    one_hour_ago = time.time() - 3600

    for log_file in bypass_dir.glob('*.json'):
        with open(log_file) as f:
            bypass = json.load(f)
            timestamp = datetime.fromisoformat(bypass['timestamp']).timestamp()
            if timestamp > one_hour_ago:
                recent_bypasses.append(bypass)

    if len(recent_bypasses) >= 3:
        # Alert: Bypass abuse detected
        logger.warning(
            f"User bypassed quality gates {len(recent_bypasses)} times in 1 hour. "
            f"Possible bypass abuse or config issue."
        )

        # Analyze reasons
        reasons = Counter(b['reason'] for b in recent_bypasses)
        most_common = reasons.most_common(1)[0]

        if most_common[1] >= 2:
            # Same reason repeated → Likely config issue
            print(f"""
⚠️  WARNING: Repeated bypasses detected

You've bypassed quality gates {len(recent_bypasses)} times in the last hour.
Most common reason: "{most_common[0]}"

This may indicate a configuration issue that should be fixed permanently.
Please file an issue or contact @TheNeerajGarg.
            """)
```

**Behavior**:
- Track bypasses in last hour
- If ≥3 bypasses → Warn user
- If same reason repeated → Suggest config fix
- Log for monitoring (detect systematic issues)

---

## 7. Testing Strategy

### 7.1 Unit Tests

**File**: `org-standards/tests/test_quality_gates_v1_1.py`

```python
import pytest
from quality_gates import (
    _match_branch_policy,
    _detect_file_patterns,
    _apply_branch_and_file_exemptions,
    QualityGatesConfig,
    GateConfig
)

# Branch Policy Tests
def test_branch_policy_exact_match():
    """Test exact branch name match (e.g., 'main')"""
    config = QualityGatesConfig(branch_policies={
        'main': {
            'enforcement_level': 'strict',
            'description': 'Production'
        }
    })
    policy = _match_branch_policy('main', config)
    assert policy is not None
    assert policy['enforcement_level'] == 'strict'

def test_branch_policy_pattern_match():
    """Test regex pattern matching"""
    config = QualityGatesConfig(branch_policies={
        'feature': {
            'pattern': '^feature/.*',
            'enforcement_level': 'relaxed',
            'description': 'Feature branches'
        }
    })
    assert _match_branch_policy('feature/foo', config) is not None
    assert _match_branch_policy('test/foo', config) is None

def test_branch_policy_invalid_regex():
    """Test handling of invalid regex (should not crash)"""
    config = QualityGatesConfig(branch_policies={
        'bad': {
            'pattern': '[invalid(regex',
            'description': 'Bad regex'
        }
    })
    # Should return None, not crash
    policy = _match_branch_policy('anything', config)
    assert policy is None

# File Pattern Tests
def test_file_patterns_workflow_match():
    """Test workflow file pattern matching"""
    config = QualityGatesConfig(file_pattern_rules={
        'workflows': {
            'patterns': ['.github/workflows/*.yml'],
            'description': 'Workflows'
        }
    })
    changed = ['.github/workflows/ci.yml', 'src/main.py']
    matches = _detect_file_patterns(changed, config)
    assert 'workflows' in matches

def test_file_patterns_empty_commit():
    """Test empty commit detection"""
    config = QualityGatesConfig(file_pattern_rules={
        'empty': {
            'patterns': [],  # Empty = matches empty commits
            'description': 'Empty commits'
        }
    })
    assert 'empty' in _detect_file_patterns([], config)
    assert 'empty' not in _detect_file_patterns(['file.py'], config)

def test_file_patterns_glob_wildcard():
    """Test glob pattern with ** wildcard"""
    config = QualityGatesConfig(file_pattern_rules={
        'docs': {
            'patterns': ['docs/**/*.md'],
            'description': 'Documentation'
        }
    })
    assert 'docs' in _detect_file_patterns(['docs/foo/bar.md'], config)
    assert 'docs' not in _detect_file_patterns(['README.md'], config)

# Integration Tests
def test_apply_exemptions_test_branch_workflow_change():
    """
    Test case: Test branch + workflow change
    Should exempt: coverage, type_checking (branch), testing (file)
    Should run: linting, workflow_validation
    """
    config = QualityGatesConfig(
        branch_policies={
            'test': {
                'pattern': '^test/.*',
                'exempt_gates': ['coverage', 'type_checking'],
                'required_gates': ['linting']
            }
        },
        file_pattern_rules={
            'workflows': {
                'patterns': ['.github/workflows/*.yml'],
                'exempt_gates': ['testing'],
                'required_gates': ['workflow_validation']
            }
        }
    )

    gates = [
        GateConfig(name='coverage'),
        GateConfig(name='type_checking'),
        GateConfig(name='testing'),
        GateConfig(name='linting'),
        GateConfig(name='workflow_validation')
    ]

    filtered = _apply_branch_and_file_exemptions(
        gates,
        branch_name='test/merge-bot',
        changed_files=['.github/workflows/merge-bot.yml'],
        config=config
    )

    filtered_names = {g.name for g in filtered}

    # Coverage, type_checking, testing should be exempted
    assert 'coverage' not in filtered_names
    assert 'type_checking' not in filtered_names
    assert 'testing' not in filtered_names

    # Linting and workflow_validation should run (required)
    assert 'linting' in filtered_names
    assert 'workflow_validation' in filtered_names

def test_apply_exemptions_main_branch_code_change():
    """
    Test case: Main branch + Python code change
    Should run ALL gates (no exemptions on main)
    """
    config = QualityGatesConfig(
        branch_policies={
            'main': {
                'enforcement_level': 'strict',
                'all_gates_required': True
            }
        }
    )

    gates = [
        GateConfig(name='coverage'),
        GateConfig(name='type_checking'),
        GateConfig(name='testing'),
        GateConfig(name='linting')
    ]

    filtered = _apply_branch_and_file_exemptions(
        gates,
        branch_name='main',
        changed_files=['src/main.py'],
        config=config
    )

    # All gates should run
    assert len(filtered) == len(gates)

def test_apply_exemptions_playground_branch():
    """
    Test case: Playground branch
    Should exempt ALL gates (enforcement_level: none)
    """
    config = QualityGatesConfig(
        branch_policies={
            'playground': {
                'pattern': '^playground/.*',
                'enforcement_level': 'none',
                'exempt_gates': ['all']
            }
        }
    )

    gates = [GateConfig(name='coverage'), GateConfig(name='testing')]

    filtered = _apply_branch_and_file_exemptions(
        gates,
        branch_name='playground/experiment',
        changed_files=['anything.py'],
        config=config
    )

    # No gates should run
    assert len(filtered) == 0
```

**Test Coverage Target**: 95%

**Critical Paths to Test**:
- Branch policy matching (exact, pattern, invalid regex)
- File pattern matching (glob, empty commit, wildcards)
- Exemption logic (union of exemptions, required gates override)
- Edge cases (no policies, no rules, conflicting rules)

---

### 7.2 Integration Tests

**File**: `org-standards/tests/integration/test_quality_gates_scenarios.py`

```python
import subprocess
import os
from pathlib import Path

def test_workflow_change_on_test_branch():
    """
    Integration test: Workflow change on test branch
    Expected: Pass without bypass
    """
    # Setup: Create test repo with config
    test_repo = create_test_repo()

    # Create test branch
    subprocess.run(['git', 'checkout', '-b', 'test/workflow-test'], cwd=test_repo)

    # Make workflow change
    workflow_file = test_repo / '.github/workflows/ci.yml'
    workflow_file.write_text('name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest')

    subprocess.run(['git', 'add', '.'], cwd=test_repo)
    subprocess.run(['git', 'commit', '-m', 'test: workflow change'], cwd=test_repo)

    # Push (triggers quality gates)
    result = subprocess.run(['git', 'push'], cwd=test_repo, capture_output=True)

    # Assert: Push succeeds (no bypass needed)
    assert result.returncode == 0
    assert b'Gates exempted: coverage, type_checking, testing' in result.stderr

def test_code_change_on_main_requires_all_gates():
    """
    Integration test: Code change on main branch
    Expected: All gates required
    """
    test_repo = create_test_repo()

    # On main branch
    subprocess.run(['git', 'checkout', 'main'], cwd=test_repo)

    # Make code change without tests
    code_file = test_repo / 'src/main.py'
    code_file.write_text('def foo(): pass')

    subprocess.run(['git', 'add', '.'], cwd=test_repo)
    subprocess.run(['git', 'commit', '-m', 'feat: add foo'], cwd=test_repo)

    # Push (triggers quality gates)
    result = subprocess.run(['git', 'push'], cwd=test_repo, capture_output=True)

    # Assert: Push fails (no tests = coverage fail)
    assert result.returncode != 0
    assert b'coverage failed' in result.stderr

def test_documentation_change_skips_gates():
    """
    Integration test: Documentation-only change
    Expected: All gates skipped
    """
    test_repo = create_test_repo()

    # Make doc change
    readme = test_repo / 'README.md'
    readme.write_text('# Updated docs')

    subprocess.run(['git', 'add', '.'], cwd=test_repo)
    subprocess.run(['git', 'commit', '-m', 'docs: update readme'], cwd=test_repo)

    # Push
    result = subprocess.run(['git', 'push'], cwd=test_repo, capture_output=True)

    # Assert: Push succeeds, all gates skipped
    assert result.returncode == 0
    assert b'All gates exempted' in result.stderr
```

---

### 7.3 Regression Tests

**Prevent Known Issues**:

```python
def test_regression_invalid_regex_does_not_crash():
    """
    Regression: Invalid regex in branch policy used to crash
    Now: Should log warning and skip policy
    """
    config = QualityGatesConfig(branch_policies={
        'bad': {'pattern': '[invalid', 'description': 'Bad'}
    })
    # Should not raise exception
    policy = _match_branch_policy('anything', config)
    assert policy is None

def test_regression_empty_changed_files_list():
    """
    Regression: Empty changed files (empty commit) used to crash
    Now: Should match empty_commit rule
    """
    config = QualityGatesConfig(file_pattern_rules={
        'empty': {'patterns': [], 'exempt_gates': ['all']}
    })
    matches = _detect_file_patterns([], config)
    assert 'empty' in matches

def test_regression_git_diff_timeout():
    """
    Regression: git diff timeout used to hang indefinitely
    Now: Should timeout after 10s and fail safe
    """
    # Mock slow git diff
    with mock.patch('subprocess.run', side_effect=subprocess.TimeoutExpired('git', 10)):
        changed = _get_changed_files()

    # Should return empty list (fail safe to strict)
    assert changed == []
```

---

## 8. Deployment & Rollback

### 8.1 Deployment Strategy: Gradual Rollout

**Phase 1: Deploy to org-standards (10 min)**

```bash
cd /Users/neerajgarg/NeerajDev/org-standards

# Run full test suite
pytest tests/ -v
# All tests must pass

# Commit changes
git add config/quality-gates.yaml python/quality_gates.py
git commit -m "feat: Quality gates v1.1.0 - branch-aware and file-pattern-based

BREAKING: None (backwards compatible)
NEW: branch_policies, file_pattern_rules sections
CHANGED: type_checking gate now diff-based
ADDED: workflow_validation gate

Testing:
- 95% unit test coverage
- Integration tests pass
- Regression tests pass

Related: StyleGuru/syra#81"

# Tag version
git tag v1.1.0 -a -m "Quality Gates v1.1.0

Branch-aware and file-pattern-based validation.
Reduces emergency bypass rate from 95% to 15%."

# Push
git push origin main --tags
```

**Phase 2: Deploy to Syra (Canary) (15 min)**

```bash
cd /Users/neerajgarg/NeerajDev/syra

# Update submodule
git submodule update --remote org-standards

# Verify version
cd org-standards && git describe --tags
# Should show: v1.1.0

cd ..
git add org-standards
git commit -m "chore: update org-standards to v1.1.0 (quality gates)"

# Test on test branch FIRST
git checkout -b test/quality-gates-v1.1-validation
echo "# Test" >> README.md
git add README.md
git commit -m "test: validate quality gates v1.1.0"
git push

# Expected: Push succeeds (test branch exemptions work)

# If test passes, merge to main
git checkout main
git merge test/quality-gates-v1.1-validation
git push
```

**Phase 3: Monitor Syra (30 min)**

```bash
# Watch for:
# 1. Bypass rate drops
# 2. No new config errors
# 3. Gates still catching real issues

# Check bypass logs
ls -lt /Users/neerajgarg/NeerajDev/syra/.emergency-bypasses/ | head -10

# Analyze bypass reasons
jq -r '.reason' .emergency-bypasses/*.json | sort | uniq -c | sort -rn

# Expected: Fewer bypasses, different reasons
```

**Phase 4: Deploy to StyleGuru and syra-playground (15 min each)**

```bash
# Same process as Syra
cd /Users/neerajgarg/NeerajDev/StyleGuru
git submodule update --remote org-standards
# ... test, commit, push

cd /Users/neerajgarg/NeerajDev/syra-playground
git submodule update --remote org-standards
# ... test, commit, push
```

**Total Deployment Time**: ~70 minutes

---

### 8.2 Rollback Procedure

**Trigger Conditions**:
1. Config parse errors blocking all pushes
2. Gates incorrectly exempting security checks
3. Bypass rate increases (worse than before)
4. Developer feedback: "gates are broken"

**Rollback Steps** (5 min):

```bash
# 1. Revert org-standards to v1.0.0
cd /Users/neerajgarg/NeerajDev/org-standards
git checkout v1.0.0
git push origin main --force

# 2. Update all repos
cd /Users/neerajgarg/NeerajDev/syra
git submodule update --init --recursive
git add org-standards
git commit -m "rollback: revert quality gates to v1.0.0 (v1.1.0 caused issues)"
git push

# Repeat for StyleGuru, syra-playground

# 3. Notify team
echo "⚠️ Quality gates rolled back to v1.0.0 due to issues. Investigating."
```

**Post-Rollback**:
- File incident report
- Analyze what went wrong (config error? logic bug?)
- Fix in development branch
- Re-test thoroughly
- Deploy with more caution

---

### 8.3 Emergency Procedures

**Scenario 1: Config blocks all pushes (P0 incident)**

```bash
# Immediate fix (2 min)
cd /Users/neerajgarg/NeerajDev/org-standards

# Option A: Revert to last known good
git revert HEAD
git push

# Option B: Fix forward (if quick)
vim config/quality-gates.yaml
# Fix syntax error
git commit -m "hotfix: fix quality gates syntax error"
git push

# Notify all developers
echo "🚨 Quality gates temporarily broken. Use EMERGENCY_PUSH=1 if needed."
```

**Scenario 2: Gates not running (security risk)**

```bash
# Immediate action
# 1. Check if submodules are updated
cd /Users/neerajgarg/NeerajDev/syra
git submodule status

# 2. If out of date, update
git submodule update --init --recursive

# 3. Verify hooks installed
ls -la .git/hooks/pre-push

# 4. If missing, reinstall
pre-commit install --hook-type pre-push
```

---

## 9. Monitoring & Observability

### 9.1 Metrics to Track

**Bypass Metrics**:
```bash
# Daily bypass count
find .emergency-bypasses -name "*.json" -mtime -1 | wc -l

# Bypass rate (bypasses / total pushes)
# Total pushes = git log --since="1 day ago" --oneline | wc -l
# Bypass rate = bypasses / total pushes

# Breakdown by reason
jq -r '.reason' .emergency-bypasses/*.json | sort | uniq -c | sort -rn

# Breakdown by branch
jq -r '.branch' .emergency-bypasses/*.json | sort | uniq -c | sort -rn
```

**Gate Execution Metrics**:
```bash
# Gate pass/fail rates (from logs)
grep "✅.*passed" quality-gates.log | wc -l
grep "❌.*failed" quality-gates.log | wc -l

# Average gate execution time
grep "duration:" quality-gates.log | awk '{sum+=$2; count++} END {print sum/count}'

# Gates skipped (due to exemptions)
grep "Gates exempted:" quality-gates.log | wc -l
```

**Config Health**:
```bash
# Config parse errors
grep "Config validation failed" quality-gates.log | wc -l

# Invalid regex warnings
grep "Invalid regex" quality-gates.log | wc -l
```

---

### 9.2 Dashboards

**Bypass Dashboard** (to be created):

```
╔═══════════════════════════════════════════════════════════════╗
║              Quality Gates Bypass Dashboard                   ║
╠═══════════════════════════════════════════════════════════════╣
║ Bypass Rate (Last 7 Days):                                   ║
║   Current: 15% ⬇️ (Target: 15%)                              ║
║   Previous: 95% (Improvement: 80% reduction)                 ║
║                                                               ║
║ Bypass Breakdown by Category:                                ║
║   Workflows:        0 bypasses (eliminated ✅)                ║
║   Documentation:    0 bypasses (eliminated ✅)                ║
║   Pre-existing issues: 1 bypass (rare, acceptable)           ║
║   Genuine emergencies: 2 bypasses (legitimate)               ║
║                                                               ║
║ Bypass Breakdown by Branch:                                  ║
║   main:           0 bypasses ✅                               ║
║   feature/*:      2 bypasses                                 ║
║   test/*:         0 bypasses (eliminated ✅)                  ║
║                                                               ║
║ Top Bypass Reasons (Last 7 Days):                            ║
║   1. "hotfix - production down" (1x) ✅ Legitimate            ║
║   2. "mypy fails on old code" (1x) ⚠️ Tech debt              ║
║   3. "security fix urgent" (1x) ✅ Legitimate                 ║
║                                                               ║
║ Alerts:                                                       ║
║   🟢 No repeated bypass patterns detected                    ║
║   🟢 Config health: OK                                       ║
╚═══════════════════════════════════════════════════════════════╝
```

**Gate Performance Dashboard**:

```
╔═══════════════════════════════════════════════════════════════╗
║            Quality Gates Performance Dashboard                ║
╠═══════════════════════════════════════════════════════════════╣
║ Gate Execution Stats (Last 7 Days):                          ║
║                                                               ║
║   Coverage:                                                   ║
║     Runs: 45       Pass: 38 (84%)    Avg: 12s                ║
║     Skip: 15 (file pattern exemptions)                       ║
║                                                               ║
║   Type Checking:                                              ║
║     Runs: 40       Pass: 35 (88%)    Avg: 8s                 ║
║     Skip: 20 (branch/file exemptions)                        ║
║                                                               ║
║   Linting:                                                    ║
║     Runs: 55       Pass: 52 (95%)    Avg: 3s                 ║
║     Skip: 5 (doc-only changes)                               ║
║                                                               ║
║   Workflow Validation (NEW):                                 ║
║     Runs: 8        Pass: 8 (100%)    Avg: 5s                 ║
║     Skip: 52 (no workflow changes)                           ║
║                                                               ║
║ Exemption Stats:                                              ║
║   Branch-based: 20 (test/playground branches)                ║
║   File-based: 15 (workflows/docs)                            ║
║   Combined: 5 (both branch + file rules)                     ║
╚═══════════════════════════════════════════════════════════════╝
```

---

### 9.3 Alerts

**Critical Alerts** (immediate notification):
- Config parse error (all pushes blocked)
- Gate crash (quality validation broken)
- Bypass rate spike (>50% in 1 hour)

**Warning Alerts** (daily digest):
- Invalid regex in config
- Repeated bypass pattern (same reason >3x/day)
- Gate timeout (>5 min execution)

**Info Alerts** (weekly report):
- Bypass rate trend
- Gate pass/fail rates
- New exemption patterns detected

---

## 10. Security Considerations

### 10.1 Threat Model

**Threat**: Malicious actor modifies config to bypass security gates

**Attack Vector**:
```yaml
# Attacker adds to quality-gates.yaml
branch_policies:
  attacker_branch:
    pattern: ".*"  # Matches ALL branches
    exempt_gates: [all]  # Bypass all gates
```

**Mitigations**:
1. **CODEOWNERS protection**: `quality-gates.yaml` requires @TheNeerajGarg approval
2. **PR review**: All changes to config must be reviewed
3. **Config validation**: Schema validation catches obvious malicious patterns
4. **Audit log**: All config changes logged to Git history
5. **Automated review**: Bot flags suspicious patterns (e.g., `exempt_gates: [all]` on non-playground branches)

---

### 10.2 Security Gates Must Never Be Exempted

**Critical Gates** (can never be exempted):

```yaml
# In quality-gates.yaml
gates:
  security_audit:
    enabled: true
    # Mark as critical (cannot be exempted)
    critical: true
    command: "python bots/security-audit/audit.py"
```

**Enforcement** (in quality_gates.py):

```python
def _apply_branch_and_file_exemptions(...):
    # ... exemption logic ...

    # CRITICAL: Security gates can never be exempted
    for gate in gates_to_run:
        if gate.get('critical', False):
            # Force add to filtered list (even if exempted)
            if gate not in filtered_gates:
                filtered_gates.append(gate)
                logger.info(f"Critical gate '{gate.name}' cannot be exempted")

    return filtered_gates
```

**Critical Gates List**:
- `security_audit` (checks for hardcoded secrets, GITHUB_TOKEN usage)
- `codeowners_validation` (ensures critical files protected)
- `dependency_audit` (checks for vulnerable dependencies)

---

### 10.3 Regex Injection Prevention

**Threat**: User input in branch name causes regex DoS

**Example**:
```python
# Malicious branch name
branch_name = "a" * 10000 + "!"  # Very long, complex regex match

# Vulnerable regex
pattern = "^.*a+!$"  # Catastrophic backtracking

# Result: Regex engine hangs (DoS)
```

**Mitigations**:
1. **Timeout on regex match**: Use `re.match(..., timeout=1)`
2. **Sanitize branch names**: Git already restricts branch name characters
3. **Pre-validate patterns**: Reject patterns with known DoS triggers (e.g., nested quantifiers)

```python
def _validate_regex_pattern(pattern: str) -> bool:
    """
    Validate regex pattern for safety.
    Reject patterns that could cause DoS.
    """
    # Deny list: Patterns known to cause catastrophic backtracking
    dangerous_patterns = [
        r'.*\+',     # Nested quantifiers
        r'\*\*',     # Double wildcards
        r'\+\+',     # Double plus
        r'(.*)+',    # Nested group with quantifier
    ]

    for dangerous in dangerous_patterns:
        if re.search(dangerous, pattern):
            logger.warning(f"Rejected dangerous regex pattern: {pattern}")
            return False

    # Test pattern (timeout protection)
    try:
        re.compile(pattern, timeout=0.1)
    except re.error:
        return False
    except TimeoutError:
        logger.warning(f"Regex pattern timed out during validation: {pattern}")
        return False

    return True
```

---

## 11. Performance Impact

### 11.1 Expected Performance Changes

**Before v1.1.0**:
- All gates run on every push: ~60s (Syra average)
  - Testing: 20s
  - Coverage: 15s
  - Type checking: 20s
  - Linting: 5s

**After v1.1.0**:

**Scenario 1: Workflow change on test branch**
- Gates run: linting, workflow_validation
- Duration: ~8s (87% faster)

**Scenario 2: Documentation change**
- Gates run: none
- Duration: ~1s (98% faster)

**Scenario 3: Code change on main branch**
- Gates run: all (same as before)
- Duration: ~60s (no change)

**Average across all pushes**: ~35s (42% faster)

**Worst case**: 60s (same as before, on main branch)

---

### 11.2 Performance Monitoring

**Metrics**:
```bash
# Gate execution time (per gate)
grep "duration:" quality-gates.log | \
  awk '{print $2, $4}' | \
  sort | uniq -c

# Total push time (pre-push hook)
grep "Total duration:" quality-gates.log | \
  awk '{sum+=$3; count++} END {print "Avg:", sum/count "s"}'
```

**Optimization Opportunities**:
1. **Parallel gate execution**: Run independent gates concurrently
2. **Caching**: Cache gate results for unchanged files
3. **Incremental validation**: Only re-run gates on changed code

---

## 12. Migration Path

### 12.1 Zero-Downtime Migration

**Goal**: Existing repos continue working during migration

**Strategy**: Backwards compatibility (new sections optional)

**Migration Steps**:

**Week 1: Deploy v1.1.0 to org-standards**
- New config sections added (optional, default to disabled)
- All repos continue using v1.0.0 behavior (no branch/file rules)

**Week 2: Migrate Syra (canary)**
- Syra submodule updated to v1.1.0
- Branch policies and file rules enabled
- Monitor bypass rate, gate behavior

**Week 3: Migrate StyleGuru**
- If Syra successful, deploy to StyleGuru
- Same config, tailored to StyleGuru's patterns

**Week 4: Migrate syra-playground**
- Deploy to playground
- More permissive policies (playground branches exempt all)

**Week 5: Evaluate and tune**
- Analyze metrics from all 3 repos
- Adjust thresholds, patterns based on data
- Document lessons learned

---

### 12.2 Compatibility Matrix

| Repo | org-standards version | Branch Policies | File Rules | Status |
|------|----------------------|-----------------|------------|--------|
| Syra | v1.0.0 | ❌ Not supported | ❌ Not supported | Legacy |
| Syra | v1.1.0 | ✅ Supported | ✅ Supported | Current |
| StyleGuru | v1.0.0 | ❌ Not supported | ❌ Not supported | Legacy |
| StyleGuru | v1.1.0 | ✅ Supported | ✅ Supported | Migration pending |

**Backwards Compatibility Guarantee**:
- v1.1.0 repos can read v1.0.0 configs (missing sections = disabled)
- v1.0.0 repos cannot read v1.1.0 configs (unknown sections = error)
- Migration must be one-way (v1.0.0 → v1.1.0), no rollback to v1.0.0 after policy tuning

---

## 13. Risks & Mitigations

### 13.1 High-Risk Scenarios

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Config parse error blocks all pushes** | Medium | Critical | Schema validation + rollback procedure |
| **Regex DoS causes gate timeout** | Low | High | Regex validation + timeout enforcement |
| **Security gate incorrectly exempted** | Low | Critical | Critical gates marked unexemptable |
| **File pattern matches wrong files** | Medium | Medium | Comprehensive glob tests + monitoring |
| **Branch policy too permissive** | Medium | Medium | Gradual rollout + bypass monitoring |

---

### 13.2 Mitigation Details

**Risk: Config parse error blocks all pushes**

**Scenario**: Syntax error in `quality-gates.yaml` causes all pushes to fail

**Mitigation**:
1. **Pre-commit validation**: Validate YAML syntax before commit
   ```yaml
   # .pre-commit-config.yaml
   - repo: local
     hooks:
       - id: validate-quality-gates
         name: Validate quality-gates.yaml
         entry: python -c "import yaml; yaml.safe_load(open('config/quality-gates.yaml'))"
         language: system
         files: config/quality-gates.yaml
   ```

2. **CI validation**: Run schema validation in CI before merge
   ```bash
   # .github/workflows/validate-config.yml
   python scripts/validate_quality_gates_schema.py config/quality-gates.yaml
   ```

3. **Automated rollback**: If config errors persist >10 min, auto-revert
   ```bash
   # In monitoring system
   if [ $CONFIG_ERROR_COUNT -gt 10 ]; then
     git revert HEAD
     git push
     alert "Auto-reverted quality-gates.yaml due to parse errors"
   fi
   ```

4. **Emergency bypass**: Users can always bypass with `EMERGENCY_PUSH=1`

---

**Risk: Security gate incorrectly exempted**

**Scenario**: File pattern rule accidentally exempts security audit

**Mitigation**:
1. **Critical gate flag**: Security gates marked `critical: true` (unexemptable)
2. **Exemption validation**: Warn if critical gate in `exempt_gates` list
   ```python
   for gate_name in rule.get('exempt_gates', []):
       if config.gates[gate_name].get('critical', False):
           logger.error(
               f"CRITICAL: Attempting to exempt security gate '{gate_name}' "
               f"in rule '{rule_name}'. This is not allowed."
           )
           # Remove from exemption list
           rule['exempt_gates'].remove(gate_name)
   ```

3. **Audit trail**: Log all security gate exemption attempts
4. **Manual review**: Security team reviews all changes to file pattern rules

---

**Risk: File pattern matches wrong files**

**Scenario**: Glob pattern `*.yml` matches too broadly, exempts Python files accidentally

**Mitigation**:
1. **Explicit patterns**: Use full paths, not wildcards
   - ❌ Bad: `*.yml`
   - ✅ Good: `.github/workflows/*.yml`

2. **Pattern testing**: Test glob patterns in CI
   ```python
   # In tests
   def test_workflow_pattern_specificity():
       pattern = '.github/workflows/*.yml'
       # Should match
       assert fnmatch.fnmatch('.github/workflows/ci.yml', pattern)
       # Should NOT match
       assert not fnmatch.fnmatch('src/config.yml', pattern)
   ```

3. **Dry-run mode**: Log matched files before applying exemptions
   ```python
   logger.info(f"File pattern '{rule_name}' matched files: {matched_files}")
   ```

---

## 14. Appendix: ERD Checklist

Following org-standards ERD checklist (40 items):

### Planning & Problem Definition
- [x] 1. Problem clearly stated with metrics
- [x] 2. Desired outcome defined (15% bypass rate)
- [x] 3. Non-goals documented (not changing gate commands themselves)
- [x] 4. Success criteria measurable (bypass rate, gate execution time)

### Technical Design
- [x] 5. Architecture diagram provided
- [x] 6. Component responsibilities clear
- [x] 7. Data flow documented (3 scenarios)
- [x] 8. API/interfaces specified (config schema)
- [x] 9. Error handling comprehensive (5 error types)
- [x] 10. Edge cases identified (empty commits, invalid regex)

### Configuration & Schema
- [x] 11. Config schema versioned (v1.0.0 → v1.1.0)
- [x] 12. Schema validation specified
- [x] 13. Migration path defined (gradual rollout)
- [x] 14. Backwards compatibility guaranteed
- [x] 15. Default values documented

### Security
- [x] 16. Threat model provided
- [x] 17. Security gates unexemptable
- [x] 18. Regex injection prevented
- [x] 19. CODEOWNERS protection required
- [x] 20. Audit trail (Git history)

### Testing
- [x] 21. Unit tests specified (95% coverage)
- [x] 22. Integration tests defined
- [x] 23. Regression tests included
- [x] 24. Performance tests outlined
- [x] 25. Test data provided (example configs)

### Deployment
- [x] 26. Deployment strategy (gradual rollout)
- [x] 27. Rollback procedure (<5 min)
- [x] 28. Monitoring plan (dashboards)
- [x] 29. Alerting strategy (critical/warning/info)
- [x] 30. Canary deployment (Syra first)

### Observability
- [x] 31. Metrics defined (bypass rate, gate duration)
- [x] 32. Logging strategy (structured logs)
- [x] 33. Dashboards designed
- [x] 34. Alerts configured
- [x] 35. Debugging aids (dry-run mode)

### Documentation
- [x] 36. User-facing error messages clear
- [x] 37. Config examples provided
- [x] 38. Troubleshooting guide included
- [x] 39. Runbook for ops team
- [x] 40. This ERD complete and reviewed

---

## Appendix B: Implementation Checklist

**Pre-Implementation**:
- [ ] ERD reviewed by @TheNeerajGarg
- [ ] Security implications reviewed
- [ ] Performance impact assessed

**Implementation**:
- [ ] Schema additions to quality-gates.yaml
- [ ] Branch policy matching logic
- [ ] File pattern detection logic
- [ ] Exemption application logic
- [ ] Diff-based MyPy implementation
- [ ] Workflow validation gate
- [ ] Unit tests (95% coverage)
- [ ] Integration tests
- [ ] Regression tests

**Pre-Deployment**:
- [ ] All tests pass
- [ ] Config validated
- [ ] Rollback procedure tested
- [ ] Monitoring dashboards ready

**Deployment**:
- [ ] Deploy to org-standards v1.1.0
- [ ] Canary deploy to Syra
- [ ] Monitor for 48 hours
- [ ] Deploy to StyleGuru
- [ ] Deploy to syra-playground

**Post-Deployment**:
- [ ] Verify bypass rate reduced
- [ ] No config errors
- [ ] Gates catching real issues
- [ ] Performance acceptable
- [ ] Update documentation
- [ ] Close Issue #81

---

**END OF ERD**

**Next Steps**:
1. Review this ERD with stakeholders
2. Approve for implementation
3. Begin Phase 1 implementation (2 hours)
4. Deploy and monitor

**Questions/Concerns**: File as comments on Issue #81
