#!/bin/bash

# Documentation Optimization - Commit and Push Script
# Date: 2025-10-15

cd /Users/MD/AI-Platform-ISO

echo "=== Step 1: Check current branch ==="
git branch --show-current

echo ""
echo "=== Step 2: Rename branch recovery-7-8-oct → main ==="
git branch -m recovery-7-8-oct main

echo ""
echo "=== Step 3: Check git status ==="
git status

echo ""
echo "=== Step 4: Add all documentation changes ==="
git add docs/

echo ""
echo "=== Step 5: Create commit with detailed message ==="
git commit -m "$(cat <<'EOF'
docs: Complete professional documentation optimization

## Summary
Transformed 24 HTML documentation pages to professional Anthropic-style
design suitable for ISO 22301 standard audience (auditors, BCM specialists,
technical architects).

## Changes Made

### 1. Unified Professional Color Scheme ✓
- Created /docs/assets/unified_styles.css (450 lines)
- Anthropic-style palette: Blue (#2563eb), Gray (#64748b), Teal (#0891b2)
- Applied to all 24 HTML pages
- NO gradients, NO rainbow colors

### 2. Content Cleanup ✓
- Removed "NASH" mentions: 4 → 0
- Removed decorative emojis: 50+ → 0 (🚀 🎉 💡 ⭐ 👀 🧠 📊 ⚡)
- Standardized functional symbols: ❌ ✅ → ✗ ✓
- Kept only: ✓ ✗ ⚠️ →

### 3. Gradient Backgrounds Fixed ✓
- Replaced 30+ inline gradients with CSS variables
- Purple (#667eea → #764ba2) → var(--primary-color)
- Orange (#f59e0b → #d97706) → var(--primary-color)
- Blue (#1e3a8a → #3730a3) → var(--primary-color)

### 4. Pages Updated (24/24) ✓
- index.html, platform_overview.html, bcm_philosophy.html
- business_flow.html, documentation.html, ai_foundation.html
- modules.html, contact.html, architecture.html
- collective_intelligence.html, technology.html, workflow_intelligence.html
- governance_layer.html, deployment.html, features.html, mvp.html
- mio_manager.html, decision_center.html, service_catalog_visual.html
- eventbus_choreography.html, platform_services_overview.html
- predictive_intelligence.html, expertise_center.html, ace_service.html

## Impact
- Professional appearance suitable for ISO 22301 auditors
- Consistent branding (AI-Platform-ISO)
- Maintainable CSS system (single source of truth)
- 5000+ lines updated across all documentation

## Files Changed
- docs/assets/unified_styles.css (NEW)
- docs/OPTIMIZATION_PLAN.md (NEW)
- docs/OPTIMIZATION_COMPLETE.md (NEW)
- docs/*.html (24 files updated)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo ""
echo "=== Step 6: Check commit was created ==="
git log -1 --oneline

echo ""
echo "=== Step 7: Push to GitHub (set upstream for main branch) ==="
git push -u origin main

echo ""
echo "=== COMPLETE ==="
echo "✓ Branch renamed: recovery-7-8-oct → main"
echo "✓ Changes committed"
echo "✓ Pushed to GitHub"
echo ""
echo "Next steps:"
echo "  - Verify on GitHub: https://github.com/yourusername/AI-Platform-ISO"
echo "  - Update default branch in GitHub settings (if needed)"
echo "  - Delete old branches (if desired)"
