# Context Management Protocol

**Purpose**: Prevent context loss between AI sessions by maintaining LATEST_CONTEXT.md

**Problem**: Directory moves, architecture changes, and workflow updates are invisible to future AI sessions, causing confusion and wasted time investigating false alarms.

**Solution**: Clear triggers for when to update LATEST_CONTEXT.md, plus verification that updates actually prevent confusion.

---

## Core Principle

> "Would a fresh AI session, starting with zero context, understand this change by reading LATEST_CONTEXT.md?"

If NO → Update LATEST_CONTEXT.md before ending session

---

## When to Update LATEST_CONTEXT.md

### ✅ Directory Structure Changes (CRITICAL)

**Trigger**: Any of these directory operations:
- Created new top-level directory (e.g., `src/new-component/`)
- Deleted directory with >5 files
- Moved directory between locations
- Moved directory between repos (StyleGuru ↔ Syra ↔ org-standards)
- Renamed major directory

**Why Critical**: Git status shows files as "deleted" → triggers false alarm

**Example Entry**:
```markdown
### [Directory Name] Migration (2025-MM-DD)
- **What**: Moved X files from [old location] to [new location]
- **Why**: [Reason - e.g., separation of concerns]
- **What Moved**: [Brief list or count]
- **What Stayed**: [If partial move]
- **Location Now**: [New paths in each repo]
- **Impact**: Git status shows N "deleted" files (expected, intentional)
- **Status**: Migration complete
```

---

### ✅ File Migrations (HIGH PRIORITY)

**Trigger**: Moved >10 files at once

**Examples**:
- Moved all BRD/PRD docs to different directory
- Reorganized test files
- Consolidated scattered configs
- Archived old code

**Example Entry**:
```markdown
### [File Type] Reorganization (2025-MM-DD)
- **What**: Moved [file type] from [old pattern] to [new pattern]
- **Count**: N files moved
- **Reason**: [Why - e.g., standardization, clarity]
- **New Pattern**: [Where to find them now]
- **Impact**: [What changes for users/bots]
```

---

### ✅ Document Storage Changes (HIGH PRIORITY)

**Trigger**: Changed where/how BRDs/PRDs/ERDs are stored

**Examples**:
- BRDs now in GitHub issues instead of files
- PRDs moved from `.workflow-poc/` to `docs/PRD/`
- ERDs split into component-specific files

**Example Entry**:
```markdown
### [Document Type] Storage Change (2025-MM-DD)
- **Old**: [Previous location/format]
- **New**: [New location/format]
- **Examples**:
  - Document X: [Location]
  - Document Y: [Location]
- **Reason**: [Why changed]
- **Migration**: [How to find old docs]
```

---

### ✅ Architecture Decisions (MEDIUM PRIORITY)

**Trigger**: Made decision that changes how system works

**Examples**:
- Separation of concerns (bot code vs product code)
- Changed repository responsibilities
- New cross-repo dependencies
- Schema format changes (JSON → JSON-LD)

**Example Entry**:
```markdown
### [Decision Name] (2025-MM-DD)
- **Decision**: [What was decided]
- **Reason**: [Why]
- **Impact**: [How it changes things]
- **New Pattern**: [What to do going forward]
- **References**: [Related docs]
```

---

### ✅ Standards Updates (MEDIUM PRIORITY)

**Trigger**: Created new `.claude/*.md` file or updated standards

**Examples**:
- New `.claude/schema-standards.md`
- Updated testing strategy
- New coding conventions
- Changed workflow process

**Example Entry**:
```markdown
### [Standard Name] (2025-MM-DD)
- **New Standard**: [Brief description]
- **Location**: [Path to doc]
- **Applies To**: [Which repos/components]
- **Key Rules**: [3-5 bullet points]
- **Reference**: [Link to full doc]
```

---

### ✅ Workflow Changes (MEDIUM PRIORITY)

**Trigger**: Changed how work gets done

**Examples**:
- New git workflow
- Changed CI/CD process
- New approval gates
- Bot automation added/removed

**Example Entry**:
```markdown
### [Workflow Name] Change (2025-MM-DD)
- **Old Workflow**: [Previous process]
- **New Workflow**: [Updated process]
- **Reason**: [Why changed]
- **Impact**: [What's different for users]
```

---

### ✅ Cross-Repo Changes (HIGH PRIORITY)

**Trigger**: Changes affecting multiple repos

**Examples**:
- Shared library moved
- New dependency between repos
- Changed which repo owns what

**Example Entry**:
```markdown
### Cross-Repo: [Change Name] (2025-MM-DD)
- **Repos Affected**: [List]
- **What Changed**: [Description]
- **New Structure**:
  - Repo A: [Responsibilities]
  - Repo B: [Responsibilities]
- **Dependencies**: [What depends on what]
```

---

### ✅ Session Handoffs (LOW PRIORITY)

**Trigger**: End of day, switching contexts, or major milestone

**Examples**:
- End of work session
- Switching from VSCode to Claude Desktop
- Completed major feature
- Before context switch to different project

**Example Entry**:
```markdown
### Session Summary (2025-MM-DD)
- **What Was Done**: [Brief summary]
- **Current State**: [Where things are]
- **Next Steps**: [What's queued up]
- **Blockers**: [If any]
- **Key Decisions**: [If any made]
```

---

## Session End Checklist

**Before ending EVERY session**, ask yourself:

```markdown
## Did I Update LATEST_CONTEXT?

1. **Directory Changes?**
   - [ ] Created/deleted/moved directories?
   - [ ] Moved files between repos?

   If YES → Update LATEST_CONTEXT.md

2. **Document Storage Changes?**
   - [ ] Changed where BRDs/PRDs/ERDs live?
   - [ ] New storage pattern?

   If YES → Update LATEST_CONTEXT.md

3. **Architecture Decisions?**
   - [ ] Made separation of concerns decisions?
   - [ ] Changed repo responsibilities?
   - [ ] New standards or patterns?

   If YES → Update LATEST_CONTEXT.md

4. **Would Fresh Session Be Confused?**
   - [ ] Missing files that used to exist?
   - [ ] New locations not documented?
   - [ ] Changed workflows?

   If YES → Update LATEST_CONTEXT.md

5. **Created New `.claude/*.md` Files?**
   - [ ] New standards documents?
   - [ ] Updated CLAUDE.md to reference them?

   If YES → Update LATEST_CONTEXT.md AND CLAUDE.md
```

---

## How to Update LATEST_CONTEXT.md

### Step 1: Add to "Recent Discoveries" Section

Location: `.ai-sessions/LATEST_CONTEXT.md` → "## Recent Discoveries (Last 7 Days)"

### Step 2: Use Template Above

Pick the appropriate template from "When to Update" section

### Step 3: Include These Elements

- **What changed**: Clear description
- **Why**: Reason for change
- **Where things live now**: Exact paths/locations
- **Impact**: What this means for future sessions
- **Status**: Complete/In Progress/Planned

### Step 4: Date the Entry

Format: `### [Name] (YYYY-MM-DD)`

### Step 5: Keep Only Last 7 Days

- Archive entries older than 7 days
- Move to Problem Registry if recurring issue
- Keep LATEST_CONTEXT focused on recent changes

---

## Verification: Does Update Actually Help?

### The Test

After updating LATEST_CONTEXT.md, ask:

> "If I started a completely fresh session tomorrow, would reading LATEST_CONTEXT prevent confusion about this change?"

**Good Update** ✅:
- Fresh session reads entry
- Understands what changed
- Knows where things are now
- Doesn't panic about "deleted" files

**Bad Update** ❌:
- Entry too vague
- Missing crucial details (locations, counts)
- Doesn't explain "deleted" files in git status
- Future session would still investigate

### Quick Verification Script

```bash
# Check if deleted files are documented
git status | grep "^D" > /tmp/deleted.txt
cat .ai-sessions/LATEST_CONTEXT.md | grep -f /tmp/deleted.txt

# If grep finds matches → Good (documented)
# If no matches → Bad (update needed)
```

---

## Anti-Patterns to Avoid

### ❌ Vague Entries

**Bad**:
```markdown
### Cleanup (2025-10-15)
- Cleaned up some files
```

**Good**:
```markdown
### .workflow-poc Migration to Syra (2025-10-15)
- **What**: Moved 193 files to Syra repo
- **Why**: Separation of concerns
- **Location**: `syra/.workflow-poc/`
- **Impact**: Git shows 193 "deleted" files (expected)
```

---

### ❌ Missing Locations

**Bad**:
```markdown
### Moved BRDs
- BRDs were moved
```

**Good**:
```markdown
### BRD Storage Change (2025-10-15)
- **Old**: `.workflow-poc/1-BRD/*.md`
- **New**: GitHub issue bodies + `docs/brd/*.md`
- **Examples**:
  - Multi-item BRD: Issue #52 body
  - Bot infrastructure BRD: `docs/brd/BRD-base-bot-infrastructure.md`
```

---

### ❌ No Impact Statement

**Bad**:
```markdown
### Directory moved
- `.workflow-poc/` moved to Syra
```

**Good**:
```markdown
### .workflow-poc Migration to Syra (2025-10-15)
- [Full details...]
- **Impact**: Future sessions see 193 "deleted" files in git status (expected, intentional)
- **Action**: No recovery needed, files in correct location
```

---

## Repository Responsibility Matrix

**Quick Reference: "Where does this file belong?"**

| File Type | Belongs In | Why |
|-----------|------------|-----|
| BRD/PRD/ERD (product features) | StyleGuru `docs/brd/`, `docs/PRD/`, `.workflow-poc/ERD/` | Product-specific documents |
| BRD/PRD/ERD (bots/workflow) | Syra `docs/brd/`, `docs/PRD/` | Bot infrastructure documents |
| Bot code (reusable) | Syra `bots/` | Shared bot infrastructure |
| Bot code (product-specific) | StyleGuru `.ai-bots/` | StyleGuru-only bots |
| Workflow orchestration | Syra `.workflow-poc/` | Workflow engine |
| Product features | StyleGuru `src/` | Extractor, crawler, viewer |
| Shared standards | org-standards | Cross-project standards |
| AI introspection logs | `.ai-sessions/` (each repo) | Repo-specific learnings |
| Claude instructions | `.claude/` (each repo) | Repo-specific AI guidance |

**When Moving Files Between Repos**:
1. Move the files
2. Update LATEST_CONTEXT.md in BOTH repos
3. Update cross-references in docs
4. Commit with clear message: `migrate: move X to Y for [reason]`

---

## Success Metrics

### Short-term (This Week)

- [ ] LATEST_CONTEXT updated for .workflow-poc migration
- [ ] Next 3 sessions reference LATEST_CONTEXT without confusion
- [ ] Zero false alarms about "deleted" files

### Medium-term (This Month)

- [ ] 80%+ of fresh sessions check LATEST_CONTEXT first
- [ ] Session end checklist used in 50%+ of sessions
- [ ] LATEST_CONTEXT prevents 5+ confusion incidents

### Long-term (Success)

- [ ] User confidence in documentation system restored
- [ ] Zero wasted time investigating false alarms
- [ ] LATEST_CONTEXT becomes habit, not exception

---

## Related Documents

- **LATEST_CONTEXT.md**: The file this protocol manages
- **CLAUDE.md**: Will reference this protocol
- **.ai-session-template.md**: Introspection template
- **PROBLEM_REGISTRY.md**: Searchable catalog of recurring issues

---

## Maintenance

**Review this protocol**:
- Monthly: Check if triggers still comprehensive
- After confusion incident: Add missing trigger
- After 10+ sessions: Assess effectiveness, adjust

**Update LATEST_CONTEXT**:
- Daily: During session if major changes
- Weekly: Archive entries >7 days old
- Monthly: Prune stale items, keep focused

---

**Last Updated**: 2025-10-15
**Next Review**: 2025-11-15
