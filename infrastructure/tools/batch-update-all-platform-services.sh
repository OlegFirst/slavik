#!/bin/bash
# Complete platform-services documentation update

SERVICES=(
    "bcm-coordination-service"
    "bia-service"
    "community-service"
    "compliance-service"
    "documents-service"
    "governance-service"
    "learning-service"
    "response-service"
    "risk-service"
    "validation-service"
    "planning_service"
    "plans_service"
)

SECTION="platform-services"
PROCESSED=0
FAILED=0
SKIPPED=0

echo "============================================================"
echo "COMPLETE PLATFORM SERVICES DOCUMENTATION UPDATE"
echo "============================================================"
echo "Total services to process: ${#SERVICES[@]}"
echo ""

for SERVICE in "${SERVICES[@]}"; do
    echo "----------------------------------------"
    echo "[$((PROCESSED + FAILED + SKIPPED + 1))/${#SERVICES[@]}] Processing: $SERVICE"
    echo "----------------------------------------"
    
    # Check if service exists
    if [ ! -d "$SECTION/$SERVICE" ]; then
        echo "⚠️  Service not found: $SECTION/$SERVICE - SKIPPING"
        ((SKIPPED++))
        echo ""
        continue
    fi
    
    # Check if README exists
    if [ ! -f "$SECTION/$SERVICE/README.md" ]; then
        echo "⚠️  No README.md found - SKIPPING"
        ((SKIPPED++))
        echo ""
        continue
    fi
    
    # Step 1: Archive
    echo "1/2 Archiving old documentation..."
    ./infrastructure/tools/archive-old-docs.sh "$SERVICE" 2>&1 | grep -E "(Archived|Archive complete)" || true
    
    # Step 2: Generate new docs
    echo "2/2 Generating new professional documentation..."
    python3 infrastructure/tools/generate-service-docs.py "$SERVICE" "$SECTION"
    
    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS: $SERVICE"
        ((PROCESSED++))
    else
        echo "❌ FAILED: $SERVICE"
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
