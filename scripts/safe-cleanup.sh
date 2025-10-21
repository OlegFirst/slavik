#!/usr/bin/env bash
#
# Safe Cleanup для AI-Platform-ISO
#
# Безопасная очистка репозитория:
# ✅ Сохраняет русский язык и Unicode
# ✅ Валидация файлов без изменений
# ✅ Prettier только для staged файлов
# ✅ Удаление только временных файлов
# ✅ НЕ трогает архивы и документацию
#
# Usage:
#   ./scripts/safe-cleanup.sh              # Dry-run (только отчет)
#   ./scripts/safe-cleanup.sh --apply      # Применить изменения
#   ./scripts/safe-cleanup.sh --validate   # Только валидация
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_DIR=".cleanup-report"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/cleanup-report-$TIMESTAMP.md"

MODE="dry-run"  # dry-run | apply | validate
VERBOSE=0

# Counters
TEMP_FILES_FOUND=0
TEMP_FILES_DELETED=0
JSON_VALID=0
JSON_INVALID=0
YAML_VALID=0
YAML_INVALID=0
PRETTIER_FILES=0
SHELLCHECK_PASS=0
SHELLCHECK_FAIL=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) MODE="apply"; shift;;
    --validate) MODE="validate"; shift;;
    -v|--verbose) VERBOSE=1; shift;;
    -h|--help)
      echo "Usage: $0 [--apply|--validate] [-v]"
      echo "  --apply     Apply cleanup changes"
      echo "  --validate  Only validate files"
      echo "  -v          Verbose output"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

# Create report directory
mkdir -p "$REPORT_DIR"

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Print header
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   🧹 Safe Cleanup для AI-Platform-ISO${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Mode: ${YELLOW}$MODE${NC}"
echo -e "Timestamp: ${YELLOW}$TIMESTAMP${NC}"
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
# Safe Cleanup Report

**Date:** $(date)
**Mode:** $MODE
**Project:** AI-Platform-ISO

---

## Summary

EOF

#
# 1. FIND TEMPORARY FILES
#
log_info "1. Searching for temporary files..."

TEMP_PATTERNS=(
  "*.bak"
  "*.tmp"
  "*.temp"
  ".DS_Store"
  "Thumbs.db"
  "*.swp"
  "*.swo"
  "*~"
  "*.orig"
  "*.rej"
)

EXCLUDE_DIRS=(
  ".git"
  "node_modules"
  "_archive"
  "можетпригодится"
  "dist"
  "build"
  ".next"
  "coverage"
  "__pycache__"
  ".venv"
  "venv"
  "_BACKUP_"
  "_OLD"
  "_old"
  ".backup."
  "18:09"
  "BACKUP_"
  "backup-"
)

TEMP_FILES=()

for pattern in "${TEMP_PATTERNS[@]}"; do
  while IFS= read -r file; do
    # Check if file is not in excluded directories
    skip=0
    for exclude in "${EXCLUDE_DIRS[@]}"; do
      if [[ "$file" == *"$exclude"* ]]; then
        skip=1
        break
      fi
    done

    if [[ $skip -eq 0 ]]; then
      TEMP_FILES+=("$file")
      ((TEMP_FILES_FOUND++))
      [[ $VERBOSE -eq 1 ]] && echo "  Found: $file"
    fi
  done < <(find . -name "$pattern" 2>/dev/null || true)
done

log_success "Found $TEMP_FILES_FOUND temporary files"

# Delete temporary files if in apply mode
if [[ "$MODE" == "apply" && ${#TEMP_FILES[@]} -gt 0 ]]; then
  log_info "Deleting temporary files..."
  for file in "${TEMP_FILES[@]}"; do
    rm -f "$file" && ((TEMP_FILES_DELETED++))
    [[ $VERBOSE -eq 1 ]] && echo "  Deleted: $file"
  done
  log_success "Deleted $TEMP_FILES_DELETED temporary files"
fi

# Add to report
cat >> "$REPORT_FILE" << EOF
### 1. Temporary Files

- **Found:** $TEMP_FILES_FOUND
- **Deleted:** $TEMP_FILES_DELETED

EOF

if [[ $TEMP_FILES_FOUND -gt 0 ]]; then
  echo "#### Files:" >> "$REPORT_FILE"
  for file in "${TEMP_FILES[@]}"; do
    echo "- \`$file\`" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
fi

#
# 2. VALIDATE JSON FILES
#
log_info "2. Validating JSON files..."

while IFS= read -r file; do
  skip=0
  for exclude in "${EXCLUDE_DIRS[@]}"; do
    if [[ "$file" == *"$exclude"* ]]; then
      skip=1
      break
    fi
  done

  if [[ $skip -eq 1 ]]; then
    continue
  fi

  if jq empty "$file" 2>/dev/null; then
    ((JSON_VALID++))
    [[ $VERBOSE -eq 1 ]] && echo "  ✅ $file"
  else
    ((JSON_INVALID++))
    log_error "Invalid JSON: $file"
  fi
done < <(find . -name "*.json" -type f 2>/dev/null || true)

if [[ $JSON_INVALID -gt 0 ]]; then
  log_error "$JSON_INVALID invalid JSON files"
else
  log_success "All $JSON_VALID JSON files valid"
fi

cat >> "$REPORT_FILE" << EOF
### 2. JSON Validation

- **Valid:** $JSON_VALID
- **Invalid:** $JSON_INVALID

EOF

#
# 3. VALIDATE YAML FILES
#
log_info "3. Validating YAML files..."

while IFS= read -r file; do
  skip=0
  for exclude in "${EXCLUDE_DIRS[@]}"; do
    if [[ "$file" == *"$exclude"* ]]; then
      skip=1
      break
    fi
  done

  if [[ $skip -eq 1 ]]; then
    continue
  fi

  if python3 -c "import yaml; yaml.safe_load(open('$file', 'r', encoding='utf-8'))" 2>/dev/null; then
    ((YAML_VALID++))
    [[ $VERBOSE -eq 1 ]] && echo "  ✅ $file"
  else
    ((YAML_INVALID++))
    log_error "Invalid YAML: $file"
  fi
done < <(find . \( -name "*.yml" -o -name "*.yaml" \) -type f 2>/dev/null || true)

if [[ $YAML_INVALID -gt 0 ]]; then
  log_error "$YAML_INVALID invalid YAML files"
else
  log_success "All $YAML_VALID YAML files valid"
fi

cat >> "$REPORT_FILE" << EOF
### 3. YAML Validation

- **Valid:** $YAML_VALID
- **Invalid:** $YAML_INVALID

EOF

#
# 4. SHELLCHECK FOR BASH SCRIPTS
#
if command -v shellcheck >/dev/null 2>&1; then
  log_info "4. Running shellcheck on bash scripts..."

  while IFS= read -r file; do
    skip=0
    for exclude in "${EXCLUDE_DIRS[@]}"; do
      if [[ "$file" == *"$exclude"* ]]; then
        skip=1
        break
      fi
    done

    if [[ $skip -eq 1 ]]; then
      continue
    fi

    if shellcheck "$file" 2>/dev/null; then
      ((SHELLCHECK_PASS++))
      [[ $VERBOSE -eq 1 ]] && echo "  ✅ $file"
    else
      ((SHELLCHECK_FAIL++))
      log_warning "Shellcheck warnings: $file"
    fi
  done < <(find . -name "*.sh" -type f 2>/dev/null || true)

  log_success "Shellcheck: $SHELLCHECK_PASS passed, $SHELLCHECK_FAIL warnings"
else
  log_warning "shellcheck not installed, skipping"
fi

cat >> "$REPORT_FILE" << EOF
### 4. Shellcheck

- **Passed:** $SHELLCHECK_PASS
- **Warnings:** $SHELLCHECK_FAIL

EOF

#
# 5. PRETTIER FOR STAGED FILES
#
if [[ "$MODE" == "apply" ]] && command -v npx >/dev/null 2>&1; then
  log_info "5. Running prettier on staged files..."

  # Get staged files
  STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -E '\.(js|ts|tsx|jsx|json|md|yml|yaml|css|scss)$' || true)

  if [[ -n "$STAGED_FILES" ]]; then
    echo "$STAGED_FILES" | xargs npx prettier --write --log-level warn 2>/dev/null || true
    PRETTIER_FILES=$(echo "$STAGED_FILES" | wc -l | tr -d ' ')
    log_success "Prettier formatted $PRETTIER_FILES staged files"
  else
    log_info "No staged files to format"
  fi
else
  log_info "5. Skipping prettier (not in apply mode or npx not found)"
fi

cat >> "$REPORT_FILE" << EOF
### 5. Prettier

- **Formatted:** $PRETTIER_FILES staged files

EOF

#
# 6. FIND LARGE FILES
#
log_info "6. Finding large files (>10MB)..."

LARGE_FILES=()
while IFS= read -r file; do
  LARGE_FILES+=("$file")
  [[ $VERBOSE -eq 1 ]] && echo "  📦 $file"
done < <(find . -type f -size +10M 2>/dev/null | grep -v ".git" || true)

if [[ ${#LARGE_FILES[@]} -gt 0 ]]; then
  log_warning "Found ${#LARGE_FILES[@]} large files (>10MB)"
else
  log_success "No large files found"
fi

cat >> "$REPORT_FILE" << EOF
### 6. Large Files (>10MB)

- **Found:** ${#LARGE_FILES[@]}

EOF

if [[ ${#LARGE_FILES[@]} -gt 0 ]]; then
  echo "#### Files:" >> "$REPORT_FILE"
  for file in "${LARGE_FILES[@]}"; do
    size=$(du -h "$file" | cut -f1)
    echo "- \`$file\` ($size)" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
fi

#
# 7. FIND EMPTY DIRECTORIES
#
log_info "7. Finding empty directories..."

EMPTY_DIRS=()
while IFS= read -r dir; do
  skip=0
  for exclude in "${EXCLUDE_DIRS[@]}"; do
    if [[ "$dir" == *"$exclude"* ]]; then
      skip=1
      break
    fi
  done

  if [[ $skip -eq 0 ]]; then
    EMPTY_DIRS+=("$dir")
    [[ $VERBOSE -eq 1 ]] && echo "  📁 $dir"
  fi
done < <(find . -type d -empty 2>/dev/null || true)

if [[ ${#EMPTY_DIRS[@]} -gt 0 ]]; then
  log_info "Found ${#EMPTY_DIRS[@]} empty directories"
else
  log_success "No empty directories found"
fi

cat >> "$REPORT_FILE" << EOF
### 7. Empty Directories

- **Found:** ${#EMPTY_DIRS[@]}

EOF

if [[ ${#EMPTY_DIRS[@]} -gt 0 ]]; then
  echo "#### Directories:" >> "$REPORT_FILE"
  for dir in "${EMPTY_DIRS[@]}"; do
    echo "- \`$dir\`" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
fi

#
# FINAL SUMMARY
#
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   📊 Cleanup Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Temporary files:  ${YELLOW}$TEMP_FILES_FOUND${NC} found, ${GREEN}$TEMP_FILES_DELETED${NC} deleted"
echo -e "JSON validation:  ${GREEN}$JSON_VALID${NC} valid, ${RED}$JSON_INVALID${NC} invalid"
echo -e "YAML validation:  ${GREEN}$YAML_VALID${NC} valid, ${RED}$YAML_INVALID${NC} invalid"
echo -e "Shellcheck:       ${GREEN}$SHELLCHECK_PASS${NC} passed, ${YELLOW}$SHELLCHECK_FAIL${NC} warnings"
echo -e "Prettier:         ${GREEN}$PRETTIER_FILES${NC} files formatted"
echo -e "Large files:      ${YELLOW}${#LARGE_FILES[@]}${NC} found"
echo -e "Empty dirs:       ${YELLOW}${#EMPTY_DIRS[@]}${NC} found"
echo ""

# Add final summary to report
cat >> "$REPORT_FILE" << EOF

---

## Final Summary

| Category | Count |
|----------|-------|
| Temporary files found | $TEMP_FILES_FOUND |
| Temporary files deleted | $TEMP_FILES_DELETED |
| JSON valid | $JSON_VALID |
| JSON invalid | $JSON_INVALID |
| YAML valid | $YAML_VALID |
| YAML invalid | $YAML_INVALID |
| Shellcheck passed | $SHELLCHECK_PASS |
| Shellcheck warnings | $SHELLCHECK_FAIL |
| Prettier formatted | $PRETTIER_FILES |
| Large files (>10MB) | ${#LARGE_FILES[@]} |
| Empty directories | ${#EMPTY_DIRS[@]} |

---

## What We PRESERVE ✅

- ✅ Русский язык (кириллица)
- ✅ Unicode и эмодзи
- ✅ Упоминания AI tools (Claude, ChatGPT)
- ✅ Архивы (_archive/)
- ✅ Документация (docs/, DOC/)
- ✅ Имена файлов (без транслитерации)

## What We CLEAN 🧹

- 🧹 Временные файлы (.bak, .tmp, .DS_Store)
- 🧹 Валидация JSON/YAML
- 🧹 Prettier только для staged файлов
- 🧹 Shellcheck warnings

---

**Report saved:** \`$REPORT_FILE\`
EOF

log_success "Report saved: $REPORT_FILE"
echo ""

# Exit with error if validation failed
if [[ $JSON_INVALID -gt 0 || $YAML_INVALID -gt 0 ]]; then
  log_error "Validation failed! Fix invalid files before applying cleanup."
  exit 1
fi

if [[ "$MODE" == "dry-run" ]]; then
  log_info "Dry-run complete. Run with --apply to make changes."
fi

log_success "Cleanup complete! ✨"
