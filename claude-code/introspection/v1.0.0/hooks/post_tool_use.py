#!/usr/bin/env python3
"""
PostToolUse Hook - Log tool failures

This hook runs after every tool execution in Claude Code.
It logs failures to the session-isolated failure tracker.

Installation:
Add to ~/.claude/settings.json:
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 /Users/neerajgarg/syra/introspection/hooks/post_tool_use.py"
      }]
    }]
  }
}
"""

import json
import logging
import sys

from introspection.core.failure_tracker import FailureTracker

logger = logging.getLogger(__name__)


def main():
    """Hook entry point - reads event from stdin, logs if failure."""
    try:
        logger.debug("PostToolUse hook started")

        # Read event data from stdin
        event_data = json.load(sys.stdin)

        # Check if it's a failure
        exit_code = event_data.get("exit_code", 0)
        stderr = event_data.get("stderr", "")
        tool_name = event_data.get("tool_name", "unknown")

        logger.debug(
            "Tool execution complete",
            extra={
                "tool_name": tool_name,
                "exit_code": exit_code,
                "has_stderr": bool(stderr),
            },
        )

        if exit_code != 0 or stderr:
            logger.debug("Failure detected, logging to tracker", extra={"tool_name": tool_name})
            # Log the failure
            tracker = FailureTracker()
            tracker.log_failure(event_data)
            logger.debug("Failure logged successfully")
        else:
            logger.debug("No failure detected, skipping")

    except Exception as e:
        # Silent failure - don't disrupt Claude's operation
        logger.error("PostToolUse hook error", exc_info=True)
        print(f"Warning: Introspection hook error: {e}", file=sys.stderr)
        pass


if __name__ == "__main__":
    main()
