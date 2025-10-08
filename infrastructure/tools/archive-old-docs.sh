#!/bin/bash
# Archive old documentation before generating new one

MODULE=$1
if [ -z "$MODULE" ]; then
    echo "Usage: ./archive-old-docs.sh <module_name>"
    exit 1
fi

REPO_PATH="/Users/MD/AI-Platform-ISO"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Detect module path
if [ -d "$REPO_PATH/intelligent-core/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/intelligent-core/$MODULE"
    SECTION="intelligent-core"
elif [ -d "$REPO_PATH/platform-services/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/platform-services/$MODULE"
    SECTION="platform-services"
elif [ -d "$REPO_PATH/infrastructure/$MODULE" ]; then
    MODULE_PATH="$REPO_PATH/infrastructure/$MODULE"
    SECTION="infrastructure"
else
    echo "❌ Module not found: $MODULE"
    exit 1
fi

# Create archive directory
ARCHIVE_DIR="$REPO_PATH/doc-project/_archived_docs/$SECTION/$MODULE/$TIMESTAMP"
mkdir -p "$ARCHIVE_DIR"

echo "🗂️  Archiving old documentation for: $MODULE"
echo "📁 Archive location: doc-project/_archived_docs/$SECTION/$MODULE/$TIMESTAMP"

# Archive README.md
if [ -f "$MODULE_PATH/README.md" ]; then
    cp "$MODULE_PATH/README.md" "$ARCHIVE_DIR/README.md"
    echo "  ✓ Archived README.md"
fi

# Archive API.md
if [ -f "$MODULE_PATH/API.md" ]; then
    cp "$MODULE_PATH/API.md" "$ARCHIVE_DIR/API.md"
    echo "  ✓ Archived API.md"
fi

# Archive ARCHITECTURE.md
if [ -f "$MODULE_PATH/ARCHITECTURE.md" ]; then
    cp "$MODULE_PATH/ARCHITECTURE.md" "$ARCHIVE_DIR/ARCHITECTURE.md"
    echo "  ✓ Archived ARCHITECTURE.md"
fi

# Archive docs/ directory
if [ -d "$MODULE_PATH/docs" ]; then
    cp -r "$MODULE_PATH/docs" "$ARCHIVE_DIR/docs"
    echo "  ✓ Archived docs/ directory"
fi

# Create archive metadata
cat > "$ARCHIVE_DIR/_ARCHIVE_INFO.txt" << METADATA
Archive Created: $(date)
Module: $MODULE
Section: $SECTION
Original Path: $MODULE_PATH

Archived Files:
$(ls -la "$ARCHIVE_DIR")

Reason: Documentation update - Professional ISO standards compliance
METADATA

echo "✅ Archive complete!"
echo ""
echo "Archived files:"
ls -lh "$ARCHIVE_DIR"
