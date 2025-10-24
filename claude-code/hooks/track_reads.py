#!/usr/bin/env python3
"""
PreToolUse hook to track Read tool calls for token usage analysis.

This hook intercepts all Read tool calls and logs them to:
- Per-session: .ai-usage-tracking/sessions/session-{SESSION_ID}.jsonl
- Aggregate: .ai-usage-tracking/read-tracking.jsonl

Usage:
  Configure in ~/.claude/settings.json (global):
  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Read",
          "hooks": [
            {
              "type": "command",
              "command": "python3 ~/org-standards/claude-code/hooks/track_reads.py"
            }
          ]
        }
      ]
    }
  }
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    # Read hook input from stdin (Claude Code provides tool call data as JSON)
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Not JSON input, exit silently (allow tool to proceed)
        sys.exit(0)

    tool_name = hook_data.get("tool_name")

    # Only track Read tool calls
    if tool_name != "Read":
        sys.exit(0)

    tool_input = hook_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Generate session ID from environment or create new one
    session_id = os.environ.get("CLAUDE_SESSION_ID")
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + str(os.getpid())
        os.environ["CLAUDE_SESSION_ID"] = session_id

    # Use CLAUDE_PROJECT_DIR if available, otherwise find git root
    project_root_str = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_root_str:
        project_root = Path(project_root_str)
    else:
        # Fallback: Find project root via git
        project_root = Path.cwd()
        git_root = project_root
        while git_root != git_root.parent:
            if (git_root / ".git").exists():
                project_root = git_root
                break
            git_root = git_root.parent

    # Setup tracking directories
    tracking_dir = project_root / ".ai-usage-tracking" / "sessions"
    tracking_dir.mkdir(parents=True, exist_ok=True)

    session_file = tracking_dir / f"session-{session_id}.jsonl"
    aggregate_file = project_root / ".ai-usage-tracking" / "read-tracking.jsonl"

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "session": session_id,
        "type": "Read",
    }

    # Write to both session file and aggregate
    try:
        with open(session_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        with open(aggregate_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Optional: Print to stderr for real-time visibility
        # Uncomment if you want to see Read calls as they happen
        # print(f"📖 Read: {Path(file_path).name}", file=sys.stderr)
    except Exception as e:
        # Silently fail - don't block the tool call
        print(f"Warning: Failed to log Read call: {e}", file=sys.stderr)

    # Exit 0 = allow tool to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
