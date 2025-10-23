# Development Workflow Process

## CRITICAL: Workflow Context (Read This First!)

**Development Model**: Single human (Neeraj) orchestrating AI bot swarm
- **Real constraint**: $ budget for AI API calls (NOT human engineering time)
- **Bottleneck**: Neeraj's review bandwidth (30-60 min/week)
- **No team coordination**: One person decides → Bots execute → Review → Iterate
- **"Separate team building X"** = Separate bot workstream (no coordination needed)

**Key Implications**:
1. ❌ Don't ask: "Who's on the team? Who's building this? How many engineers?"
2. ✅ Do ask: "What's the $ budget? What review cadence works for you?"
3. ❌ Don't estimate: "3 engineers for 4 weeks"
4. ✅ Do estimate: "$X for AI development + $Y for runtime + Z review cycles"
5. **Always provide line-item cost breakdown upfront** (never trust high-level estimates without validation)

**Document Scope Boundaries** (CRITICAL - prevents scope creep):
- **PRD** = WHAT to build (400-600 lines, max 800) - Feature descriptions, acceptance criteria, UI mockups, success metrics
- **ERD** = HOW to build (800-1200 lines) - Architecture, algorithms, schemas, API contracts, code
- **Stop signs**: If PRD has code blocks, complete JSON schemas, or implementation algorithms → Move to ERD

## Before Writing Any Code

ALL significant development MUST follow this process:

1. **BRD (Business Requirements Document)**: Define the problem and business value
2. **PRD (Product Requirements Document)**: Define the solution and requirements
3. **ERD (Engineering Requirements Document)**: Define the technical design
4. **Implementation**: Write the code

**NEVER skip this process unless**:
- User explicitly says "just implement X" or "skip the docs"
- It's a trivial fix (< 5 lines of code)
- It's an emergency hotfix

**If user asks you to implement something significant, STOP and say**:
```
⚠️  This requires following the BRD → PRD → ERD process.

Should I:
1. Create a BRD first (recommended)
2. Skip to implementation (if this is trivial)

Which would you prefer?
```

## When to Ask Clarifying Questions

ALWAYS ask before proceeding when:
- **Multiple repos could be the target** (StyleGuru, syra, org-standards)
- **Multiple workflows exist** (V1 GitHub Actions, Syra workflows)
- **Architectural decision needed** (build vs buy, which framework)
- **Uncertain about requirements** (ambiguous scope, missing context)
- **Process unclear** (which workflow to follow)

## V1 Workflow: BRD → PRD → ERD (Bot-Driven)

**Current Implementation**: GitHub Actions with bot reviewers (NO Supabase)

**How It Works**:
1. **Create GitHub Issue** with BRD/PRD/ERD content
2. **Add Labels** to trigger bot reviews:
   - `engineering-pending` - Needs engineering review
   - `ux-pending` - Needs UX review
   - `pm-pending` - Needs PM review
   - `review-task` - Mark as review task
3. **Bots Auto-Review**: GitHub Actions (`reviewer-bots.yml`) runs every minute
   - Reads issue content
   - Reviews with Claude
   - Posts comments with feedback
4. **Human Responds**: Answer questions in issue comments
5. **Bots Re-Review**: Automatically pick up human responses
6. **Generate Next Doc**: PRD bot, ERD bot auto-create follow-on documents

**Files**:
- Workflows: `.github/workflows/reviewer-bots.yml`, `prd-bot.yml`, `erd-bot.yml`
- Bots: `.workflow-poc/phase1/bot_reviewer_github.py`

**To Use V1 Workflow**:
```bash
# 1. Create issue with BRD content
gh issue create --title "BRD: [Feature Name]" --body "$(cat your-brd.md)"

# 2. Add labels to trigger reviews
gh issue edit <issue-number> --add-label "engineering-pending,ux-pending,pm-pending,review-task"

# 3. Wait for bot reviews (runs every minute)
# Bots will post comments with feedback

# 4. Answer questions in issue comments
# Bots automatically detect human responses and re-review
```

## CRITICAL: Check Deployed State Before Suggesting Setup

**BEFORE suggesting "we need to set up X", ALWAYS verify current state**:

1. **Check what's deployed**:
   ```bash
   ls .github/workflows/              # Check GitHub Actions
   gh workflow list                    # Check active workflows
   ```

2. **Read deployed code, not just docs**:
   - **Documentation may be outdated** (describes aspirations)
   - **Implementation is source of truth** (shows reality)
   - **Recent commits show changes**: `git log --oneline | head -20`

3. **Test assumptions**:
   ```bash
   # Don't assume Supabase needed - check if referenced
   grep -r "supabase" .github/workflows/

   # Don't assume setup needed - check if already running
   gh workflow list | grep -i "brd\|review"
   ```

**Rule**: Deployed Code > Recent Commits > Documentation

**Why**: Documentation describes plans/aspirations, deployed code describes current reality

## Repository Guide

**StyleGuru** (`/Users/neerajgarg/StyleGuru/`, repo: `StyleGuru/StyleGuru`):
- Product code for StyleGuru fashion AI
- V1 workflow in `.github/workflows/` (GitHub Actions, active, no Supabase)
- V1 bots in `.workflow-poc/phase1/` (bot_reviewer_github.py)
- V2 in `.workflow-poc/v2/` (vision docs only, not implemented)
- Use for: Product features, fashion AI improvements

**syra** (`/Users/neerajgarg/syra/`):
- Dev tooling, bot infrastructure, AI workflows
- Clean architecture, Phase 0 (foundation)
- Use for: Dev tools, introspection, bot systems, workflow infrastructure

**org-standards** (`/Users/neerajgarg/org-standards/`):
- Shared coding standards across all projects
- Use for: Standards that apply to multiple projects

**Rule of thumb**: Dev tools → Syra, Product features → StyleGuru, Shared standards → org-standards

## Organization Priorities

**Read `/Users/neerajgarg/PRIORITIES.md` before starting any significant work.**

**Mission**: Learn what blocks 10× software development productivity (full SDLC, not just coding)

**Current Phase**: Discovery - go broad, find all problems, document root causes, solve tactically

**Key Projects**:
- **StyleGuru** (StyleGuru): Real product for revenue + learning
- **Syra**: Productize SDLC learnings
- **Playground**: Rapid experimentation

**When task doesn't clearly fit priorities → Ask before starting**

## Repository Rename Checklist

**When a repository is renamed, update ALL references systematically.**

### Step-by-Step Process

1. **Update git remote**:
   ```bash
   git remote set-url origin <new-url>
   git remote -v  # Verify
   ```

2. **Find ALL references**:
   ```bash
   grep -r "old-repo-name" . --exclude-dir=.git --exclude-dir=node_modules
   ```

3. **Update systematically** (check each):
   - [ ] `.github/workflows/*.yml` - Checkout paths, repo names
   - [ ] `.ai-sessions/LATEST_CONTEXT.md` - Project name
   - [ ] `.ai-sessions/PROBLEM_REGISTRY.md` - Project references
   - [ ] `.ai-sessions/*/*.md` - All introspection logs (Project field)
   - [ ] `CLAUDE.md` - Repository references
   - [ ] `README.md` - Project name, links
   - [ ] Documentation files (`docs/**/*.md`)
   - [ ] Bot configuration files (`bots/**/config`)
   - [ ] Docker configs (`Dockerfile`, `docker-compose.yml`)
   - [ ] CI/CD configs (`.github/workflows`, `.gitlab-ci.yml`)
   - [ ] Package files (`package.json`, `setup.py`, `pyproject.toml`)

4. **Use variables instead of hardcoding**:
   - ✅ `${{ github.repository }}` (owner/repo)
   - ✅ `${{ github.repository_owner }}` (owner)
   - ❌ Hardcoded "old-name" or "new-name"

5. **Verify completeness**:
   ```bash
   grep -r "old-repo-name" . --exclude-dir=.git --exclude-dir=node_modules
   # Should return ZERO results (except this checklist)
   ```

6. **Commit once**: All changes in single commit
   ```bash
   git add -A
   git commit -m "refactor: complete repo rename from old-name to new-name"
   ```

### Common Mistakes to Avoid

- ❌ **Only updating git remote** - Leaves references inconsistent
- ❌ **Updating workflows but not docs** - Half-done rename
- ❌ **Continuing to create new files with old name** - Compounds problem
- ❌ **Not using GitHub context variables** - Creates maintenance burden

### Why This Matters

**Incomplete renames cause**:
- Confusion (What's the repo name?)
- Broken searchability (Can't find all references)
- Documentation debt (Every new file compounds issue)
- Signals sloppiness (Basics wrong → What else is wrong?)

**Complete renames provide**:
- Consistency across all files
- Easy searchability
- Professional polish
- Reduced future maintenance
