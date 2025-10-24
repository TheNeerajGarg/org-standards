#!/usr/bin/env python3
"""Validate quality-gates.yaml against schema and semantic rules.

Usage:
    python scripts/validate-config.py                    # Validate config/quality-gates.yaml
    python scripts/validate-config.py path/to/config.yaml  # Validate specific file

Exit codes:
    0: Valid
    1: Invalid (schema or semantic errors)
"""

import json
import sys
from pathlib import Path
from typing import Any

try:
    import jsonschema
    import yaml
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install pyyaml jsonschema")
    sys.exit(1)


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error in {path}:")
        print(f"   {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ File not found: {path}")
        sys.exit(1)


def validate_schema(config: dict[str, Any], schema_path: Path) -> bool:
    """Validate config against JSON Schema."""
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        print(f"❌ Schema file not found: {schema_path}")
        return False
    except json.JSONDecodeError as e:
        print("❌ Schema JSON syntax error:")
        print(f"   {e}")
        return False

    try:
        jsonschema.validate(instance=config, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print("❌ Schema validation failed:")
        print(f"   {e.message}")
        if e.absolute_path:
            print(f"   Path: {' -> '.join(str(p) for p in e.absolute_path)}")
        return False


def validate_semantic(config: dict[str, Any]) -> bool:
    """Validate semantic rules (circular deps, undefined gates, etc.)."""
    errors: list[str] = []

    gates = config.get("gates", {})
    execution_order = config.get("execution_order", [])

    # Rule 1: All gates in execution_order must be defined
    defined_gates = set(gates.keys())
    ordered_gates = set(execution_order)

    undefined = ordered_gates - defined_gates
    if undefined:
        errors.append(f"Undefined gates in execution_order: {undefined}")

    # Rule 2: All enabled gates should appear in execution_order
    enabled_gates = {name for name, cfg in gates.items() if cfg.get("enabled", False)}
    missing_from_order = enabled_gates - ordered_gates
    if missing_from_order:
        errors.append(f"Enabled gates missing from execution_order: {missing_from_order}")

    # Rule 3: Check circular dependencies
    for gate_name, gate_config in gates.items():
        depends_on = gate_config.get("depends_on", [])
        if gate_name in depends_on:
            errors.append(f"Gate '{gate_name}' depends on itself (circular dependency)")

        # Check transitive circular deps
        visited: set[str] = set()
        stack: list[str] = [gate_name]

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)

            current_deps = gates.get(current, {}).get("depends_on", [])
            for dep in current_deps:
                if dep == gate_name:
                    errors.append(f"Circular dependency detected: {gate_name} -> ... -> {dep}")
                    break
                if dep in gates:
                    stack.append(dep)

    # Rule 4: Dependencies must be defined gates
    for gate_name, gate_config in gates.items():
        depends_on = gate_config.get("depends_on", [])
        for dep in depends_on:
            if dep not in gates:
                errors.append(f"Gate '{gate_name}' depends on undefined gate '{dep}'")

    # Rule 5: Dependencies should appear earlier in execution_order
    gate_positions = {gate: idx for idx, gate in enumerate(execution_order)}
    for gate_name, gate_config in gates.items():
        if gate_name not in gate_positions:
            continue
        gate_pos = gate_positions[gate_name]

        depends_on = gate_config.get("depends_on", [])
        for dep in depends_on:
            if dep not in gate_positions:
                continue
            dep_pos = gate_positions[dep]
            if dep_pos >= gate_pos:
                errors.append(
                    f"Gate '{gate_name}' depends on '{dep}', but '{dep}' appears "
                    f"later in execution_order (position {dep_pos} >= {gate_pos})"
                )

    # Rule 6: Version format
    version = config.get("version", "")
    if not version:
        errors.append("Missing 'version' field")
    elif not all(part.isdigit() for part in version.split(".")):
        errors.append(f"Invalid version format '{version}' (expected X.Y.Z)")

    # Rule 7: Required tools exist (basic check)
    known_tools = {
        "pytest",
        "diff-cover",
        "mypy",
        "ruff",
        "coverage",
        "bandit",
        "black",
        "flake8",
    }
    for gate_name, gate_config in gates.items():
        tool = gate_config.get("tool", "")
        if tool and tool not in known_tools:
            # Warning, not error (allow custom tools)
            print(f"⚠️  Warning: Gate '{gate_name}' uses unknown tool '{tool}'")

    # Print all errors
    if errors:
        print("❌ Semantic validation failed:")
        for error in errors:
            print(f"   - {error}")
        return False

    return True


def main() -> int:
    """Main validation function."""
    # Determine config path
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    else:
        config_path = Path(__file__).parent.parent / "config" / "quality-gates.yaml"

    schema_path = Path(__file__).parent.parent / "config" / "quality-gates.schema.json"

    print(f"🔍 Validating: {config_path}")

    # Load config
    config = load_yaml(config_path)

    # Validate schema
    print("📋 Checking schema...")
    schema_valid = validate_schema(config, schema_path)

    if not schema_valid:
        return 1

    print("✅ Schema validation passed")

    # Validate semantics
    print("🧠 Checking semantic rules...")
    semantic_valid = validate_semantic(config)

    if not semantic_valid:
        return 1

    print("✅ Semantic validation passed")
    print(f"✅ {config_path} is valid")

    return 0


if __name__ == "__main__":
    sys.exit(main())
