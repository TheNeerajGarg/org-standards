#!/usr/bin/env python3
"""
Introspection Document Schema Validator

Validates that introspection documents contain required sections.
Used by pre-commit hook to enforce introspection quality.

Usage:
    python3 scripts/validate-introspection.py <file_path>

Exit codes:
    0: Valid introspection document
    1: Invalid (missing required sections or file not found)

Required sections:
    - ## What Was the Problem?
    - ## Why Did It Happen?
    - ## How Could It Have Been Prevented?
"""

import sys
from pathlib import Path

# Required sections in introspection documents
REQUIRED_SECTIONS = [
    "## What Was the Problem?",
    "## Why Did It Happen?",
    "## How Could It Have Been Prevented?",
]


def validate_introspection(file_path: str) -> tuple[bool, str]:
    """
    Validate introspection document has required sections.

    Args:
        file_path: Path to introspection document

    Returns:
        (is_valid, message): Tuple of validation result and message
    """
    path = Path(file_path)

    # Check file exists
    if not path.exists():
        return False, f"File not found: {file_path}"

    # Check file is readable
    if not path.is_file():
        return False, f"Not a file: {file_path}"

    # Read content
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Error reading file: {e}"

    # Check for required sections
    missing_sections = []
    for section in REQUIRED_SECTIONS:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        return False, "Missing required sections:\n  - " + "\n  - ".join(missing_sections)

    # Check minimum content length (avoid empty sections)
    if len(content.strip()) < 200:
        return (
            False,
            f"Document too short ({len(content)} chars). "
            "Introspection should provide meaningful analysis.",
        )

    return True, "Valid introspection document"


def main() -> int:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate-introspection.py <file_path>")
        return 1

    file_path = sys.argv[1]

    is_valid, message = validate_introspection(file_path)

    if is_valid:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ Validation failed: {message}", file=sys.stderr)
        print("\nExpected sections:", file=sys.stderr)
        for section in REQUIRED_SECTIONS:
            print(f"  - {section}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
