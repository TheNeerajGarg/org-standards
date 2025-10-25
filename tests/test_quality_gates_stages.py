#!/usr/bin/env python3
"""Tests for stage-aware quality gates."""

import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from quality_gates import (
    GateConfig,
    QualityGatesConfig,
    _apply_stage_relaxations,
    _detect_stage,
)


def test_stage_relaxations_applied_for_pre_push():
    """Test pre-push stage applies relaxations correctly."""
    # Create config with stage relaxations
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "coverage": GateConfig(
                name="coverage",
                enabled=True,
                tool="diff-cover",
                threshold=85,  # Base threshold
                required=True,
                stage_relaxations={
                    "pre-push": {"threshold": 70},
                },
            )
        },
        execution_order=["coverage"],
        emergency_bypass={},
    )

    # Apply pre-push relaxations
    relaxed = _apply_stage_relaxations(config, "pre-push")

    # Verify relaxation applied
    assert relaxed.gates["coverage"].threshold == 70


def test_stage_relaxations_applied_for_pr():
    """Test PR stage applies relaxations correctly."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "coverage": GateConfig(
                name="coverage",
                enabled=True,
                tool="diff-cover",
                threshold=85,  # Base
                required=True,
                stage_relaxations={
                    "pr": {"threshold": 80},
                },
            )
        },
        execution_order=["coverage"],
        emergency_bypass={},
    )

    relaxed = _apply_stage_relaxations(config, "pr")

    assert relaxed.gates["coverage"].threshold == 80


def test_push_to_main_uses_base_config():
    """Test push-to-main stage uses base config (no relaxations)."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "coverage": GateConfig(
                name="coverage",
                enabled=True,
                tool="diff-cover",
                threshold=85,  # Base
                required=True,
                stage_relaxations={
                    "pre-push": {"threshold": 70},
                    "pr": {"threshold": 80},
                },
            )
        },
        execution_order=["coverage"],
        emergency_bypass={},
    )

    # Apply push-to-main (should be no-op)
    relaxed = _apply_stage_relaxations(config, "push-to-main")

    # Verify NO relaxations applied
    assert relaxed.gates["coverage"].threshold == 85  # Still base


def test_stage_none_uses_base_config():
    """Test stage=None uses base config (highest standard)."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "coverage": GateConfig(
                name="coverage",
                enabled=True,
                tool="diff-cover",
                threshold=85,
                required=True,
                stage_relaxations={
                    "pre-push": {"threshold": 70},
                },
            )
        },
        execution_order=["coverage"],
        emergency_bypass={},
    )

    relaxed = _apply_stage_relaxations(config, None)

    # Verify NO relaxations applied (safe default)
    assert relaxed.gates["coverage"].threshold == 85


def test_invalid_stage_name_raises_error():
    """Test invalid stage name raises clear error."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "coverage": GateConfig(
                name="coverage",
                enabled=True,
                tool="diff-cover",
                threshold=85,
                required=True,
            )
        },
        execution_order=["coverage"],
        emergency_bypass={},
    )

    # Try invalid stage name (typo: underscore instead of hyphen)
    with pytest.raises(ValueError, match="Unknown stage 'pre_push'"):
        _apply_stage_relaxations(config, "pre_push")


def test_config_without_stage_relaxations_works():
    """Test backward compatibility - configs without stage_relaxations work."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "testing": GateConfig(
                name="testing",
                enabled=True,
                tool="pytest",
                command="pytest",
                required=True,
                # No stage_relaxations field
            )
        },
        execution_order=["testing"],
        emergency_bypass={},
    )

    # Should work without errors
    relaxed = _apply_stage_relaxations(config, "pre-push")
    assert relaxed.gates["testing"].enabled is True


def test_detect_stage_github_pr():
    """Test stage detection for GitHub Actions pull request."""
    # Mock GitHub Actions PR environment
    os.environ["GITHUB_ACTIONS"] = "true"
    os.environ["GITHUB_EVENT_NAME"] = "pull_request"

    try:
        stage = _detect_stage()
        assert stage == "pr"
    finally:
        # Cleanup
        del os.environ["GITHUB_ACTIONS"]
        del os.environ["GITHUB_EVENT_NAME"]


def test_detect_stage_github_push_to_main():
    """Test stage detection for GitHub Actions push to main."""
    os.environ["GITHUB_ACTIONS"] = "true"
    os.environ["GITHUB_EVENT_NAME"] = "push"
    os.environ["GITHUB_REF"] = "refs/heads/main"

    try:
        stage = _detect_stage()
        assert stage == "push-to-main"
    finally:
        del os.environ["GITHUB_ACTIONS"]
        del os.environ["GITHUB_EVENT_NAME"]
        del os.environ["GITHUB_REF"]


def test_detect_stage_local_environment():
    """Test stage detection for local environment (not CI)."""
    # Clear any CI-related env vars
    ci_vars = [k for k in os.environ if k.startswith("GITHUB") or k == "CI"]
    backup = {k: os.environ.pop(k) for k in ci_vars if k in os.environ}

    try:
        stage = _detect_stage()
        assert stage is None  # Cannot detect
    finally:
        # Restore
        os.environ.update(backup)


def test_multiple_relaxations_applied():
    """Test multiple relaxations can be applied to same gate."""
    config = QualityGatesConfig(
        version="1.0.0",
        gates={
            "testing": GateConfig(
                name="testing",
                enabled=True,
                tool="pytest",
                command="pytest --tb=short",
                required=True,
                timeout_seconds=600,
                stage_relaxations={
                    "pre-push": {
                        "command": "pytest tests/unit -x",
                        "timeout_seconds": 60,
                    },
                },
            )
        },
        execution_order=["testing"],
        emergency_bypass={},
    )

    relaxed = _apply_stage_relaxations(config, "pre-push")

    # Both relaxations should be applied
    assert relaxed.gates["testing"].command == "pytest tests/unit -x"
    assert relaxed.gates["testing"].timeout_seconds == 60
