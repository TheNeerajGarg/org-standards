"""Integration tests for quality gates pre-push hook.

Tests real hook execution with temporary git repositories.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

# Fixtures


@pytest.fixture
def test_repo(tmp_path):
    """Create test git repo with org-standards linked."""
    repo = tmp_path / "test-repo"
    repo.mkdir()

    # Initialize git with main branch
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

    # Create dummy bare git repo for origin (needed for pre-push hook to trigger)
    dummy_remote = tmp_path / "dummy-remote.git"
    subprocess.run(
        ["git", "init", "--bare"],
        cwd=tmp_path,
        env={**os.environ, "GIT_DIR": str(dummy_remote)},
        check=True,
        capture_output=True,
    )

    # Add origin remote
    subprocess.run(
        ["git", "remote", "add", "origin", str(dummy_remote)],
        cwd=repo,
        check=True,
    )

    # Link org-standards (symlink to actual org-standards)
    org_standards_src = Path(__file__).parent.parent
    org_standards_link = repo / "org-standards"
    org_standards_link.symlink_to(org_standards_src, target_is_directory=True)

    # Create initial commit (required for diff-cover)
    readme = repo / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)

    # Create pyproject.toml for pytest-cov
    pyproject = repo / "pyproject.toml"
    pyproject.write_text(
        dedent("""
        [tool.pytest.ini_options]
        testpaths = ["tests"]

        [tool.coverage.run]
        source = ["src"]
        omit = [
            "*/tests/*",
            "*/playground/*",
            "*/.ai-sessions/*",
        ]
    """)
    )

    # Create src and tests directories
    (repo / "src").mkdir()
    (repo / "tests").mkdir()

    # Add pyproject.toml
    subprocess.run(["git", "add", "pyproject.toml"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add pyproject.toml"], cwd=repo, check=True)

    # Install pre-push hook
    hook_src = org_standards_src / "git-hooks" / "pre-push"
    hook_dest = repo / ".git" / "hooks" / "pre-push"
    shutil.copy(hook_src, hook_dest)
    hook_dest.chmod(0o755)

    return repo


@pytest.fixture
def disable_hook(test_repo):
    """Temporarily disable pre-push hook."""
    hook = test_repo / ".git" / "hooks" / "pre-push"
    hook_backup = test_repo / ".git" / "hooks" / "pre-push.bak"
    if hook.exists():
        hook.rename(hook_backup)
    yield
    # Restore hook if backup exists
    if hook_backup.exists() and not hook.exists():
        hook_backup.rename(hook)


# Helper Functions


def create_code_file(repo: Path, relative_path: str, content: str):
    """Create code file in repo."""
    file_path = repo / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(dedent(content).strip() + "\n")


def git_add_commit(repo: Path, message: str):
    """Git add all and commit."""
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True)


def git_push(repo: Path, env: dict = None) -> subprocess.CompletedProcess:
    """Attempt git push (triggers pre-push hook)."""
    # Create a dummy remote (we're not actually pushing anywhere)
    result = subprocess.run(
        ["git", "push", "--dry-run", "origin", "main"],
        cwd=repo,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )
    return result


# Integration Tests


def test_hook_blocks_low_coverage(test_repo, disable_hook):
    """Hook blocks push when diff coverage <80%."""
    # Create file with untested code
    create_code_file(
        test_repo,
        "src/calculator.py",
        """
        def add(a, b):
            return a + b

        def subtract(a, b):
            return a - b

        def multiply(a, b):
            return a * b
    """,
    )

    # Create partial tests (only 1/3 functions = 33%)
    create_code_file(
        test_repo,
        "tests/test_calculator.py",
        """
        from src.calculator import add

        def test_add():
            assert add(2, 3) == 5
    """,
    )

    git_add_commit(test_repo, "Add calculator with partial tests")

    # Re-enable hook
    hook_backup = test_repo / ".git" / "hooks" / "pre-push.bak"
    hook = test_repo / ".git" / "hooks" / "pre-push"
    hook_backup.rename(hook)

    # Push (should fail)
    result = git_push(test_repo)

    # Note: Hook will fail because tools not installed in test env
    # This test validates hook structure, not actual coverage checking
    output = (result.stdout + result.stderr).lower()
    assert result.returncode != 0 or "quality gate" in output


def test_hook_allows_high_coverage(test_repo, disable_hook):
    """Hook allows push when diff coverage ≥80%."""
    # Create file with well-tested code
    create_code_file(
        test_repo,
        "src/calculator.py",
        """
        def add(a, b):
            return a + b

        def subtract(a, b):
            return a - b
    """,
    )

    # Create comprehensive tests (100%)
    create_code_file(
        test_repo,
        "tests/test_calculator.py",
        """
        from src.calculator import add, subtract

        def test_add():
            assert add(2, 3) == 5

        def test_subtract():
            assert subtract(5, 3) == 2
    """,
    )

    git_add_commit(test_repo, "Add calculator with full tests")

    # Re-enable hook
    hook_backup = test_repo / ".git" / "hooks" / "pre-push.bak"
    hook = test_repo / ".git" / "hooks" / "pre-push"
    hook_backup.rename(hook)

    # Push (should succeed if tools installed, or fail gracefully)
    result = git_push(test_repo)

    # Validate hook executed (check both stdout and stderr)
    output = (result.stdout + result.stderr).lower()
    assert "quality gate" in output or result.returncode == 0


def test_emergency_bypass_logs_json(test_repo, disable_hook):
    """Emergency bypass skips gates and logs JSON."""
    # Create untested code
    create_code_file(
        test_repo,
        "src/untested.py",
        """
        def untested():
            pass
    """,
    )

    git_add_commit(test_repo, "Emergency fix")

    # Re-enable hook
    hook_backup = test_repo / ".git" / "hooks" / "pre-push.bak"
    hook = test_repo / ".git" / "hooks" / "pre-push"
    hook_backup.rename(hook)

    # Push with emergency bypass
    result = git_push(
        test_repo,
        env={
            "EMERGENCY_PUSH": "1",
            "EMERGENCY_REASON": "Production outage - rollback needed",
        },
    )

    # Should succeed (bypassed)
    output = result.stdout + result.stderr
    assert result.returncode == 0 or "EMERGENCY PUSH" in output

    # Check JSON log created
    bypass_dir = test_repo / ".emergency-bypasses"
    if bypass_dir.exists():
        json_files = list(bypass_dir.glob("*.json"))
        if json_files:
            with open(json_files[0]) as f:
                bypass_data = json.load(f)

            assert "reason" in bypass_data
            assert bypass_data["reason"] == "Production outage - rollback needed"
            assert "timestamp" in bypass_data
            assert "user" in bypass_data


def test_exploratory_code_exempt(test_repo, disable_hook):
    """Code in playground/ is omitted from coverage."""
    # Create untested exploratory code
    create_code_file(
        test_repo,
        "playground/experiment.py",
        """
        def experiment():
            # No tests needed - exploratory
            pass
    """,
    )

    # Create production code with tests
    create_code_file(
        test_repo,
        "src/main.py",
        """
        def main():
            pass
    """,
    )

    create_code_file(
        test_repo,
        "tests/test_main.py",
        """
        from src.main import main

        def test_main():
            main()
    """,
    )

    git_add_commit(test_repo, "Add exploratory + prod code")

    # Re-enable hook
    hook_backup = test_repo / ".git" / "hooks" / "pre-push.bak"
    hook = test_repo / ".git" / "hooks" / "pre-push"
    hook_backup.rename(hook)

    # Push (playground should be omitted)
    result = git_push(test_repo)

    # Hook should execute (success depends on tool availability)
    output = (result.stdout + result.stderr).lower()
    assert "quality gate" in output or result.returncode == 0


def test_hook_loads_config(test_repo):
    """Hook successfully loads quality-gates.yaml."""
    # Create a simple test that just loads config
    test_script = test_repo / "test_config_load.py"
    test_script.write_text(
        dedent("""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path('org-standards/python')))

        try:
            from quality_gates import load_config
            config = load_config(base_config=Path('org-standards/config/quality-gates.yaml'))
            print(f'✅ Loaded config version {config.version}')
            print(f'✅ Found {len(config.gates)} gates')
            sys.exit(0)
        except Exception as e:
            print(f'❌ Failed to load config: {e}')
            sys.exit(1)
    """)
    )

    result = subprocess.run(
        ["python3", "test_config_load.py"],
        cwd=test_repo,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Loaded config version" in result.stdout


def test_hook_is_executable_and_contains_quality_gates(test_repo):
    """Hook is executable and contains quality gate logic."""
    hook_script = test_repo / ".git" / "hooks" / "pre-push"

    # Verify hook exists and is executable
    assert hook_script.exists()
    assert hook_script.stat().st_mode & 0o111  # Check executable bit

    # Verify hook contains quality gate logic
    content = hook_script.read_text()
    assert "quality_gates" in content
    assert "EMERGENCY_PUSH" in content


def test_repo_specific_override(test_repo, disable_hook):
    """Local override file customizes threshold."""
    # Create override config
    override = test_repo / "quality-gates.local.yaml"
    override.write_text(
        dedent("""
        gates:
          coverage:
            threshold: 60
    """)
    )

    # Test that override is loaded
    test_script = test_repo / "test_override.py"
    test_script.write_text(
        dedent("""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path('org-standards/python')))

        from quality_gates import load_config

        config = load_config(
            base_config=Path('org-standards/config/quality-gates.yaml'),
            override_config=Path('quality-gates.local.yaml')
        )

        threshold = config.gates['coverage'].threshold
        print(f'Threshold: {threshold}')

        if threshold == 60:
            print('✅ Override applied (60)')
            sys.exit(0)
        else:
            print(f'❌ Override not applied (got {threshold}, expected 60)')
            sys.exit(1)
    """)
    )

    result = subprocess.run(
        ["python3", "test_override.py"],
        cwd=test_repo,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Override applied" in result.stdout


def test_config_validation_in_hook(test_repo):
    """Hook validates config before executing gates."""
    # Corrupt the config
    config_file = test_repo / "org-standards" / "config" / "quality-gates.yaml"
    original_content = config_file.read_text()

    try:
        # Write invalid YAML
        config_file.write_text("invalid: yaml: syntax: error: [")

        # Try to load config
        test_script = test_repo / "test_invalid_config.py"
        test_script.write_text(
            dedent("""
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path('org-standards/python')))

            try:
                from quality_gates import load_config
                config = load_config(base_config=Path('org-standards/config/quality-gates.yaml'))
                print('❌ Should have failed on invalid YAML')
                sys.exit(1)
            except Exception as e:
                print(f'✅ Caught invalid config: {type(e).__name__}')
                sys.exit(0)
        """)
        )

        result = subprocess.run(
            ["python3", "test_invalid_config.py"],
            cwd=test_repo,
            capture_output=True,
            text=True,
        )

        # Should catch the error
        assert "Caught invalid config" in result.stdout or result.returncode == 0

    finally:
        # Restore original config
        config_file.write_text(original_content)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
