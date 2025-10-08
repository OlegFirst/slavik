#!/bin/bash
# Batch documentation update for Platform Services

SERVICES=(
    "validation-service"
    "documents-service"
    "governance-service"
    "incident-service"
    "bia-service"
    "risk-service"
    "compliance-service"
)

SECTION="platform-services"
PROCESSED=0
FAILED=0

echo "============================================================"
echo "BATCH DOCUMENTATION UPDATE - Platform Services"
echo "============================================================"
echo "Total services: ${#SERVICES[@]}"
echo ""

for SERVICE in "${SERVICES[@]}"; do
    echo "----------------------------------------"
    echo "[$((PROCESSED + FAILED + 1))/${#SERVICES[@]}] Processing: $SERVICE"
    echo "----------------------------------------"
    
    # Check if service exists
    if [ ! -d "$SECTION/$SERVICE" ]; then
        echo "⚠️  Service directory not found: $SECTION/$SERVICE"
        echo "   Skipping..."
        ((FAILED++))
        continue
    fi
    
    # Step 1: Archive old docs
    echo "1/2 Archiving old documentation..."
    ./infrastructure/tools/archive-old-docs.sh "$SERVICE" platform-services "$SECTION" 2>&1 | grep -E "(Archived|Archive complete|ERROR)" || true
    
    # Step 2: Generate new docs
    echo "2/2 Generating new documentation..."
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
echo "❌ Failed: $FAILED"
echo "📁 Archives: doc-project/_archived_docs/$SECTION/"
