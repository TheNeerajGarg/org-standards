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
HOOKS_DIR="$ORG_STANDARDS_DIR/claude-code/introspection/current/hooks"
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
        "command": "python3 ~/org-standards/claude-code/introspection/current/hooks/post_tool_use.py"
      }]
    }],
    "SessionEnd": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/org-standards/claude-code/introspection/current/hooks/session_end.py"
      }]
    }],
    "UserPromptSubmit": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/org-standards/claude-code/hooks/track_messages_context.py 2>/dev/null || true"
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
if echo "$TEST_INPUT" | python3 ~/org-standards/claude-code/introspection/current/hooks/post_tool_use.py > /dev/null 2>&1; then
    echo "✅ Hook scripts working"
else
    echo "⚠️  Warning: Hook test failed"
    echo "   This is OK if you haven't installed dependencies yet"
fi
echo ""

# Step 6: Validate configuration
echo "Validating hook configuration..."

# Check that all expected hooks are present
EXPECTED_HOOKS=("PostToolUse" "SessionEnd" "UserPromptSubmit")
MISSING_HOOKS=()

for hook in "${EXPECTED_HOOKS[@]}"; do
    if ! grep -q "\"$hook\"" "$SETTINGS_FILE"; then
        MISSING_HOOKS+=("$hook")
    fi
done

if [ ${#MISSING_HOOKS[@]} -eq 0 ]; then
    echo "✅ All hooks configured (PostToolUse, SessionEnd, UserPromptSubmit)"
else
    echo "⚠️  WARNING: Missing hooks: ${MISSING_HOOKS[*]}"
    echo "   Configuration may be incomplete"
fi
echo ""

# Step 7: Instructions
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
echo "=== Hooks Installed ==="
echo "✅ PostToolUse: Automatic failure tracking"
echo "✅ SessionEnd: Pattern detection & introspection generation"
echo "✅ UserPromptSubmit: Conversation context size warnings (>10KB)"
echo ""
echo "=== This Works Everywhere ==="
echo "✅ All repositories (StyleGuru, Syra, etc.)"
echo "✅ Company-wide standard"
echo ""
echo "Questions? Ask in #engineering Slack channel"
echo ""
