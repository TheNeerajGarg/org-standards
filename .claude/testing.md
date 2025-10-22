# Testing Standards

## MANDATORY: Test Coverage
- All public functions must have tests
- Test both success and failure cases
- Use descriptive test names: `test_function_name_scenario`
- Group related tests in classes: `TestClassName`

## CRITICAL: Testing Anti-Patterns to Avoid

**Problem**: Excessive mocking causes tests to pass while code fails in production (wasted 3-4 days debugging)

**Anti-Patterns**:
- ❌ **Excessive Mocking**: Mocking internal business logic defeats purpose of tests
  - Don't mock: Domain models, validators, business logic
  - Only mock: External dependencies (APIs, file system, databases)
- ❌ **Mock-Only Tests**: Tests that only verify mocks were called, not actual behavior
- ❌ **100% Unit Tests**: No integration tests means missing component interaction bugs
- ❌ **Tests that Pass, Code Fails**: If this happens, you're mocking too much

**What to Mock vs. Test Real**:

✅ **Mock These** (external dependencies):
```python
# Mock external API calls
with patch('requests.post') as mock_post:
    ...

# Mock file system (when testing logic, not I/O)
with patch('builtins.open') as mock_open:
    ...

# Mock external services
with patch('anthropic.Anthropic') as mock_client:
    ...
```

❌ **Don't Mock These** (internal logic):
```python
# DON'T mock domain models
# with patch('src.models.Product'):  # NO!

# DON'T mock validators
# with patch('src.validators.validate_schema'):  # NO!

# DON'T mock business logic
# with patch('src.extractor.extract_attributes'):  # NO!
```

**Testing Strategy** (70/20/10):
- **Unit tests (70%)**: Fast, mock external dependencies only
- **Integration tests (20%)**: Real component interactions, catch integration bugs
- **System tests (10%)**: End-to-end workflows, no mocking

**See Also**: Strategic solution tracked in [Syra Issue #1](https://github.com/StyleGuru/syra/issues/1)

## Test Structure

```python
class TestClassName:
    """Test class for ClassName"""

    def setup_method(self):
        """Set up test fixtures"""
        pass

    def teardown_method(self):
        """Clean up test fixtures"""
        pass

    def test_method_success_case(self):
        """Test successful execution"""
        # Arrange
        # Act
        # Assert
        pass

    def test_method_failure_case(self):
        """Test failure handling"""
        # Arrange
        # Act
        # Assert
        pass
```

## CRITICAL: Test Fixture Anti-Patterns

### ❌ FORBIDDEN: Overriding Base Class Attributes with Context Managers

**NEVER use `with ... as self.attribute:` pattern in tests!**

```python
# ❌ FORBIDDEN
class MyTest(FashionExtractTestBase):
    def test_something(self):
        # Base class provides self.test_dir as Path object
        with tempfile.TemporaryDirectory() as self.test_dir:  # ❌ Overwrites Path with string!
            temp_path = Path(self.test_dir)
            # ... test code ...
        # tearDown() crashes: AttributeError: 'str' has no attribute 'exists'
```

**Why this fails:**
1. Base class creates: `self.test_dir = Path("/tmp/some/dir")` (Path object)
2. Context manager overwrites: `self.test_dir = "/tmp/string/dir"` (string)
3. Base tearDown tries: `self.test_dir.exists()` → CRASH!

### ✅ CORRECT: Use Base Class Features or Intermediate Variables

**Option 1: Use base class test_dir (BEST)**
```python
class MyTest(FashionExtractTestBase):
    def test_something(self):
        # ✅ Use what base class provides - it's already there!
        test_file = self.test_dir / 'test.json'
        test_file.write_text('{"data": "value"}')
        # Base class handles cleanup automatically
```

**Option 2: Intermediate variable**
```python
class MyTest(FashionExtractTestBase):
    def test_something(self):
        # ✅ Use intermediate variable, not self.attribute
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            test_file = temp_dir / 'test.json'
            test_file.write_text('data')
        # self.test_dir remains untouched - tearDown works!
```

## Mock Usage Guidelines
- Use `unittest.mock.Mock` and `unittest.mock.patch`
- Mock external dependencies, not internal logic
- Use `@patch` decorator for clean mocking
- Verify mock calls when important
- Never try to unpack Mock objects: `var1, var2 = Mock()` will fail
- Use pytest fixtures to provide properly structured test data

## MANDATORY: Testing Strategy

**Unit Tests (70%) - Mock External Dependencies**
```python
# ✅ CORRECT: Unit test with appropriate mocking
def test_batch_processor_success():
    """Test batch processor with mocked external dependencies."""
    with patch('src.components.extractor.providers.openai_provider.OpenAIProvider') as mock_provider:
        mock_provider.return_value.process_image.return_value = {"color": "blue"}
        processor = BatchProcessor()
        result = processor.process_image("test.jpg")
        assert result.success
        assert result.attributes["color"] == "blue"
```

**Integration Tests (20%) - Real Dependencies**
```python
# ✅ CORRECT: Integration test with real dependencies
def test_end_to_end_batch_processing():
    """Test complete batch processing workflow with real files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_image = Path(temp_dir) / "test.jpg"
        test_image.write_bytes(b"fake image data")
        processor = BatchProcessor()
        result = processor.process_batch([test_image])
        assert result.success
        assert len(result.processed_images) == 1
```

**System Tests (10%) - Full System**
```python
# ✅ CORRECT: System test with full environment
def test_cli_command_line_interface():
    """Test CLI interface with real command execution."""
    result = subprocess.run([
        "python", "src/components/extractor/core/batch_processor.py",
        "--model", "gpt-4o",
        "--images-dir", "/test/images",
        "--output-dir", "/test/output"
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Processing complete" in result.stdout
```

## MANDATORY: Runtime Error Test Cases

**Every runtime error encountered MUST have a corresponding test case:**

1. **Error Reproduction**: Test must reproduce the exact error condition
2. **Error Message Validation**: Test must verify error message is appropriate
3. **Error Handling**: Test must verify proper error handling and recovery
4. **Integration Coverage**: Test must cover component interactions
5. **Real Data Testing**: Test must use actual data structures when possible
6. **Command Line Testing**: Test must verify CLI argument handling
7. **Module Import Testing**: Test must verify all imports resolve

**Test case implementation pattern:**
```python
def test_runtime_error_scenario():
    """Test case for specific runtime error.

    Error: [Describe the error]
    Fix: [Describe the fix]
    """
    # Arrange: Set up exact conditions that caused error
    # Act: Execute code that caused error
    # Assert: Verify error handled correctly or fix works
```
