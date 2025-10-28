#!/bin/bash
# NeerajDev Workspace Setup Script
# Creates symlinks and workspace files for unified multi-repo development

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORG_STANDARDS_DIR="$(dirname "$SCRIPT_DIR")"
NEERAJDEV_DIR="$(dirname "$ORG_STANDARDS_DIR")"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         NeerajDev Workspace Setup                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "NeerajDev Directory: $NEERAJDEV_DIR"
echo "Org Standards Directory: $ORG_STANDARDS_DIR"
echo ""

# Verify we're in the right location
if [ ! -d "$ORG_STANDARDS_DIR/.devcontainer" ]; then
    echo "❌ Error: org-standards/.devcontainer not found"
    echo "   Are you running this script from the correct location?"
    exit 1
fi

# Step 1: Create symlink for .devcontainer
echo "📁 Setting up .devcontainer symlink..."
if [ -L "$NEERAJDEV_DIR/.devcontainer" ]; then
    echo "   ✓ Symlink already exists"
elif [ -d "$NEERAJDEV_DIR/.devcontainer" ]; then
    echo "   ⚠️  .devcontainer directory exists (not a symlink)"
    echo "   Backing up to .devcontainer.backup..."
    mv "$NEERAJDEV_DIR/.devcontainer" "$NEERAJDEV_DIR/.devcontainer.backup"
    ln -sf org-standards/.devcontainer "$NEERAJDEV_DIR/.devcontainer"
    echo "   ✓ Created symlink (old directory backed up)"
else
    ln -sf org-standards/.devcontainer "$NEERAJDEV_DIR/.devcontainer"
    echo "   ✓ Created symlink"
fi

# Step 2: Copy workspace file if it doesn't exist
echo "📝 Setting up VSCode workspace file..."
if [ -f "$NEERAJDEV_DIR/neerajdev.code-workspace" ]; then
    echo "   ✓ Workspace file already exists"
else
    cp "$ORG_STANDARDS_DIR/.devcontainer/neerajdev.code-workspace.template" \
       "$NEERAJDEV_DIR/neerajdev.code-workspace"
    echo "   ✓ Created workspace file from template"
fi

# Step 3: Setup Claude Code managed settings symlink
echo ""
echo "⚙️  Setting up Claude Code managed settings..."
MANAGED_SETTINGS_SOURCE="/workspace/org-standards/claude-code/managed-settings.json"
MANAGED_SETTINGS_TARGET="/Library/Application Support/ClaudeCode/managed-settings.json"

if [ ! -f "$MANAGED_SETTINGS_SOURCE" ]; then
    echo "   ❌ Error: $MANAGED_SETTINGS_SOURCE not found"
    echo "   This file should exist in org-standards"
    exit 1
fi

# Create target directory
sudo mkdir -p "/Library/Application Support/ClaudeCode"

# Create or update symlink
if [ -L "$MANAGED_SETTINGS_TARGET" ]; then
    echo "   ✓ Symlink already exists"
    echo "   Updating to ensure it points to correct location..."
    sudo ln -sf "$MANAGED_SETTINGS_SOURCE" "$MANAGED_SETTINGS_TARGET"
    echo "   ✓ Symlink updated"
elif [ -f "$MANAGED_SETTINGS_TARGET" ]; then
    echo "   ⚠️  Regular file exists (not a symlink)"
    echo "   Backing up to managed-settings.json.backup..."
    sudo mv "$MANAGED_SETTINGS_TARGET" "$MANAGED_SETTINGS_TARGET.backup"
    sudo ln -sf "$MANAGED_SETTINGS_SOURCE" "$MANAGED_SETTINGS_TARGET"
    echo "   ✓ Created symlink (old file backed up)"
else
    sudo ln -sf "$MANAGED_SETTINGS_SOURCE" "$MANAGED_SETTINGS_TARGET"
    echo "   ✓ Created symlink"
fi

# Verify symlink
if [ -L "$MANAGED_SETTINGS_TARGET" ]; then
    echo "   ✓ Symlink verified: $(readlink "$MANAGED_SETTINGS_TARGET")"
    echo "   ℹ️  Restart Claude Code to apply (no Mac reboot needed)"
else
    echo "   ❌ Error: Failed to create symlink"
    exit 1
fi

# Step 4: Verify all repos are present
echo ""
echo "🔍 Verifying repository structure..."
REPOS=("StyleGuru" "syra" "syra-playground" "org-standards")
ALL_PRESENT=true

for repo in "${REPOS[@]}"; do
    if [ -d "$NEERAJDEV_DIR/$repo" ]; then
        echo "   ✓ $repo"
    else
        echo "   ❌ $repo (missing)"
        ALL_PRESENT=false
    fi
done

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Workspace Structure:"
echo "   $NEERAJDEV_DIR/"
echo "   ├── .devcontainer/           → org-standards/.devcontainer/"
echo "   ├── neerajdev.code-workspace"
echo "   ├── StyleGuru/"
echo "   ├── syra/"
echo "   ├── syra-playground/"
echo "   └── org-standards/"
echo ""
echo "⚙️  Claude Code Configuration:"
echo "   /Library/Application Support/ClaudeCode/managed-settings.json"
echo "   → /workspace/org-standards/claude-code/managed-settings.json"
echo ""

if [ "$ALL_PRESENT" = true ]; then
    echo "✅ All repositories present"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Restart Claude Code (if running) to apply managed settings"
    echo "   2. Open: $NEERAJDEV_DIR/neerajdev.code-workspace in VSCode"
    echo "   3. Click 'Reopen in Container' when prompted"
    echo "   4. Wait for container build and dependency installation"
    echo "   5. Start coding across all repos!"
else
    echo "⚠️  Some repositories are missing"
    echo "   Clone missing repos to $NEERAJDEV_DIR/"
fi

echo ""
echo "📖 Documentation: $ORG_STANDARDS_DIR/.devcontainer/README.md"
echo ""
