#!/bin/bash
# Batch documentation update with archival

MODULES=(
    "collective"
    "community_intelligence"
    "predictive"
    "orchestration"
    "expertise-center"
    "workflow-engine"
    "event_intelligence"
    "ai_workflow_optimizer"
)

SECTION="intelligent-core"
PROCESSED=0
FAILED=0

echo "============================================================"
echo "BATCH DOCUMENTATION UPDATE - Intelligent Core"
echo "============================================================"
echo "Total modules: ${#MODULES[@]}"
echo ""

for MODULE in "${MODULES[@]}"; do
    echo "----------------------------------------"
    echo "[$((PROCESSED + FAILED + 1))/${#MODULES[@]}] Processing: $MODULE"
    echo "----------------------------------------"
    
    # Step 1: Archive old docs
    echo "1/2 Archiving old documentation..."
    ./infrastructure/tools/archive-old-docs.sh "$MODULE" 2>&1 | grep -E "(Archived|Archive complete|ERROR)" || true
    
    # Step 2: Generate new docs
    echo "2/2 Generating new documentation..."
    python3 infrastructure/tools/generate-module-docs.py "$MODULE" "$SECTION"
    
    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS: $MODULE"
        ((PROCESSED++))
    else
        echo "❌ FAILED: $MODULE"
        ((FAILED++))
    fi
    
    echo ""
done

echo "============================================================"
echo "BATCH UPDATE COMPLETE"
echo "============================================================"
echo "✅ Processed: $PROCESSED"
echo "❌ Failed: $FAILED"
echo "📁 Archives: doc-project/_archived_docs/$SECTION/"
