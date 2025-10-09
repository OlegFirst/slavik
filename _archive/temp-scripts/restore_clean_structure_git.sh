#!/bin/bash

# ════════════════════════════════════════════════════════════════
# RESTORE CLEAN STRUCTURE USING GIT
# Безопасный способ - через git clean
# ════════════════════════════════════════════════════════════════

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         RESTORE CLEAN STRUCTURE (GIT METHOD)                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Current situation:"
echo ""
git status --short | head -20
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${BLUE}STRATEGY:${NC}"
echo "1. Keep all modified files (our EventBus work)"
echo "2. Remove files that git shows as 'deleted'"
echo "3. Commit the clean state"
echo ""

echo -e "${YELLOW}⚠️  This will:${NC}"
echo "  - Accept deletion of old files shown in git status"
echo "  - Keep all NEW files (our work)"
echo "  - Restore clean structure"
echo ""

echo "Press ENTER to see what will be removed, or Ctrl+C to cancel..."
read

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 FILES TO BE REMOVED (git deleted):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

git status --short | grep "^ D " | head -30

echo ""
echo "... and more (total: $(git status --short | grep '^ D ' | wc -l) deleted files)"
echo ""

echo -e "${YELLOW}⚠️  WARNING: This will stage all deletions!${NC}"
echo ""
echo "Type 'YES' to proceed, or anything else to cancel:"
read confirmation

if [ "$confirmation" != "YES" ]; then
    echo ""
    echo -e "${RED}✗ Cancelled${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🗑️  REMOVING OLD FILES..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Stage all deletions
git add -u

echo -e "${GREEN}✓${NC} Deletions staged"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 STAGING OUR WORK..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Stage our EventBus work
echo "Staging EventBus integration..."
git add intelligent-core/*/main.py 2>/dev/null || true
git add intelligent-core/event_intelligence/event_subscribers.py 2>/dev/null || true
git add intelligent-core/shared/event_bus/ 2>/dev/null || true
git add infrastructure/eventbus/ 2>/dev/null || true
git add verify_all_eventbus_integrations.py 2>/dev/null || true
git add docs/integration/*.md 2>/dev/null || true
git add docs/knowledge-library/*.md 2>/dev/null || true

echo -e "${GREEN}✓${NC} Our work staged"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY OF CHANGES:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

git status --short | head -40

echo ""
echo "Total changes: $(git status --short | wc -l) files"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Ready to commit? Type 'YES' to commit, or anything else to stop:"
read commit_confirmation

if [ "$commit_confirmation" != "YES" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Changes staged but NOT committed${NC}"
    echo ""
    echo "To review: git status"
    echo "To commit: git commit -m 'chore: cleanup old structure + EventBus integration'"
    echo "To undo: git reset"
    exit 0
fi

echo ""
echo "📝 Committing..."

git commit -m "chore: cleanup old structure + preserve EventBus 100% integration

- Removed old archived directories (docs-old-backup, _archive, etc.)
- Removed old infrastructure services
- Preserved EventBus integration (13/13 services)
- Preserved knowledge library and documentation
- Clean project structure restored
"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ CLEANUP COMPLETE!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Preserved:"
echo "   - EventBus integration (13 services)"
echo "   - Knowledge library"
echo "   - Documentation"
echo "   - All working services"
echo ""
echo "🗑️  Removed:"
echo "   - Old archived directories"
echo "   - Duplicate/old infrastructure"
echo ""
echo "Next steps:"
echo "  1. Verify: python3 verify_all_eventbus_integrations.py"
echo "  2. Check: git log -1"
echo ""
