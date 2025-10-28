# Claude Code Hooks Sync Strategy

## Problem: Managed Settings Don't Work in CLI

**Bug**: Claude Code CLI doesn't load `managed-settings.json` (GitHub Issue [#6313](https://github.com/anthropics/claude-code/issues/6313), confirmed August 2025, unfixed as of v2.0.28)

**Impact**:
- ❌ Hooks defined in `/Library/Application Support/ClaudeCode/managed-settings.json` (Mac) ignored
- ❌ Hooks defined in `/etc/claude-code/managed-settings.json` (Linux/Container) ignored
- ❌ Claude CLI runs without organization-mandated tracking/warnings
- ❌ ClaudeRunner automation bots have no hook enforcement

**Expected Behavior** (per docs):
- Managed settings should override user settings
- Organization policies enforced across all environments

**Actual Behavior** (confirmed 2025-10-28):
- Managed settings completely ignored by Claude CLI
- Only user settings (`~/.claude/settings.json`) load
- `/hooks` command shows "No hooks configured"

## Solution: Sync Script

### Strategy

**Source of truth**: `org-standards/claude-code/managed-settings.json`
- Contains organization-wide hook definitions
- Updated via git pull (version controlled)
- Shared across all projects

**Deployment target**: `~/.claude/settings.json` (user settings)
- Only location that actually works in Claude CLI
- Created/updated by `sync-claude-settings.sh`

**Sync script** (`sync-claude-settings.sh`):
- Reads hooks from `managed-settings.json`
- Merges into user settings (preserves personal preferences)
- Non-interactive (safe for automation)
- Idempotent (safe to run multiple times)

### Script Usage

**Manual** (Mac development):
```bash
/workspace/org-standards/claude-code/sync-claude-settings.sh

# Dry-run to preview changes
/workspace/org-standards/claude-code/sync-claude-settings.sh --dry-run
```

**Automatic** (container startup):
- Runs in devcontainer `postCreateCommand`
- Ensures hooks installed on every container rebuild
- No manual setup required

### What Gets Synced

**Copied from managed-settings.json**:
- `hooks.PreToolUse` - Track Read tool calls
- `hooks.PostToolUse` - Track tool I/O sizes
- `hooks.UserPromptSubmit` - Warn at 10KB message threshold

**Preserved in user settings**:
- `alwaysThinkingEnabled` (personal preference)
- `permissions.allow` (project-specific access)
- Any other user-defined fields

**Result**: User settings = personal preferences + organization hooks

### Backup Strategy

Script automatically creates timestamped backups:
```bash
~/.claude/settings.json.backup.20251028_122013
```

Restore if needed:
```bash
cp ~/.claude/settings.json.backup.YYYYMMDD_HHMMSS ~/.claude/settings.json
```

## How It Works

### Architecture

```
org-standards/claude-code/managed-settings.json (source of truth)
                    |
                    | sync-claude-settings.sh
                    v
            ~/.claude/settings.json (actual loaded config)
                    |
                    | Claude CLI loads at startup
                    v
              Hooks execute ✅
```

### Workflow

**1. Organization updates hooks**:
```bash
cd /workspace/org-standards
# Edit managed-settings.json
git commit -m "Update context threshold to 20KB"
git push
```

**2. Developers sync**:
```bash
# Mac
cd /workspace/org-standards
git pull
/workspace/org-standards/claude-code/sync-claude-settings.sh

# Container (automatic on rebuild)
# Runs in postCreateCommand
```

**3. Hooks take effect**:
- Restart Claude Code session
- New hooks loaded from ~/.claude/settings.json
- Organization policy enforced ✅

### Path Resolution

**Cross-platform hook paths**:
```bash
/workspace/org-standards/claude-code/hooks/track_reads.py
```

**Works on**:
- ✅ Mac: `/workspace` → `/Users/neerajgarg/NeerajDev` (symlink)
- ✅ Container: `/workspace` → mounted from host
- ✅ ClaudeRunner: Runs in `/workspace` context

## Containers

### Dev Containers

**Setup**: `org-standards/.devcontainer/devcontainer.json`

**postCreateCommand**:
```bash
# 1. Create managed settings symlink (for ClaudeRunner)
sudo mkdir -p /etc/claude-code
sudo ln -sf /workspace/org-standards/claude-code/managed-settings.json /etc/claude-code/managed-settings.json

# 2. Sync hooks to user settings (for Claude CLI) ⭐
/workspace/org-standards/claude-code/sync-claude-settings.sh

# 3. Install Python dependencies...
```

**Result**:
- Container starts
- Hooks automatically synced to `/home/vscode/.claude/settings.json`
- Claude CLI loads hooks ✅
- ClaudeRunner has managed settings symlink (for future if bug fixed)

### CI/CD Containers

**ClaudeRunner behavior** (`bots/common/claude_runner.py`):
1. Auto-deploys managed settings symlink (lines 43-111)
2. Executes: `claude --print "prompt"` (line 215)
3. **BUG**: Symlink ignored, no hooks load ❌

**Workaround needed**:
- Add sync script to ClaudeRunner initialization
- OR: Pre-bake hooks into CI container image
- OR: Run sync script in workflow before ClaudeRunner

**Status**: TODO - ClaudeRunner hooks not yet working

## Verification

### Check if Hooks Are Active

```bash
# View current hooks
cat ~/.claude/settings.json | jq '.hooks'

# Expected output
{
  "PreToolUse": [...],
  "PostToolUse": [...],
  "UserPromptSubmit": [...]
}

# In Claude Code, type:
/hooks

# Should show 3 hook types configured
```

### Test Hook Execution

```bash
# Start Claude Code
claude

# Use Read tool (triggers PreToolUse hook)
# Check tracking file
ls -la /Users/neerajgarg/NeerajDev/syra/.ai-usage-tracking/read-tracking.jsonl

# Send messages (triggers UserPromptSubmit hook)
# Should see warning when messages > 10KB
```

## Troubleshooting

### Hooks Not Firing

**Symptom**: No tracking files created, no warnings shown

**Check**:
```bash
# 1. Verify hooks in settings
cat ~/.claude/settings.json | jq '.hooks | keys'
# Should show: ["PostToolUse", "PreToolUse", "UserPromptSubmit"]

# 2. Verify hook scripts exist
ls -la /workspace/org-standards/claude-code/hooks/track_*.py
# Should show 3 executable Python scripts

# 3. Check Claude Code version
claude --version
# Known bug in v2.0.27-2.0.28: hooks need --debug flag
```

**Fix**:
```bash
# Option 1: Restart Claude with debug flag (workaround for v2.0.27+ bug)
claude --debug

# Option 2: Re-run sync script
/workspace/org-standards/claude-code/sync-claude-settings.sh

# Option 3: Manual hook approval (security feature)
# In Claude Code, type: /hooks
# Review and approve changes
```

### Script Fails: "jq not found"

**Install jq**:
```bash
# Mac
brew install jq

# Linux/Container
apt-get install jq
```

### Script Fails: "org-standards not found"

**Check paths**:
```bash
# Verify /workspace symlink exists
ls -la /workspace

# Mac: Should point to ~/NeerajDev
# Container: Should be mounted volume

# Create symlink if missing (Mac only)
sudo ln -s $HOME/NeerajDev /workspace
```

### Hooks Use Wrong Paths

**Symptom**: Errors like `No such file or directory: /opt/org-standards/...`

**Cause**: Old hook configuration with incorrect paths

**Fix**:
```bash
# Re-run sync script (uses correct /workspace paths)
/workspace/org-standards/claude-code/sync-claude-settings.sh

# Verify paths after sync
cat ~/.claude/settings.json | jq '.hooks.PreToolUse[].hooks[].command'
# Should all start with: python3 /workspace/org-standards/...
```

## Known Issues

### Claude Code Bug: Hook Initialization (v2.0.27+)

**Issue**: Hook initialization incorrectly placed inside debug-mode-only code paths

**Workaround**: Launch Claude Code with `--debug` flag
```bash
claude --debug
```

**Permanent fix**: Wait for Anthropic to patch (tracked in GitHub Issue #10399)

### Managed Settings Ignored

**Issue**: `managed-settings.json` not loaded by Claude CLI (GitHub Issue #6313)

**Workaround**: This sync script (merge hooks into user settings)

**Permanent fix**: Wait for Anthropic to patch

### ClaudeRunner Hooks Not Working

**Issue**: Automation bots (merge-guardian, introspection-bot) don't have hooks

**Cause**: ClaudeRunner uses Claude CLI → doesn't load managed settings

**Workaround**: TODO - Add sync script to ClaudeRunner initialization

**Status**: In progress

## Migration from Old Approach

### What Changed (2025-10-28)

**Before** (broken):
- ❌ Relied on managed-settings.json
- ❌ Assumed Claude CLI loads /Library/Application Support/ClaudeCode/managed-settings.json
- ❌ Hooks never worked (bug undetected)

**After** (working):
- ✅ Sync hooks to ~/.claude/settings.json
- ✅ Claude CLI actually loads user settings
- ✅ Hooks working on Mac (verified with tracking files)
- ⏳ Containers: sync script added to postCreateCommand (pending test)

### Action Required

**Mac developers**:
```bash
# One-time: Sync hooks to your Mac
/workspace/org-standards/claude-code/sync-claude-settings.sh

# Restart Claude Code
exit
claude
```

**Container users**:
- Rebuild container (sync runs automatically in postCreateCommand)
- OR: Manually run sync script inside container

**ClaudeRunner users**:
- TODO: Update ClaudeRunner to run sync script on init
- Until then: Hooks not enforced in automation bots

## Related Documentation

- **Hooks Reference**: `org-standards/claude-code/hooks/README.md`
- **Bug Reports**:
  - [#6313](https://github.com/anthropics/claude-code/issues/6313) - Managed settings ignored
  - [#10399](https://github.com/anthropics/claude-code/issues/10399) - Hooks need --debug flag (v2.0.27+)
- **Original Handoff**: `.ai-sessions/2025-10-28/HANDOFF-hook-configuration-fix.md`

## Future Work

1. **ClaudeRunner integration**: Add sync script to `bots/common/claude_runner.py:__init__`
2. **CI container images**: Pre-bake hooks into base images
3. **Monitor Anthropic fixes**: Remove workaround when bugs patched
4. **Template consistency**: Decide if `settings.template.json` should include hooks (currently excluded)

---

**Last Updated**: 2025-10-28
**Status**: Working on Mac, pending container test
**Owner**: Neeraj Garg
