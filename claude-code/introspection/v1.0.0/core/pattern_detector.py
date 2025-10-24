#!/usr/bin/env python3
"""
Pattern Detector - Cross-session pattern analysis

Analyzes failure patterns across multiple sessions to identify
recurring issues and trends.

Author: Syra Introspection System
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects patterns across multiple Claude Code sessions.
    Analyzes archived session data to identify trends.
    """

    def __init__(self, tracker_base: Path | None = None):
        if tracker_base is None:
            tracker_base = Path.home() / ".claude" / "failure-tracker"
        self.tracker_base = tracker_base
        self.sessions_dir = self.tracker_base / "sessions"
        self.archive_dir = self.tracker_base / "archive"

    def analyze_recent(self, days: int = 7) -> dict[str, Any]:
        """
        Analyze patterns from recent sessions.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary containing pattern analysis
        """
        logger.info("Starting pattern analysis", extra={"days": days})

        cutoff = datetime.now().timestamp() - (days * 86400)
        all_failures = []

        # Collect failures from active sessions
        if self.sessions_dir.exists():
            logger.debug(
                "Analyzing active sessions",
                extra={"sessions_dir": str(self.sessions_dir)},
            )
            for session_dir in self.sessions_dir.iterdir():
                if not session_dir.is_dir():
                    continue

                failures = self._read_session_failures(session_dir, cutoff)
                all_failures.extend(failures)
                logger.debug(
                    "Read failures from session",
                    extra={
                        "session_id": session_dir.name,
                        "failure_count": len(failures),
                    },
                )

        # Collect failures from recent archives
        if self.archive_dir.exists():
            logger.debug(
                "Analyzing archived sessions",
                extra={"archive_dir": str(self.archive_dir)},
            )
            for date_dir in self.archive_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                for session_dir in date_dir.iterdir():
                    if not session_dir.is_dir():
                        continue

                    failures = self._read_session_failures(session_dir, cutoff)
                    all_failures.extend(failures)

        if not all_failures:
            logger.info("No failures found in analysis period", extra={"days": days})
            return {
                "period": f"Last {days} days",
                "total_failures": 0,
                "patterns": [],
                "summary": "No failures in this period",
            }

        # Analyze patterns
        logger.info(
            "Analyzing patterns from failures",
            extra={
                "total_failures": len(all_failures),
                "total_sessions": len({f["session_id"] for f in all_failures}),
            },
        )
        patterns = self._detect_patterns(all_failures)

        result = {
            "period": f"Last {days} days",
            "total_failures": len(all_failures),
            "total_sessions": len({f["session_id"] for f in all_failures}),
            "patterns": patterns,
            "summary": self._generate_summary(patterns),
        }

        logger.info(
            "Pattern analysis complete",
            extra={
                "total_failures": len(all_failures),
                "patterns_detected": len(patterns),
                "summary": result["summary"],
            },
        )

        return result

    def _read_session_failures(
        self, session_dir: Path, cutoff_timestamp: float
    ) -> list[dict]:
        """Read failures from a session directory."""
        failures: list[dict] = []
        failure_log = session_dir / "failures.jsonl"

        if not failure_log.exists():
            return failures

        try:
            with open(failure_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(
                            record["timestamp"]
                        ).timestamp()

                        if timestamp >= cutoff_timestamp:
                            failures.append(record)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except OSError:
            pass

        return failures

    def _detect_patterns(self, failures: list[dict]) -> list[dict]:
        """
        Detect recurring patterns in failures.

        Returns:
            List of pattern dictionaries
        """
        logger.debug(
            "Detecting patterns in failures", extra={"failure_count": len(failures)}
        )
        patterns = []

        # Pattern 1: Recurring error types
        by_error_type = defaultdict(list)
        for failure in failures:
            by_error_type[failure["error_type"]].append(failure)

        for error_type, error_failures in by_error_type.items():
            if len(error_failures) >= 3:  # At least 3 occurrences
                sessions = {f["session_id"] for f in error_failures}
                pattern = {
                    "type": "recurring_error_type",
                    "error_type": error_type,
                    "occurrences": len(error_failures),
                    "affected_sessions": len(sessions),
                    "severity": self._calculate_severity(
                        len(error_failures), len(sessions)
                    ),
                    "first_seen": error_failures[0]["timestamp"],
                    "last_seen": error_failures[-1]["timestamp"],
                    "sample_message": error_failures[-1]["error_message"],
                }
                patterns.append(pattern)
                logger.info(
                    "Detected recurring error pattern",
                    extra={
                        "error_type": error_type,
                        "occurrences": len(error_failures),
                        "affected_sessions": len(sessions),
                        "severity": pattern["severity"],
                    },
                )

        # Pattern 2: Same tool failing repeatedly across sessions
        by_tool = defaultdict(list)
        for failure in failures:
            by_tool[failure["tool_name"]].append(failure)

        for tool_name, tool_failures in by_tool.items():
            if len(tool_failures) >= 5:  # At least 5 occurrences
                sessions = {f["session_id"] for f in tool_failures}
                if len(sessions) >= 2:  # Affects multiple sessions
                    patterns.append(
                        {
                            "type": "problematic_tool",
                            "tool_name": tool_name,
                            "occurrences": len(tool_failures),
                            "affected_sessions": len(sessions),
                            "severity": self._calculate_severity(
                                len(tool_failures), len(sessions)
                            ),
                            "common_errors": self._get_common_errors(
                                tool_failures, top=3
                            ),
                        }
                    )

        # Pattern 3: Host-specific issues
        by_host = defaultdict(list)
        for failure in failures:
            hostname = failure.get("hostname", "unknown")
            by_host[hostname].append(failure)

        for hostname, host_failures in by_host.items():
            if len(host_failures) >= 10:  # Significant failures on one host
                total_sessions = len({f["session_id"] for f in failures})
                host_sessions = len({f["session_id"] for f in host_failures})

                if host_sessions / total_sessions > 0.5:  # >50% on this host
                    patterns.append(
                        {
                            "type": "host_specific_issue",
                            "hostname": hostname,
                            "occurrences": len(host_failures),
                            "affected_sessions": host_sessions,
                            "severity": "HIGH",
                            "common_errors": self._get_common_errors(
                                host_failures, top=3
                            ),
                        }
                    )

        # Sort by severity
        patterns.sort(
            key=lambda p: (
                {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(
                    p.get("severity", "LOW"), 3
                ),
                -p.get("occurrences", 0),
            )
        )

        return patterns

    def _calculate_severity(self, occurrences: int, sessions: int) -> str:
        """Calculate severity based on frequency and spread."""
        # High frequency + multi-session = critical
        if occurrences >= 10 and sessions >= 3:
            return "CRITICAL"
        elif occurrences >= 5 and sessions >= 2:
            return "HIGH"
        elif occurrences >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_common_errors(
        self, failures: list[dict], top: int = 3
    ) -> list[tuple[str, int]]:
        """Get most common error types from failures."""
        error_types = [f["error_type"] for f in failures]
        counter = Counter(error_types)
        return counter.most_common(top)

    def _generate_summary(self, patterns: list[dict]) -> str:
        """Generate human-readable summary of patterns."""
        if not patterns:
            return "No significant patterns detected"

        critical = len([p for p in patterns if p.get("severity") == "CRITICAL"])
        high = len([p for p in patterns if p.get("severity") == "HIGH"])
        medium = len([p for p in patterns if p.get("severity") == "MEDIUM"])

        summary_parts = []

        if critical > 0:
            summary_parts.append(f"{critical} CRITICAL pattern(s)")
        if high > 0:
            summary_parts.append(f"{high} HIGH severity pattern(s)")
        if medium > 0:
            summary_parts.append(f"{medium} MEDIUM severity pattern(s)")

        return f"Found: {', '.join(summary_parts)}"

    def get_session_details(self, session_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific session.

        Args:
            session_id: Session ID to query

        Returns:
            Dictionary containing session details
        """
        # Check active sessions
        session_dir = self.sessions_dir / session_id

        if not session_dir.exists():
            # Check archives
            for date_dir in self.archive_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                archived_session = date_dir / session_id
                if archived_session.exists():
                    session_dir = archived_session
                    break

        if not session_dir.exists():
            return {"error": f"Session {session_id} not found"}

        # Read session info
        session_info = {}
        info_file = session_dir / "session-info.json"
        if info_file.exists():
            try:
                with open(info_file) as f:
                    session_info = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass

        # Read failures
        failures = self._read_session_failures(session_dir, 0)

        # Read alerts
        alerts = []
        alert_file = session_dir / "alerts.json"
        if alert_file.exists():
            try:
                with open(alert_file) as f:
                    alert_data = json.load(f)
                    alerts = alert_data.get("alerts", [])
            except (OSError, json.JSONDecodeError):
                pass

        return {
            "session_id": session_id,
            "session_info": session_info,
            "total_failures": len(failures),
            "failures_by_type": Counter(f["error_type"] for f in failures),
            "alerts": alerts,
            "failures": failures,
        }

    def compare_sessions(self, session_id1: str, session_id2: str) -> dict[str, Any]:
        """
        Compare two sessions to identify differences.

        Args:
            session_id1: First session ID
            session_id2: Second session ID

        Returns:
            Comparison analysis
        """
        session1 = self.get_session_details(session_id1)
        session2 = self.get_session_details(session_id2)

        if "error" in session1 or "error" in session2:
            return {
                "error": "One or both sessions not found",
                "session1": session1,
                "session2": session2,
            }

        return {
            "session1_id": session_id1,
            "session2_id": session_id2,
            "failure_count": {
                "session1": session1["total_failures"],
                "session2": session2["total_failures"],
                "difference": session1["total_failures"] - session2["total_failures"],
            },
            "common_errors": set(session1["failures_by_type"].keys())
            & set(session2["failures_by_type"].keys()),
            "unique_to_session1": set(session1["failures_by_type"].keys())
            - set(session2["failures_by_type"].keys()),
            "unique_to_session2": set(session2["failures_by_type"].keys())
            - set(session1["failures_by_type"].keys()),
        }
