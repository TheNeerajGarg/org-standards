#!/usr/bin/env python3
"""
SessionEnd Hook - Generate introspection at session end

This hook runs when a Claude Code session ends.
If patterns were detected, it generates an introspection document.

Installation:
Add to ~/.claude/settings.json:
{
  "hooks": {
    "SessionEnd": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 /Users/neerajgarg/syra/introspection/hooks/session_end.py"
      }]
    }]
  }
}
"""

import logging
import sys
from pathlib import Path

from introspection.core.failure_tracker import FailureTracker
from introspection.core.introspection_generator import IntrospectionGenerator

logger = logging.getLogger(__name__)


def main():
    """Hook entry point - generate introspection if alerts exist."""
    try:
        logger.debug("SessionEnd hook started")

        tracker = FailureTracker()

        logger.debug(
            "Checking for pending alerts",
            extra={"session_id": tracker.session.session_id},
        )
        # Check for pending alerts
        alerts = tracker.get_pending_alerts()

        if not alerts:
            logger.debug("No pending alerts, skipping introspection generation")
            # No patterns detected, nothing to do
            return

        logger.info(
            "Pending alerts found, generating introspection",
            extra={
                "alert_count": len(alerts),
                "session_id": tracker.session.session_id,
            },
        )

        # Generate introspection document
        generator = IntrospectionGenerator()
        session_id = tracker.session.session_id

        introspection_md = generator.generate(alerts, session_id)

        # Save to current repository's .ai-sessions/
        repo_path = Path.cwd()
        output_file = generator.save_to_repo(introspection_md, repo_path, session_id)

        logger.info(
            "Introspection document created", extra={"output_file": str(output_file)}
        )

        print(f"✅ Created self-introspection: {output_file}", file=sys.stderr)
        print(
            f"🚨 ATTENTION: Repeated failures detected in session {session_id}!",
            file=sys.stderr,
        )
        print(f"📝 Review: {output_file}", file=sys.stderr)

        # Clear alerts after processing
        tracker.clear_alerts()
        logger.debug("Alerts cleared")

    except Exception as e:
        # Silent failure - don't disrupt Claude's operation
        logger.error("SessionEnd hook error", exc_info=True)
        print(f"Warning: Introspection hook error: {e}", file=sys.stderr)
        pass


if __name__ == "__main__":
    main()
