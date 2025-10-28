# GitHub Actions: Deploy Managed Settings

**Purpose**: Deploy org-standards managed-settings.json for bot workflows using Claude Code CLI

---

## Add to Bot Workflows

**Location**: After installing Claude Code CLI, before running bot

**Workflows to update**:
- `.github/workflows/bot-implementation.yml`
- `.github/workflows/merge-bot.yml`
- `.github/workflows/bot-simple.yml`
- `.github/workflows/test-fresh-deployment.yml`
- Any future workflows using Claude Code CLI

---

## Deployment Code (Option A - Recommended)

**Using $GITHUB_WORKSPACE** (simpler for GitHub Actions):

```yaml
- name: Install Claude Code CLI
  run: npm install -g @anthropic-ai/claude-code

- name: Deploy managed settings
  run: |
    # Deploy org-standards managed-settings.json (organization-wide hooks)
    # CRITICAL: Bots use Claude Code CLI, which requires this for tracking/warnings

    SOURCE="$GITHUB_WORKSPACE/org-standards/claude-code/managed-settings.json"
    TARGET="/etc/claude-code/managed-settings.json"

    # Validate source exists
    if [ ! -f "$SOURCE" ]; then
      echo "ERROR: managed-settings.json not found at $SOURCE"
      echo "Did org-standards submodule checkout fail?"
      ls -la "$GITHUB_WORKSPACE/org-standards/claude-code/" || true
      exit 1
    fi

    # Create system directory and symlink
    sudo mkdir -p /etc/claude-code
    sudo ln -sf "$SOURCE" "$TARGET"

    # Validate JSON and symlink
    python3 -m json.tool "$TARGET" > /dev/null

    # Report success
    echo "✓ Managed settings deployed"
    echo "  Source: $SOURCE"
    echo "  Target: $TARGET (symlink)"
    ls -la "$TARGET"

- name: Run Bot
  run: |
    # Bot now uses Claude Code CLI with org-wide hooks
    python bots/implementation-bot/bot.py --issue ${{ github.event.issue.number }}
```

---

## What This Does

1. ✅ **Creates symlink**: `/etc/claude-code/managed-settings.json` → `$GITHUB_WORKSPACE/org-standards/...`
2. ✅ **Validates JSON**: Ensures file is valid before bot runs
3. ✅ **Reports success**: Shows symlink details in logs
4. ✅ **Enables org-wide hooks**:
   - Read tracking (PreToolUse)
   - Context size tracking (PostToolUse)
   - Message warnings @ 10KB (UserPromptSubmit)

---

## Why Symlink in GitHub Actions?

**Question**: Why symlink instead of copy?

**Answer**: Consistency with Mac/Container approach
- Mac: Symlink to `/workspace/org-standards/...`
- Container: Symlink to `/workspace/org-standards/...`
- GitHub Actions: Symlink to `$GITHUB_WORKSPACE/org-standards/...`

**Benefit**: Same pattern everywhere (easier to understand, debug)

**Note**: GitHub Actions runners are ephemeral (destroyed after run), so symlink vs copy doesn't matter for persistence - we just use symlink for consistency.

---

## Verification

**Check workflow logs for**:
```
✓ Managed settings deployed
  Source: /home/runner/work/syra/syra/org-standards/claude-code/managed-settings.json
  Target: /etc/claude-code/managed-settings.json (symlink)
lrwxrwxrwx ... /etc/claude-code/managed-settings.json -> /home/runner/work/syra/syra/org-standards/...
```

**Bot should create tracking files**:
- `.ai-usage-tracking/read-tracking.jsonl`
- `.ai-usage-tracking/context-tracking.jsonl`
- `.ai-usage-tracking/message-context-tracking.jsonl`

---

## Example: Complete Bot Workflow

```yaml
name: Implementation Bot

on:
  issues:
    types: [labeled]

jobs:
  implement:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive  # CRITICAL: Get org-standards submodule

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Claude Code CLI
        run: npm install -g @anthropic-ai/claude-code

      - name: Deploy managed settings  # ← ADD THIS STEP
        run: |
          SOURCE="$GITHUB_WORKSPACE/org-standards/claude-code/managed-settings.json"
          TARGET="/etc/claude-code/managed-settings.json"

          if [ ! -f "$SOURCE" ]; then
            echo "ERROR: $SOURCE not found"
            exit 1
          fi

          sudo mkdir -p /etc/claude-code
          sudo ln -sf "$SOURCE" "$TARGET"
          python3 -m json.tool "$TARGET" > /dev/null

          echo "✓ Managed settings deployed"
          ls -la "$TARGET"

      - name: Install dependencies
        run: pip install anthropic PyGithub

      - name: Run Bot
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.BOT_GITHUB_TOKEN }}
        run: |
          # Bot uses Claude Code CLI (loads managed-settings.json automatically)
          python bots/implementation-bot/bot.py --issue ${{ github.event.issue.number }}
```

---

## Troubleshooting

### Error: "managed-settings.json not found"

**Cause**: org-standards submodule not checked out

**Fix**: Add to checkout step:
```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive  # ← Add this
```

### Error: "Invalid JSON"

**Cause**: managed-settings.json has syntax error

**Fix**: Validate locally:
```bash
python3 -m json.tool org-standards/claude-code/managed-settings.json
```

### Hooks not executing

**Cause**: Claude Code CLI not loading managed-settings.json

**Debug**:
```yaml
- name: Debug managed settings
  run: |
    echo "Source file:"
    cat "$GITHUB_WORKSPACE/org-standards/claude-code/managed-settings.json"

    echo "Symlink:"
    ls -la /etc/claude-code/managed-settings.json

    echo "Target file (via symlink):"
    cat /etc/claude-code/managed-settings.json
```

---

## Next Steps

1. ✅ Add deployment step to bot workflows
2. ✅ Test workflow runs
3. ✅ Verify tracking files created
4. ✅ Confirm hooks execute (check logs for hook output)

---

## Related Files

- `managed-settings.json` - The actual config
- `org-standards/scripts/setup-neerajdev-workspace.sh` - Mac deployment
- `org-standards/.devcontainer/devcontainer.json` - Container deployment
