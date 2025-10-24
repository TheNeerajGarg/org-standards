#!/bin/bash
# Git Hooks Installer
#
# Installs organizational standard git hooks to enforce quality gates
#
# Source: org-standards/git-hooks/install.sh
# Version: 1.0.0 (2025-01-23)

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Git Hooks Installer${NC}"
echo -e "${BLUE}  Organizational Quality Gates${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Determine script location (works with symlinks)
if [ -L "$0" ]; then
    SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
else
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

# Find repository root (where .git directory is)
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "")

if [ -z "$REPO_ROOT" ]; then
    echo -e "${RED}❌ ERROR: Not in a git repository${NC}"
    echo ""
    echo "Run this script from within a git repository"
    exit 1
fi

echo -e "${GREEN}✅ Repository: $REPO_ROOT${NC}"
echo ""

HOOKS_DIR="$REPO_ROOT/.git/hooks"

# ============================================================================
# Install pre-commit hook
# ============================================================================

echo -e "${BLUE}📦 Installing pre-commit hook...${NC}"

if [ -f "$HOOKS_DIR/pre-commit" ]; then
    # Backup existing hook
    BACKUP_FILE="$HOOKS_DIR/pre-commit.backup.$(date +%Y%m%d%H%M%S)"
    echo -e "${YELLOW}⚠️  Backing up existing pre-commit hook${NC}"
    echo "   Backup: $BACKUP_FILE"
    mv "$HOOKS_DIR/pre-commit" "$BACKUP_FILE"
    echo ""
fi

cp "$SCRIPT_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"
echo -e "${GREEN}✅ pre-commit hook installed${NC}"
echo "   Location: $HOOKS_DIR/pre-commit"
echo "   Behavior: Warnings only (never blocks commits)"
echo ""

# ============================================================================
# Install pre-push hook
# ============================================================================

echo -e "${BLUE}📦 Installing pre-push hook...${NC}"

if [ -f "$HOOKS_DIR/pre-push" ]; then
    # Backup existing hook
    BACKUP_FILE="$HOOKS_DIR/pre-push.backup.$(date +%Y%m%d%H%M%S)"
    echo -e "${YELLOW}⚠️  Backing up existing pre-push hook${NC}"
    echo "   Backup: $BACKUP_FILE"
    mv "$HOOKS_DIR/pre-push" "$BACKUP_FILE"
    echo ""
fi

cp "$SCRIPT_DIR/pre-push" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"
echo -e "${GREEN}✅ pre-push hook installed${NC}"
echo "   Location: $HOOKS_DIR/pre-push"
echo "   Behavior: Enforces quality gates (blocks push if failing)"
echo ""

# ============================================================================
# Check dependencies
# ============================================================================

echo -e "${BLUE}🔍 Checking dependencies...${NC}"
echo ""

MISSING_DEPS=()

if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest not installed${NC}"
    MISSING_DEPS+=("pytest")
else
    echo -e "${GREEN}✅ pytest installed${NC}"
fi

if ! command -v mypy &> /dev/null; then
    echo -e "${YELLOW}⚠️  mypy not installed${NC}"
    MISSING_DEPS+=("mypy")
else
    echo -e "${GREEN}✅ mypy installed${NC}"
fi

if ! command -v ruff &> /dev/null; then
    echo -e "${YELLOW}⚠️  ruff not installed${NC}"
    MISSING_DEPS+=("ruff")
else
    echo -e "${GREEN}✅ ruff installed${NC}"
fi

echo ""

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo ""
    echo "Install with:"
    echo "  pip install ${MISSING_DEPS[*]}"
    echo ""
    echo "Hooks are installed but may not work without these dependencies"
    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo "═══════════════════════════════════════════════"
echo -e "${GREEN}✅ Git hooks installed successfully${NC}"
echo "═══════════════════════════════════════════════"
echo ""
echo "Quality gate enforcement:"
echo "  • Pre-commit: Warnings only (saves WIP work)"
echo "  • Pre-push:   Enforces standards (blocks if failing)"
echo "  • CI:         Authoritative gate (cannot bypass)"
echo ""
echo "Emergency bypass (use with extreme caution):"
echo "  EMERGENCY_PUSH=1 git push"
echo ""
echo "To test hooks:"
echo "  git commit --allow-empty -m 'test: hook validation'"
echo "  git push --dry-run"
echo ""
