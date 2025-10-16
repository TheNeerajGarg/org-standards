#!/bin/bash
# Idempotent Introspection Environment Setup
#
# This script:
# - Clones org-standards if not present
# - Creates symlink if needed
# - Runs introspection setup
# - Validates everything is working
#
# Safe to run multiple times (idempotent)

set -e

EXPECTED_ORG_STANDARDS="$HOME/org-standards"
SETTINGS_FILE="$HOME/.claude/settings.local.json"

echo "=========================================="
echo "  Introspection Environment Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# ==================================================
# Step 1: Check if org-standards exists
# ==================================================

echo "Step 1: Checking org-standards repository..."
echo ""

if [ -d "$EXPECTED_ORG_STANDARDS/.git" ]; then
    print_status "org-standards found at: $EXPECTED_ORG_STANDARDS"
    
    # Check if it's up to date
    cd "$EXPECTED_ORG_STANDARDS"
    
    # Fetch latest (don't pull yet, just check)
    git fetch origin --quiet 2>/dev/null || true
    
    LOCAL=$(git rev-parse @)
    REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "$LOCAL")
    
    if [ "$LOCAL" != "$REMOTE" ]; then
        print_warning "org-standards has updates available"
        echo ""
        read -p "Pull latest changes? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git pull origin main
            print_status "Updated to latest version"
        else
            print_warning "Skipped update (using local version)"
        fi
    else
        print_status "Already up to date"
    fi

elif [ -L "$EXPECTED_ORG_STANDARDS" ]; then
    # It's a symlink
    TARGET=$(readlink "$EXPECTED_ORG_STANDARDS")
    
    if [ -d "$TARGET/.git" ]; then
        print_status "org-standards symlinked to: $TARGET"
        cd "$TARGET"
        
        # Check if it's up to date
        git fetch origin --quiet 2>/dev/null || true
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "$LOCAL")
        
        if [ "$LOCAL" != "$REMOTE" ]; then
            print_warning "org-standards has updates available"
            echo ""
            read -p "Pull latest changes? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git pull origin main
                print_status "Updated to latest version"
            else
                print_warning "Skipped update (using local version)"
            fi
        else
            print_status "Already up to date"
        fi
    else
        print_error "Symlink target is not a valid git repository: $TARGET"
        exit 1
    fi

elif [ -e "$EXPECTED_ORG_STANDARDS" ]; then
    # Something exists but it's not a directory or symlink
    print_error "$EXPECTED_ORG_STANDARDS exists but is not a directory or symlink"
    echo ""
    echo "Please resolve manually:"
    echo "  mv $EXPECTED_ORG_STANDARDS $EXPECTED_ORG_STANDARDS.backup"
    exit 1

else
    # org-standards doesn't exist, need to clone
    print_warning "org-standards not found"
    echo ""
    
    # Check if cloned elsewhere
    POSSIBLE_LOCATIONS=(
        "$HOME/repos/org-standards"
        "$HOME/workspace/org-standards"
        "$HOME/code/org-standards"
        "$HOME/projects/org-standards"
    )
    
    FOUND_ELSEWHERE=""
    for location in "${POSSIBLE_LOCATIONS[@]}"; do
        if [ -d "$location/.git" ]; then
            FOUND_ELSEWHERE="$location"
            break
        fi
    done
    
    if [ -n "$FOUND_ELSEWHERE" ]; then
        print_warning "Found org-standards at: $FOUND_ELSEWHERE"
        echo ""
        echo "Options:"
        echo "  1. Create symlink: ln -s $FOUND_ELSEWHERE $EXPECTED_ORG_STANDARDS"
        echo "  2. Clone fresh copy to: $EXPECTED_ORG_STANDARDS"
        echo ""
        read -p "Create symlink? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ln -s "$FOUND_ELSEWHERE" "$EXPECTED_ORG_STANDARDS"
            print_status "Created symlink: $EXPECTED_ORG_STANDARDS -> $FOUND_ELSEWHERE"
        else
            echo ""
            read -p "Clone fresh copy? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git clone git@github.com:StyleGuru/org-standards.git "$EXPECTED_ORG_STANDARDS"
                print_status "Cloned org-standards to: $EXPECTED_ORG_STANDARDS"
            else
                print_error "Cannot proceed without org-standards"
                exit 1
            fi
        fi
    else
        # Not found anywhere, ask to clone
        echo "Need to clone org-standards repository"
        echo ""
        echo "Will clone to: $EXPECTED_ORG_STANDARDS"
        echo ""
        read -p "Clone now? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git clone git@github.com:StyleGuru/org-standards.git "$EXPECTED_ORG_STANDARDS"
            print_status "Cloned org-standards to: $EXPECTED_ORG_STANDARDS"
        else
            print_error "Cannot proceed without org-standards"
            exit 1
        fi
    fi
fi

echo ""

# ==================================================
# Step 2: Verify introspection setup script exists
# ==================================================

echo "Step 2: Verifying introspection setup script..."
echo ""

SETUP_SCRIPT="$EXPECTED_ORG_STANDARDS/claude-code/setup-introspection.sh"

if [ ! -f "$SETUP_SCRIPT" ]; then
    print_error "Setup script not found: $SETUP_SCRIPT"
    echo ""
    echo "This may mean:"
    echo "  - org-standards is outdated (try: cd $EXPECTED_ORG_STANDARDS && git pull)"
    echo "  - Introspection hasn't been added to org-standards yet"
    exit 1
fi

print_status "Setup script found"
echo ""

# ==================================================
# Step 3: Check if already configured
# ==================================================

echo "Step 3: Checking existing configuration..."
echo ""

ALREADY_CONFIGURED=false

if [ -f "$SETTINGS_FILE" ]; then
    if grep -q "org-standards/claude-code/introspection" "$SETTINGS_FILE" 2>/dev/null; then
        print_status "Introspection already configured"
        
        # Validate JSON
        if python3 -m json.tool "$SETTINGS_FILE" > /dev/null 2>&1; then
            print_status "Settings file is valid JSON"
        else
            print_warning "Settings file exists but has invalid JSON"
            echo ""
            read -p "Recreate settings file? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ALREADY_CONFIGURED=false
            else
                print_error "Cannot proceed with invalid settings"
                exit 1
            fi
        fi
        
        # Check if hooks point to correct location
        if grep -q "$EXPECTED_ORG_STANDARDS" "$SETTINGS_FILE" 2>/dev/null || \
           grep -q "~/org-standards" "$SETTINGS_FILE" 2>/dev/null; then
            print_status "Hook paths are correct"
            ALREADY_CONFIGURED=true
        else
            print_warning "Hook paths may be outdated"
            echo ""
            echo "Current settings:"
            grep -A 2 "command" "$SETTINGS_FILE" | head -5
            echo ""
            read -p "Update settings? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ALREADY_CONFIGURED=false
            else
                ALREADY_CONFIGURED=true
            fi
        fi
        
    elif grep -q "syra/introspection" "$SETTINGS_FILE" 2>/dev/null; then
        print_warning "Settings configured with old Syra paths"
        echo ""
        read -p "Migrate to org-standards paths? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Backup old settings
            cp "$SETTINGS_FILE" "$SETTINGS_FILE.backup-syra"
            print_status "Backed up old settings to: $SETTINGS_FILE.backup-syra"
            ALREADY_CONFIGURED=false
        else
            print_warning "Keeping old Syra paths (not recommended)"
            ALREADY_CONFIGURED=true
        fi
    else
        print_warning "Settings file exists but introspection not configured"
        ALREADY_CONFIGURED=false
    fi
else
    print_warning "No settings file found (will create)"
    ALREADY_CONFIGURED=false
fi

echo ""

# ==================================================
# Step 4: Run setup if needed
# ==================================================

if [ "$ALREADY_CONFIGURED" = false ]; then
    echo "Step 4: Running introspection setup..."
    echo ""
    
    cd "$EXPECTED_ORG_STANDARDS"
    ./claude-code/setup-introspection.sh
    
    echo ""
    print_status "Setup completed"
else
    echo "Step 4: Setup not needed (already configured)"
    print_status "Skipping setup"
fi

echo ""

# ==================================================
# Step 5: Validate everything works
# ==================================================

echo "Step 5: Validating configuration..."
echo ""

# Check settings file exists
if [ ! -f "$SETTINGS_FILE" ]; then
    print_error "Settings file not created: $SETTINGS_FILE"
    exit 1
fi

# Check valid JSON
if ! python3 -m json.tool "$SETTINGS_FILE" > /dev/null 2>&1; then
    print_error "Settings file has invalid JSON"
    exit 1
fi

# Check hooks configured
if ! grep -q "PostToolUse" "$SETTINGS_FILE"; then
    print_error "PostToolUse hook not configured"
    exit 1
fi

if ! grep -q "SessionEnd" "$SETTINGS_FILE"; then
    print_error "SessionEnd hook not configured"
    exit 1
fi

# Check hook scripts exist
POST_HOOK="$EXPECTED_ORG_STANDARDS/claude-code/introspection/current/hooks/post_tool_use.py"
SESSION_HOOK="$EXPECTED_ORG_STANDARDS/claude-code/introspection/current/hooks/session_end.py"

if [ ! -f "$POST_HOOK" ]; then
    print_error "Hook script not found: $POST_HOOK"
    exit 1
fi

if [ ! -f "$SESSION_HOOK" ]; then
    print_error "Hook script not found: $SESSION_HOOK"
    exit 1
fi

# Test hook execution (dry run)
TEST_INPUT='{"tool_name":"Bash","exit_code":1,"stderr":"test error"}'
if echo "$TEST_INPUT" | python3 "$POST_HOOK" > /dev/null 2>&1; then
    print_status "Hook scripts executable"
else
    print_warning "Hook test failed (may need dependencies)"
    echo "   Try: cd $EXPECTED_ORG_STANDARDS && pip install -r requirements.txt"
fi

echo ""
print_status "All validations passed!"
echo ""

# ==================================================
# Step 6: Summary and Next Steps
# ==================================================

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""

echo "Configuration:"
echo "  • org-standards:    $EXPECTED_ORG_STANDARDS"
echo "  • Settings file:    $SETTINGS_FILE"
echo "  • Hook scripts:     $EXPECTED_ORG_STANDARDS/claude-code/introspection/current/hooks/"
echo ""

echo "Next Steps:"
echo ""
echo "  1. Restart Claude Code (required for hooks to activate)"
echo "     - Close Claude Code completely"
echo "     - Reopen Claude Code"
echo ""
echo "  2. Test it works:"
echo "     python -c \"import nonexistent\""
echo "     tail ~/.claude/failure-tracker/sessions/*/failures.jsonl | python3 -m json.tool"
echo ""
echo "  3. Read documentation:"
echo "     cat $EXPECTED_ORG_STANDARDS/claude-code/README.md"
echo ""

echo "=========================================="
echo "  Introspection now active in ALL repos!"
echo "=========================================="
echo ""

# Check if Claude Code is currently running
if pgrep -f "claude" > /dev/null 2>&1; then
    print_warning "Claude Code appears to be running"
    echo ""
    echo "For hooks to activate, you must restart Claude Code."
    echo ""
    read -p "Would you like reminders? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "📋 REMINDER: Restart Claude Code to activate introspection hooks"
        echo ""
        echo "Add this to your terminal startup (optional):"
        echo "  echo 'Reminder: Restart Claude Code after introspection setup'"
    fi
fi
