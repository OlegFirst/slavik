#!/bin/bash

# ════════════════════════════════════════════════════════════════
# CLEANUP PROJECT STRUCTURE
# Удаляет старый мусор, сохраняет рабочую структуру
# ════════════════════════════════════════════════════════════════

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              CLEANUP PROJECT STRUCTURE                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Backup first
echo "📦 Creating backup..."
BACKUP_DIR="_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}⚠️  WARNING: This will DELETE old/archived files!${NC}"
echo ""
echo "Press ENTER to continue, or Ctrl+C to cancel..."
read

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  DELETING OLD DIRECTORIES..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to safely delete directory
safe_delete_dir() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "  🗑️  Deleting: $dir"
        # Backup first
        if [ -d "$dir" ]; then
            cp -r "$dir" "$BACKUP_DIR/" 2>/dev/null || true
        fi
        # Delete
        rm -rf "$dir"
        echo -e "  ${GREEN}✓${NC} Deleted: $dir"
    fi
}

# Delete archived directories
safe_delete_dir "intelligent-core/_archive"
safe_delete_dir "_archive"
safe_delete_dir "docs-old-backup"
safe_delete_dir "human-interface"
safe_delete_dir "intelligent-core/simulation"
safe_delete_dir "intelligent-core/devops-ai"
safe_delete_dir "intelligent-core/living-docs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  DELETING OLD INFRASTRUCTURE SERVICES..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Keep only essential infrastructure
KEEP_INFRASTRUCTURE=(
    "eventbus"
    "database"
    "observability"
    "gateway"
    "security"
    "scripts"
)

for dir in infrastructure/*/; do
    dir_name=$(basename "$dir")
    keep=false

    for keep_dir in "${KEEP_INFRASTRUCTURE[@]}"; do
        if [ "$dir_name" = "$keep_dir" ]; then
            keep=true
            break
        fi
    done

    if [ "$keep" = false ]; then
        safe_delete_dir "$dir"
    else
        echo "  ✅ Keeping: $dir"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  DELETING OLD ROOT FILES..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Delete old root files
OLD_FILES=(
    "SETUP_ALGORITHM.md"
    "V7_MIGRATION_PLAN.md"
    "V7_READY_STATUS.md"
)

for file in "${OLD_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  🗑️  Deleting: $file"
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
        rm -f "$file"
        echo -e "  ${GREEN}✓${NC} Deleted: $file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CLEANUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Backup saved to: $BACKUP_DIR"
echo ""
echo "✅ PRESERVED:"
echo "   - intelligent-core/ (all services)"
echo "   - infrastructure/eventbus/ (CRITICAL!)"
echo "   - infrastructure/database/"
echo "   - infrastructure/observability/"
echo "   - docs/integration/"
echo "   - verify_all_eventbus_integrations.py"
echo ""
echo "🗑️  DELETED:"
echo "   - _archive/, docs-old-backup/"
echo "   - human-interface/, simulation/, devops-ai/, living-docs/"
echo "   - Old infrastructure services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Verify: python3 verify_all_eventbus_integrations.py"
echo "2. Check: git status"
echo "3. Commit: git add . && git commit -m 'chore: cleanup old structure'"
echo ""
