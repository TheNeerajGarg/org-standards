"""Unit tests for quality gates configuration system.

Tests configuration loading, validation, and parsing logic.
"""
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from quality_gates import (
    ExecutionResults,
    GateConfig,
    GateResult,
    QualityGatesConfig,
    load_config,
    _merge_configs,
    _parse_config,
    _validate_config,
)


# Fixtures

@pytest.fixture
def valid_config_dict():
    """Valid configuration dictionary."""
    return {
        "version": "1.0.0",
        "gates": {
            "testing": {
                "enabled": True,
                "tool": "pytest",
                "command": "pytest --tb=short",
                "description": "Run tests",
                "required": True,
                "timeout_seconds": 300,
            },
            "coverage": {
                "enabled": True,
                "tool": "diff-cover",
                "threshold": 80,
                "command": "diff-cover coverage.xml --fail-under={threshold}",
                "description": "Check coverage",
                "required": True,
                "depends_on": ["testing"],
                "timeout_seconds": 60,
            },
        },
        "execution_order": ["testing", "coverage"],
        "emergency_bypass": {
            "enabled": True,
            "env_var": "EMERGENCY_PUSH",
            "log_dir": ".emergency-bypasses",
        },
    }


@pytest.fixture
def invalid_config_missing_version():
    """Invalid config - missing version."""
    return {
        "gates": {},
        "execution_order": [],
    }


@pytest.fixture
def invalid_config_undefined_gate():
    """Invalid config - execution_order references undefined gate."""
    return {
        "version": "1.0.0",
        "gates": {
            "testing": {
                "enabled": True,
                "tool": "pytest",
                "description": "Tests",
                "required": True,
            }
        },
        "execution_order": ["testing", "coverage"],  # 'coverage' not defined
    }


@pytest.fixture
def config_with_circular_dependency():
    """Config with circular dependency."""
    return {
        "version": "1.0.0",
        "gates": {
            "gate_a": {
                "enabled": True,
                "tool": "tool_a",
                "description": "Gate A",
                "required": True,
                "depends_on": ["gate_b"],
            },
            "gate_b": {
                "enabled": True,
                "tool": "tool_b",
                "description": "Gate B",
                "required": True,
                "depends_on": ["gate_a"],  # Circular!
            },
        },
        "execution_order": ["gate_a", "gate_b"],
    }


# Unit Tests - Configuration Validation


def test_validate_config_valid(valid_config_dict):
    """Valid config passes validation."""
    # Should not raise
    _validate_config(valid_config_dict)


def test_validate_config_missing_version(invalid_config_missing_version):
    """Config missing 'version' fails validation."""
    with pytest.raises(ValueError, match="Missing required fields.*version"):
        _validate_config(invalid_config_missing_version)


def test_validate_config_missing_gates():
    """Config missing 'gates' fails validation."""
    config = {"version": "1.0.0", "execution_order": []}
    with pytest.raises(ValueError, match="Missing required fields.*gates"):
        _validate_config(config)


def test_validate_config_missing_execution_order():
    """Config missing 'execution_order' fails validation."""
    config = {"version": "1.0.0", "gates": {}}
    with pytest.raises(ValueError, match="Missing required fields.*execution_order"):
        _validate_config(config)


def test_validate_config_undefined_gate_in_order(invalid_config_undefined_gate):
    """Config with undefined gate in execution_order fails."""
    with pytest.raises(ValueError, match="execution_order references undefined gates.*coverage"):
        _validate_config(invalid_config_undefined_gate)


# Unit Tests - Configuration Merging


def test_merge_configs_empty_override(valid_config_dict):
    """Merging empty override returns base config."""
    result = _merge_configs(valid_config_dict, {})
    assert result == valid_config_dict


def test_merge_configs_gate_override(valid_config_dict):
    """Override can modify gate properties."""
    override = {
        "gates": {
            "coverage": {
                "threshold": 70  # Override 80 -> 70
            }
        }
    }
    result = _merge_configs(valid_config_dict, override)
    assert result["gates"]["coverage"]["threshold"] == 70
    assert result["gates"]["coverage"]["tool"] == "diff-cover"  # Unchanged


def test_merge_configs_add_new_gate(valid_config_dict):
    """Override can add new gates."""
    override = {
        "gates": {
            "linting": {
                "enabled": True,
                "tool": "ruff",
                "description": "Lint code",
                "required": True,
            }
        }
    }
    result = _merge_configs(valid_config_dict, override)
    assert "linting" in result["gates"]
    assert result["gates"]["linting"]["tool"] == "ruff"


def test_merge_configs_override_version(valid_config_dict):
    """Override can change version."""
    override = {"version": "2.0.0"}
    result = _merge_configs(valid_config_dict, override)
    assert result["version"] == "2.0.0"


def test_merge_configs_override_execution_order(valid_config_dict):
    """Override can change execution order."""
    override = {"execution_order": ["coverage", "testing"]}
    result = _merge_configs(valid_config_dict, override)
    assert result["execution_order"] == ["coverage", "testing"]


# Unit Tests - Configuration Parsing


def test_parse_config_creates_typed_objects(valid_config_dict):
    """Parsing creates typed dataclass objects."""
    config = _parse_config(valid_config_dict)

    assert isinstance(config, QualityGatesConfig)
    assert config.version == "1.0.0"
    assert len(config.gates) == 2
    assert "testing" in config.gates
    assert "coverage" in config.gates

    testing_gate = config.gates["testing"]
    assert isinstance(testing_gate, GateConfig)
    assert testing_gate.tool == "pytest"
    assert testing_gate.required is True


def test_parse_config_handles_optional_fields(valid_config_dict):
    """Parsing handles optional fields with defaults."""
    config = _parse_config(valid_config_dict)

    testing = config.gates["testing"]
    assert testing.threshold is None  # Optional, not provided
    assert testing.depends_on == []  # Default empty list

    coverage = config.gates["coverage"]
    assert coverage.threshold == 80  # Provided
    assert coverage.depends_on == ["testing"]  # Provided


def test_parse_config_preserves_execution_order(valid_config_dict):
    """Parsing preserves execution order."""
    config = _parse_config(valid_config_dict)
    assert config.execution_order == ["testing", "coverage"]


# Unit Tests - Configuration Loading


def test_load_config_valid_file(tmp_path, valid_config_dict):
    """Loading valid config file succeeds."""
    config_file = tmp_path / "quality-gates.yaml"
    with open(config_file, "w") as f:
        yaml.dump(valid_config_dict, f)

    config = load_config(base_config=config_file)

    assert isinstance(config, QualityGatesConfig)
    assert config.version == "1.0.0"
    assert len(config.gates) == 2


def test_load_config_file_not_found():
    """Loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Config not found"):
        load_config(base_config=Path("/nonexistent/file.yaml"))


def test_load_config_with_override(tmp_path, valid_config_dict):
    """Loading config with override merges correctly."""
    base_file = tmp_path / "base.yaml"
    override_file = tmp_path / "override.yaml"

    with open(base_file, "w") as f:
        yaml.dump(valid_config_dict, f)

    override = {
        "gates": {
            "coverage": {"threshold": 60}
        }
    }
    with open(override_file, "w") as f:
        yaml.dump(override, f)

    config = load_config(base_config=base_file, override_config=override_file)

    assert config.gates["coverage"].threshold == 60  # Overridden
    assert config.gates["testing"].tool == "pytest"  # Unchanged


def test_load_config_override_file_missing(tmp_path, valid_config_dict):
    """Loading with non-existent override file uses base only."""
    base_file = tmp_path / "base.yaml"
    with open(base_file, "w") as f:
        yaml.dump(valid_config_dict, f)

    override_file = tmp_path / "nonexistent.yaml"

    config = load_config(base_config=base_file, override_config=override_file)

    # Should succeed with base config only
    assert config.version == "1.0.0"


# Unit Tests - Gate Results


def test_gate_result_success():
    """GateResult for successful gate."""
    result = GateResult(
        gate_name="testing",
        passed=True,
        duration_seconds=5.2,
        message="All tests passed",
    )
    assert result.passed is True
    assert result.gate_name == "testing"
    assert result.duration_seconds == 5.2


def test_gate_result_failure():
    """GateResult for failed gate."""
    result = GateResult(
        gate_name="coverage",
        passed=False,
        duration_seconds=2.1,
        message="Coverage 70% (need 80%)",
        fail_message="Add more tests",
    )
    assert result.passed is False
    assert result.fail_message == "Add more tests"


# Unit Tests - Execution Results


def test_execution_results_all_passed():
    """ExecutionResults when all gates pass."""
    results = [
        GateResult("testing", True, 5.0),
        GateResult("coverage", True, 2.0),
    ]

    exec_results = ExecutionResults(
        passed=True,
        failed_count=0,
        total_count=2,
        duration_seconds=7.0,
        results=results,
        failures=[],
    )

    assert exec_results.passed is True
    assert exec_results.failed_count == 0
    assert len(exec_results.failures) == 0


def test_execution_results_some_failed():
    """ExecutionResults when some gates fail."""
    pass_result = GateResult("testing", True, 5.0)
    fail_result = GateResult("coverage", False, 2.0, "Too low")

    exec_results = ExecutionResults(
        passed=False,
        failed_count=1,
        total_count=2,
        duration_seconds=7.0,
        results=[pass_result, fail_result],
        failures=[fail_result],
    )

    assert exec_results.passed is False
    assert exec_results.failed_count == 1
    assert len(exec_results.failures) == 1
    assert exec_results.failures[0].gate_name == "coverage"


# Unit Tests - GateConfig


def test_gate_config_defaults():
    """GateConfig uses default values for optional fields."""
    gate = GateConfig(
        name="test_gate",
        enabled=True,
        tool="pytest",
        description="Test gate",
        required=True,
    )

    assert gate.command is None
    assert gate.commands is None
    assert gate.threshold is None
    assert gate.depends_on == []
    assert gate.omit_patterns == []
    assert gate.fail_message == ""
    assert gate.timeout_seconds == 300  # Default


def test_gate_config_with_all_fields():
    """GateConfig with all fields populated."""
    gate = GateConfig(
        name="coverage",
        enabled=True,
        tool="diff-cover",
        command="diff-cover coverage.xml",
        threshold=80,
        description="Coverage check",
        required=True,
        depends_on=["testing"],
        omit_patterns=["playground/*"],
        fail_message="Add tests",
        timeout_seconds=60,
    )

    assert gate.name == "coverage"
    assert gate.threshold == 80
    assert gate.depends_on == ["testing"]
    assert gate.omit_patterns == ["playground/*"]
    assert gate.timeout_seconds == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
