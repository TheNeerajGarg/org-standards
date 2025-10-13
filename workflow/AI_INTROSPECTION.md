# AI Introspection Standards

**Purpose**: Capture learnings from human-AI interactions to prevent recurring mistakes and improve AI assistant effectiveness.

## MANDATORY: Automatic Introspection Logging

### When to Create Introspection Logs

**ALWAYS create introspection log IMMEDIATELY when**:

1. **Human corrects you** - Any correction, big or small
2. **Human says explicit trigger** - "Log this", "Log correction", "Why did this happen?"
3. **You make a mistake** - Even if human doesn't explicitly correct
4. **Unexpected behavior occurs** - Bug, error, wrong assumption

**DO NOT wait for human to say "Log this"** - Auto-detect corrections and log immediately.

### Auto-Detection Patterns

Create log automatically when human says:
- "That's wrong" / "That's incorrect" / "No, actually..."
- "You should have..." / "You missed..."
- "Why did you..." (questioning your decision)
- Provides correct information after you gave wrong information
- Points out missing context or assumptions

### Introspection Log Format

**Location**: `.ai-sessions/YYYY-MM-DD/correction-HHMMSS.md`

**Required Template**:
```markdown
# Introspection Log
**Timestamp**: {ISO 8601 timestamp}
**Project**: {repo name}
**Context**: {what you were working on}

## What Happened
{Extract relevant conversation showing the mistake}

## Human's Correction
{What human said - exact quote}

## Root Cause Analysis
**Why did this happen?**
{Deep analysis: What context was missing? What did I assume? What pattern failed?}

**What was I missing?**
{Specific information, context, or understanding I lacked}

**What pattern/heuristic failed?**
{Which mental model or decision rule led me astray?}

## Prevention Strategy

**Immediate (Tactical)**:
{What specific text should be added to CLAUDE.md NOW?}

```markdown
{Exact CLAUDE.md addition}
```

**Strategic (Requires Discussion)**:
{What systemic changes would prevent this class of errors?}
- Tool changes
- Workflow changes
- Context architecture changes

## Impact Assessment
**Severity**: {Low/Medium/High/Critical}
**Frequency**: {How often does this class of error occur?}
**Blast Radius**: {How much damage did/could this cause?}

## Proposed Fix
**Should apply to CLAUDE.md?**: {Yes/No}
**Confidence**: {1-10}/10
**Rationale**: {Why this fix will/won't work}

## What Human Could Have Done Differently
{How could human have provided context upfront to prevent this?}
{This is NOT blame - it's about improving the human-AI interface}
```

### Response Pattern After Creating Log

After creating introspection log, ALWAYS respond to human with:

```
✅ Logged to .ai-sessions/YYYY-MM-DD/correction-HHMMSS.md

📊 **Summary**:
- Issue: {one sentence}
- Root cause: {one sentence}
- Proposed fix: {one sentence}
- Confidence: {N}/10

**Proposed CLAUDE.md update**:
```markdown
{show the exact addition}
```

Should I apply this fix to CLAUDE.md now? (yes/no)
```

### Integration with Git Workflow

**Pre-commit hook**: Gate 1 validates introspection document exists for every commit

**GitHub workflows** (syra):
- `capture-learning.yml`: Analyzes new logs when pushed
- `hourly-analysis.yml`: Identifies patterns across logs
- `daily-review.yml`: Daily summary and recommendations

### Examples

#### Example 1: Wrong Repository Choice

**Human**: "This should go in syra, not fashion-extract"

**AI Action** (automatic):
1. Create `.ai-sessions/2025-10-13/correction-124530.md`
2. Analyze: Why did I choose wrong repo?
3. Propose: Strengthen repository guide in CLAUDE.md
4. Ask: Should I apply fix?

**DO NOT just say**: "You're right, let me fix that"

#### Example 2: Missing Context

**Human**: "We already have a function for this in utils.py"

**AI Action** (automatic):
1. Create introspection log
2. Analyze: Why didn't I search for existing code?
3. Propose: Add "search before implement" to CLAUDE.md
4. Ask: Should I apply fix?

#### Example 3: Incorrect Assumption

**Human**: "No, we use pytest-asyncio, not asyncio"

**AI Action** (automatic):
1. Create introspection log
2. Analyze: Why did I assume wrong framework?
3. Propose: Add testing framework list to CLAUDE.md
4. Ask: Should I apply fix?

## Quality Standards

### Good Introspection Log

✅ **Root cause identified**: "I chose wrong repo because 'dev tools' wasn't bolded"
✅ **Specific fix proposed**: "Add **RULE**: Dev tools → Syra to CLAUDE.md line 65"
✅ **Confidence assessed**: "8/10 - high confidence this prevents recurrence"
✅ **Human context considered**: "You could have said 'in syra' upfront"

### Poor Introspection Log

❌ **No root cause**: "I made a mistake"
❌ **Vague fix**: "Add more documentation"
❌ **No confidence**: Missing confidence rating
❌ **No human feedback**: Doesn't suggest how human could help

## Metrics and Success Criteria

**Track**:
- Correction frequency (should decrease over time)
- Repeat errors (same root cause = fix didn't work)
- Confidence accuracy (were 9/10 fixes actually effective?)
- Coverage (% of corrections logged)

**Success**:
- Decreasing correction rate
- Zero repeat errors after fix applied
- High confidence fixes are 90%+ effective
- 100% of corrections logged

## Related Standards

- [Definition of Done](./DEFINITION_OF_DONE.md) - Task completion criteria
- [BRD→PRD→ERD Workflow](../README.md#workflow) - Development process
- Syra Introspection System - Automated analysis workflows

---

**Last Updated**: 2025-10-13
**Status**: Active (deployed to syra GitHub workflows)
