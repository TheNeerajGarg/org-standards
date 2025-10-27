#!/usr/bin/env bash
#
# Install org-standards Claude Code hooks on host machine
#
# USAGE:
#   cd /path/to/your/repo
#   ./org-standards/claude-code/install-hooks.sh
#
# WHAT IT DOES:
#   1. Checks if Claude Code is installed
#   2. Creates ~/.claude/settings.json if it doesn't exist
#   3. Merges hook configuration from org-standards/claude-code/settings.template.json
#   4. Preserves existing user settings
#
# REQUIREMENTS:
#   - Claude Code CLI installed (npm install -g @anthropic-ai/claude-code)
#   - org-standards available at ~/org-standards or as git submodule
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Claude Code Hooks Installation${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if /workspace symlink exists
if [ ! -L "/workspace" ]; then
    echo -e "${YELLOW}⚠ /workspace symlink not found${NC}"
    echo -e "${YELLOW}  This is required for hooks to work across all environments.${NC}"
    echo -e ""
    echo -e "${BLUE}To set up /workspace (one-time):${NC}"
    echo -e "  sudo ln -s $HOME/NeerajDev /workspace"
    echo -e ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ /workspace symlink exists${NC}"
    WORKSPACE_TARGET=$(readlink -f /workspace 2>/dev/null || realpath /workspace 2>/dev/null)
    echo -e "${GREEN}  → $WORKSPACE_TARGET${NC}"
fi

# Check if Claude Code is installed
if ! command -v claude-code &> /dev/null; then
    echo -e "${RED}✗ Claude Code is not installed${NC}"
    echo -e "${YELLOW}Install it with: npm install -g @anthropic-ai/claude-code${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Claude Code is installed${NC}"

# Find org-standards location (prefer /workspace for consistency)
ORG_STANDARDS_DIR=""
if [ -d "/workspace/org-standards" ]; then
    ORG_STANDARDS_DIR="/workspace/org-standards"
elif [ -d "$HOME/org-standards" ]; then
    ORG_STANDARDS_DIR="$HOME/org-standards"
elif [ -d "org-standards" ]; then
    ORG_STANDARDS_DIR="$(pwd)/org-standards"
elif [ -d "../org-standards" ]; then
    ORG_STANDARDS_DIR="$(cd ../org-standards && pwd)"
else
    echo -e "${RED}✗ org-standards not found${NC}"
    echo -e "${YELLOW}Expected locations:${NC}"
    echo -e "  - /workspace/org-standards (preferred)"
    echo -e "  - ~/org-standards"
    echo -e "  - ./org-standards (git submodule)"
    echo -e "  - ../org-standards"
    exit 1
fi
echo -e "${GREEN}✓ Found org-standards at: $ORG_STANDARDS_DIR${NC}"

# Check if template exists
TEMPLATE_FILE="$ORG_STANDARDS_DIR/claude-code/settings.template.json"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}✗ Template not found: $TEMPLATE_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found settings template${NC}"

# Create .claude directory if it doesn't exist
CLAUDE_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_DIR"
echo -e "${GREEN}✓ Claude directory: $CLAUDE_DIR${NC}"

# Settings file location
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

# Backup existing settings if they exist
if [ -f "$SETTINGS_FILE" ]; then
    BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$SETTINGS_FILE" "$BACKUP_FILE"
    echo -e "${YELLOW}⚠ Backed up existing settings to: $BACKUP_FILE${NC}"
fi

# Install settings
# If no existing settings, just copy template
if [ ! -f "$SETTINGS_FILE" ]; then
    cp "$TEMPLATE_FILE" "$SETTINGS_FILE"
    echo -e "${GREEN}✓ Installed Claude Code settings${NC}"
else
    # If settings exist, we need to merge (for now, just warn user)
    echo -e "${YELLOW}⚠ Settings file already exists: $SETTINGS_FILE${NC}"
    echo -e "${YELLOW}  To use org-standards hooks, manually merge settings from:${NC}"
    echo -e "${YELLOW}  $TEMPLATE_FILE${NC}"
    echo -e "${YELLOW}  Or delete your settings file and re-run this script.${NC}"

    # Ask user if they want to replace
    read -p "Replace existing settings with org-standards template? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$TEMPLATE_FILE" "$SETTINGS_FILE"
        echo -e "${GREEN}✓ Replaced settings with org-standards template${NC}"
    else
        echo -e "${YELLOW}⚠ Kept existing settings (you'll need to merge manually)${NC}"
        exit 0
    fi
fi

# Verify hooks are accessible
echo -e "\n${BLUE}Verifying hooks...${NC}"

HOOKS=(
    "track_reads.py"
    "track_context_size.py"
)

for hook in "${HOOKS[@]}"; do
    HOOK_PATH="$ORG_STANDARDS_DIR/claude-code/hooks/$hook"
    if [ -f "$HOOK_PATH" ]; then
        echo -e "${GREEN}✓ Found: $hook${NC}"
        # Test if hook is executable by Python
        if python3 -m py_compile "$HOOK_PATH" 2>/dev/null; then
            echo -e "${GREEN}  ✓ Syntax valid${NC}"
        else
            echo -e "${RED}  ✗ Syntax error in hook${NC}"
        fi
    else
        echo -e "${RED}✗ Missing: $hook${NC}"
    fi
done

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\nHooks installed:"
echo -e "  • ${GREEN}Read tracking${NC} - Logs all file reads to .ai-usage-tracking/"
echo -e "  • ${GREEN}Context size warnings${NC} - Warns when session context > 10KB"
echo -e "\nConfiguration:"
echo -e "  • Settings: $SETTINGS_FILE"
echo -e "  • Hooks: $ORG_STANDARDS_DIR/claude-code/hooks/"
echo -e "\nCustomize thresholds with environment variables:"
echo -e "  export CONTEXT_SIZE_THRESHOLD_KB=50"
echo -e "  export CONTEXT_SIZE_WARNING_INTERVAL=600"
echo -e "\n${BLUE}Start Claude Code to use hooks:${NC}"
echo -e "  claude-code"
echo ""
