# Pre-push Test Review (2-3 minutes)

**When to use**: After pre-push hook passes, before pushing code

**How to use**:
- **Manual**: Review test files against this checklist (2-3 min)
- **Haiku automation**: In Claude Code: "Review my tests before push"

**Purpose**: Validate test quality (strategy, mocking, edge cases, readability)

---

## Test Structure (5 items)

- [ ] **70/20/10 ratio maintained**
      Unit tests: 70%, Integration: 20%, System (E2E): 10%

      Why: Optimal test distribution (fast feedback + comprehensive coverage)

      How to check:
      - Count test files/functions by type
      - Unit: Tests single function/class in isolation
      - Integration: Tests multiple components together
      - System: Tests full system end-to-end

      Example:
      ```
      50 tests total:
      - 35 unit tests (70%) ✅
      - 10 integration tests (20%) ✅
      - 5 E2E tests (10%) ✅
      ```

      Anti-pattern:
      ```
      50 tests total:
      - 20 unit tests (40%) ❌
      - 30 integration tests (60%) ❌ Over-mocking, slow tests
      ```

      Reference: [Testing Standards](org-standards/.claude/testing.md)

- [ ] **Test file naming convention**
      Files named `test_*.py` or `*_test.py`

      Why: Pytest auto-discovery, consistent structure

      Example:
      ```
      ✅ test_orders.py
      ✅ orders_test.py
      ❌ orders.py (not discoverable)
      ❌ test-orders.py (wrong separator)
      ```

- [ ] **Test function names descriptive**
      Names describe what's being tested: `test_<function>_<scenario>_<expected>`

      Why: Readable test output, clear intent

      Example:
      ```python
      # Good ✅
      def test_calculate_total_with_discount_returns_reduced_price():
      def test_calculate_total_with_empty_cart_raises_value_error():

      # Bad ❌
      def test_1():  # What does this test?
      def test_calculate():  # What scenario?
      ```

- [ ] **One assertion focus per test**
      Each test focuses on single behavior (or clearly related assertions)

      Why: Clear failure messages, easy debugging

      Example:
      ```python
      # Good ✅
      def test_create_user_returns_user_with_id():
          user = create_user("Alice")
          assert user.id is not None
          assert user.name == "Alice"  # Related to same behavior

      # Bad ❌
      def test_user_crud():  # Tests multiple behaviors
          user = create_user("Alice")
          assert user.id is not None
          updated = update_user(user.id, "Bob")
          assert updated.name == "Bob"
          delete_user(user.id)
          assert get_user(user.id) is None  # Too many unrelated assertions
      ```

- [ ] **Test independence**
      Tests don't depend on execution order, each test is self-contained

      Why: Parallelization, reliable test suite

      How to check: Run tests in random order (`pytest --random-order`)

      Anti-pattern:
      ```python
      # Bad ❌ - Tests depend on order
      def test_1_create_user():
          global user_id
          user_id = create_user("Alice")

      def test_2_update_user():
          update_user(user_id, "Bob")  # Depends on test_1
      ```

---

## Mocking Strategy (4 items)

- [ ] **External dependencies mocked**
      APIs, databases, filesystem, network calls are mocked

      Why: Fast tests, no external service dependencies, deterministic

      What to mock:
      - ✅ HTTP requests (requests, httpx)
      - ✅ Database queries (SQLAlchemy, Postgres)
      - ✅ File I/O (open, pathlib)
      - ✅ External services (Stripe, SendGrid)
      - ✅ Time/dates (datetime.now)

      Example:
      ```python
      @patch('requests.get')
      def test_fetch_user_data(mock_get):
          mock_get.return_value.json.return_value = {'name': 'Alice'}
          result = fetch_user_data(123)
          assert result['name'] == 'Alice'
      ```

- [ ] **Internal business logic NOT mocked**
      Don't mock your own code under test

      Why: Want to test real behavior, not mock behavior

      What NOT to mock:
      - ❌ Business logic functions
      - ❌ Domain models
      - ❌ Utility functions
      - ❌ Internal services (unless integration testing)

      Example:
      ```python
      # Bad ❌
      @patch('my_app.calculate_discount')  # Don't mock your own code!
      def test_calculate_total(mock_discount):
          mock_discount.return_value = 10
          total = calculate_total(items)
          assert total == 90  # You're testing the mock, not your code

      # Good ✅
      def test_calculate_total():
          items = [Item(price=50), Item(price=50)]
          total = calculate_total(items)  # Real calculation
          assert total == 90  # Tests actual discount logic
      ```

      Reference: [Testing Anti-patterns](. claude/detailed-guides/testing-anti-patterns.md)

- [ ] **Mock objects clearly named**
      Mock names indicate what's being mocked: `mock_<object>`

      Why: Readability, clear intent

      Example:
      ```python
      # Good ✅
      @patch('my_app.api.StripeClient')
      def test_charge_card(mock_stripe_client):
          mock_stripe_client.charge.return_value = {'status': 'success'}

      # Bad ❌
      @patch('my_app.api.StripeClient')
      def test_charge_card(m):  # What is 'm'?
          m.charge.return_value = {'status': 'success'}
      ```

- [ ] **Mock assertions verify behavior**
      Mocks have assertions: `mock.assert_called_once_with(expected_args)`

      Why: Verify side effects, ensure functions called correctly

      Example:
      ```python
      @patch('my_app.email.send_email')
      def test_notify_user(mock_send_email):
          notify_user(user, "Welcome!")

          # Verify email was sent ✅
          mock_send_email.assert_called_once_with(
              to=user.email,
              subject="Welcome!",
              body=ANY
          )
      ```

---

## Edge Cases (4 items)

- [ ] **Null/None inputs tested**
      Test functions with None values for optional parameters

      Why: Common source of NoneType errors

      Example:
      ```python
      def test_calculate_total_with_no_discount():
          total = calculate_total(items, discount=None)
          assert total == 100  # No discount applied

      def test_validate_email_with_none_raises_value_error():
          with pytest.raises(ValueError):
              validate_email(None)
      ```

- [ ] **Empty collections tested**
      Test with empty lists, dicts, strings

      Why: Common edge case, often causes bugs

      Example:
      ```python
      def test_calculate_total_with_empty_cart_raises_value_error():
          with pytest.raises(ValueError):
              calculate_total([])  # Empty list

      def test_format_names_with_empty_list_returns_empty_string():
          result = format_names([])
          assert result == ""
      ```

- [ ] **Boundary values tested**
      Test with 0, -1, MAX_INT, empty strings

      Why: Off-by-one errors, overflow, underflow

      Example:
      ```python
      def test_calculate_discount_with_zero_price():
          discount = calculate_discount(price=0, rate=0.1)
          assert discount == 0

      def test_paginate_with_negative_page_raises_value_error():
          with pytest.raises(ValueError):
              paginate(items, page=-1)
      ```

- [ ] **Error conditions tested**
      Test that expected exceptions are raised

      Why: Verify error handling works correctly

      Example:
      ```python
      def test_divide_by_zero_raises_zero_division_error():
          with pytest.raises(ZeroDivisionError):
              divide(10, 0)

      def test_fetch_user_with_invalid_id_raises_not_found():
          with pytest.raises(UserNotFound):
              fetch_user(id=999999)
      ```

---

## Test Quality (4 items)

- [ ] **AAA pattern** (Arrange-Act-Assert)
      Tests follow clear structure: setup, execute, verify

      Why: Readability, maintainability

      Example:
      ```python
      def test_create_order_calculates_total():
          # Arrange
          items = [Item(price=50), Item(price=30)]
          user = User(id=1)

          # Act
          order = create_order(user, items)

          # Assert
          assert order.total == 80
          assert order.user_id == 1
      ```

- [ ] **No test duplication**
      Similar tests consolidated using `pytest.mark.parametrize`

      Why: DRY principle, easier maintenance

      Example:
      ```python
      # Bad ❌ - Duplication
      def test_calculate_discount_10_percent():
          discount = calculate_discount(100, 0.1)
          assert discount == 10

      def test_calculate_discount_20_percent():
          discount = calculate_discount(100, 0.2)
          assert discount == 20

      # Good ✅ - Parametrized
      @pytest.mark.parametrize("price,rate,expected", [
          (100, 0.1, 10),
          (100, 0.2, 20),
          (100, 0.5, 50),
      ])
      def test_calculate_discount(price, rate, expected):
          discount = calculate_discount(price, rate)
          assert discount == expected
      ```

- [ ] **Fixtures used for shared setup**
      Common test data/setup extracted to pytest fixtures

      Why: DRY, consistent test data

      Example:
      ```python
      # conftest.py or test file
      @pytest.fixture
      def sample_user():
          return User(id=1, name="Alice", email="alice@example.com")

      def test_create_order(sample_user):
          order = create_order(sample_user, items=[])
          assert order.user_id == sample_user.id

      def test_send_notification(sample_user):
          send_notification(sample_user, "Hello")
          # Test uses same user fixture
      ```

- [ ] **Test data realistic**
      Test data resembles real-world data (not just "test", "foo", "bar")

      Why: Catches real-world issues, better validation

      Example:
      ```python
      # Bad ❌
      def test_validate_email():
          assert validate_email("test") == True  # Unrealistic

      # Good ✅
      def test_validate_email():
          assert validate_email("alice@example.com") == True
          assert validate_email("bob+filter@company.co.uk") == True
          assert validate_email("invalid@") == False
      ```

---

## Coverage (2 items)

- [ ] **New code coverage ≥80%**
      Run `pytest --cov` and check coverage for new/modified code

      Why: Quality gate requirement, comprehensive testing

      How to check:
      ```bash
      pytest --cov=src --cov-report=term-missing
      # Look for coverage % in output
      ```

      Coverage targets:
      - ✅ ≥80% overall (minimum)
      - ✅ ≥90% for critical paths (auth, payments, data integrity)
      - ✅ 100% for security-sensitive code

      Note: Coverage ≠ quality, but <80% usually indicates missing tests

- [ ] **Critical paths covered**
      Happy path + main error paths have tests

      Why: Most important code must work

      Critical paths:
      - ✅ Happy path (normal user flow)
      - ✅ Authentication/authorization
      - ✅ Data creation/modification
      - ✅ Payment processing
      - ✅ Error handling (API errors, DB errors)

      Example:
      ```python
      # Happy path
      def test_create_order_success():
          order = create_order(user, items)
          assert order.status == "pending"

      # Error path
      def test_create_order_with_insufficient_stock_fails():
          with pytest.raises(InsufficientStock):
              create_order(user, out_of_stock_items)
      ```

---

## How to Use This Checklist

### Manual Review (2-3 minutes)

1. Open test files in your changes
2. Review each category (Test Structure, Mocking, Edge Cases, Quality, Coverage)
3. Check each item (yes/no)
4. Fix any issues before pushing

### Haiku Automation (30-60 seconds)

In Claude Code session:

```
User: "Review my tests before push"

Claude: [Delegates to Haiku subagent]
```

Haiku will:
- Analyze all test files in your changes
- Check each of the 19 items
- Report findings with file:line references
- Provide specific recommendations

Cost: $0.25-0.50 (90% cheaper than Sonnet)

---

## Relationship to Quality Gates

**This checklist = Why tests are good**
**Pre-push hook = Tests pass (yes/no)**

| Check | Pre-push Hook (Enforcement) | This Checklist (Guidance) |
|-------|----------------------------|---------------------------|
| Tests exist | ✅ pytest runs | ✅ Tests added item |
| Tests pass | ✅ Blocks if fail | N/A |
| Coverage ≥80% | ✅ Blocks if <80% | ✅ Coverage items |
| Test quality | ❌ Not checked | ✅ All 19 items |

**Key**: Hook enforces pass/fail, checklist explains what makes good tests

---

## Time Investment

**Manual review**: 2-3 minutes
**Haiku automation**: 30-60 seconds
**Cost**: Free (manual) or $0.25-0.50 (Haiku)

**Value**: Catch test quality issues before push (cheaper than PR rework)

---

## Related

- **Previous stage**: Pre-commit self-check
- **Next stage**: Pre-PR full review (before creating PR)
- **Reference**: [Testing Standards](org-standards/.claude/testing.md)
- **Reference**: [Testing Anti-patterns](.claude/detailed-guides/testing-anti-patterns.md)
