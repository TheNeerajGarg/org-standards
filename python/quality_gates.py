#!/usr/bin/env python3
"""Quality gates configuration loader and executor.

This module provides the core infrastructure for loading and executing quality gates
defined in quality-gates.yaml. It handles:
- Loading base configuration with optional repository overrides
- Executing gates in configured order
- Respecting dependencies and timeouts
- Reporting results

Example usage:
    from quality_gates import load_config, execute_gates

    config = load_config()
    results = execute_gates(config, phase="pre-push")
    if not results.passed:
        sys.exit(1)
"""

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class GateConfig:
    """Configuration for a single quality gate.

    Base configuration represents the HIGHEST STANDARD (push-to-main requirements).
    Stage relaxations allow explicit opt-out for earlier stages.
    """

    name: str
    enabled: bool
    tool: str
    command: str | None = None
    commands: dict[str, str] | None = None
    threshold: int | None = None
    description: str = ""
    required: bool = True
    depends_on: list[str] = field(default_factory=list)
    omit_patterns: list[str] = field(default_factory=list)
    fail_message: str = ""
    timeout_seconds: int = 300
    stage_relaxations: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class QualityGatesConfig:
    """Complete quality gate configuration."""

    version: str
    gates: dict[str, GateConfig]
    execution_order: list[str]
    emergency_bypass: dict[str, Any]
    override_file: str | None = None


@dataclass
class GateResult:
    """Result of executing a single gate."""

    gate_name: str
    passed: bool
    duration_seconds: float
    message: str = ""
    fail_message: str = ""


@dataclass
class ExecutionResults:
    """Results of executing all gates."""

    passed: bool
    failed_count: int
    total_count: int
    duration_seconds: float
    results: list[GateResult]
    failures: list[GateResult]


def load_config(
    base_config: Path | str | None = None,
    override_config: Path | str | None = None,
) -> QualityGatesConfig:
    """Load quality gate configuration with optional overrides.

    Args:
        base_config: Path to base configuration file (defaults to org-standards/config/quality-gates.yaml)
        override_config: Path to override configuration file (defaults to quality-gates.local.yaml)

    Returns:
        Parsed and merged quality gates configuration

    Raises:
        FileNotFoundError: If base config not found
        ValueError: If config is invalid or inconsistent
    """
    if base_config is None:
        base_config = Path("org-standards/config/quality-gates.yaml")
    elif isinstance(base_config, str):
        base_config = Path(base_config)

    if not base_config.exists():
        raise FileNotFoundError(f"Config not found: {base_config}")

    # Load base config
    with open(base_config) as f:
        base = yaml.safe_load(f)

    # Load overrides if exist
    if override_config is None:
        override_file = base.get("override_file", "quality-gates.local.yaml")
        override_config = Path(override_file)
    elif isinstance(override_config, str):
        override_config = Path(override_config)

    overrides: dict[str, Any] = {}
    if override_config.exists():
        with open(override_config) as f:
            overrides = yaml.safe_load(f) or {}

    # Merge configs
    config = _merge_configs(base, overrides)

    # Validate
    _validate_config(config)

    # Parse
    return _parse_config(config)


def execute_gates(config: QualityGatesConfig, phase: str = "pre-push") -> ExecutionResults:
    """Execute quality gates in configured order.

    Base configuration = HIGHEST STANDARD (push-to-main requirements).
    Relaxations applied for pre-push/pr stages for development speed.

    Args:
        config: Quality gates configuration
        phase: Stage name ("pre-push", "pr", "push-to-main")
               If not provided, auto-detects from environment

    Returns:
        Execution results with pass/fail status and details
    """
    # Detect stage if not explicitly provided
    stage = phase or _detect_stage()

    # Log stage
    if stage:
        print(f"🎯 Stage: {stage}")
        if stage == "push-to-main":
            print("   Using highest standard (no relaxations)")
        else:
            print(f"   Applying relaxations for '{stage}' stage")

    # Apply stage relaxations
    config = _apply_stage_relaxations(config, stage)

    start_time = time.time()
    results = []
    failures = []

    for gate_name in config.execution_order:
        gate = config.gates[gate_name]

        if not gate.enabled:
            continue

        print(f"▶️  Running {gate_name} ({gate.tool})...")

        result = _execute_gate(gate)
        results.append(result)

        if not result.passed:
            failures.append(result)
            if gate.required:
                print(f"❌ {gate_name} failed (required gate)")
                break
            else:
                print(f"⚠️  {gate_name} failed (optional, continuing)")
        else:
            print(f"✅ {gate_name} passed ({result.duration_seconds:.1f}s)")

    total_duration = time.time() - start_time

    return ExecutionResults(
        passed=len(failures) == 0,
        failed_count=len(failures),
        total_count=len(results),
        duration_seconds=total_duration,
        results=results,
        failures=failures,
    )


def _execute_gate(gate: GateConfig) -> GateResult:
    """Execute a single quality gate.

    Args:
        gate: Gate configuration

    Returns:
        Result of gate execution
    """
    start_time = time.time()

    # Check tool availability
    tool_check = subprocess.run(
        ["which", gate.tool],
        capture_output=True,
        text=True,
    )

    if tool_check.returncode != 0:
        if gate.required:
            return GateResult(
                gate_name=gate.name,
                passed=False,
                duration_seconds=0,
                message=f"Tool '{gate.tool}' not installed",
                fail_message=f"Install: pip install {gate.tool}",
            )
        else:
            return GateResult(
                gate_name=gate.name,
                passed=True,  # Skip optional gates if tool missing
                duration_seconds=0,
                message=f"Tool '{gate.tool}' not installed (skipped - optional)",
            )

    # Execute command
    command = gate.command or (" && ".join(gate.commands.values()) if gate.commands else "")

    # Substitute placeholders
    if gate.threshold:
        command = command.replace("{threshold}", str(gate.threshold))

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=gate.timeout_seconds,
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            return GateResult(
                gate_name=gate.name,
                passed=True,
                duration_seconds=duration,
                message="Passed",
            )
        else:
            return GateResult(
                gate_name=gate.name,
                passed=False,
                duration_seconds=duration,
                message=result.stdout + result.stderr,
                fail_message=gate.fail_message,
            )

    except subprocess.TimeoutExpired:
        return GateResult(
            gate_name=gate.name,
            passed=False,
            duration_seconds=gate.timeout_seconds,
            message=f"Timeout after {gate.timeout_seconds} seconds",
        )


def _merge_configs(base: dict, overrides: dict) -> dict:
    """Deep merge override config into base config.

    Args:
        base: Base configuration dictionary
        overrides: Override configuration dictionary

    Returns:
        Merged configuration
    """
    result = base.copy()

    if "gates" in overrides:
        for gate_name, gate_overrides in overrides["gates"].items():
            if gate_name in result["gates"]:
                result["gates"][gate_name].update(gate_overrides)
            else:
                result["gates"][gate_name] = gate_overrides

    for key in ["version", "execution_order", "emergency_bypass"]:
        if key in overrides:
            result[key] = overrides[key]

    return result


def _validate_config(config: dict) -> None:
    """Validate config structure and consistency.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid
    """
    required = ["version", "gates", "execution_order"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    # Check execution_order references valid gates
    gate_names = set(config["gates"].keys())
    order = config["execution_order"]
    invalid = [g for g in order if g not in gate_names]
    if invalid:
        raise ValueError(f"execution_order references undefined gates: {invalid}")


def _parse_config(config: dict) -> QualityGatesConfig:
    """Parse raw config dict into typed dataclasses.

    Args:
        config: Raw configuration dictionary

    Returns:
        Parsed QualityGatesConfig object
    """
    gates = {}
    for name, gate_dict in config["gates"].items():
        gates[name] = GateConfig(
            name=name,
            enabled=gate_dict["enabled"],
            tool=gate_dict["tool"],
            command=gate_dict.get("command"),
            commands=gate_dict.get("commands"),
            threshold=gate_dict.get("threshold"),
            description=gate_dict.get("description", ""),
            required=gate_dict["required"],
            depends_on=gate_dict.get("depends_on", []),
            omit_patterns=gate_dict.get("omit_patterns", []),
            fail_message=gate_dict.get("fail_message", ""),
            timeout_seconds=gate_dict.get("timeout_seconds", 300),
        )

    return QualityGatesConfig(
        version=config["version"],
        gates=gates,
        execution_order=config["execution_order"],
        emergency_bypass=config.get("emergency_bypass", {}),
        override_file=config.get("override_file"),
    )


# Valid stage names
VALID_STAGES = {"pre-push", "pr", "push-to-main"}


def _detect_stage() -> str | None:
    """Auto-detect stage from environment.

    Returns:
        Stage name ("pre-push", "pr", "push-to-main") or None if cannot detect
    """
    import os

    # GitHub Actions detection
    if os.getenv("GITHUB_ACTIONS") == "true":
        event_name = os.getenv("GITHUB_EVENT_NAME")
        ref = os.getenv("GITHUB_REF")

        if event_name == "pull_request":
            return "pr"
        elif ref in ("refs/heads/main", "refs/heads/master"):
            return "push-to-main"

    # Cannot detect stage - will use base config (highest standard)
    return None


def _apply_stage_relaxations(
    config: QualityGatesConfig,
    stage: str | None,
) -> QualityGatesConfig:
    """Apply stage-specific relaxations to gate configurations.

    Base configuration = HIGHEST STANDARD (push-to-main requirements).
    Relaxations allow explicit opt-out for earlier stages.

    Args:
        config: Base quality gates configuration (strictest requirements)
        stage: Stage to apply ("pre-push", "pr", "push-to-main", or None)

    Returns:
        Configuration with stage relaxations applied
    """
    # No relaxations for push-to-main or unknown stages
    if stage is None or stage == "push-to-main":
        return config

    # Validate stage name
    if stage not in VALID_STAGES:
        raise ValueError(
            f"Unknown stage '{stage}'. Valid stages: {', '.join(sorted(VALID_STAGES))}.\n"
            f"Check for typos (e.g., 'pre_push' should be 'pre-push')."
        )

    # Deep copy config to avoid modifying original
    import copy

    config = copy.deepcopy(config)

    # Apply relaxations for each gate
    for gate_name, gate in config.gates.items():
        if stage in gate.stage_relaxations:
            relaxations = gate.stage_relaxations[stage]

            # Apply each relaxation
            for key, value in relaxations.items():
                if hasattr(gate, key):
                    setattr(gate, key, value)
                else:
                    # Log warning for unknown keys
                    print(f"⚠️  Unknown relaxation key '{key}' for gate '{gate_name}' stage '{stage}'")

    return config
