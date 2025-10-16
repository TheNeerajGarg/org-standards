#!/bin/bash
# Organization-Wide Introspection Setup
# Part of org-standards (company-wide tooling)

set -e

echo "=== Claude Code Introspection Setup ==="
echo ""
echo "This will configure automatic failure tracking across ALL repositories."
echo ""

# Step 1: Verify org-standards is cloned
ORG_STANDARDS_DIR="${HOME}/org-standards"
if [ ! -d "$ORG_STANDARDS_DIR" ]; then
    echo "❌ ERROR: org-standards not found at $ORG_STANDARDS_DIR"
    echo ""
    echo "Please clone org-standards first:"
    echo "  git clone git@github.com:StyleGuru/org-standards.git ~/org-standards"
    echo ""
    exit 1
fi

echo "✅ Found org-standards at: $ORG_STANDARDS_DIR"
echo ""

# Step 2: Verify hook scripts exist
HOOKS_DIR="$ORG_STANDARDS_DIR/claude-code/introspection/hooks"
if [ ! -f "$HOOKS_DIR/post_tool_use.py" ]; then
    echo "❌ ERROR: Hook scripts not found"
    echo "Expected: $HOOKS_DIR/post_tool_use.py"
    echo ""
    echo "Please pull latest org-standards:"
    echo "  cd ~/org-standards && git pull"
    echo ""
    exit 1
fi

echo "✅ Found hook scripts"
echo ""

# Step 3: Create user-level settings
SETTINGS_FILE="${HOME}/.claude/settings.local.json"
SETTINGS_DIR="${HOME}/.claude"

mkdir -p "$SETTINGS_DIR"

echo "Creating user-level settings..."
cat > "$SETTINGS_FILE" <<'EOF'
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/org-standards/claude-code/introspection/hooks/post_tool_use.py"
      }]
    }],
    "SessionEnd": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/org-standards/claude-code/introspection/hooks/session_end.py"
      }]
    }]
  }
}
EOF

echo "✅ Created: $SETTINGS_FILE"
echo ""

# Step 4: Validate JSON
if python3 -m json.tool "$SETTINGS_FILE" > /dev/null 2>&1; then
    echo "✅ Valid JSON configuration"
else
    echo "❌ ERROR: Invalid JSON in settings file"
    exit 1
fi
echo ""

# Step 5: Test hook execution
echo "Testing hook scripts..."
TEST_INPUT='{"tool_name":"Bash","exit_code":1,"stderr":"test error","tool_input":{"command":"test"}}'
if echo "$TEST_INPUT" | python3 ~/org-standards/claude-code/introspection/hooks/post_tool_use.py > /dev/null 2>&1; then
    echo "✅ Hook scripts working"
else
    echo "⚠️  Warning: Hook test failed"
    echo "   This is OK if you haven't installed dependencies yet"
fi
echo ""

# Step 6: Instructions
echo "=== Setup Complete! ==="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Restart Claude Code:"
echo "   - Close Claude Code completely"
echo "   - Reopen Claude Code"
echo ""
echo "2. Test it works:"
echo "   python -c \"import nonexistent\""
echo "   tail ~/.claude/failure-tracker/sessions/*/failures.jsonl | python3 -m json.tool"
echo ""
echo "3. Read documentation:"
echo "   cat ~/org-standards/claude-code/README.md"
echo ""
echo "=== This Works Everywhere ==="
echo "✅ All repositories (StyleGuru, Syra, etc.)"
echo "✅ Automatic failure tracking"
echo "✅ Pattern detection (recurring errors)"
echo "✅ Introspection generation"
echo "✅ Company-wide standard"
echo ""
echo "Questions? Ask in #engineering Slack channel"
echo ""
