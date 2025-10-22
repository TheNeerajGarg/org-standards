# Context Warning Hook

Automatically warns when Claude Code context grows too large, helping prevent expensive API costs.

## What It Does

Tracks two metrics per session:
1. **Message count**: Warns at 15 messages (configurable)
2. **Large file reads**: Warns after 2 large files (>20K tokens each)

## Why It Matters

**Cost Example**: A session with 50 messages + 3 large docs (30K tokens each):
```
Estimated context: 15K (system) + 100K (messages) + 90K (files) = 205K tokens
Cost per API call: 205K × $3/M = $0.615 per message
50 messages = $30.75 just for that session
```

With warnings at message 15:
```
Estimated context: 15K (system) + 30K (messages) = 45K tokens
Cost per API call: 45K × $3/M = $0.135 per message
15 messages = $2.03 per session
```

**Savings**: 15× cheaper by starting fresh sessions frequently!

## Installation

Already installed if you're reading this! The hook is configured in:
- `~/.claude/settings.local.json` (user-level)
- Or `.claude/settings.json` (project-level)

## Configuration

Customize thresholds via environment variables:

```bash
# In ~/.zshrc or ~/.bashrc
export CLAUDE_MAX_MESSAGES=15           # Warn after N messages (default: 15)
export CLAUDE_MAX_LARGE_FILES=2         # Warn after N large files (default: 2)
export CLAUDE_LARGE_FILE_THRESHOLD=20000 # "Large" file token threshold (default: 20K)
```

## What You'll See

### Message Limit Warning (at 15 messages)
```
⚠️  WARNING: Context limit reached: 15 messages in this session
   💡 Consider exiting and starting fresh session to reduce API costs
   💰 Every message now includes 15+ previous messages
   📊 Context size is cumulative and grows with each interaction
```

### Large File Read Warning
```
⚠️  WARNING: Large file read: ~30,862 tokens (docs/BRD.md)
   📄 This file will be in context for ALL future API calls in this session
   📊 Large reads so far: 1/2
   💡 Tip: Use Grep to search instead of reading entire files
```

### Critical Context Warning (every 5 messages after limit)
```
❌ CRITICAL: High context: 25 messages (recommended: 15)
   💸 API costs are likely 3-5× normal due to large context
```

### Total Context Estimate (every 5 messages)
```
❌ CRITICAL: Estimated context size: ~126,000 tokens
   💰 Each API call costs ~$0.378 in input tokens alone
   📊 Context breakdown:
      - Messages: 25 × ~2K = ~50,000 tokens
      - Large files: 2 × ~30K = ~60,000 tokens
   🔄 STRONGLY RECOMMEND: Exit and start fresh session
```

## Best Practices

### ✅ DO
- Exit Claude after 15 messages (when warning appears)
- Use `Grep` to search files instead of `Read`
- Read large docs in separate short sessions
- Start fresh sessions for each major task

### ❌ DON'T
- Ignore the warnings
- Read BRD/PRD/ERD files in long sessions
- Let sessions grow beyond 20 messages
- Keep container Claude sessions running for hours

## Manual Session Reset

If you want to manually reset counters:

```bash
# Reset context tracking for current session
rm ~/.claude/context_tracker/pid-*

# View current session stats
ls -lh ~/.claude/context_tracker/
```

## Disabling the Hook

To temporarily disable:

```bash
# Remove from settings.local.json
# Or set very high thresholds:
export CLAUDE_MAX_MESSAGES=999
export CLAUDE_MAX_LARGE_FILES=999
```

## Troubleshooting

### Hook not showing warnings

Check if hook is running:
```bash
# View hook errors (if any)
cat ~/.claude/context_tracker/context_warning_errors.log
```

### False positives

Adjust thresholds:
```bash
export CLAUDE_MAX_MESSAGES=20  # More lenient
export CLAUDE_LARGE_FILE_THRESHOLD=30000  # Only warn on very large files
```

## Related

- **Post Tool Use Hook**: Logs tool failures
- **Session End Hook**: Runs cleanup at session end
- See `~/org-standards/claude-code/introspection/README.md` for full hook system
