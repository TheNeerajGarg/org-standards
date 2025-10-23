# Organization Context

**This file contains cross-project organizational context that applies to ALL repositories.**

## Development Model

Single human (Neeraj) orchestrating AI bot swarm

**Key Constraints:**
- **CRITICAL: Token budget** - Stay under 50K tokens per conversation. Be concise, avoid verbose responses.
- **Real constraint**: $ budget for AI API calls - Token usage directly = cost
- **Bottleneck**: Neeraj's review bandwidth (30-60 min/week)
- **Mission**: Learn what blocks 10× software development productivity
- **Current Phase**: Discovery - go broad, find all problems, document root causes

## Repository Map

**Where to work:**
- **StyleGuru** (`/Users/neerajgarg/StyleGuru/` or `/workspaces/StyleGuru/`): Product features, fashion AI
- **syra** (`/Users/neerajgarg/syra/`): Dev tools, introspection, workflow infrastructure
- **syra-playground** (`/Users/neerajgarg/syra-playground/`): Rapid experimentation, prototyping
- **org-standards** (`/Users/neerajgarg/org-standards/`): Shared coding standards

**Rule**:
- Dev tools → Syra
- Product features → StyleGuru
- Rapid experimentation → syra-playground
- Standards → org-standards

## Global Philosophy

### Root Cause Fixes Over Workarounds
**Organization mission**: Learn what blocks 10× productivity → Workarounds hide problems

- ❌ "Use `--no-verify`" → ✅ **Fix the hook**
- ❌ "Skip this check" → ✅ **Make check work**
- **Always apply 5 whys before suggesting solutions**

### Check Deployed State First
**Before suggesting "we need to set up X":**
```bash
ls .github/workflows/              # Check what's deployed
gh workflow list                    # Check active workflows
git log --oneline | head -20       # Check recent changes
```

**Rule**: Deployed Code > Recent Commits > Documentation

### Communication Style
- **BE CONCISE** - Token efficiency is critical. Avoid verbose explanations.
- **No emojis** unless explicitly requested
- **Short responses** - Get to the point quickly
- **Avoid examples in responses** unless specifically requested
- Professional objectivity - technical accuracy over validation
- **When corrected**: Brief acknowledgment + fix. Skip lengthy introspection unless asked.

## Global Standards

**Never Do:**
- ❌ Suggest workarounds without fixing root cause
- ❌ Claim "done" without DoD verification
- ❌ Trust documentation without checking deployed code

**Always Do:**
- ✅ Apply 5 whys before suggesting solutions
- ✅ Auto-detect corrections and self-introspect
- ✅ Check deployed state before suggesting setup
- ✅ Test with real dependencies (not just mocks)
