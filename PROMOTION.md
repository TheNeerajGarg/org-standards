# Promoting Standards from Development to Stable

## Overview

org-standards uses a two-branch strategy:
- **main**: Development version (used by Syra, Syra-playground)
- **stable**: Production version (used by StyleGuru)

## Promotion Process

### 1. Test in Development (1-2 weeks)

Changes committed to `main` are automatically available to Syra/Syra-playground:

```bash
# Syra pulls latest main
cd ~/NeerajDev/syra
git submodule update --remote org-standards
```

**Validation criteria**:
- ✅ No rollbacks needed in 1-2 weeks
- ✅ All CI checks passing
- ✅ No open issues tagged with 'standards'
- ✅ Used in at least 5-10 Syra commits

### 2. Promote to Stable

When development standards are proven:

```bash
cd ~/NeerajDev/org-standards

# Switch to stable branch
git checkout stable

# Merge from main (preserves history)
git merge main --no-ff -m "promote: [describe changes]

- Change 1
- Change 2

Tested in Syra for [duration]"

# Tag the release
git tag -a v1.x.x -m "Release v1.x.x

- Change summary
- Links to relevant PRs/issues"

# Push
git push origin stable --tags
```

**Version numbering** (semantic):
- **v1.x.0**: Major improvements (new standards, significant updates)
- **v1.0.x**: Minor updates (clarifications, fixes)

### 3. Notify Consumers (Optional)

Post in #engineering or create GitHub Release:
```bash
gh release create v1.x.x \
  --title "Org Standards v1.x.x" \
  --notes "Summary of changes..."
```

### 4. StyleGuru Adoption (When Ready)

StyleGuru updates when team decides:

```bash
cd ~/NeerajDev/StyleGuru
git submodule update --remote org-standards
git add org-standards
git commit -m "chore: update org-standards to v1.x.x"
git push
```

## Emergency Hotfixes

If production (stable) needs urgent fix:

```bash
# Fix directly on stable
git checkout stable
# Make fix
git add . && git commit -m "hotfix: [description]"
git tag v1.x.y
git push origin stable --tags

# Backport to main
git checkout main
git cherry-pick <commit-sha>
git push origin main
```

## Rollback

If a promotion causes issues:

**In org-standards**:
```bash
git checkout stable
git reset --hard v1.x.x  # Last good version
git push origin stable --force
```

**In StyleGuru**:
```bash
cd org-standards
git checkout v1.x.x  # Last good version
cd ..
git add org-standards
git commit -m "revert: rollback org-standards to v1.x.x"
```

## Notes

- **Always edit on main** (not stable directly)
- Stable is for proven, tested changes only
- Promotion is one-way: main → stable
- StyleGuru can stay on older versions indefinitely
- Version tags are permanent (don't delete/rewrite)
