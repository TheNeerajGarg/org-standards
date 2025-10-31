#!/usr/bin/env python3
"""
Git Worktree Manager

Manages git worktrees across NeerajDev repositories (syra, StyleGuru, org-standards).
Ensures worktrees are created in the correct location for container/host access.

Usage:
    python worktree-manager.py list [repo]
    python worktree-manager.py create <repo> <branch>
    python worktree-manager.py remove <path>
    python worktree-manager.py goto <worktree-name>
    python worktree-manager.py info

Examples:
    python worktree-manager.py list syra
    python worktree-manager.py create syra feature-branch
    python worktree-manager.py goto syra-main

Exit codes:
    0 - Success
    1 - Error (invalid args, worktree not found, etc.)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional


class Color:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


class WorktreeManager:
    """Manages git worktrees for NeerajDev repositories.

    Note: /workspace works on both Mac host (symlink to ~/NeerajDev) and container
    (mount of ~/NeerajDev), so we always use /workspace paths.
    """

    # Use /workspace which works on both Mac and container
    WORKSPACE_ROOT = Path("/workspace")
    WORKTREES_DIR = WORKSPACE_ROOT / ".worktrees"
    REPOS = ["syra", "StyleGuru", "org-standards"]

    def __init__(self) -> None:
        """Initialize the worktree manager."""
        self.validate_environment()

    def validate_environment(self) -> None:
        """Validate that /workspace directory exists."""
        if not self.WORKSPACE_ROOT.exists():
            self._error(f"/workspace directory not found at {self.WORKSPACE_ROOT}")
            self._error("Expected: /workspace symlink (Mac) or mount (container) to ~/NeerajDev")
            sys.exit(1)

        # Create .worktrees directory if it doesn't exist
        self.WORKTREES_DIR.mkdir(exist_ok=True)

    def _error(self, message: str) -> None:
        """Print error message."""
        print(f"{Color.RED}Error: {message}{Color.NC}", file=sys.stderr)

    def _success(self, message: str) -> None:
        """Print success message."""
        print(f"{Color.GREEN}{message}{Color.NC}")

    def _info(self, message: str) -> None:
        """Print info message."""
        print(f"{Color.BLUE}{message}{Color.NC}")

    def _warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Color.YELLOW}{message}{Color.NC}")

    def _run_git(self, repo_path: Path, args: list[str]) -> subprocess.CompletedProcess:
        """
        Run git command in specified repository.

        Args:
            repo_path: Path to repository
            args: Git command arguments

        Returns:
            CompletedProcess result
        """
        return subprocess.run(
            ["git"] + args, cwd=repo_path, capture_output=True, text=True
        )

    def _normalize_repo_name(self, repo: str) -> str:
        """
        Normalize repository name.

        Args:
            repo: Repository name (case-insensitive)

        Returns:
            Normalized repository name
        """
        repo_lower = repo.lower()
        if repo_lower in ["styleguru", "style-guru"]:
            return "StyleGuru"
        if repo_lower in ["syra"]:
            return "syra"
        if repo_lower in ["org-standards", "orgstandards"]:
            return "org-standards"
        return repo

    def _get_repo_path(self, repo: str) -> Optional[Path]:
        """
        Get repository path.

        Args:
            repo: Repository name

        Returns:
            Path to repository or None if not found
        """
        repo = self._normalize_repo_name(repo)
        repo_path = self.WORKSPACE_ROOT / repo

        if not repo_path.exists():
            self._error(f"Repository not found: {repo_path}")
            return None

        return repo_path

    def list_worktrees(self, filter_repo: Optional[str] = None) -> None:
        """
        List all worktrees, optionally filtered by repository.

        Args:
            filter_repo: Optional repository name to filter by
        """
        self._info("=== Available Worktrees ===\n")

        for repo in self.REPOS:
            if filter_repo:
                normalized_filter = self._normalize_repo_name(filter_repo)
                if repo != normalized_filter:
                    continue

            repo_path = self.WORKSPACE_ROOT / repo
            if not repo_path.exists():
                continue

            result = self._run_git(repo_path, ["worktree", "list"])
            if result.returncode != 0:
                continue

            self._success(f"{repo}:")
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                # Parse worktree list output
                parts = line.split(maxsplit=2)
                if not parts:
                    continue

                wt_path = Path(parts[0])

                # Display path (same on Mac and container due to /workspace symlink)
                print(f"  {Color.YELLOW}Path:{Color.NC} {wt_path}")
                if len(parts) > 1:
                    print(f"  {Color.YELLOW}Info:{Color.NC} {' '.join(parts[1:])}")
                print()

    def create_worktree(self, repo: str, branch: str) -> None:
        """
        Create a new worktree for the specified repository and branch.

        Args:
            repo: Repository name
            branch: Branch name to checkout
        """
        repo_path = self._get_repo_path(repo)
        if not repo_path:
            sys.exit(1)

        # Create worktree name
        repo_normalized = self._normalize_repo_name(repo)
        worktree_name = f"{repo_normalized.lower()}-{branch}"
        worktree_path = self.WORKTREES_DIR / worktree_name

        # Check if worktree already exists
        if worktree_path.exists():
            self._error(f"Worktree already exists at {worktree_path}")
            sys.exit(1)

        self._info(f"Creating worktree for {repo_normalized}/{branch}...")

        result = self._run_git(repo_path, ["worktree", "add", str(worktree_path), branch])

        if result.returncode != 0:
            self._error(f"Failed to create worktree:\n{result.stderr}")
            sys.exit(1)

        self._success("✓ Worktree created successfully!")
        self._warning(f"Path: {worktree_path}")
        print()
        self._info("To use (Mac or container):")
        print(f"  cd {worktree_path}")

    def remove_worktree(self, worktree_path: str) -> None:
        """
        Remove a worktree.

        Args:
            worktree_path: Path to worktree to remove
        """
        wt_path = Path(worktree_path)

        # Find which repo this worktree belongs to
        for repo in self.REPOS:
            repo_path = self.WORKSPACE_ROOT / repo
            if not repo_path.exists():
                continue

            result = self._run_git(repo_path, ["worktree", "list"])
            if result.returncode == 0 and str(wt_path) in result.stdout:
                self._info(f"Removing worktree: {wt_path}")
                remove_result = self._run_git(
                    repo_path, ["worktree", "remove", str(wt_path)]
                )

                if remove_result.returncode == 0:
                    self._success("✓ Removed")
                    return
                else:
                    self._error(f"Failed to remove:\n{remove_result.stderr}")
                    sys.exit(1)

        self._error(f"Worktree not found: {wt_path}")
        sys.exit(1)

    def goto_worktree(self, worktree_name: str) -> None:
        """
        Show cd command for accessing a worktree.

        Args:
            worktree_name: Name of the worktree
        """
        worktree_path = self.WORKTREES_DIR / worktree_name

        if not worktree_path.exists():
            self._error(f"Worktree not found at {worktree_path}")
            print(f"\n{Color.YELLOW}Available worktrees:{Color.NC}")
            worktrees = list(self.WORKTREES_DIR.iterdir()) if self.WORKTREES_DIR.exists() else []
            if worktrees:
                for wt in sorted(worktrees):
                    if wt.is_dir():
                        print(f"  {wt.name}")
            else:
                print("  None")
            sys.exit(1)

        self._info(f"=== Worktree: {worktree_name} ===\n")
        self._warning("Navigate (Mac or container):")
        print(f"  cd {worktree_path}\n")
        self._success("Copy the command above")

    def show_info(self) -> None:
        """Show information about worktree setup and path mapping."""
        print(f"{Color.BLUE}=== Worktree Path Mapping ==={Color.NC}\n")
        print(f"{Color.YELLOW}/workspace Setup:{Color.NC}")
        print(f"  Mac host:  /workspace → ~/NeerajDev (symlink)")
        print(f"  Container: /workspace → ~/NeerajDev (mount)")
        print(f"  Result:    Same paths work everywhere!\n")
        print(f"{Color.YELLOW}Worktree Location:{Color.NC}")
        print(f"  {self.WORKTREES_DIR}\n")
        print(f"{Color.YELLOW}Repository Locations:{Color.NC}")
        print(f"  syra:          {self.WORKSPACE_ROOT}/syra (bare repo)")
        print(f"  StyleGuru:     {self.WORKSPACE_ROOT}/StyleGuru (main worktree)")
        print(f"  org-standards: {self.WORKSPACE_ROOT}/org-standards\n")
        print(f"{Color.YELLOW}Usage Pattern:{Color.NC}")
        print("  1. Create worktree: python worktree-manager.py create syra my-branch")
        print("  2. Navigate:        cd /workspace/.worktrees/syra-my-branch")
        print("  3. Work:            # Same command works on Mac or in container!")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage git worktrees across NeerajDev repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all worktrees
  %(prog)s list syra                      # List only syra worktrees
  %(prog)s create syra my-feature-branch  # Create new worktree
  %(prog)s goto syra-main                 # Show cd command for syra-main worktree
  %(prog)s info                           # Show container path mapping
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list command
    list_parser = subparsers.add_parser("list", help="List worktrees")
    list_parser.add_argument("repo", nargs="?", help="Filter by repository")

    # create command
    create_parser = subparsers.add_parser("create", help="Create new worktree")
    create_parser.add_argument("repo", help="Repository name")
    create_parser.add_argument("branch", help="Branch name")

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove worktree")
    remove_parser.add_argument("path", help="Path to worktree")

    # goto command
    goto_parser = subparsers.add_parser("goto", help="Show cd commands for worktree")
    goto_parser.add_argument("worktree_name", help="Worktree name")

    # info command
    subparsers.add_parser("info", help="Show worktree path mapping info")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    manager = WorktreeManager()

    if args.command == "list":
        manager.list_worktrees(args.repo)
    elif args.command == "create":
        manager.create_worktree(args.repo, args.branch)
    elif args.command == "remove":
        manager.remove_worktree(args.path)
    elif args.command == "goto":
        manager.goto_worktree(args.worktree_name)
    elif args.command == "info":
        manager.show_info()


if __name__ == "__main__":
    main()
