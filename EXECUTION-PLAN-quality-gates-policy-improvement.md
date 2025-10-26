# Execution Plan: Quality Gates Policy Improvement

**Issue**: https://github.com/StyleGuru/syra/issues/81
**Analysis**: [EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md](EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md)
**Created**: 2025-10-25
**Owner**: @TheNeerajGarg
**Estimated Total Time**: 8-10 hours (across 3 phases)

---

## Objective

Reduce emergency bypass rate from **95% to 15%** by implementing branch-aware and file-pattern-based quality gates that align with repository purpose while maintaining code quality standards.

---

## Phase 1: Immediate (Deploy Today) - 2 hours

**Goal**: Eliminate 80% of bypasses (16/19) within 24 hours

### Task 1.1: Add Branch-Aware Policies (30 min)

**File**: `org-standards/config/quality-gates.yaml`

**Add new section**:
```yaml
# =============================================================================
# Branch-Aware Quality Gates (v1.1.0)
# =============================================================================
branch_policies:
  # Production branch: Full gates required
  main:
    enforcement_level: strict
    all_gates_required: true
    description: "Production code requires all quality gates"

  # Feature branches: Relaxed for iterative development
  feature:
    pattern: "^feature/.*"
    enforcement_level: relaxed
    exempt_gates: []  # All gates run, but lower thresholds
    coverage_threshold: 60  # Lower bar during development (vs 85% on main)
    description: "Feature branches allow iteration, full validation at PR"

  # Test branches: Minimal validation only
  test:
    pattern: "^test/.*"
    enforcement_level: minimal
    exempt_gates: [coverage, type_checking]
    required_gates: [linting, testing]
    description: "Test branches for experimentation, PR review ensures quality"

  # Workflow development branches: Workflow-specific gates
  workflow:
    pattern: "^workflow/.*"
    enforcement_level: specialized
    exempt_gates: [coverage, type_checking, testing]
    required_gates: [workflow_validation]
    description: "Workflow development uses YAML validation, not code coverage"

  # Playground branches: No gates (learning environment)
  playground:
    pattern: "^playground/.*"
    enforcement_level: none
    exempt_gates: [all]
    description: "Playground is for learning, no gates enforced"
```

**Verification**:
```bash
# Test on Syra
cd /Users/neerajgarg/NeerajDev/syra
git checkout -b test/policy-validation
echo "# Test" >> README.md
git add README.md
git commit -m "test: verify test branch policies"
git push

# Expected: Push succeeds without emergency bypass (coverage/type_checking skipped)
```

**Success Criteria**:
- Test branch pushes do not require emergency bypass
- Main branch still requires all gates

---

### Task 1.2: Add File-Pattern-Based Gate Selection (45 min)

**File**: `org-standards/config/quality-gates.yaml`

**Add new section**:
```yaml
# =============================================================================
# File Pattern Rules - Smart Gate Selection
# =============================================================================
file_pattern_rules:
  # GitHub Actions workflows: YAML validation only
  workflows:
    patterns:
      - ".github/workflows/*.yml"
      - ".github/workflows/*.yaml"
    exempt_gates: [coverage, type_checking, testing]
    required_gates: [workflow_validation]
    description: "Workflows are declarative config, need YAML validation not code coverage"

  # Documentation: Minimal validation
  documentation:
    patterns:
      - ".ai-sessions/**/*.md"
      - "docs/**/*.md"
      - "*.md"
      - "*.txt"
    exempt_gates: [coverage, type_checking, testing, linting]
    required_gates: []
    description: "Documentation changes don't require code quality gates"

  # Configuration files: Syntax validation only
  configs:
    patterns:
      - "*.yaml"
      - "*.yml"
      - "*.toml"
      - "*.json"
      - ".github/**/*.json"
    exempt_gates: [coverage, type_checking, testing]
    required_gates: [linting]
    description: "Config files need syntax validation, not code coverage"

  # Introspection logs: No gates (append-only)
  introspection:
    patterns:
      - ".ai-sessions/**/*.md"
      - ".ai-sessions/**/*.json"
    exempt_gates: [all]
    description: "Introspection logs are append-only, no validation needed"

  # Empty commits: No gates (used for CI triggers)
  empty_commit:
    patterns: []  # Special case: no files changed
    exempt_gates: [all]
    description: "Empty commits used to trigger workflows, no code to validate"
```

**Verification**:
```bash
# Test workflow-only change
cd /Users/neerajgarg/NeerajDev/syra
git checkout -b test/workflow-only-change
echo "# comment" >> .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "test: workflow comment"
git push

# Expected: Workflow validation runs, coverage/testing skipped
```

**Success Criteria**:
- Workflow changes skip coverage/testing gates
- Documentation changes skip all gates
- Python code changes still run all gates

---

### Task 1.3: Implement Diff-Based MyPy Validation (30 min)

**File**: `org-standards/config/quality-gates.yaml`

**Update type_checking gate**:
```yaml
gates:
  type_checking:
    enabled: true
    tool: mypy
    description: "Type check changed Python files only (diff-based)"
    required: true

    # OLD: command: "mypy ."
    # NEW: Diff-based validation
    command: |
      CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep '\.py$' || true)
      if [ -z "$CHANGED_FILES" ]; then
        echo "✓ No Python files changed, skipping MyPy"
        exit 0
      fi
      echo "Running MyPy on changed files:"
      echo "$CHANGED_FILES"
      echo "$CHANGED_FILES" | xargs mypy

    fail_message: |
      Type checking failed on your changes.

      Fix: Add type hints to new/modified functions

      Note: Pre-existing MyPy failures in other files don't block your work.
      This gate only checks files you modified.

    timeout_seconds: 120
```

**Verification**:
```bash
# Test with new code that has type hints
cd /Users/neerajgarg/NeerajDev/syra
git checkout -b feature/new-typed-code
# Add new file with type hints
cat > new_module.py <<EOF
def greet(name: str) -> str:
    return f"Hello, {name}"
EOF
git add new_module.py
git commit -m "feat: add new typed module"
git push

# Expected: MyPy only checks new_module.py, ignores pre-existing failures
```

**Success Criteria**:
- New code with type hints passes MyPy
- Pre-existing MyPy failures in unrelated files don't block push

---

### Task 1.4: Update quality_gates.py Implementation (45 min)

**File**: `org-standards/python/quality_gates.py`

**Add functions**:

```python
def _match_branch_policy(branch_name: str, config: QualityGatesConfig) -> Optional[Dict]:
    """
    Match current branch against branch policies.

    Returns policy configuration if match found, None otherwise.
    """
    if not hasattr(config, 'branch_policies'):
        return None

    for policy_name, policy in config.branch_policies.items():
        if policy_name == 'main' and branch_name == 'main':
            return policy
        elif 'pattern' in policy:
            import re
            if re.match(policy['pattern'], branch_name):
                return policy
    return None


def _detect_file_patterns(changed_files: List[str], config: QualityGatesConfig) -> List[str]:
    """
    Detect which file pattern rules apply to changed files.

    Returns list of rule names that match.
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

        # Check if any changed file matches any pattern
        import fnmatch
        for file_path in changed_files:
            for pattern in patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    matched_rules.append(rule_name)
                    break

    return list(set(matched_rules))  # Deduplicate


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
    # Check branch policy
    branch_policy = _match_branch_policy(branch_name, config)
    exempt_gates = set()

    if branch_policy:
        print(f"📋 Branch policy: {branch_policy.get('description', 'N/A')}")
        exempt_gates.update(branch_policy.get('exempt_gates', []))

    # Check file pattern rules
    matched_rules = _detect_file_patterns(changed_files, config)
    if matched_rules:
        print(f"📋 File patterns detected: {', '.join(matched_rules)}")
        for rule_name in matched_rules:
            rule = config.file_pattern_rules[rule_name]
            exempt_gates.update(rule.get('exempt_gates', []))

    # Filter gates
    if 'all' in exempt_gates:
        print("✓ All gates exempted")
        return []

    filtered_gates = [
        gate for gate in gates_to_run
        if gate.name not in exempt_gates
    ]

    if len(filtered_gates) < len(gates_to_run):
        exempted = [g.name for g in gates_to_run if g not in filtered_gates]
        print(f"✓ Gates exempted: {', '.join(exempted)}")

    return filtered_gates
```

**Integrate into main execution**:
```python
# In main() function, after loading config and before running gates:

# Detect current branch
current_branch = subprocess.run(
    ["git", "branch", "--show-current"],
    capture_output=True, text=True
).stdout.strip()

# Get changed files
changed_files = subprocess.run(
    ["git", "diff", "--name-only", "origin/main...HEAD"],
    capture_output=True, text=True
).stdout.strip().split('\n')

# Apply exemptions
gates_to_run = _apply_branch_and_file_exemptions(
    gates_to_run, current_branch, changed_files, config
)
```

**Verification**:
```bash
cd /Users/neerajgarg/NeerajDev/org-standards
pytest tests/test_quality_gates_branch_policies.py -v
```

**Success Criteria**:
- Tests pass for branch policy matching
- Tests pass for file pattern detection
- Integration test shows gates correctly exempted

---

### Task 1.5: Deploy to org-standards and Propagate (15 min)

**Steps**:
```bash
cd /Users/neerajgarg/NeerajDev/org-standards

# Commit changes
git add config/quality-gates.yaml python/quality_gates.py
git commit -m "feat: Add branch-aware and file-pattern-based quality gates (v1.1.0)

Implements smart gate selection based on branch type and file patterns
to reduce emergency bypass rate from 95% to 15%.

Changes:
- Branch policies: test/feature/main branches have different gates
- File pattern rules: workflows/docs/configs skip code coverage gates
- Diff-based MyPy: only check changed files, not entire repo

Impact:
- Eliminates 80% of emergency bypasses (16/19)
- Test branches can iterate without coverage gate friction
- Workflow changes validated with YAML checks, not code coverage

Related: StyleGuru/syra#81"

# Tag as v1.1.0
git tag v1.1.0
git push origin main --tags

# Update submodules in all repos
cd /Users/neerajgarg/NeerajDev/syra
git submodule update --remote org-standards
git add org-standards
git commit -m "chore: update org-standards to v1.1.0 (quality gates improvements)"
git push

cd /Users/neerajgarg/NeerajDev/StyleGuru
git submodule update --remote org-standards
git add org-standards
git commit -m "chore: update org-standards to v1.1.0 (quality gates improvements)"
git push

cd /Users/neerajgarg/NeerajDev/syra-playground
git submodule update --remote org-standards
git add org-standards
git commit -m "chore: update org-standards to v1.1.0 (quality gates improvements)"
git push
```

**Rollback Plan**:
```bash
# If issues arise, revert to v1.0.0
cd /Users/neerajgarg/NeerajDev/org-standards
git checkout v1.0.0
git push origin main --force

# Update submodules back
cd /Users/neerajgarg/NeerajDev/syra
git submodule update --init --recursive
```

**Success Criteria**:
- org-standards tagged as v1.1.0
- All 3 repos using updated org-standards
- Test branch pushes work without bypasses

---

## Phase 2: This Week (2-4 hours)

**Goal**: Eliminate remaining friction points, add specialized validation

### Task 2.1: Add Workflow Validation Gate (2 hours)

**Install tools**:
```bash
# In CI environment (GitHub Actions)
pip install yamllint
brew install actionlint  # or download binary for CI
```

**Create .yamllint.yml**:
```yaml
extends: default
rules:
  line-length:
    max: 120
  comments:
    min-spaces-from-content: 1
  indentation:
    spaces: 2
```

**Add to quality-gates.yaml**:
```yaml
gates:
  workflow_validation:
    enabled: true
    tool: composite
    description: "Validate GitHub Actions workflows (YAML syntax + security)"
    required: true

    commands:
      # YAML syntax validation
      syntax: "yamllint -c .yamllint.yml .github/workflows/"

      # Security check: no hardcoded secrets
      security: |
        if grep -r 'secrets\.GITHUB_TOKEN' .github/workflows/; then
          echo "❌ Found GITHUB_TOKEN usage (should use BOT_GITHUB_TOKEN)"
          exit 1
        fi
        if grep -rE '(password|api_key|secret).*=.*["\']' .github/workflows/; then
          echo "❌ Found potential hardcoded secrets"
          exit 1
        fi

      # Workflow schema validation
      actionlint: "actionlint .github/workflows/*.yml"

    fail_message: |
      Workflow validation failed.

      Fixes:
      - Syntax errors: Run 'yamllint .github/workflows/' locally
      - Security issues: Use secrets.BOT_GITHUB_TOKEN, not secrets.GITHUB_TOKEN
      - Schema errors: Run 'actionlint .github/workflows/*.yml' locally

    timeout_seconds: 60
    applies_to_patterns: [".github/workflows/*.yml"]
```

**Verification**:
```bash
# Test on workflow change
cd /Users/neerajgarg/NeerajDev/syra
git checkout -b workflow/test-validation
# Make invalid YAML change
echo "invalid: yaml: syntax:" >> .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "test: invalid yaml"
git push

# Expected: Workflow validation catches syntax error
```

**Success Criteria**:
- Workflow syntax errors caught before push
- Security violations (hardcoded tokens) blocked
- Valid workflow changes pass validation

**Estimated Time**: 2 hours

---

### Task 2.2: Trust Pre-Commit Hooks (1 hour)

**Update linting gate in quality-gates.yaml**:
```yaml
gates:
  linting:
    enabled: true
    tool: ruff
    description: "Linting (trusts pre-commit if already run)"
    required: true

    # Check if pre-commit already ran
    pre_check: |
      if git log -1 --pretty=%B | grep -q "\\[pre-commit\\]"; then
        echo "✓ Pre-commit hooks already validated formatting"
        echo "✓ Skipping redundant linting check"
        exit 0
      fi

    commands:
      format_check: "ruff format --check ."
      lint_check: "ruff check ."

    fail_message: |
      Linting failed.

      Fix:
      1. Run pre-commit hooks: pre-commit run --all-files
      2. Commit changes: git commit -m "fix: apply linting fixes [pre-commit]"
      3. Push again

      Note: Pre-commit hooks auto-fix most issues. If hooks pass, this gate will be skipped.
```

**Update pre-commit hook to mark commits**:
```bash
# In .git/hooks/pre-commit
# After all checks pass, append [pre-commit] to commit message
# (Most pre-commit frameworks do this automatically)
```

**Verification**:
```bash
# Test with pre-commit hook
cd /Users/neerajgarg/NeerajDev/syra
pre-commit run --all-files
git commit -m "fix: apply linting [pre-commit]"
git push

# Expected: Linting gate skipped (pre-commit marker detected)
```

**Success Criteria**:
- Pre-commit hook passes → Linting gate skipped
- No pre-commit marker → Linting gate runs

**Estimated Time**: 1 hour

---

### Task 2.3: Graduated Quality Thresholds (1 hour)

**Update coverage gate in quality-gates.yaml**:
```yaml
gates:
  coverage:
    enabled: true
    tool: diff-cover
    threshold: 85  # Production standard (main branch)
    required: true

    # Branch-based threshold graduation
    stage_relaxations:
      # Feature branches: Lower bar for WIP
      feature:
        threshold: 60
        branch_pattern: "^feature/.*"
        description: "Feature branches allow iteration with lower coverage"

      # Test branches: Even lower for experimentation
      test:
        threshold: 40
        branch_pattern: "^test/.*"
        description: "Test branches for experimentation"

      # PR stage: Moderate requirement before merge
      pr:
        threshold: 80
        description: "PR must improve coverage before merge"

      # Main branch: Full standard (uses base threshold: 85%)
```

**Verification**:
```bash
# Test on feature branch
cd /Users/neerajgarg/NeerajDev/syra
git checkout -b feature/test-graduated-thresholds
# Add code with 65% coverage
git push

# Expected: Passes (65% > 60% feature threshold)

# Test on main branch
git checkout main
git merge feature/test-graduated-thresholds
git push

# Expected: Fails (65% < 85% main threshold) or requires PR review
```

**Success Criteria**:
- Feature branches accept 60% coverage
- Main branch requires 85% coverage
- PR review enforces 80% threshold

**Estimated Time**: 1 hour

---

## Phase 3: Next Quarter (4-6 hours)

**Goal**: Self-learning quality gate system

### Task 3.1: Build Bypass Pattern Analyzer (2-3 hours)

**Create bypass analyzer script**:
```python
# org-standards/python/bypass_analyzer.py

def analyze_bypass_logs(bypass_dir: str) -> Dict[str, Any]:
    """
    Analyze emergency bypass logs to detect patterns.

    Returns:
    - Common bypass reasons
    - File pattern correlations
    - Suggested auto-exemptions
    """
    import json
    from pathlib import Path
    from collections import Counter

    bypasses = []
    for log_file in Path(bypass_dir).glob("*.json"):
        with open(log_file) as f:
            bypasses.append(json.load(f))

    # Cluster by reason
    reasons = Counter(b['reason'] for b in bypasses)

    # Detect file patterns
    # (requires git log inspection)

    # Generate recommendations
    recommendations = []
    if reasons.most_common(1)[0][1] > 5:  # >5 instances
        recommendations.append({
            'pattern': reasons.most_common(1)[0][0],
            'confidence': 0.9,
            'suggested_exemption': '...'
        })

    return {
        'total_bypasses': len(bypasses),
        'common_reasons': dict(reasons.most_common(5)),
        'recommendations': recommendations
    }
```

**Integration**:
- Run analyzer weekly in CI
- Generate report in `.ai-sessions/YYYY-MM-DD/bypass-analysis-report.md`
- Alert if new patterns detected

**Success Criteria**:
- Analyzer runs weekly
- Recommendations logged
- Pattern detection accuracy >80%

**Estimated Time**: 2-3 hours

---

### Task 3.2: Implement Contextual Gates (2-3 hours)

**Add repository type detection**:
```yaml
# org-standards/config/repository-types.yaml
repository_types:
  development-tooling:
    indicators:
      - ".github/workflows/" directory exists
      - "bots/" directory exists
      - More workflow files than source files

    contextual_rules:
      workflows:
        gates: [workflow_validation, security_audit]
        skip: [coverage, type_checking]

      bots:
        gates: [testing, type_checking, coverage]
        coverage_threshold: 70  # Lower for experimental

      introspection:
        gates: [linting]
        skip: [coverage, type_checking]
```

**Success Criteria**:
- Repository type auto-detected
- Contextual rules applied
- Gate selection adapts to file purpose

**Estimated Time**: 2-3 hours

---

## Monitoring & Success Metrics

### Metrics to Track

**Daily**:
```bash
# Count bypasses
wc -l .emergency-bypasses/*.json

# Breakdown by reason
jq -r '.reason' .emergency-bypasses/*.json | sort | uniq -c
```

**Weekly Review**:
- Bypass rate trend (should decrease from 95% → 15%)
- New bypass patterns (flag for analysis)
- False positive rate (gates blocking legitimate work)

**Monthly**:
- Policy effectiveness review
- Threshold adjustments
- New exemption rules

### Target Metrics

| Metric | Current | After Phase 1 | After Phase 2 | Target (Phase 3) |
|--------|---------|---------------|---------------|------------------|
| Bypass Rate | 95% | 15% | 10% | <5% |
| Workflow-Only Bypasses | 13 | 0 | 0 | 0 |
| Test Branch Bypasses | 19 | 0 | 0 | 0 |
| Iteration Cycles | 4 pushes | 1 push | 1 push | 1 push |

---

## Rollback & Risk Mitigation

### Rollback Procedure

**If Phase 1 causes issues**:
```bash
cd /Users/neerajgarg/NeerajDev/org-standards
git revert HEAD  # Revert to v1.0.0
git push origin main

# Update all repos
cd /Users/neerajgarg/NeerajDev/syra
git submodule update --init --recursive
```

### Risk Mitigation

**Risk**: Workflow bugs slip through without code coverage
**Mitigation**: Add workflow validation gate (Phase 2, Task 2.1)

**Risk**: Test branches merge without proper review
**Mitigation**: PR review still required (GitHub branch protection)

**Risk**: Diff-based MyPy misses global type issues
**Mitigation**: Run full MyPy weekly in CI (non-blocking, tech debt tracking)

---

## Definition of Done

### Phase 1 Complete When:
- [ ] Branch policies implemented in quality-gates.yaml
- [ ] File pattern rules implemented
- [ ] Diff-based MyPy working
- [ ] quality_gates.py supports new features
- [ ] All tests pass
- [ ] Deployed to org-standards v1.1.0
- [ ] All repos updated
- [ ] Test branch pushes succeed without bypasses
- [ ] Workflow changes skip code coverage gates
- [ ] Issue #81 updated with results

### Phase 2 Complete When:
- [ ] Workflow validation gate implemented
- [ ] Pre-commit trust working
- [ ] Graduated thresholds active
- [ ] Bypass logs showing <10% rate
- [ ] Documentation updated

### Phase 3 Complete When:
- [ ] Bypass analyzer running weekly
- [ ] Contextual gates implemented
- [ ] Bypass rate <5%
- [ ] Self-learning recommendations generated

---

## Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1 | 2 hours | 2025-10-25 | 2025-10-25 (Today) |
| Phase 2 | 2-4 hours | 2025-10-28 | 2025-11-01 (This week) |
| Phase 3 | 4-6 hours | 2025-11-04 | 2026-01-31 (Q1 2026) |

**Total**: 8-12 hours across 3 months

---

## Related Documents

- **Analysis**: [EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md](https://github.com/TheNeerajGarg/org-standards/blob/main/EMERGENCY_BYPASS_ANALYSIS_2025-10-25.md)
- **Issue**: https://github.com/StyleGuru/syra/issues/81
- **Current Config**: [quality-gates.yaml](https://github.com/TheNeerajGarg/org-standards/blob/main/config/quality-gates.yaml)

---

**Created**: 2025-10-25
**Owner**: @TheNeerajGarg
**Reviewers**: Principal Engineer, Test Architect
