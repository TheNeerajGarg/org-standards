# Claude Memory Sync Workflow

**Goal**: Keep Git as single source of truth while leveraging Claude's memory hierarchy

## Architecture

```
Git Repository (Source of Truth)
├── CLAUDE.md                          # Project-specific rules
├── .claude/
│   ├── org-context.md                 # Organization context (cross-repo)
│   ├── workflow.md                    # Project workflow
│   ├── architecture.md                # Project architecture
│   └── ...other docs...

User Memory (Imports from Git)
└── ~/.claude/CLAUDE.md                # Imports org-context.md from Git
```

## How It Works

### Memory Loading Hierarchy

When Claude Code starts, it loads memory in this order:

1. **User memory**: `~/.claude/CLAUDE.md`
   - Imports: `@/workspaces/fashion-extract/.claude/org-context.md`
   - Contains: Personal preferences, cross-project context

2. **Project memory**: `/workspaces/fashion-extract/CLAUDE.md`
   - Contains: Project-specific rules (Top 10 Critical Rules)
   - References: Links to `.claude/*.md` documentation

3. **Detailed docs**: Loaded on-demand via `@` syntax
   - Example: `@.claude/workflow.md` when needed

### Workflow: Updating Organization Context

**To update cross-project rules** (applies to ALL repositories):

```bash
# 1. Edit org-context.md in Git
vim /workspaces/fashion-extract/.claude/org-context.md

# 2. Commit and push to main
git add .claude/org-context.md
git commit -m "docs: update organization context"
git push origin main

# 3. Changes automatically available in next Claude session
# No manual sync needed - ~/.claude/CLAUDE.md imports from Git repo
```

### Workflow: Updating Project-Specific Rules

**To update project-specific rules** (StyleGuru only):

```bash
# 1. Edit CLAUDE.md or .claude/*.md files
vim CLAUDE.md
vim .claude/workflow.md

# 2. Commit and push to main
git add CLAUDE.md .claude/workflow.md
git commit -m "docs: update project workflow"
git push origin main

# 3. Changes available in next session
```

## Key Benefits

✅ **Git is source of truth**: All memory files checked into version control
✅ **Automatic sync**: User memory imports from Git, no manual copying
✅ **Cross-project consistency**: Organization context shared via import
✅ **Reduced token usage**: User memory loaded once, project memory is smaller
✅ **Collaboration ready**: Team members get same context from Git

## File Responsibilities

### In Git (Version Controlled)

**`.claude/org-context.md`** - Cross-project context:
- Development model (bot swarm, constraints)
- Repository map (StyleGuru, syra, org-standards)
- Global philosophy (root cause fixes, 5 whys)
- Communication style

**`CLAUDE.md`** - Project-specific:
- Project overview (fashion AI engine)
- Top 10 Critical Rules
- Development commands
- Business context

**`.claude/*.md`** - Detailed documentation:
- Workflow, architecture, testing, quality standards, etc.

### Outside Git (User Local)

**`~/.claude/CLAUDE.md`** - User memory:
- Imports org-context.md from Git
- Personal preferences
- Cross-session context

## Testing the Setup

```bash
# Verify user memory exists
cat ~/.claude/CLAUDE.md

# Verify org context is in Git
git status .claude/org-context.md

# Test import works (should see org-context content)
# Start new Claude session and ask: "What's the organization development model?"
```

## Migration to Other Machines

**On new machine:**

```bash
# 1. Clone repository
git clone <repo-url> /workspaces/fashion-extract

# 2. Create user memory (one-time setup)
mkdir -p ~/.claude
cat > ~/.claude/CLAUDE.md <<'EOF'
# User Memory - Neeraj

@/workspaces/fashion-extract/.claude/org-context.md

## Personal Preferences
- Concise, technical communication
- No emojis unless explicitly requested
EOF

# 3. Done! Organization context automatically imported from Git
```

## Important Notes

- **User memory path is absolute**: `@/workspaces/fashion-extract/.claude/org-context.md`
- **Imports have 5-hop max**: Don't create deep import chains
- **Changes require new session**: Claude loads memory at startup
- **Dev container compatible**: Works in devcontainer, codespaces, local

## Troubleshooting

**Q: Changes not appearing?**
A: Start new Claude session (memory loads at startup)

**Q: Import not working?**
A: Check absolute path in `~/.claude/CLAUDE.md` matches repo location

**Q: Symlink issues?**
A: Use `@import` syntax instead of symlinks (more reliable)
