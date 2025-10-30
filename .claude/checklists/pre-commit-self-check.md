# Pre-commit Self-Check (30 seconds)

**When to use**: Before every `git commit` (quick sanity check)

**How to use**: Mentally review or scan this list (7 items, 30 seconds)

**Purpose**: Catch basic hygiene issues before committing (cheap to fix now vs later)

---

## Checklist

- [ ] **Tests added** (or N/A for docs/refactor)
      New functions/classes have corresponding tests in `tests/`

      Why: Tests are part of the feature, not afterthought
      Quality gate: Pre-push hook will enforce, but check now

- [ ] **Docstrings present** (public functions only)
      Google-style docstrings with Args, Returns, Raises sections

      Why: API documentation helps future developers (including you)
      Example:
      ```python
      def calculate_total(items: list[Item]) -> Decimal:
          """Calculate total price for items.

          Args:
              items: List of items to sum

          Returns:
              Total price as Decimal

          Raises:
              ValueError: If items list is empty
          """
      ```

- [ ] **Type hints included** (all parameters and returns)
      All function parameters, return types fully typed

      Why: MyPy enforcement, IDE support, documentation
      Quality gate: MyPy will catch missing hints, but check now

- [ ] **Debug code removed**
      No `print()`, `import pdb`, `breakpoint()`, `console.log()`

      Exception: `print()` is OK for CLI tools (executable scripts in `scripts/` or with shebang)

      Why: Debug code pollutes production logs, confuses developers
      Check: Grep for common debug patterns before commit

      Example:
      ```python
      # Production code ❌
      def calculate_total(items):
          print(f"Items: {items}")  # Remove this
          return sum(item.price for item in items)

      # CLI tool ✅
      if __name__ == "__main__":
          result = calculate_total(items)
          print(f"Total: ${result}")  # OK for CLI output
      ```

- [ ] **TODO comments removed** (use GitHub issues instead)
      No `# TODO:`, `# FIXME:`, `# HACK:` in committed code

      Why: TODOs get lost in code, GitHub issues get tracked
      Action: Create issue, link in commit message, remove TODO

- [ ] **Sensitive data check**
      No API keys, passwords, tokens, PII in committed files

      Why: Once in git history, hard to remove (security risk)
      Check: Review `.env` changes, config files, test fixtures

- [ ] **Imports organized**
      No unused imports, imports grouped (stdlib, third-party, local)

      Why: Ruff will fix, but visual clutter during review
      Quality gate: Ruff check in pre-push hook

---

## Not Checked Here (Automated Quality Gates Handle)

These items are enforced by pre-commit/pre-push hooks, no manual check needed:

- ✅ Ruff formatting (pre-commit hook auto-fixes)
- ✅ Ruff linting (pre-push hook blocks)
- ✅ MyPy type checking (pre-push hook blocks)
- ✅ Pytest execution (pre-push hook blocks)
- ✅ Coverage ≥80% (pre-push hook blocks)

---

## Time Investment

**Target**: <30 seconds (quick mental review)

**If any item fails**: Fix immediately (cheaper now than in PR review)

---

## Related

- **Next stage**: Pre-push review (after pre-push hook passes)
- **Automation**: Not automated (too fast, manual is fine)
- **Cost**: Free (30 seconds of your time)
