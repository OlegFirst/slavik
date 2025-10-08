#!/bin/bash
# Infrastructure components documentation update

COMPONENTS=(
    "database"
    "eventbus"
    "observability"
    "tools"
    "security"
    "AI-office-infrastructure"
    "gateway"
    "runtime"
    "deployment"
)

SECTION="infrastructure"
PROCESSED=0
FAILED=0
SKIPPED=0

echo "============================================================"
echo "INFRASTRUCTURE DOCUMENTATION UPDATE"
echo "============================================================"
echo "Total components: ${#COMPONENTS[@]}"
echo ""

for COMPONENT in "${COMPONENTS[@]}"; do
    echo "----------------------------------------"
    echo "[$((PROCESSED + FAILED + SKIPPED + 1))/${#COMPONENTS[@]}] Processing: $COMPONENT"
    echo "----------------------------------------"
    
    # Check if component exists
    if [ ! -d "$SECTION/$COMPONENT" ]; then
        echo "⚠️  Component not found: $SECTION/$COMPONENT - SKIPPING"
        ((SKIPPED++))
        echo ""
        continue
    fi
    
    # Check if README exists
    if [ ! -f "$SECTION/$COMPONENT/README.md" ]; then
        echo "⚠️  No README.md found - SKIPPING"
        ((SKIPPED++))
        echo ""
        continue
    fi
    
    # Step 1: Archive
    echo "1/2 Archiving old documentation..."
    ./infrastructure/tools/archive-old-docs.sh "$COMPONENT" 2>&1 | grep -E "(Archived|Archive complete)" || true
    
    # Step 2: Generate new docs
    echo "2/2 Generating new professional documentation..."
    python3 infrastructure/tools/generate-infrastructure-docs.py "$COMPONENT" "$SECTION"
    
    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS: $COMPONENT"
        ((PROCESSED++))
    else
        echo "❌ FAILED: $COMPONENT"
        ((FAILED++))
    fi
    
    echo ""
done

echo "============================================================"
echo "BATCH UPDATE COMPLETE"
echo "============================================================"
echo "✅ Processed: $PROCESSED"
echo "⚠️  Skipped: $SKIPPED"
echo "❌ Failed: $FAILED"
echo "📁 Archives: doc-project/_archived_docs/$SECTION/"
