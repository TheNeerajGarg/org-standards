#!/bin/bash
# Sync organization-wide Claude documentation to all repos
#
# Source of truth: org-standards/.claude/
# Copies to: fashion-extract/.claude/, syra/.claude/, syra-playground/.claude/
#
# Run this after updating any org-wide documentation

set -e

# Detect environment
if [ -d "/workspace" ]; then
    NEERAJ_DEV="/workspace"
else
    NEERAJ_DEV="$HOME/NeerajDev"
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    Syncing Organization-wide Claude Documentation             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Source directory
ORG_CLAUDE="$NEERAJ_DEV/org-standards/.claude"

# Target repositories
REPOS=("fashion-extract" "syra" "syra-playground")

# Org-wide documentation files to sync
ORG_DOCS=(
    "org-context.md"
    "quality-standards.md"
    "brd-prd-erd-standards.md"
    "execution-plan-standards.md"
    "planning-checklist.md"
    "testing.md"
    "technical.md"
    "workflow.md"
    "introspection.md"
    "memory-sync-workflow.md"
    "context-management.md"
    "grandfather-policy.md"
    "schema-standards.md"
)

# Verify source directory exists
if [ ! -d "$ORG_CLAUDE" ]; then
    echo "❌ Error: Source directory not found: $ORG_CLAUDE"
    exit 1
fi

echo "Source: $ORG_CLAUDE"
echo "Targets: ${REPOS[@]}"
echo ""

# Sync to each repository
TOTAL_SYNCED=0
for repo in "${REPOS[@]}"; do
    REPO_PATH="$NEERAJ_DEV/$repo"
    REPO_CLAUDE="$REPO_PATH/.claude"

    # Check if repo exists
    if [ ! -d "$REPO_PATH" ]; then
        echo "⚠️  Skipping $repo (not found)"
        continue
    fi

    # Create .claude directory if it doesn't exist
    mkdir -p "$REPO_CLAUDE"

    echo "📂 Syncing to $repo:"

    # Copy each org-wide doc
    for doc in "${ORG_DOCS[@]}"; do
        SOURCE="$ORG_CLAUDE/$doc"
        TARGET="$REPO_CLAUDE/$doc"

        if [ -f "$SOURCE" ]; then
            cp "$SOURCE" "$TARGET"
            echo "   ✓ $doc"
            ((TOTAL_SYNCED++))
        else
            echo "   ⚠️  $doc (source not found)"
        fi
    done
    echo ""
done

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Sync Complete!                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Total files synced: $TOTAL_SYNCED"
echo ""
echo "Next steps:"
echo "  1. Review changes: git status in each repo"
echo "  2. Commit in org-standards (source of truth)"
echo "  3. Commit synced copies in each repo"
echo ""
echo "Note: org-standards/.claude/ is the source of truth."
echo "      Always edit there, then run this script to sync."
echo ""
