#!/bin/bash
# Documentation Validation Script

echo "=== Documentation Quality Check ==="
echo

# Check for emojis
echo "1. Checking for emojis..."
EMOJI_COUNT=$(find docs intelligent-core platform-services infrastructure -name "*.md" -type f -exec grep -l "🎯\|✅\|🚀\|🤖\|💡\|⚡" {} \; 2>/dev/null | wc -l)
if [ "$EMOJI_COUNT" -eq 0 ]; then
    echo "   ✓ No emojis found"
else
    echo "   ✗ Found $EMOJI_COUNT files with emojis"
fi

# Check for Russian text
echo "2. Checking for Russian text..."
RUSSIAN_COUNT=$(find docs intelligent-core platform-services infrastructure -name "*.md" -type f -exec grep -l "[а-яА-Я]" {} \; 2>/dev/null | wc -l)
if [ "$RUSSIAN_COUNT" -eq 0 ]; then
    echo "   ✓ No Russian text found"
else
    echo "   ✗ Found $RUSSIAN_COUNT files with Russian text"
fi

# Check for broken links
echo "3. Checking for broken internal links..."
echo "   (This is a placeholder - implement link checker)"

# Count documentation files
echo "4. Documentation statistics..."
README_COUNT=$(find . -name "README.md" | wc -l)
TOTAL_DOCS=$(find docs intelligent-core platform-services infrastructure -name "*.md" -type f | wc -l)
echo "   - README files: $README_COUNT"
echo "   - Total docs: $TOTAL_DOCS"

echo
echo "=== Documentation validation complete ==="
