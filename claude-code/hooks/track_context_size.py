#!/usr/bin/env python3
"""
PostToolUse hook to track message context size and warn when it grows too large.

This hook monitors the cumulative message context size and alerts when:
- Context exceeds 10KB (configurable threshold)
- Helps manage costs from cache hits and long sessions

Usage:
  Configure in ~/.claude/settings.json (global) or .claude/settings.local.json (project):
  {
    "hooks": {
      "PostToolUse": [
        {
          "matcher": "*",
          "hooks": [
            {
              "type": "command",
              "command": "python3 /workspace/org-standards/claude-code/hooks/track_context_size.py 2>/dev/null || true"
            }
          ]
        }
      ]
    }
  }

  Note: /workspace should be symlinked to your dev directory on host:
    ln -s /Users/yourusername/NeerajDev /workspace

Environment Variables:
  CONTEXT_SIZE_THRESHOLD_KB: Warning threshold in KB (default: 10)
  CONTEXT_SIZE_WARNING_INTERVAL: Minimum seconds between warnings (default: 300)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Configuration
DEFAULT_THRESHOLD_KB = 10
DEFAULT_WARNING_INTERVAL_SEC = 300  # 5 minutes between warnings


def get_session_id() -> str:
    """Get or create session ID for tracking."""
    session_id = os.environ.get("CLAUDE_SESSION_ID")
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + str(os.getpid())
        os.environ["CLAUDE_SESSION_ID"] = session_id
    return session_id


def get_project_root() -> Path:
    """Find project root directory."""
    project_root_str = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_root_str:
        return Path(project_root_str)

    # Fallback: Find git root
    project_root = Path.cwd()
    git_root = project_root
    while git_root != git_root.parent:
        if (git_root / ".git").exists():
            return git_root
        git_root = git_root.parent
    return project_root


def estimate_size(data: Any) -> int:
    """Estimate size of data in bytes (JSON serialized)."""
    try:
        return len(json.dumps(data, ensure_ascii=False))
    except Exception:
        return 0


def load_session_state(session_file: Path) -> Dict[str, Any]:
    """Load session tracking state."""
    if not session_file.exists():
        return {
            "cumulative_size_bytes": 0,
            "message_count": 0,
            "last_warning_time": None,
            "warnings_shown": [],
        }

    try:
        with open(session_file, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except Exception:
        return {
            "cumulative_size_bytes": 0,
            "message_count": 0,
            "last_warning_time": None,
            "warnings_shown": [],
        }


def save_session_state(session_file: Path, state: Dict[str, Any]) -> None:
    """Save session tracking state."""
    try:
        with open(session_file, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save session state: {e}", file=sys.stderr)


def should_warn(state: Dict[str, Any], threshold_kb: int, warning_interval_sec: int) -> bool:
    """Check if we should show a warning."""
    size_kb = state["cumulative_size_bytes"] / 1024

    # Check if we've crossed threshold
    if size_kb < threshold_kb:
        return False

    # Check if we've already warned at this threshold
    threshold_key = f"{threshold_kb}KB"
    if threshold_key in state.get("warnings_shown", []):
        return False

    # Check if enough time has passed since last warning
    last_warning = state.get("last_warning_time")
    if last_warning:
        try:
            last_time = datetime.fromisoformat(last_warning)
            elapsed = (datetime.now() - last_time).total_seconds()
            if elapsed < warning_interval_sec:
                return False
        except Exception:
            pass

    return True


def show_warning(size_kb: float, threshold_kb: int) -> None:
    """Display warning to user."""
    print("\n" + "=" * 60, file=sys.stderr)
    print("⚠️  CONTEXT SIZE WARNING", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(
        f"Session message context: {size_kb:.1f}KB (threshold: {threshold_kb}KB)",
        file=sys.stderr,
    )
    print("\nLarge context increases costs from:", file=sys.stderr)
    print("  • Cache hits on input context", file=sys.stderr)
    print("  • Long message chains", file=sys.stderr)
    print("\nConsider:", file=sys.stderr)
    print("  1. Start new session for unrelated work", file=sys.stderr)
    print("  2. Use /clear to reset context", file=sys.stderr)
    print("  3. Save current work and create handoff doc", file=sys.stderr)
    print("=" * 60 + "\n", file=sys.stderr)


def main() -> None:
    """Main hook logic."""
    # Read hook input from stdin
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Get configuration
    threshold_kb = int(os.environ.get("CONTEXT_SIZE_THRESHOLD_KB", DEFAULT_THRESHOLD_KB))
    warning_interval = int(os.environ.get("CONTEXT_SIZE_WARNING_INTERVAL", DEFAULT_WARNING_INTERVAL_SEC))

    # Setup paths
    session_id = get_session_id()
    project_root = get_project_root()
    tracking_dir = project_root / ".ai-usage-tracking" / "context"
    tracking_dir.mkdir(parents=True, exist_ok=True)

    session_file = tracking_dir / f"session-{session_id}.json"

    # Load current state
    state = load_session_state(session_file)

    # Estimate size of this tool call + response
    tool_call_size = estimate_size(hook_data.get("tool_input", {}))
    tool_response_size = estimate_size(hook_data.get("tool_output", {}))
    message_size = tool_call_size + tool_response_size

    # Update state
    state["cumulative_size_bytes"] += message_size
    state["message_count"] += 1
    state["last_tool_call"] = {
        "timestamp": datetime.now().isoformat(),
        "tool_name": hook_data.get("tool_name", "unknown"),
        "size_bytes": message_size,
    }

    # Check if we should warn
    if should_warn(state, threshold_kb, warning_interval):
        size_kb = state["cumulative_size_bytes"] / 1024
        show_warning(size_kb, threshold_kb)

        # Mark this threshold as warned
        threshold_key = f"{threshold_kb}KB"
        if "warnings_shown" not in state:
            state["warnings_shown"] = []
        state["warnings_shown"].append(threshold_key)
        state["last_warning_time"] = datetime.now().isoformat()

    # Save updated state
    save_session_state(session_file, state)

    # Also log to aggregate tracking
    try:
        aggregate_file = project_root / ".ai-usage-tracking" / "context-tracking.jsonl"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session": session_id,
            "cumulative_size_kb": state["cumulative_size_bytes"] / 1024,
            "message_count": state["message_count"],
            "tool_name": hook_data.get("tool_name", "unknown"),
        }
        with open(aggregate_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Don't block on logging errors

    sys.exit(0)


if __name__ == "__main__":
    main()
