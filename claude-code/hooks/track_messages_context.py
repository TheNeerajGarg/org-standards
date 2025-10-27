#!/usr/bin/env python3
"""
UserPromptSubmit hook to track conversation message context size and warn when too large.

This hook monitors the cumulative conversation message context and alerts when:
- Messages context exceeds 10KB (configurable threshold)
- Helps manage costs from cache hits and long conversation sessions

How it works:
- Runs on UserPromptSubmit (before each user prompt is processed)
- Reads the transcript file to get full conversation history
- Calculates total size of all messages in conversation
- Warns once per threshold crossing

Usage:
  Configure in ~/.claude/settings.json:
  {
    "hooks": {
      "UserPromptSubmit": [
        {
          "matcher": "*",
          "hooks": [
            {
              "type": "command",
              "command": "python3 /opt/org-standards/claude-code/hooks/track_messages_context.py \\
                         2>/dev/null || python3 ~/org-standards/claude-code/hooks/track_messages_context.py \\
                         2>/dev/null || true"
            }
          ]
        }
      ]
    }
  }

Environment Variables:
  CONTEXT_SIZE_THRESHOLD_KB: Warning threshold in KB (default: 10)
  CONTEXT_SIZE_WARNING_INTERVAL: Minimum seconds between warnings (default: 300)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configuration
DEFAULT_THRESHOLD_KB = 10
DEFAULT_WARNING_INTERVAL_SEC = 300  # 5 minutes between warnings


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


def read_transcript_messages(transcript_path: str) -> List[Dict[str, Any]]:
    """Read all messages from the transcript JSONL file."""
    messages = []
    try:
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            return messages

        with open(transcript_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Each JSONL entry might contain a message or conversation state
                    # We want to extract the actual messages
                    if isinstance(entry, dict):
                        # If this is a message entry, add it
                        if "role" in entry and "content" in entry:
                            messages.append(entry)
                        # If this is a wrapper with messages array, extract them
                        elif "messages" in entry:
                            if isinstance(entry["messages"], list):
                                messages.extend(entry["messages"])
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Warning: Failed to read transcript: {e}", file=sys.stderr)

    return messages


def calculate_messages_size(messages: List[Dict[str, Any]]) -> int:
    """Calculate total size of all messages in bytes."""
    total_size = 0
    for msg in messages:
        total_size += estimate_size(msg)
    return total_size


def get_session_tracking_file(session_id: str, project_root: Path) -> Path:
    """Get path to session tracking file."""
    tracking_dir = project_root / ".ai-usage-tracking" / "message-context"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    return tracking_dir / f"session-{session_id}.json"


def load_session_state(session_file: Path) -> Dict[str, Any]:
    """Load session tracking state."""
    if not session_file.exists():
        return {
            "last_warning_time": None,
            "warnings_shown": [],
            "last_check_timestamp": None,
        }

    try:
        with open(session_file, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except Exception:
        return {
            "last_warning_time": None,
            "warnings_shown": [],
            "last_check_timestamp": None,
        }


def save_session_state(session_file: Path, state: Dict[str, Any]) -> None:
    """Save session tracking state."""
    try:
        with open(session_file, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save session state: {e}", file=sys.stderr)


def should_warn(
    state: Dict[str, Any],
    size_kb: float,
    threshold_kb: int,
    warning_interval_sec: int,
) -> bool:
    """Check if we should show a warning."""
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


def show_warning(size_kb: float, message_count: int, threshold_kb: int) -> None:
    """Display warning to user."""
    print("\n" + "=" * 60, file=sys.stderr)
    print("⚠️  CONVERSATION CONTEXT SIZE WARNING", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(
        f"Conversation messages: {size_kb:.1f}KB ({message_count} messages)",
        file=sys.stderr,
    )
    print(f"Threshold: {threshold_kb}KB", file=sys.stderr)
    print("\nLarge context increases costs from:", file=sys.stderr)
    print("  • Prompt caching on accumulated messages", file=sys.stderr)
    print("  • Long message chains sent with every request", file=sys.stderr)
    print("\nConsider:", file=sys.stderr)
    print("  1. Use /clear to reset conversation", file=sys.stderr)
    print("  2. Start new session for unrelated work", file=sys.stderr)
    print("  3. Create handoff doc and start fresh", file=sys.stderr)
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

    # Get session ID and transcript path from hook data
    session_id = hook_data.get("session_id", "unknown")
    transcript_path = hook_data.get("transcript_path")

    if not transcript_path:
        # No transcript available, exit silently
        sys.exit(0)

    # Setup paths
    project_root = get_project_root()
    session_file = get_session_tracking_file(session_id, project_root)

    # Load current state
    state = load_session_state(session_file)

    # Read and measure messages from transcript
    messages = read_transcript_messages(transcript_path)
    messages_size_bytes = calculate_messages_size(messages)
    size_kb = messages_size_bytes / 1024

    # Update state
    state["last_check_timestamp"] = datetime.now().isoformat()
    state["last_size_kb"] = size_kb
    state["message_count"] = len(messages)

    # Check if we should warn
    if should_warn(state, size_kb, threshold_kb, warning_interval):
        show_warning(size_kb, len(messages), threshold_kb)

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
        aggregate_file = project_root / ".ai-usage-tracking" / "message-context-tracking.jsonl"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session": session_id,
            "size_kb": size_kb,
            "message_count": len(messages),
            "warned": threshold_key if should_warn(state, size_kb, threshold_kb, warning_interval) else None,
        }
        with open(aggregate_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass  # Don't block on logging errors

    sys.exit(0)


if __name__ == "__main__":
    main()
