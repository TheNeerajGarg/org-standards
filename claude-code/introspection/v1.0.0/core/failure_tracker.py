#!/usr/bin/env python3
"""
Concurrency-Safe, Multi-Host Safe Failure Tracker

Uses GUID for session isolation across containers/hosts.
Thread-safe and multi-host safe using atomic operations and file locking.

Author: Syra Introspection System
"""

import atexit
import fcntl
import json
import logging
import os
import socket
import sys
import tempfile
import threading
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Configuration
TRACKER_BASE = Path.home() / ".claude" / "failure-tracker"
PATTERN_THRESHOLD = 2

# Track temp files globally for cleanup on crash
_temp_files: list[str] = []

# Cache boot time to prevent session fragmentation
_BOOT_TIME_CACHE: float | None = None
_BOOT_TIME_CACHE_LOCK = threading.Lock()


def _cleanup_temp_file(temp_path: str):
    """
    Best-effort cleanup of temp file.
    Logs failure but doesn't raise.
    """
    try:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Cleaned up temp file: {temp_path}")
    except OSError as e:
        # Log but don't raise - we're already handling an error
        logger.warning(
            "Could not clean up temp file",
            extra={"temp_path": temp_path, "error": str(e), "error_type": type(e).__name__},
        )


@atexit.register
def _cleanup_all_temp_files():
    """Clean up any remaining temp files on process exit."""
    for temp_path in _temp_files[:]:  # Copy list to avoid modification during iteration
        _cleanup_temp_file(temp_path)


def _get_boot_time() -> float:
    """
    Get system boot time as Unix timestamp with caching.
    Used to detect container restarts and prevent PID reuse collisions.

    Caches boot time for process lifetime to prevent session fragmentation
    on platforms where boot time detection fails (macOS, Windows).

    Returns:
        Unix timestamp of system boot time (or process start time if unavailable)

    Priority:
        1. /proc/uptime (Linux containers, most accurate)
        2. psutil.boot_time() (cross-platform, if available)
        3. psutil.Process().create_time() (fallback - process start time)
        4. Current time CACHED (last resort - prevents fragmentation)
    """
    global _BOOT_TIME_CACHE

    # Return cached value if available
    if _BOOT_TIME_CACHE is not None:
        return _BOOT_TIME_CACHE

    with _BOOT_TIME_CACHE_LOCK:
        # Double-check after acquiring lock
        if _BOOT_TIME_CACHE is not None:
            return _BOOT_TIME_CACHE

        # Method 1: /proc/uptime (Linux)
        try:
            proc_uptime = Path("/proc/uptime")
            if proc_uptime.exists():
                with open(proc_uptime) as f:
                    uptime_seconds = float(f.read().split()[0])
                    boot_time = time.time() - uptime_seconds
                    logger.debug(f"Boot time from /proc/uptime: {boot_time}")
                    _BOOT_TIME_CACHE = boot_time
                    return boot_time
        except (OSError, ValueError, IndexError) as e:
            logger.debug(f"Could not read /proc/uptime: {e}")

        # Method 2: psutil.boot_time() (cross-platform)
        try:
            import psutil

            boot_time = psutil.boot_time()
            logger.debug(f"Boot time from psutil: {boot_time}")
            _BOOT_TIME_CACHE = boot_time
            return boot_time
        except ImportError:
            logger.debug("psutil not available")
        except Exception as e:
            logger.debug(f"Could not get boot time from psutil: {e}")

        # Method 3: psutil.Process().create_time() (fallback - process start time)
        try:
            import psutil

            process = psutil.Process(os.getpid())
            process_start_time = process.create_time()
            logger.warning(
                "Could not determine boot time, using process start time. "
                "Session will be per-process (won't persist across hook restarts)."
            )
            _BOOT_TIME_CACHE = process_start_time
            return process_start_time
        except (ImportError, Exception) as e:
            logger.debug(f"Could not get process start time: {e}")

        # Last resort: Use current time but CACHE IT to prevent fragmentation
        logger.warning(
            "Could not determine boot time or process start time. "
            "Using current time (CACHED). Session will be per-Python-process."
        )
        _BOOT_TIME_CACHE = time.time()
        return _BOOT_TIME_CACHE


class SessionManager:
    """
    Manages session isolation with GUID-based session IDs.
    Safe for multiple hosts, containers, and parallel sessions.
    """

    def __init__(self):
        self.session_id = self._get_or_create_session_id()
        self.session_dir = TRACKER_BASE / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def _get_or_create_session_id(self) -> str:
        """
        Get or create GUID-based session ID.
        Uses boot time to prevent PID reuse after container restart.

        Priority:
        1. Environment variable (set by Claude Code or user)
        2. Create new GUID + persist for this process

        Format: session-{guid}
        Example: session-a3f2d8e1-4b5c-6d7e-8f9a-0b1c2d3e4f5a
        """
        # Priority 1: Environment variable
        session_id = os.environ.get("CLAUDE_SESSION_ID")
        if session_id:
            logger.info("Using session ID from environment", extra={"session_id": session_id})
            return session_id

        # Priority 2: Atomic check-and-create with file lock
        boot_time_int = int(_get_boot_time())  # Unix timestamp as int
        ppid = os.getppid()

        # Include boot time in filename: claude-session-{boot_time}-{ppid}.txt
        # This ensures different file after container restart even with same PID
        session_file = Path("/tmp") / f"claude-session-{boot_time_int}-{ppid}.txt"
        session_file.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "Checking session file",
            extra={
                "session_file": str(session_file),
                "boot_time": boot_time_int,
                "ppid": ppid,
            },
        )

        # Use file lock for atomic check-and-create
        lock_file = session_file.with_suffix(".lock")
        lock_file.touch(exist_ok=True)

        try:
            with open(lock_file, "r+") as lock_fd:
                # Acquire exclusive lock (blocks other processes)
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)

                try:
                    # Double-check: session file might have been created while waiting for lock
                    if session_file.exists():
                        with open(session_file) as f:
                            existing_id = f.read().strip()
                            if existing_id:
                                logger.info(
                                    "Reusing existing session ID",
                                    extra={
                                        "session_id": existing_id,
                                        "session_file": str(session_file),
                                    },
                                )
                                return existing_id

                    # Create new GUID-based session ID
                    guid = str(uuid.uuid4())
                    session_id = f"session-{guid}"

                    # Write atomically
                    with open(session_file, "w") as f:
                        f.write(session_id)
                        f.flush()
                        os.fsync(f.fileno())

                    logger.info(
                        "Created new session ID",
                        extra={
                            "session_id": session_id,
                            "hostname": socket.gethostname(),
                            "pid": os.getpid(),
                            "ppid": ppid,
                            "boot_time": boot_time_int,
                        },
                    )
                    return session_id

                finally:
                    # Release lock
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)

        except OSError as e:
            # Fallback: if locking fails, create session ID without persistence
            logger.warning(
                "Could not acquire session lock, creating ephemeral session",
                extra={"error": str(e)},
            )
            guid = str(uuid.uuid4())
            return f"session-{guid}"

    def get_session_dir(self) -> Path:
        """Get this session's isolated directory."""
        return self.session_dir

    def write_session_info(self):
        """Write session metadata with host information."""
        info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "hostname": socket.gethostname(),
            "working_dir": os.getcwd(),
            "user": os.environ.get("USER", "unknown"),
            "container_id": os.environ.get("HOSTNAME", socket.gethostname()),
        }

        info_file = self.session_dir / "session-info.json"

        # Only write if doesn't exist (first hook invocation)
        if not info_file.exists():
            with atomic_write(info_file) as f:
                json.dump(info, f, indent=2)


@contextmanager
def atomic_write(filepath: Path):
    """
    Atomic write using temp file + rename with cleanup tracking.
    Prevents partial writes and corruption.
    Works correctly on shared filesystems (NFS, etc.).

    Registers temp files for cleanup on abnormal exit to prevent disk space leaks.
    """
    # Write to temp file in same directory (same filesystem)
    temp_fd, temp_path = tempfile.mkstemp(dir=filepath.parent, prefix=f".{filepath.name}.tmp.", suffix=".tmp")

    # Register for cleanup on abnormal exit
    _temp_files.append(temp_path)

    logger.debug("Starting atomic write", extra={"filepath": str(filepath), "temp_path": temp_path})

    success = False
    try:
        with os.fdopen(temp_fd, "w") as f:
            yield f
            # Explicit flush before rename
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename (POSIX guarantees atomicity on same filesystem)
        os.rename(temp_path, filepath)
        success = True
        logger.debug("Completed atomic write", extra={"filepath": str(filepath)})

    except Exception as e:
        # Clean up temp file on error
        logger.error(
            "Atomic write failed",
            extra={
                "filepath": str(filepath),
                "temp_path": temp_path,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise
    finally:
        # Always attempt cleanup if write failed
        if not success:
            _cleanup_temp_file(temp_path)

        # Remove from tracking list
        try:
            _temp_files.remove(temp_path)
        except ValueError:
            pass  # Already removed


@contextmanager
def file_lock(filepath: Path, timeout: float = 5.0, stale_threshold: float = 300.0):
    """
    Advisory file lock with stale lock detection.
    Uses flock (works across processes and hosts on NFS v3+).

    Args:
        filepath: File to lock
        timeout: How long to wait for lock (seconds)
        stale_threshold: Consider lock stale if older than this (seconds, default 5 min)

    Stale Lock Detection:
        If a process crashes while holding a lock, the lock file remains forever.
        This function detects stale locks by checking file modification time (mtime).
        If lock is held for > stale_threshold seconds, it's removed and retried.

    Note: On NFS, requires lockd daemon running.
    Falls back gracefully if locking not available.
    """
    lock_file = filepath.parent / f".{filepath.name}.lock"
    lock_file.touch(exist_ok=True)

    logger.debug("Attempting to acquire file lock", extra={"filepath": str(filepath), "timeout": timeout})

    try:
        fd = os.open(str(lock_file), os.O_RDWR)
    except OSError as e:
        # If can't open lock file, proceed without locking
        import warnings

        logger.warning(
            "Could not open lock file, proceeding without lock",
            extra={"lock_file": str(lock_file), "error": str(e)},
        )
        warnings.warn(f"Could not open lock file {lock_file}: {e}", stacklevel=2)
        yield
        return

    try:
        # Try to acquire lock with timeout and stale detection
        import time

        start = time.time()

        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Acquired lock - update mtime to mark as active
                lock_file.touch()
                logger.debug("Lock acquired", extra={"filepath": str(filepath), "lock_file": str(lock_file)})
                break

            except BlockingIOError as e:
                elapsed = time.time() - start

                # Check if lock is stale
                lock_age = None
                try:
                    lock_stat = lock_file.stat()
                    lock_age = time.time() - lock_stat.st_mtime

                    if lock_age > stale_threshold:
                        # Lock is potentially stale - log warning
                        logger.warning(
                            "Detected potentially stale lock",
                            extra={
                                "lock_file": str(lock_file),
                                "lock_age_seconds": lock_age,
                                "threshold": stale_threshold,
                            },
                        )

                        # Try to acquire with LOCK_NB - if it succeeds, holder released it
                        # This is SAFE: we don't remove the lock, we just try to acquire it
                        try:
                            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            # Success! Lock was released, we got it
                            lock_file.touch()
                            logger.debug(
                                "Lock acquired after detecting staleness (holder released it)",
                                extra={"lock_file": str(lock_file)},
                            )
                            break
                        except BlockingIOError:
                            # Still held - it's stale, but we can't safely force it
                            # Log error and continue waiting for timeout
                            logger.error(
                                "Lock is stale but still held - possible crashed process",
                                extra={"lock_file": str(lock_file), "lock_age": lock_age},
                            )
                            # Continue waiting - will hit overall timeout if truly stuck

                except OSError:
                    pass  # Ignore stat errors

                # Check overall timeout
                if elapsed > timeout:
                    logger.error(
                        "Lock acquisition timeout",
                        extra={
                            "lock_file": str(lock_file),
                            "timeout": timeout,
                            "lock_age": lock_age,
                        },
                    )
                    raise TimeoutError(f"Could not acquire lock on {filepath} after {timeout}s") from e

                time.sleep(0.01)

        yield

    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            logger.debug("Lock released", extra={"filepath": str(filepath)})
        except OSError:
            pass
        try:
            os.close(fd)
        except OSError:
            pass


class FailureTracker:
    """
    GUID-based session-isolated failure tracker.
    Safe for:
    - 10+ parallel Claude sessions
    - Multiple containers/hosts
    - Shared filesystems (NFS, CIFS, etc.)
    """

    def __init__(self):
        self.session = SessionManager()
        self.session_dir = self.session.get_session_dir()

        self.failure_log = self.session_dir / "failures.jsonl"
        self.alert_file = self.session_dir / "alerts.json"

        # Ensure session info written once
        session_info = self.session_dir / "session-info.json"
        if not session_info.exists():
            self.session.write_session_info()

    def log_failure(self, event_data: dict[str, Any]):
        """
        Log failure to this session's isolated file.
        Thread-safe and multi-host safe using GUID + file locking.
        Falls back to emergency log if permissions denied.
        """
        failure_record = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session.session_id,
            "hostname": socket.gethostname(),
            "tool_name": event_data.get("tool_name", "unknown"),
            "error_type": self._extract_error_type(event_data),
            "error_message": self._extract_error_message(event_data),
            "tool_input": event_data.get("tool_input", {}),
            "exit_code": event_data.get("exit_code"),
        }

        logger.debug(
            "Recording failure",
            extra={
                "session_id": self.session.session_id,
                "error_type": failure_record["error_type"],
                "tool_name": failure_record["tool_name"],
            },
        )

        # Use file lock for safe concurrent append
        try:
            with file_lock(self.failure_log):
                with open(self.failure_log, "a") as f:
                    f.write(json.dumps(failure_record) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                logger.debug(
                    "Failure logged successfully",
                    extra={
                        "session_id": self.session.session_id,
                        "failure_log": str(self.failure_log),
                    },
                )
        except PermissionError as e:
            # Permission denied - fallback to emergency log in /tmp
            emergency_log = Path(f"/tmp/failures-emergency-{self.session.session_id}.jsonl")

            logger.warning(
                "Permission denied on failure log - using emergency log",
                extra={
                    "session_id": self.session.session_id,
                    "failure_log": str(self.failure_log),
                    "emergency_log": str(emergency_log),
                    "error": str(e),
                },
            )

            try:
                # Write to emergency log in /tmp (usually writable)
                with open(emergency_log, "a") as f:
                    f.write(json.dumps(failure_record) + "\n")
                    f.write("# WARNING: Written to emergency log due to permission error\n")
                    f.flush()
                logger.info(
                    "Failure written to emergency log",
                    extra={"emergency_log": str(emergency_log)},
                )
            except Exception as e2:
                logger.error(
                    "Could not write to emergency log",
                    extra={"emergency_log": str(emergency_log), "error": str(e2)},
                )
                # Re-raise original permission error
                raise RuntimeError(
                    f"Could not log failure due to permissions. Check {emergency_log} for recovery."
                ) from e
        except TimeoutError as e:
            # Lock timeout - DO NOT write without lock to avoid corruption
            # Write to emergency backup log instead (for manual recovery)
            emergency_log = self.session_dir / "failures-emergency.jsonl"

            logger.error(
                "Lock acquisition timeout - failure written to emergency log",
                extra={
                    "session_id": self.session.session_id,
                    "failure_log": str(self.failure_log),
                    "emergency_log": str(emergency_log),
                    "timeout": 5.0,
                    "error_type": failure_record["error_type"],
                },
            )

            try:
                # Write to emergency log with warning comment
                with open(emergency_log, "a") as f:
                    f.write(json.dumps(failure_record) + "\n")
                    f.write("# WARNING: Written without lock due to timeout\n")
                    f.flush()
                logger.warning(
                    "Failure written to emergency log (needs manual recovery)",
                    extra={"emergency_log": str(emergency_log)},
                )
            except Exception as e2:
                logger.error(
                    "Could not write to emergency log",
                    extra={"emergency_log": str(emergency_log), "error": str(e2)},
                )
                # Re-raise original timeout error
                raise RuntimeError(
                    f"Could not log failure due to lock timeout. Check {emergency_log} for recovery."
                ) from e

    def _extract_error_type(self, event_data: dict) -> str:
        """Classify error type from tool output."""
        stderr = event_data.get("stderr", "")
        stdout = event_data.get("stdout", "")
        combined = stderr + stdout

        # Pattern matching for common errors
        error_patterns = [
            ("module_not_found", ["ModuleNotFoundError", "No module named"]),
            ("file_not_found", ["FileNotFoundError", "No such file"]),
            ("permission_denied", ["PermissionError", "Permission denied"]),
            ("syntax_error", ["SyntaxError"]),
            ("type_error", ["TypeError"]),
            ("pre_commit_failed", ["pre-commit", "failed"]),
            ("type_check_failed", ["mypy", "error"]),
            ("linting_failed", ["ruff"]),
            ("import_error", ["ImportError", "cannot import"]),
            ("test_failed", ["FAILED", "ERROR", "test"]),
            ("no_verify_used", ["--no-verify"]),  # Track forbidden pattern
        ]

        for error_type, patterns in error_patterns:
            if any(pattern in combined for pattern in patterns):
                return error_type

        if event_data.get("exit_code", 0) != 0:
            return "command_failed"

        return "unknown_error"

    def _extract_error_message(self, event_data: dict) -> str:
        """Extract concise error message."""
        stderr = event_data.get("stderr", "")
        stdout = event_data.get("stdout", "")

        # Try stderr first
        if stderr:
            lines = [line.strip() for line in stderr.split("\n") if line.strip()]
            if lines:
                return lines[0][:200]

        # Fall back to stdout
        if stdout:
            lines = [line.strip() for line in stdout.split("\n") if line.strip()]
            if lines:
                return lines[0][:200]

        return "No error message"

    def analyze_patterns(self, lookback_hours: int = 1) -> list[dict]:
        """
        Analyze THIS SESSION's failures for patterns.
        GUID ensures no cross-session contamination.
        """
        if not self.failure_log.exists():
            return []

        cutoff_time = datetime.now().timestamp() - (lookback_hours * 3600)
        recent_failures = []

        # Read with lock (safe concurrent read)
        try:
            with file_lock(self.failure_log):
                with open(self.failure_log) as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            timestamp = datetime.fromisoformat(record["timestamp"]).timestamp()
                            if timestamp >= cutoff_time:
                                recent_failures.append(record)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        except TimeoutError:
            # If can't acquire lock, read anyway (read-only is safer)
            with open(self.failure_log) as f:
                for line in f:
                    try:
                        record = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(record["timestamp"]).timestamp()
                        if timestamp >= cutoff_time:
                            recent_failures.append(record)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

        if not recent_failures:
            return []

        # Detect patterns
        alerts = []

        # Group by error type
        by_error_type = defaultdict(list)
        for failure in recent_failures:
            by_error_type[failure["error_type"]].append(failure)

        # Check for recurring patterns
        for error_type, failures in by_error_type.items():
            if len(failures) >= PATTERN_THRESHOLD:
                alerts.append(
                    {
                        "pattern_type": "recurring_error",
                        "error_type": error_type,
                        "occurrences": len(failures),
                        "first_occurrence": failures[0]["timestamp"],
                        "last_occurrence": failures[-1]["timestamp"],
                        "sample_message": failures[-1]["error_message"],
                        "tool_name": failures[-1]["tool_name"],
                        "session_id": self.session.session_id,
                        "hostname": failures[-1].get("hostname", "unknown"),
                    }
                )

        # Check for same command failing repeatedly
        by_command = defaultdict(list)
        for failure in recent_failures:
            tool_input = failure.get("tool_input", {})
            if "command" in tool_input:
                command = tool_input["command"][:100]
                by_command[command].append(failure)

        for command, failures in by_command.items():
            if len(failures) >= PATTERN_THRESHOLD:
                alerts.append(
                    {
                        "pattern_type": "command_repeated_failure",
                        "command": command,
                        "occurrences": len(failures),
                        "first_occurrence": failures[0]["timestamp"],
                        "last_occurrence": failures[-1]["timestamp"],
                        "sample_message": failures[-1]["error_message"],
                        "session_id": self.session.session_id,
                        "hostname": failures[-1].get("hostname", "unknown"),
                    }
                )

        return alerts

    def save_alerts(self, alerts: list[dict]):
        """Save alerts with atomic write (multi-host safe)."""
        if alerts:
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session.session_id,
                "hostname": socket.gethostname(),
                "alerts": alerts,
            }

            # Atomic write (safe even on NFS)
            with atomic_write(self.alert_file) as f:
                json.dump(alert_data, f, indent=2)

    def get_pending_alerts(self) -> list[dict]:
        """Get THIS SESSION's alerts (GUID-isolated)."""
        if not self.alert_file.exists():
            return []

        try:
            with file_lock(self.alert_file):
                with open(self.alert_file) as f:
                    data = json.load(f)
                    return data.get("alerts", [])
        except (json.JSONDecodeError, KeyError, FileNotFoundError, TimeoutError):
            return []

    def clear_alerts(self):
        """Clear alerts after introspection generated."""
        if self.alert_file.exists():
            try:
                self.alert_file.unlink()
            except OSError:
                pass

    def cleanup_old_sessions(self, days: int = 7) -> int:
        """
        Archive sessions older than N days.
        Safe to run from any session.
        NEVER deletes - only archives.

        Returns:
            Number of sessions archived
        """
        sessions_dir = TRACKER_BASE / "sessions"
        archive_dir = TRACKER_BASE / "archive"

        logger.info("Starting session cleanup", extra={"days": days, "sessions_dir": str(sessions_dir)})

        if not sessions_dir.exists():
            logger.debug("Sessions directory does not exist, nothing to cleanup")
            return 0

        cutoff = datetime.now().timestamp() - (days * 86400)
        archived_count = 0

        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue

            # Check session age
            session_info = session_dir / "session-info.json"
            if session_info.exists():
                try:
                    with open(session_info) as f:
                        info = json.load(f)
                        start_time = datetime.fromisoformat(info["start_time"]).timestamp()

                        if start_time < cutoff:
                            # Archive to date-based directory
                            date_str = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
                            dest = archive_dir / date_str / session_dir.name
                            dest.parent.mkdir(parents=True, exist_ok=True)

                            # Move to archive (NOT delete)
                            import shutil

                            shutil.move(str(session_dir), str(dest))
                            archived_count += 1
                            logger.info(
                                "Archived session",
                                extra={"session_id": session_dir.name, "archive_path": str(dest)},
                            )

                except (json.JSONDecodeError, KeyError, OSError) as e:
                    # Log error but continue
                    logger.error(
                        "Could not archive session",
                        extra={"session_dir": session_dir.name, "error": str(e)},
                        exc_info=True,
                    )
                    print(f"Warning: Could not archive {session_dir.name}: {e}", file=sys.stderr)
                    continue

        logger.info("Completed session cleanup", extra={"archived_count": archived_count})
        return archived_count


def main():
    """Entry point for hook scripts."""
    if len(sys.argv) < 2:
        print("Usage: failure_tracker.py <command>", file=sys.stderr)
        print("Commands: log, analyze, alerts, clear, cleanup, session-id", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "session-id":
        # Just print session ID (useful for debugging)
        session = SessionManager()
        print(session.session_id)
        sys.exit(0)

    tracker = FailureTracker()

    if command == "log":
        event_data = json.load(sys.stdin)
        exit_code = event_data.get("exit_code", 0)
        stderr = event_data.get("stderr", "")

        if exit_code != 0 or stderr:
            tracker.log_failure(event_data)

    elif command == "analyze":
        alerts = tracker.analyze_patterns(lookback_hours=1)
        if alerts:
            tracker.save_alerts(alerts)

    elif command == "alerts":
        alerts = tracker.get_pending_alerts()
        print(json.dumps(alerts, indent=2))

    elif command == "clear":
        tracker.clear_alerts()

    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        archived_count = tracker.cleanup_old_sessions(days=days)
        print(f"Archived {archived_count} sessions older than {days} days", file=sys.stderr)

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
