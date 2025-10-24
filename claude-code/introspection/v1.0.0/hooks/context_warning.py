#!/usr/bin/env python3
"""
Context Warning Hook - Warn when context gets too large

This hook runs after every tool execution in Claude Code.
It tracks message count and large file reads to warn users
when context grows too large, preventing expensive API costs.

Installation:
Add to ~/.claude/settings.local.json or project .claude/settings.json:
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/org-standards/claude-code/introspection/current/hooks/context_warning.py"
      }]
    }]
  }
}

Configuration (via environment variables):
- CLAUDE_MAX_MESSAGES: Max messages before warning (default: 15)
- CLAUDE_MAX_LARGE_FILES: Max large file reads before warning (default: 2)
- CLAUDE_LARGE_FILE_THRESHOLD: Token threshold for "large" files (default: 20000)
"""

import json
import os
import sys
from pathlib import Path

# Configuration from environment or defaults
MAX_MESSAGES = int(os.getenv("CLAUDE_MAX_MESSAGES", "15"))
MAX_LARGE_FILE_READS = int(os.getenv("CLAUDE_MAX_LARGE_FILES", "2"))
LARGE_FILE_THRESHOLD = int(os.getenv("CLAUDE_LARGE_FILE_THRESHOLD", "20000"))

# Session tracking directory
SESSION_DIR = Path.home() / ".claude" / "context_tracker"


def estimate_tokens(text: str) -> int:
    """
    Rough token estimate: ~4 characters per token
    This is conservative (actual is closer to 3.5 for English)
    """
    return len(text) // 4


def get_or_create_session_id() -> str:
    """Get current session ID from Claude environment or create tracking ID"""
    # Try to get actual Claude session ID from event data
    # Fallback to PID-based tracking if not available
    return os.getenv("CLAUDE_SESSION_ID", f"pid-{os.getppid()}")


def increment_counter(counter_name: str) -> int:
    """Increment and return counter value"""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    session_id = get_or_create_session_id()
    counter_file = SESSION_DIR / f"{session_id}_{counter_name}"

    current_value = 0
    if counter_file.exists():
        try:
            current_value = int(counter_file.read_text().strip())
        except (ValueError, OSError):
            current_value = 0

    current_value += 1
    counter_file.write_text(str(current_value))

    return current_value


def get_counter(counter_name: str) -> int:
    """Get current counter value without incrementing"""
    session_id = get_or_create_session_id()
    counter_file = SESSION_DIR / f"{session_id}_{counter_name}"

    if counter_file.exists():
        try:
            return int(counter_file.read_text().strip())
        except (ValueError, OSError):
            return 0
    return 0


def reset_session_counters():
    """Reset all counters for current session"""
    session_id = get_or_create_session_id()
    for counter_file in SESSION_DIR.glob(f"{session_id}_*"):
        counter_file.unlink()


def warn(message: str, level: str = "WARNING"):
    """Print warning to stderr in a visible format"""
    symbols = {"WARNING": "⚠️ ", "CRITICAL": "❌", "INFO": "ℹ️ "}
    symbol = symbols.get(level, "⚠️ ")
    print(f"\n{symbol}  {level}: {message}", file=sys.stderr)


def check_message_count():
    """Check message count and warn if approaching limit"""
    message_count = increment_counter("messages")

    if message_count == MAX_MESSAGES:
        warn(f"Context limit reached: {message_count} messages in this session")
        print(
            "   💡 Consider exiting and starting fresh session to reduce API costs",
            file=sys.stderr,
        )
        print(
            f"   💰 Every message now includes {message_count}+ previous messages",
            file=sys.stderr,
        )
        print(
            "   📊 Context size is cumulative and grows with each interaction\n",
            file=sys.stderr,
        )

    elif message_count > MAX_MESSAGES:
        # Show periodic reminders every 5 messages after limit
        if (message_count - MAX_MESSAGES) % 5 == 0:
            warn(
                f"High context: {message_count} messages (recommended: {MAX_MESSAGES})",
                "CRITICAL",
            )
            print(
                "   💸 API costs are likely 3-5× normal due to large context\n",
                file=sys.stderr,
            )


def check_large_file_read(tool_name: str, result: str, file_path: str | None = None):
    """Check if a large file was read and warn"""
    if tool_name != "Read":
        return

    tokens = estimate_tokens(result)

    if tokens > LARGE_FILE_THRESHOLD:
        large_reads = increment_counter("large_files")

        file_info = f" ({file_path})" if file_path else ""
        warn(f"Large file read: ~{tokens:,} tokens{file_info}")
        print(
            "   📄 This file will be in context for ALL future API calls in this session",
            file=sys.stderr,
        )
        print(
            f"   📊 Large reads so far: {large_reads}/{MAX_LARGE_FILE_READS}",
            file=sys.stderr,
        )

        if large_reads >= MAX_LARGE_FILE_READS:
            print(
                f"   💸 COST ALERT: {large_reads} large files in context!",
                file=sys.stderr,
            )
            print(
                "   💡 Consider starting fresh session to reset context\n",
                file=sys.stderr,
            )
        else:
            print(
                "   💡 Tip: Use Grep to search instead of reading entire files\n",
                file=sys.stderr,
            )


def check_total_context():
    """Estimate and warn about total context size"""
    message_count = get_counter("messages")
    large_file_count = get_counter("large_files")

    # Rough estimate:
    # - Base system prompt: ~15K tokens
    # - Average message: ~2K tokens
    # - Large files: ~30K tokens each
    estimated_context = 15000 + (message_count * 2000) + (large_file_count * 30000)

    if estimated_context > 100000:  # 100K tokens
        warn(f"Estimated context size: ~{estimated_context:,} tokens", "CRITICAL")
        print(
            f"   💰 Each API call costs ~${estimated_context * 3 / 1000000:.3f} in input tokens alone",
            file=sys.stderr,
        )
        print("   📊 Context breakdown:", file=sys.stderr)
        print(
            f"      - Messages: {message_count} × ~2K = ~{message_count * 2000:,} tokens",
            file=sys.stderr,
        )
        print(
            f"      - Large files: {large_file_count} × ~30K = ~{large_file_count * 30000:,} tokens",
            file=sys.stderr,
        )
        print("   🔄 STRONGLY RECOMMEND: Exit and start fresh session\n", file=sys.stderr)


def main():
    """Hook entry point - reads event from stdin, checks context"""
    try:
        # Read event data from stdin
        event_data = json.load(sys.stdin)

        tool_name = event_data.get("tool_name", "")
        result = event_data.get("result", "")

        # Track message count on every tool use
        check_message_count()

        # Check for large file reads
        if tool_name == "Read":
            # Try to extract file path from tool parameters
            params = event_data.get("parameters", {})
            file_path = params.get("file_path")
            check_large_file_read(tool_name, result, file_path)

        # Check total context size periodically (every 5 messages)
        if get_counter("messages") % 5 == 0:
            check_total_context()

    except Exception as e:
        # Silent failure - don't disrupt Claude's operation
        # But log to a debug file for troubleshooting
        debug_log = SESSION_DIR / "context_warning_errors.log"
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        with open(debug_log, "a") as f:
            f.write(f"Error in context_warning hook: {e}\n")


if __name__ == "__main__":
    main()
