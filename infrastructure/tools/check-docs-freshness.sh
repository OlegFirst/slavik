#!/bin/bash
# Check documentation freshness based on "Last Updated" dates

echo "============================================================"
echo "DOCUMENTATION FRESHNESS CHECK"
echo "============================================================"
echo ""

SECTIONS=("intelligent-core" "platform-services")
TODAY=$(date +%Y-%m-%d)
WARN_DAYS=30
ERROR_DAYS=90

for SECTION in "${SECTIONS[@]}"; do
    echo "Section: $SECTION"
    echo "---"
    
    for README in $SECTION/*/README.md; do
        if [ ! -f "$README" ]; then
            continue
        fi
        
        MODULE=$(dirname "$README" | cut -d/ -f2)
        
        # Extract last updated date
        LAST_UPDATED=$(grep "Last Updated" "$README" | sed 's/.*: //' | sed 's/\*\*//')
        
        if [ -z "$LAST_UPDATED" ]; then
            echo "  ⚠️  $MODULE: NO DATE FOUND"
            continue
        fi
        
        # Calculate days difference
        LAST_SEC=$(date -j -f "%Y-%m-%d" "$LAST_UPDATED" +%s 2>/dev/null || echo "0")
        TODAY_SEC=$(date +%s)
        DAYS_OLD=$(( ($TODAY_SEC - $LAST_SEC) / 86400 ))
        
        if [ "$DAYS_OLD" -gt "$ERROR_DAYS" ]; then
            echo "  ❌ $MODULE: $DAYS_OLD days old ($LAST_UPDATED) - CRITICAL"
        elif [ "$DAYS_OLD" -gt "$WARN_DAYS" ]; then
            echo "  ⚠️  $MODULE: $DAYS_OLD days old ($LAST_UPDATED) - WARNING"
        else
            echo "  ✅ $MODULE: $DAYS_OLD days old ($LAST_UPDATED) - FRESH"
        fi
    done
    
    echo ""
done

echo "============================================================"
echo "LEGEND:"
echo "  ✅ FRESH: Updated within 30 days"
echo "  ⚠️  WARNING: Updated 30-90 days ago"
echo "  ❌ CRITICAL: Updated >90 days ago or no date"
echo "============================================================"
