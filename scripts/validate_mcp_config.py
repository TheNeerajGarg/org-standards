#!/usr/bin/env python3
"""
MCP Configuration Validator

Validates .mcp.json files for Claude Code integration.

Usage:
    python validate_mcp_config.py <path-to-.mcp.json>
    python validate_mcp_config.py --all  # Validate all repos

Exit codes:
    0 - All validations passed
    1 - Validation errors found
    2 - File not found or invalid JSON
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class MCPConfigValidator:
    """Validates MCP server configurations."""

    REQUIRED_FIELDS = ["type", "command", "args"]
    VALID_TYPES = ["stdio"]

    def __init__(self, config_path: Path) -> None:
        """
        Initialize validator.

        Args:
            config_path: Path to .mcp.json file
        """
        self.config_path = config_path
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Run all validations.

        Returns:
            True if all validations pass, False otherwise
        """
        # Check file exists
        if not self.config_path.exists():
            self.errors.append(f"File not found: {self.config_path}")
            return False

        # Load and parse JSON
        try:
            with open(self.config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

        # Validate structure
        self._validate_structure(config)

        # Validate each server
        if "mcpServers" in config:
            for server_name, server_config in config["mcpServers"].items():
                self._validate_server(server_name, server_config)

        return len(self.errors) == 0

    def _validate_structure(self, config: Dict[str, Any]) -> None:
        """Validate top-level structure."""
        if "mcpServers" not in config:
            self.errors.append("Missing required field: 'mcpServers'")
            return

        if not isinstance(config["mcpServers"], dict):
            self.errors.append("'mcpServers' must be an object")
            return

        if len(config["mcpServers"]) == 0:
            self.warnings.append("No MCP servers defined")

    def _validate_server(self, name: str, config: Dict[str, Any]) -> None:
        """
        Validate individual server configuration.

        Args:
            name: Server name
            config: Server configuration object
        """
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in config:
                self.errors.append(f"Server '{name}': Missing required field '{field}'")

        # Validate type
        if "type" in config:
            if config["type"] not in self.VALID_TYPES:
                self.errors.append(
                    f"Server '{name}': Invalid type '{config['type']}'. Valid types: {', '.join(self.VALID_TYPES)}"
                )

        # Validate args is array
        if "args" in config:
            if not isinstance(config["args"], list):
                self.errors.append(f"Server '{name}': 'args' must be an array")
            else:
                self._validate_args(name, config["args"])

        # Validate env is object (if present)
        if "env" in config:
            if not isinstance(config["env"], dict):
                self.errors.append(f"Server '{name}': 'env' must be an object")

    def _validate_args(self, server_name: str, args: List[str]) -> None:
        """
        Validate server arguments.

        Args:
            server_name: Server name
            args: Server arguments list
        """
        # Check for module invocation pattern
        if len(args) >= 2 and args[0] == "-m":
            module_name = args[1]
            if not self._is_valid_module_name(module_name):
                self.warnings.append(f"Server '{server_name}': Module name '{module_name}' may not be valid")

        # Check for absolute paths (workspace root should be absolute)
        if len(args) >= 3:
            workspace_path = args[-1]  # Assume last arg is workspace path
            if not workspace_path.startswith("/"):
                self.warnings.append(
                    f"Server '{server_name}': Workspace path '{workspace_path}' "
                    f"is not absolute. Use full path for reliability."
                )
            else:
                # Validate path exists
                if not Path(workspace_path).exists():
                    self.errors.append(f"Server '{server_name}': Workspace path '{workspace_path}' does not exist")

    def _is_valid_module_name(self, name: str) -> bool:
        """
        Check if module name looks valid.

        Args:
            name: Module name to check

        Returns:
            True if valid, False otherwise
        """
        # Basic check: alphanumeric + underscore + dots
        import re

        return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", name))

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print(f"\n❌ Validation FAILED for {self.config_path}")
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print(f"✅ Validation PASSED for {self.config_path}")
        elif not self.errors:
            print(f"\n✅ Validation PASSED (with warnings) for {self.config_path}")


def validate_all_repos() -> Tuple[int, int]:
    """
    Validate MCP configs in all known repos.

    Returns:
        Tuple of (total_repos, failed_repos)
    """
    # Known repos (relative to org-standards parent)
    org_standards_path = Path(__file__).parent.parent
    parent_dir = org_standards_path.parent

    repos = [
        parent_dir / "syra",
        parent_dir / "StyleGuru",
        parent_dir / "StyleGuru",
        org_standards_path,
    ]

    total = 0
    failed = 0

    print("Validating MCP configs across all repos...\n")

    for repo in repos:
        mcp_config = repo / ".mcp.json"

        if not mcp_config.exists():
            print(f"⚠️  {repo.name}: No .mcp.json found (skipping)")
            continue

        total += 1
        validator = MCPConfigValidator(mcp_config)

        if not validator.validate():
            failed += 1

        validator.print_results()
        print()

    return total, failed


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code
    """
    if len(sys.argv) < 2:
        print("Usage: python validate_mcp_config.py <path-to-.mcp.json>")
        print("       python validate_mcp_config.py --all")
        return 2

    if sys.argv[1] == "--all":
        total, failed = validate_all_repos()

        print(f"Validated {total} repos: {total - failed} passed, {failed} failed")
        return 1 if failed > 0 else 0

    # Validate single file
    config_path = Path(sys.argv[1])
    validator = MCPConfigValidator(config_path)

    success = validator.validate()
    validator.print_results()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
