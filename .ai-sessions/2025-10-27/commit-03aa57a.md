# Introspection: Validation Script - Move to org-standards for Automatic Propagation

**Session**: 2025-10-27
**Commit Hash**: 03aa57a (pending)
**Type**: Architecture Fix
**Repo**: org-standards

---

## What Was the Problem?

Validation script was created in Syra only, but pre-commit hook (in org-standards) referenced it. This meant:
- ❌ Syra would have validation (has script locally)
- ❌ StyleGuru would get hook but NO validation (missing script)
- ❌ Inconsistent enforcement across repos
- ❌ Required manual setup in each repo

**Root Issue**: Script needed to propagate automatically with org-standards, not be repo-specific.

**Change Made**:
- Moved `scripts/validate-introspection.py` from Syra → `org-standards/scripts/`
- Updated pre-commit hook to reference `org-standards/scripts/validate-introspection.py`
- Now works automatically everywhere: GitHub Actions, containers, new Macs
- Zero setup required

---

## Why Did It Happen?

**Root Cause**: Initial implementation didn't follow the org-standards propagation pattern.

**Context I Lacked**:
- Initially placed script in Syra's `scripts/` (repo-specific)
- Hook referenced `scripts/validate-introspection.py` (assumed local copy)
- Didn't realize hook can reference org-standards submodule directly

**Assumptions I Made**:
- ❌ WRONG: Assumed repos needed to copy/symlink script locally
- ✅ CORRECT: Hook can reference submodule path directly

**User Correction**:
User asked: "Why can't the hook directly reference the sub-module?"
- Highlighted that symlinking was unnecessary complexity
- Pointed out that direct submodule reference is simpler and automatic

---

## How Could It Have Been Prevented?

**What I Could Have Done Differently**:
1. Asked upfront: "Where should shared scripts live for automatic propagation?"
2. Read org-standards structure first (check existing `scripts/` directory)
3. Followed the pattern: If it's in org-standards repo, it propagates automatically

**What Would Help Prevent This Class of Issue**:
- **CLAUDE.md Rule**: When adding validation/tooling that needs to work across all repos:
  - Check if org-standards has a pattern for this (git-hooks/, scripts/, etc.)
  - If tool is shared → put in org-standards (automatic propagation)
  - If tool is repo-specific → put in repo's scripts/
  - Hook/script can reference org-standards submodule directly (no copying/symlinking)

**Proposed CLAUDE.md Addition**:
```markdown
## Org-Standards Propagation Pattern

When adding shared tooling (validation, scripts, configs):

1. **Shared across all repos** → Add to org-standards
   - git-hooks/ → Pre-commit/pre-push hooks
   - scripts/ → Validation scripts, utilities
   - .claude/ → Documentation
   - Reference in hooks: `org-standards/scripts/tool.py`

2. **Repo-specific** → Add to individual repo
   - Custom workflows, configs, features

**Anti-Pattern**: Creating repo-specific scripts that hooks expect (breaks propagation)
**Correct Pattern**: Put script in org-standards, reference submodule path
```

---

## Impact Assessment

**Blast Radius**: Low - Fixes propagation issue before StyleGuru adoption
**Risk**: Very low - Same validation logic, just moved location
**Rollback**: Easy - Move script back, update hook reference

---

## Testing Plan

**Verification in Syra**:
```bash
# Test hook references submodule correctly
git commit -m "test" (with valid introspection)
# Should see: "📝 Validating introspection schema... ✅ Introspection schema valid"

# Test validation actually runs
git commit -m "test" (with invalid introspection)
# Should be BLOCKED with clear error
```

**Verification in StyleGuru** (after propagation):
```bash
# Update submodule
git submodule update --remote org-standards

# Test validation works automatically (no manual setup needed)
git commit -m "test"
# Should validate using org-standards/scripts/validate-introspection.py
```

---

## Related Context

- **Status Document**: Syra `.claude/ARTIFACT-STORAGE-STATUS.md`
- **User Feedback**: "Why can't the hook directly reference the sub-module?"
- **Architecture Decision**: Direct submodule reference > copying/symlinking
- **Benefit**: Zero setup, works everywhere automatically
