#!/usr/bin/env bash
#
# Sync Claude Code hooks from managed-settings.json to user settings
#
# PROBLEM: Claude Code CLI doesn't load managed-settings.json (confirmed bug #6313)
# SOLUTION: Merge hooks from managed-settings.json into ~/.claude/settings.json
#
# USAGE:
#   ./sync-claude-settings.sh [--dry-run]
#
# WHAT IT DOES:
#   1. Reads hooks from org-standards/claude-code/managed-settings.json
#   2. Merges hooks into ~/.claude/settings.json (preserves personal settings)
#   3. Backs up existing settings before modifying
#   4. Non-interactive (safe for automation)
#   5. Idempotent (safe to run multiple times)
#
# REQUIREMENTS:
#   - jq (JSON processor)
#   - org-standards available at /workspace/org-standards or ~/org-standards
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}\n"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Claude Code Settings Sync${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}✗ jq is not installed${NC}"
    echo -e "${YELLOW}Install it with:${NC}"
    echo -e "  Mac: brew install jq"
    echo -e "  Linux: apt-get install jq"
    exit 1
fi
echo -e "${GREEN}✓ jq is installed${NC}"

# Find org-standards location (prefer /workspace for consistency)
ORG_STANDARDS_DIR=""
if [ -d "/workspace/org-standards" ]; then
    ORG_STANDARDS_DIR="/workspace/org-standards"
elif [ -d "$HOME/NeerajDev/org-standards" ]; then
    ORG_STANDARDS_DIR="$HOME/NeerajDev/org-standards"
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
    echo -e "  - ~/NeerajDev/org-standards"
    echo -e "  - ~/org-standards"
    echo -e "  - ./org-standards (git submodule)"
    echo -e "  - ../org-standards"
    exit 1
fi
echo -e "${GREEN}✓ Found org-standards at: $ORG_STANDARDS_DIR${NC}"

# Check if managed-settings.json exists
MANAGED_SETTINGS="$ORG_STANDARDS_DIR/claude-code/managed-settings.json"
if [ ! -f "$MANAGED_SETTINGS" ]; then
    echo -e "${RED}✗ Managed settings not found: $MANAGED_SETTINGS${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found managed-settings.json${NC}"

# Validate managed-settings.json has hooks
if ! jq -e '.hooks' "$MANAGED_SETTINGS" >/dev/null 2>&1; then
    echo -e "${RED}✗ Managed settings has no hooks section${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Managed settings contains hooks${NC}"

# Settings file location
CLAUDE_DIR="$HOME/.claude"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

# Create .claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Read or create default user settings
if [ -f "$SETTINGS_FILE" ]; then
    echo -e "${GREEN}✓ Found existing settings: $SETTINGS_FILE${NC}"

    # Backup existing settings
    if [ "$DRY_RUN" = false ]; then
        BACKUP_FILE="$SETTINGS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$SETTINGS_FILE" "$BACKUP_FILE"
        echo -e "${YELLOW}📦 Backed up to: $BACKUP_FILE${NC}"
    fi

    USER_SETTINGS=$(cat "$SETTINGS_FILE")
else
    echo -e "${YELLOW}⚠ No existing settings found${NC}"
    echo -e "${BLUE}Creating default settings with hooks...${NC}"

    # Default minimal user settings
    USER_SETTINGS='{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "description": "User-specific Claude Code settings. Hooks synced from org-standards/claude-code/managed-settings.json",
  "alwaysThinkingEnabled": true,
  "permissions": {
    "allow": [
      "Read(//workspace/**)",
      "Read(//home/vscode/**)",
      "Bash(python3:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Bash(mypy:*)",
      "Bash(git:*)",
      "Bash(gh:*)"
    ],
    "deny": [],
    "ask": []
  }
}'
fi

# Extract hooks from managed settings
MANAGED_HOOKS=$(jq '.hooks' "$MANAGED_SETTINGS")

# Merge: Add hooks from managed-settings to user settings
# Strategy: User settings take precedence for non-hook fields, hooks come from managed-settings
MERGED_SETTINGS=$(echo "$USER_SETTINGS" | jq \
    --argjson hooks "$MANAGED_HOOKS" \
    '. + {hooks: $hooks}')

# Show diff if dry-run
if [ "$DRY_RUN" = true ]; then
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}Changes that would be made:${NC}"
    echo -e "${BLUE}========================================${NC}"

    if [ -f "$SETTINGS_FILE" ]; then
        echo -e "${YELLOW}Current settings:${NC}"
        jq '.hooks // "No hooks"' "$SETTINGS_FILE"
        echo ""
    fi

    echo -e "${GREEN}New settings (hooks from managed-settings.json):${NC}"
    echo "$MERGED_SETTINGS" | jq '.hooks'
    echo ""

    echo -e "${BLUE}Run without --dry-run to apply changes${NC}"
    exit 0
fi

# Write merged settings
echo "$MERGED_SETTINGS" | jq '.' > "$SETTINGS_FILE"
echo -e "${GREEN}✓ Updated settings with hooks from managed-settings.json${NC}"

# Verify hooks are in place
echo -e "\n${BLUE}Verifying hooks...${NC}"

HOOKS_COUNT=$(jq '[.hooks | to_entries[]] | length' "$SETTINGS_FILE")
echo -e "${GREEN}✓ $HOOKS_COUNT hook types configured:${NC}"

for hook_type in PreToolUse PostToolUse UserPromptSubmit; do
    if jq -e ".hooks.$hook_type" "$SETTINGS_FILE" >/dev/null 2>&1; then
        MATCHERS=$(jq -r ".hooks.$hook_type[].matcher" "$SETTINGS_FILE" | paste -sd, -)
        echo -e "${GREEN}  • $hook_type: $MATCHERS${NC}"
    fi
done

# Verify hook scripts exist
echo -e "\n${BLUE}Verifying hook scripts...${NC}"

HOOK_SCRIPTS=(
    "track_reads.py"
    "track_context_size.py"
    "track_messages_context.py"
)

for script in "${HOOK_SCRIPTS[@]}"; do
    SCRIPT_PATH="$ORG_STANDARDS_DIR/claude-code/hooks/$script"
    if [ -f "$SCRIPT_PATH" ]; then
        echo -e "${GREEN}✓ Found: $script${NC}"
    else
        echo -e "${RED}✗ Missing: $script${NC}"
        echo -e "${YELLOW}  Expected at: $SCRIPT_PATH${NC}"
    fi
done

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Sync complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${YELLOW}⚠ IMPORTANT: Restart Claude Code for hooks to take effect${NC}"
echo -e "${BLUE}Hooks configured:${NC}"
echo -e "  • ${GREEN}PreToolUse[Read]${NC} - Track all file reads"
echo -e "  • ${GREEN}PostToolUse[*]${NC} - Track tool I/O sizes"
echo -e "  • ${GREEN}UserPromptSubmit[*]${NC} - Warn at 10KB message threshold"
echo -e "\n${BLUE}Settings file:${NC} $SETTINGS_FILE"
echo -e "${BLUE}Hook scripts:${NC} $ORG_STANDARDS_DIR/claude-code/hooks/"
echo ""
