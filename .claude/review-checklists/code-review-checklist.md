# Code Review Checklist

Use this checklist to review code changes from multiple perspectives in a single pass.

**How to use**: `"Review [changes] using .claude/review-checklists/code-review-checklist.md"`

**When to use**: Before creating PR (`gh pr create`)

**Result**: Single comprehensive review covering all perspectives (replaces launching 5+ separate subagent reviews).

**Target time**: 5-10 minutes (manual) or 1-2 minutes (Haiku automation)

---

## 1. Principal Engineer Perspective (10 items)

### Architecture & Design

- [ ] **System boundaries clear**
      Separation of concerns maintained, components don't overlap responsibilities

      Check: Can you describe each component's purpose in one sentence?

      Example:
      ```python
      # Good ✅ - Clear boundaries
      class OrderService:  # Handles order business logic
      class PaymentGateway:  # Handles payment processing
      class EmailNotifier:  # Handles email sending

      # Bad ❌ - Overlapping responsibilities
      class OrderService:
          def process_order(self):
              self.charge_card()  # Payment logic in order service
              self.send_email()   # Email logic in order service
      ```

- [ ] **Dependencies justified**
      All new dependencies (libraries, services) have clear justification

      Why: Each dependency adds maintenance burden, security risk

      Check: Can you explain why each new dependency is necessary?

- [ ] **Design patterns appropriate**
      If design patterns used (Factory, Strategy, Observer), are they appropriate?

      Why: Patterns solve specific problems, don't force them

      Anti-pattern: Using patterns for the sake of patterns (over-engineering)

- [ ] **Error handling comprehensive**
      All error paths handled, specific exceptions used (not bare `except`)

      Check:
      - Network errors handled (API calls)
      - Database errors handled (queries)
      - User input errors handled (validation)
      - No bare `except:` clauses

      Example:
      ```python
      # Good ✅
      try:
          result = api.fetch_data()
      except requests.Timeout:
          logger.error("API timeout")
          raise ServiceUnavailable()
      except requests.HTTPError as e:
          logger.error(f"API error: {e}")
          raise

      # Bad ❌
      try:
          result = api.fetch_data()
      except:  # Bare except catches everything, including KeyboardInterrupt
          pass
      ```

- [ ] **Configuration appropriate**
      Hardcoded values vs config appropriate (magic numbers eliminated)

      What should be configurable:
      - ✅ Environment-specific (URLs, credentials)
      - ✅ Business rules (thresholds, limits)
      - ✅ Feature flags

      What can be hardcoded:
      - ✅ Constants (HTTP status codes, math constants)
      - ✅ Default values (if config missing)

- [ ] **Scalability considered**
      Design will scale with growth (users, data, requests)

      Check:
      - No N+1 queries (database)
      - No quadratic algorithms (O(n²))
      - Pagination for large datasets
      - Caching for repeated queries

- [ ] **Maintainability**
      Future developers can understand and modify this code

      Check:
      - Code is self-explanatory (or has comments for complex parts)
      - Functions are small (<50 lines)
      - Classes have single responsibility
      - No "clever" code (straightforward is better)

- [ ] **Technical debt tracked**
      Any shortcuts/hacks documented in GitHub issues (not TODOs in code)

      Why: TODOs get lost, GitHub issues get tracked

      Action: Create issue, link in commit message, no TODOs in production code

- [ ] **Breaking changes handled**
      If API changes break compatibility, migration path documented

      What constitutes breaking change:
      - Function signature changed (parameters added/removed/reordered)
      - Return type changed
      - Exception types changed
      - Database schema changed

      Required: Migration guide, deprecation warnings, version bump

- [ ] **Code reuse**
      Duplication eliminated or justified (DRY principle)

      Check: Same logic repeated in multiple places?

      Exceptions where duplication is OK:
      - Test code (clarity over DRY)
      - Performance-critical paths (avoid function call overhead)
      - Coupling would be worse than duplication

---

## 2. Test Architect Perspective (8 items)

### Test Strategy

- [ ] **70/20/10 ratio maintained**
      Unit: 70%, Integration: 20%, System: 10%

      Check: Count tests by type, calculate percentages

      Why: Fast feedback (unit), comprehensive coverage (integration), confidence (E2E)

      Reference: [Pre-push Review](.claude/checklists/pre-push-review.md)

- [ ] **Mocking boundaries appropriate**
      External dependencies mocked, internal business logic not mocked

      What to mock:
      - ✅ External APIs, databases, filesystem
      - ✅ Time/dates (datetime.now)

      What NOT to mock:
      - ❌ Your own business logic
      - ❌ Domain models
      - ❌ Utility functions

      Reference: [Testing Anti-patterns](.claude/detailed-guides/testing-anti-patterns.md)

- [ ] **Coverage adequate**
      Overall ≥80%, critical paths ≥90%

      How to check: `pytest --cov=src --cov-report=term-missing`

      Critical paths requiring ≥90%:
      - Authentication/authorization
      - Payment processing
      - Data integrity (CRUD operations)
      - Security-sensitive code

- [ ] **Edge cases comprehensive**
      Null inputs, empty collections, boundary values, error conditions all tested

      Checklist:
      - ✅ None/null tested
      - ✅ Empty lists/dicts tested
      - ✅ Zero, -1, MAX_INT tested
      - ✅ Exceptions tested (pytest.raises)

- [ ] **Integration tests present**
      Cross-component interactions tested (not just unit tests)

      What to test:
      - API endpoints (request → response)
      - Database interactions (ORM → DB)
      - Service interactions (ServiceA → ServiceB)

      Example:
      ```python
      def test_create_order_integration(db_session):
          # Tests: API → Service → Database
          response = client.post("/orders", json=order_data)
          assert response.status_code == 201

          # Verify in database
          order = db_session.query(Order).filter_by(id=response.json['id']).first()
          assert order is not None
      ```

- [ ] **Test readability**
      AAA pattern (Arrange-Act-Assert), descriptive names, no magic values

      Check:
      - ✅ Clear setup, execution, verification sections
      - ✅ Test names describe scenario: `test_<function>_<scenario>_<expected>`
      - ✅ No magic numbers (use named constants)

- [ ] **Test data realistic**
      Test data resembles production data (not "foo", "bar", "test")

      Why: Catches real-world issues (encoding, validation, edge cases)

- [ ] **No flakiness**
      Tests are deterministic (no time dependencies, no order dependencies)

      How to check: Run tests multiple times, randomize order

      Common causes of flakiness:
      - Time-dependent (datetime.now without mocking)
      - Order-dependent (shared state between tests)
      - External services (unmocked API calls)
      - Race conditions (threading, async)

---

## 3. Simplicity Perspective (8 items)

### Problem & Solution

- [ ] **Solving actual problem**
      Change addresses root cause, not symptoms

      Check: Apply "5 whys" - does this solve the underlying issue?

      Example:
      - ❌ Symptom: "API is slow" → Solution: Increase timeout (workaround)
      - ✅ Root cause: "API makes N+1 queries" → Solution: Add query optimization (fix)

- [ ] **YAGNI** (You Aren't Gonna Need It)
      Not building features before they're needed

      Red flags:
      - ❌ "We might need this later"
      - ❌ "This makes it more flexible"
      - ❌ Generic abstractions with no current use case

      Test: Remove the code - does anything break? If no, it's YAGNI.

- [ ] **Simplest approach taken**
      No over-engineering, straightforward solution

      Check: Could this be simpler?

      Example:
      ```python
      # Over-engineered ❌
      class BaseTransform:
          def transform(self, data): raise NotImplementedError

      class StringTransform(BaseTransform):
          def transform(self, data): return str(data)

      class IntTransform(BaseTransform):
          def transform(self, data): return int(data)

      # Simple ✅
      def to_string(data): return str(data)
      def to_int(data): return int(data)
      ```

- [ ] **Not over-configurable**
      Configuration exists for actual needs, not hypothetical flexibility

      Red flags:
      - ❌ Config options that no one will change
      - ❌ "Just in case" configurability
      - ❌ More config than code

      Rule: Add config when second use case appears, not speculatively

- [ ] **No unnecessary dependencies**
      New dependencies justified by significant value

      Question: Could you implement this in 10 lines instead of adding a library?

      Example:
      - ❌ Adding lodash for one array operation
      - ✅ Adding SQLAlchemy for database ORM (significant value)

- [ ] **Cognitive load low**
      Code can be understood at a glance (no mental stack overflow)

      Checklist:
      - ✅ Functions <50 lines
      - ✅ Classes <300 lines
      - ✅ Nesting depth <4 levels
      - ✅ No "clever" code (clarity > cleverness)

- [ ] **Minimal code volume**
      Solved problem with minimal lines (but not golfed/unreadable)

      Check: Could you delete 20% of this code and keep same functionality?

      Balance: Concise but readable

- [ ] **No premature optimization**
      Optimize only after profiling shows actual bottleneck

      Red flags:
      - ❌ "This will be faster"
      - ❌ Complex caching before performance issue
      - ❌ Micro-optimizations in non-critical code

      Rule: Make it work, make it right, make it fast (in that order)

---

## 4. Standards & Security Perspective (8 items)

### Code Standards

- [ ] **Coding standards followed**
      Ruff, MyPy, pytest conventions followed

      Pre-push hook enforces these, but double-check:
      - ✅ Ruff formatting (no linting errors)
      - ✅ MyPy type checking (no type errors)
      - ✅ Pytest conventions (test files, function names)

- [ ] **Type hints complete**
      All functions have parameter and return type hints

      Example:
      ```python
      # Complete ✅
      def calculate_total(items: list[Item], discount: float = 0.0) -> Decimal:
          ...

      # Incomplete ❌
      def calculate_total(items, discount=0.0):  # Missing types
          ...
      ```

- [ ] **Docstrings present**
      All public functions have Google-style docstrings

      Required sections:
      - Summary line
      - Args: (if parameters)
      - Returns: (if return value)
      - Raises: (if exceptions)

      Example:
      ```python
      def calculate_total(items: list[Item], discount: float = 0.0) -> Decimal:
          """Calculate total price with optional discount.

          Args:
              items: List of items to sum
              discount: Discount rate (0.0 to 1.0)

          Returns:
              Total price as Decimal after discount

          Raises:
              ValueError: If items is empty or discount invalid
          """
      ```

- [ ] **Import structure correct**
      Absolute imports for cross-component, relative for intra-component

      Example:
      ```python
      # Cross-component (different top-level packages) ✅
      from syra.context_stack import ContextStackManager

      # Intra-component (same package) ✅
      from .models import User
      from ..utils import format_date

      # Avoid ❌
      import sys
      sys.path.append('..')  # Don't manipulate sys.path
      ```

- [ ] **Naming conventions**
      snake_case (functions/variables), PascalCase (classes), SCREAMING_SNAKE (constants)

      Examples:
      ```python
      # Functions/variables: snake_case ✅
      def calculate_total(): ...
      user_count = 10

      # Classes: PascalCase ✅
      class OrderService: ...

      # Constants: SCREAMING_SNAKE_CASE ✅
      MAX_RETRY_ATTEMPTS = 3
      API_BASE_URL = "https://api.example.com"
      ```

- [ ] **Anti-patterns avoided**
      No sys.path manipulation, no bare except, no warning suppression

      Banned patterns:
      - ❌ `sys.path.append(...)` in production code
      - ❌ `except:` without exception type
      - ❌ `# noqa` without justification
      - ❌ `warnings.filterwarnings("ignore")`

### Security

- [ ] **No SQL injection**
      All database queries use parameterized queries (not string concatenation)

      Example:
      ```python
      # Vulnerable ❌
      query = f"SELECT * FROM users WHERE id = {user_id}"
      db.execute(query)

      # Safe ✅
      query = "SELECT * FROM users WHERE id = ?"
      db.execute(query, (user_id,))
      ```

- [ ] **Input validation**
      All user inputs validated (type, range, format)

      Checklist:
      - ✅ Type validation (isinstance, pydantic)
      - ✅ Range validation (min/max)
      - ✅ Format validation (regex for emails, URLs)
      - ✅ Sanitization (strip HTML, escape special chars)

      Example:
      ```python
      def create_user(email: str, age: int) -> User:
          if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
              raise ValueError("Invalid email format")
          if not 0 < age < 150:
              raise ValueError("Invalid age range")
          return User(email=email, age=age)
      ```

---

## 5. Documentation & Communication Perspective (8 items)

### Code Documentation

- [ ] **Comments explain why, not what**
      Code is self-explanatory (what), comments explain reasoning (why)

      Example:
      ```python
      # Bad ❌ - Explains what (obvious from code)
      # Increment counter
      counter += 1

      # Good ✅ - Explains why (non-obvious reasoning)
      # Retry after 5 seconds to avoid rate limiting
      time.sleep(5)
      ```

- [ ] **Complex logic explained**
      Non-obvious algorithms, business rules documented

      When to comment:
      - ✅ Complex algorithms (sorting, caching)
      - ✅ Business rules (why threshold is 100)
      - ✅ Workarounds (why not ideal solution)
      - ✅ Performance optimizations (why this approach)

- [ ] **API documentation complete**
      Public interfaces (classes, functions) have docstrings

      What needs docstrings:
      - ✅ All public functions/methods
      - ✅ All public classes
      - ✅ Module-level docstrings

      What doesn't need docstrings:
      - Private functions (unless complex)
      - Test functions (name is documentation)

- [ ] **Migration notes for breaking changes**
      If API changes, migration guide provided

      Required in commit message or PR description:
      - What changed (old API → new API)
      - Why changed (motivation)
      - How to migrate (step-by-step)
      - Timeline (deprecation date)

- [ ] **No TODOs in code**
      All TODOs converted to GitHub issues

      Why: TODOs get lost in code, issues get tracked

      Action:
      1. Create GitHub issue
      2. Link issue in commit message
      3. Remove TODO from code

- [ ] **Commit messages clear**
      Conventional commits format, explains what and why

      Format: `<type>(<scope>): <subject>`

      Example:
      ```
      feat(orders): add discount calculation (#155)

      Adds calculate_discount() to support promotional discounts.
      Uses tiered discount rates based on order total.

      Closes #155
      ```

- [ ] **README updated if needed**
      User-facing changes reflected in README

      When to update README:
      - ✅ New features (user-visible)
      - ✅ Installation changes (dependencies)
      - ✅ Configuration changes (new env vars)
      - ✅ Breaking changes (API changes)

- [ ] **CHANGELOG updated if needed**
      For releases, changes documented in CHANGELOG

      Format: Keep a Changelog (https://keepachangelog.com)

      Sections: Added, Changed, Deprecated, Removed, Fixed, Security

---

## How to Apply This Checklist

### For Manual Review (5-10 minutes)

1. Review changed files in your PR
2. Apply each perspective (Principal Engineer → Test Architect → Simplicity → Standards → Documentation)
3. Check each item within perspective
4. Fix any issues before creating PR

### For Haiku Automation (1-2 minutes, default)

**In Claude Code session:**

```
User: "Ready to create PR"

Claude: "Before creating PR, let me run pre-PR review (Haiku, 5-10 min)..."

[Claude delegates to Haiku subagent with this checklist]

Claude: "✅ Pre-PR review complete (cost: $0.45):

**Principal Engineer**:
- Architecture: ✅ Good separation of concerns
- ⚠️  Over-abstraction in utils.py:45 (3 layers for simple transform)

**Test Architect**:
- Test strategy: ✅ 70/20/10 maintained
- Coverage: ✅ 85% (exceeds 80%)

**Simplicity**:
- YAGNI: ✅ All features needed
- ⚠️  Over-engineering in utils.py (same as Principal Engineer)

**Standards & Security**:
- Type hints: ✅ Complete
- Security: ✅ Input validation present

**Documentation**:
- Docstrings: ✅ All public functions documented
- 💡 Add docstring to create_user() (api/users.py:23)

**Severity Summary**:
- 🔴 Critical: 0
- ⚠️  Warning: 1 (over-engineering)
- 💡 Suggestion: 1 (docstring)

**Recommendation**: Address over-engineering warning before PR. Fix now?"
```

**Cost**: $0.25-0.50 (Haiku) vs $3-5 (Sonnet main session) = 90% savings

---

## Severity Levels

- 🔴 **Critical**: Must fix before merging (security, data loss, breaking change without migration)
- ⚠️  **Warning**: Should fix before PR (design issues, maintainability, test gaps)
- 💡 **Suggestion**: Nice to have (minor improvements, style, additional docs)

---

## Relationship to Quality Gates

**Quality gates = Enforcement** (pass/fail, blocking)
**This checklist = Guidance** (why, best practices, reasoning)

| Check | Pre-push Hook (Gate) | This Checklist (Guidance) |
|-------|----------------------|---------------------------|
| Tests pass | ✅ Blocks if fail | ✅ Test strategy explained |
| Type hints | ✅ MyPy enforces | ✅ Why type hints matter |
| Linting | ✅ Ruff enforces | ✅ Coding standards |
| Architecture | ❌ Not checked | ✅ Principal Engineer perspective |
| Design quality | ❌ Not checked | ✅ Simplicity perspective |

**Key**: Quality gates enforce minimum bar, checklist guides toward excellence

---

## Time Investment

**Manual review**: 5-10 minutes (one-time before PR)
**Haiku automation**: 1-2 minutes
**Cost**: Free (manual) or $0.25-0.50 (Haiku)

**Value**: Catch design issues before PR (cheaper than multi-round PR review)

---

## Related

- **Previous stage**: Pre-push test review (after quality gates pass)
- **Next stage**: Create PR (after checklist passes)
- **Reference**: [Document Review Checklist](.claude/review-checklists/document-review-checklist.md)
- **Reference**: [Testing Standards](org-standards/.claude/testing.md)
- **Reference**: [Testing Anti-patterns](.claude/detailed-guides/testing-anti-patterns.md)
