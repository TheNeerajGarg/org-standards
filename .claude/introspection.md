# AI Introspection & Learning

**CRITICAL: TOKEN EFFICIENCY FIRST** - Be brief. Only create detailed logs when explicitly requested.

**Full Introspection Standards**: [org-standards/workflow/AI_INTROSPECTION.md](https://github.com/TheNeerajGarg/org-standards/blob/main/workflow/AI_INTROSPECTION.md)

## CRITICAL: Auto-Detect Corrections and Log Immediately

**DO NOT wait for human to say "Log this"** - Automatically create introspection log when you detect a correction.
**KEEP IT BRIEF** - Short acknowledgment + fix. Verbose introspection only when requested.

### Auto-Detection Patterns (MUST create log immediately):

**Human corrects you**:
- "That's wrong" / "That's incorrect" / "No, actually..."
- "You should have..." / "You missed..."
- "Why did you..." (questioning your decision)
- Provides correct information after you gave wrong information
- Points out missing context or assumptions you made
- Redirects you to different approach
- Identifies gap in your understanding

**Explicit triggers** (100% certainty):
- "Log this" / "Log correction"
- "Why did this happen?"
- "What would prevent this?"
- "Add to learnings"
- "Create introspection log"
- "Do an introspection"

### Response Pattern When Trigger Detected:

1. **STOP** current task immediately
2. **CREATE** introspection log: `.ai-sessions/YYYY-MM-DD/correction-HHMMSS.md`
3. **ANALYZE** in the log:
   - What was the correction?
   - Why did I miss/misunderstand it?
   - What context did I lack?
   - How to prevent recurrence?
4. **THEN** continue with corrected approach

**Example of correct response** (CONCISE VERSION):
```
Human: "We don't want workaround, fix root cause"

AI: "Understood. Fixing root cause instead of workaround.
The hook needs to auto-stage the introspection file after validation.
Logged to .ai-sessions/2025-10-13/correction-121620.md"
```

## When Human Corrects You

**Default response** (BRIEF):
```
Understood. [Brief fix]. Logged to .ai-sessions/YYYY-MM-DD/correction-HHMMSS.md
```

**Only if user asks "why?" or "log this with details"**, provide full analysis:

**Key**: Always introspect BOTH:
- What I (AI) was missing
- What you (human) could have provided upfront

## When Human Says "Log this" or "Log correction"

**Immediately create introspection log with this format**:

```markdown
# Introspection Log
**Timestamp**: {current_time}
**Project**: {current_repo}

## What Happened
{Extract from conversation context}

## Human's Correction
{What human said}

## Root Cause (AI's Analysis)
{Analyze: Why did this happen? What context was missing?}

## What Would Prevent This
**Proposed CLAUDE.md update**:
```markdown
{Exact text to add}
```

## Confidence
{1-10 based on how certain this will prevent recurrence}
```

**Save to**: `.ai-sessions/YYYY-MM-DD/correction-HHMMSS.md`

**Then respond to human**:
```
✅ Logged to .ai-sessions/2025-01-13/correction-142530.md

Summary:
- Issue: {brief}
- Root cause: {brief}
- Proposed fix: {brief}
- Confidence: {1-10}/10

Should I apply the fix to CLAUDE.md now? (yes/no)
```

## MANDATORY: Self-Introspection Triggers (Without Human Prompt)

**AI MUST self-introspect immediately when these patterns occur**:

### 1. Repeated Failure (2+ Times Same Error Type)

**Trigger**: Same error/failure happens twice or more

**Examples**:
- Pre-commit hook fails twice with same issue (whitespace, imports)
- Same test fails twice
- Same command fails twice
- Get same error message twice

**Action**:
1. **STOP** immediately after 2nd occurrence
2. **CREATE**: `.ai-sessions/YYYY-MM-DD/self-introspection-HHMMSS.md`
3. **ANALYZE**:
   - What failed (specific error)
   - How many times (count)
   - Why I keep making same mistake
   - What I should do differently (specific tool/command)
4. **PROPOSE**: Update to CLAUDE.md or workflow automation

**Example**:
```
❌ git commit → pre-commit failed: trailing whitespace
❌ git commit → pre-commit failed: EOF newlines
⚠️ PATTERN DETECTED: Whitespace failures (2x)

→ IMMEDIATE ACTION: Create self-introspection log
→ ANALYZE: Why am I not running pre-commit before commit?
→ FIX: Add "Run pre-commit run --files X before git add" to workflow
```

### 2. Tool Rejection by User

**Trigger**: User blocks/rejects a tool use with reason

**Action**:
1. **READ** rejection reason carefully
2. **CREATE**: `.ai-sessions/YYYY-MM-DD/self-introspection-HHMMSS.md`
3. **ANALYZE**:
   - What was I about to do wrong?
   - Why did I think that was correct?
   - What CLAUDE.md rule did I miss?
4. **THEN** proceed with correct approach

### 3. Obvious Preventable Error

**Trigger**: Did something CLAUDE.md explicitly forbids or warns against

**Examples**:
- Suggested workaround instead of root cause fix
- Trusted documentation without checking deployed code
- Skipped Definition of Done checks
- Used wrong workflow labels

**Action**:
1. **CREATE** introspection log immediately
2. **ANALYZE** why I ignored existing guidance
3. **UPDATE** CLAUDE.md with strengthened rule

### Self-Introspection Log Format

```markdown
# Self-Introspection: [Brief Description]

---
**Date**: YYYY-MM-DD
**Time**: HH:MM:SS
**Actor**: AI Assistant (self-initiated)
**Event Type**: repeated-failure | tool-rejection | preventable-error
**Failure Count**: N (if repeated)
**Tags**: [relevant, tags]
---

## What Failed (Repeatedly)

[Description of what went wrong, how many times]

## Why I Kept Failing

**Immediate Cause**: [What I did wrong]
**Root Causes**: [Why I did it wrong]
**Why I Didn't Self-Correct Earlier**: [Meta-analysis]

## How to Prevent This

**Immediate Fix** (Tactical): [Specific command/tool to use]
**Systemic Fix** (Strategic): [Workflow change, automation]

## Actionable Changes

**CLAUDE.md Updates**:
- [ ] [Specific addition]

**Workflow Changes**:
- [ ] [Specific process change]

## Confidence

Rating: X/10
Why: [Justification]
```

### Key Principle: Proactive vs Reactive

**DON'T WAIT** for human to ask "Why did you fail?"

**Self-Monitor**: Track your own error patterns
**Self-Correct**: Create introspection when you detect pattern
**Self-Improve**: Propose prevention mechanisms

**Current introspection is reactive** (human-initiated)
**Needed introspection is proactive** (self-initiated on pattern detection)

## Quick Logging Commands

When human says any of these, create introspection log:

- **"Log this"** - Log the current issue/correction
- **"Log correction"** - Same as above
- **"Why did this happen?"** - Create log with root cause analysis
- **"What would prevent this?"** - Create log with prevention strategy
- **"Add to learnings"** - Create log and update CLAUDE.md immediately

## Examples

**Human**: "Log this: You used StyleGuru when this should go in syra"

**AI Response**:
```
✅ Logged to .ai-sessions/2025-01-13/correction-143000.md

Summary:
- Issue: Wrong repository (used StyleGuru instead of syra)
- Root cause: Repository guide exists but not clear enough about dev tools
- Proposed fix: Strengthen "Rule of thumb" with bold emphasis
- Confidence: 7/10

Proposed CLAUDE.md update:
**RULE**: ALL dev tooling goes in Syra. ALL product features go in StyleGuru.

Should I apply this fix now?
```

## MANDATORY: Introspection-First Commit Workflow

**CRITICAL**: Pre-commit hooks require an introspection document. Create it BEFORE staging files.

**Correct Workflow**:
```bash
# 1. Complete your work (code, tests, docs)
# ... write code, tests, etc ...

# 2. CREATE INTROSPECTION DOCUMENT (use ANY descriptive name - no hash required!)
cat > .ai-sessions/$(date +%Y-%m-%d)/fix-provider-bug.md <<'EOF'
# Introspection: Fix Provider Authentication Bug

## What Changed
Fixed authentication token refresh logic in provider.py

## Why This Change
Users were experiencing 401 errors after 1 hour of usage.

## How to Prevent Similar Issues
Add integration test for token refresh scenarios.

## Confidence Level
8/10 - Fix tested locally, needs monitoring in production.
EOF

# 3. Stage ALL files INCLUDING introspection
git add src/provider.py \
        tests/test_provider.py \
        .ai-sessions/$(date +%Y-%m-%d)/fix-provider-bug.md

# 4. Commit (hook will find introspection and pass first time)
git commit -m "fix: provider token refresh logic"
```

**Valid Introspection File Names**:
- Descriptive: `fix-auth-bug.md`, `add-provider-support.md`, `refactor-core.md`
- Generic: `task-completion.md`, `commit-description.md`
- Timestamped: `143000-feature.md`, `session-work.md`

**Why This Matters**:
- Pre-commit hook checks for ANY `.md` file in `.ai-sessions/YYYY-MM-DD/`
- No hash dependency = no circular dependency issues
- Descriptive names improve traceability

**Introspection Template** (use `.ai-session-template.md` as starting point):
```markdown
# Introspection: [Task/Change Title]

**Timestamp**: [ISO timestamp]
**Type**: [Feature/Bugfix/Refactor/etc]

## What Changed
- File 1: [description]
- File 2: [description]

## Why This Change
[Problem being solved, business value, decision rationale]

## How to Prevent Similar Issues
[Lessons learned, prevention strategies, what would help catch this earlier]

## Root Cause Analysis (if applicable)
[Why was this needed? What was the underlying issue?]

## Confidence Level
[1-10 with rationale]

## Next Steps
[What comes after this]
```

**Common Mistakes**:
- ❌ Staging files, then creating introspection → Hash changes, hook fails again
- ❌ Using `--no-verify` to bypass → Loses introspection benefit
- ✅ Creating introspection FIRST, then staging everything → Works first time

**See**: [.ai-sessions/2025-10-14/learning-introspection-workflow.md](.ai-sessions/2025-10-14/learning-introspection-workflow.md)
