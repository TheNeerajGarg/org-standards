# Claude Code Hooks

**Organizational Standards**: These hooks are org-wide infrastructure that apply everywhere:
- ✅ Local development (your Mac)
- ✅ Dev containers (VS Code Remote Containers)
- ✅ GitHub Actions (when bots use Claude Code)

Pre-configured hooks for tracking usage and managing costs.

## Quick Start

**Host (Mac/Linux)**:
```bash
cd /path/to/your/repo
./org-standards/claude-code/install-hooks.sh
```

**Dev Container**: Hooks are automatically installed (see `org-standards/devcontainer/Dockerfile`)

**GitHub Actions**: Hooks are installed when Claude Code is used in workflows

## Available Hooks

### 1. Read Tracking Hook (`track_reads.py`)

**Purpose**: Track all Read tool calls for token usage analysis

**Output**:
- Per-session: `.ai-usage-tracking/sessions/session-{SESSION_ID}.jsonl`
- Aggregate: `.ai-usage-tracking/read-tracking.jsonl`

**Hook Type**: `PreToolUse` (runs before Read tool executes)

### 2. Tool I/O Tracking Hook (`track_context_size.py`)

**Purpose**: Track individual tool call I/O sizes

**Output**:
- Per-session state: `.ai-usage-tracking/context/session-{SESSION_ID}.json`
- Aggregate log: `.ai-usage-tracking/context-tracking.jsonl`

**Hook Type**: `PostToolUse` (runs after every tool call)

**Note**: This tracks tool-level I/O, NOT conversation messages. See `track_messages_context.py` below.

### 3. Conversation Messages Warning Hook (`track_messages_context.py`)

**Purpose**: Warn when conversation message context exceeds threshold (manages prompt caching costs)

**Output**:
- Per-session state: `.ai-usage-tracking/message-context/session-{SESSION_ID}.json`
- Aggregate log: `.ai-usage-tracking/message-context-tracking.jsonl`

**Hook Type**: `UserPromptSubmit` (runs before each user prompt is processed)

**Environment Variables**:
- `CONTEXT_SIZE_THRESHOLD_KB`: Warning threshold in KB (default: 10)
- `CONTEXT_SIZE_WARNING_INTERVAL`: Minimum seconds between warnings (default: 300)

**Warning Display** (from `track_messages_context.py`):
```
============================================================
⚠️  CONVERSATION CONTEXT SIZE WARNING
============================================================
Conversation messages: 12.3KB (45 messages)
Threshold: 10KB

Large context increases costs from:
  • Prompt caching on accumulated messages
  • Long message chains sent with every request

Consider:
  1. Use /clear to reset conversation
  2. Start new session for unrelated work
  3. Create handoff doc and start fresh
============================================================
```

## Deployment Architecture

### Path Resolution Strategy

Hooks use a **fallback chain** that works in all environments:

```bash
python3 /opt/org-standards/claude-code/hooks/{hook}.py 2>/dev/null || \
python3 ~/org-standards/claude-code/hooks/{hook}.py 2>/dev/null || \
true
```

**Where hooks are located**:
- **Container**: `/opt/org-standards/` (copied during Docker build)
- **Host**: `~/org-standards/` (symlink to git clone)
- **Fail-safe**: `|| true` prevents Claude Code from failing if hooks missing

### Installation Locations

**Dev Container** (`/home/vscode/.claude/settings.json`):
- Installed automatically during Docker build
- See: `org-standards/devcontainer/Dockerfile`
- Configured when container starts

**Host** (`~/.claude/settings.json`):
- Install manually via: `./org-standards/claude-code/install-hooks.sh`
- Or manually copy: `org-standards/claude-code/settings.template.json`

**GitHub Actions** (TODO):
- Install during workflow setup step
- Document when we use Claude Code in CI

## Configuration Reference

### Full Settings Template

See [`org-standards/claude-code/settings.template.json`](../settings.template.json) for complete configuration.

**Key sections**:
```json
{
  "hooks": {
    "PreToolUse": [...],   // Read tracking
    "PostToolUse": [...]   // Context size warnings
  },
  "alwaysThinkingEnabled": true,
  "permissions": {
    "allow": [...]  // Common tool permissions
  }
}
```

### Customizing Thresholds

Set environment variables before starting Claude Code:

```bash
# Warn at 50KB instead of 10KB
export CONTEXT_SIZE_THRESHOLD_KB=50

# Warn every 10 minutes instead of 5
export CONTEXT_SIZE_WARNING_INTERVAL=600

# Start Claude Code
claude-code
```

Or set in your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export CONTEXT_SIZE_THRESHOLD_KB=50
export CONTEXT_SIZE_WARNING_INTERVAL=600
```

## Troubleshooting

### Hook not triggering?

1. **Check hook script exists**:
   ```bash
   ls -la ~/org-standards/claude-code/hooks/
   # Container: ls -la /opt/org-standards/claude-code/hooks/
   ```

2. **Verify Python 3 available**:
   ```bash
   which python3
   python3 --version
   ```

3. **Test script manually**:
   ```bash
   echo '{}' | python3 ~/org-standards/claude-code/hooks/track_context_size.py
   # Should exit 0 (no output expected)
   ```

4. **Check Claude Code settings loaded**:
   ```bash
   cat ~/.claude/settings.json | grep -A 5 "hooks"
   ```

### No warnings shown?

1. **Check threshold**:
   ```bash
   echo $CONTEXT_SIZE_THRESHOLD_KB  # Should be 10 or your custom value
   ```

2. **View session state**:
   ```bash
   cat .ai-usage-tracking/context/session-*.json | jq
   ```

3. **Check if already warned**:
   Look for `warnings_shown` in session state - hook only warns once per threshold

### Tracking files not created?

1. **Check write permissions**:
   ```bash
   ls -la .ai-usage-tracking/
   ```

2. **Verify project root detected**:
   Hook uses `CLAUDE_PROJECT_DIR` env var or finds git root

3. **Check stderr output** (debugging):
   ```bash
   # Temporarily remove 2>/dev/null from hook command in settings.json
   # to see error messages
   ```

## Development

### Testing Hooks Locally

```bash
# Test track_reads.py
echo '{"tool_name": "Read", "tool_input": {"file_path": "/tmp/test.txt"}}' | \
  python3 org-standards/claude-code/hooks/track_reads.py

# Test track_context_size.py
echo '{"tool_name": "Read", "tool_input": {}, "tool_output": {"content": "test"}}' | \
  python3 org-standards/claude-code/hooks/track_context_size.py
```

### Adding New Hooks

1. Create hook script in `org-standards/claude-code/hooks/`
2. Add hook configuration to `org-standards/claude-code/settings.template.json`
3. Update this README
4. Commit to org-standards repo
5. Update submodule references in all repos
6. Users re-run `install-hooks.sh` to get new settings

## Maintenance

### Updating Hooks Organization-Wide

1. **Update in org-standards**:
   ```bash
   cd org-standards
   git add claude-code/hooks/
   git commit -m "feat: update Claude Code hooks"
   git push origin main
   ```

2. **Update submodule in each repo**:
   ```bash
   cd /path/to/repo
   git submodule update --remote org-standards
   git add org-standards
   git commit -m "chore: update org-standards (hook changes)"
   git push origin main
   ```

3. **Users update their host settings**:
   ```bash
   ./org-standards/claude-code/install-hooks.sh
   # Answer "y" to replace existing settings
   ```

4. **Rebuild dev containers**:
   - VS Code: "Dev Containers: Rebuild Container"
   - Docker: `docker build --no-cache ...`

## Related Documentation

- **Hook Installation**: [`org-standards/claude-code/install-hooks.sh`](../install-hooks.sh)
- **Settings Template**: [`org-standards/claude-code/settings.template.json`](../settings.template.json)
- **Container Setup**: [`org-standards/devcontainer/Dockerfile`](../../devcontainer/Dockerfile)
