#!/bin/bash

# BCM Module XML Validation Script
# Проверяет все XML файлы модулей перед установкой

BCM_ADDONS_PATH="/Users/MD/ISO-22301/core/odoo-18.0/addons"
LOG_FILE="/tmp/bcm_validation.log"

echo "🔍 BCM Module XML Validation Started $(date)" | tee $LOG_FILE

validate_module() {
    local module_path=$1
    local module_name=$(basename $module_path)

    echo "📦 Validating module: $module_name" | tee -a $LOG_FILE

    # Check for XML syntax errors
    local xml_errors=0

    for xml_file in $(find $module_path -name "*.xml" 2>/dev/null); do
        if ! xmllint --noout "$xml_file" 2>/dev/null; then
            echo "❌ XML Syntax Error in: $xml_file" | tee -a $LOG_FILE
            xmllint --noout "$xml_file" 2>&1 | tee -a $LOG_FILE
            xml_errors=$((xml_errors + 1))
        fi
    done

    # Check for unescaped ampersands
    local ampersand_errors=0
    for xml_file in $(find $module_path -name "*.xml" 2>/dev/null); do
        if grep -q " & " "$xml_file" 2>/dev/null; then
            echo "⚠️  Unescaped ampersand in: $xml_file" | tee -a $LOG_FILE
            grep -n " & " "$xml_file" | tee -a $LOG_FILE
            ampersand_errors=$((ampersand_errors + 1))
        fi
    done

    # Check for deprecated tree views
    local tree_errors=0
    for xml_file in $(find $module_path -name "*.xml" 2>/dev/null); do
        if grep -q "<tree" "$xml_file" 2>/dev/null; then
            echo "⚠️  Deprecated <tree> view in: $xml_file" | tee -a $LOG_FILE
            grep -n "<tree" "$xml_file" | tee -a $LOG_FILE
            tree_errors=$((tree_errors + 1))
        fi
    done

    # Check for chatter fields without mail.thread inheritance
    local chatter_errors=0
    for xml_file in $(find $module_path -name "*.xml" 2>/dev/null); do
        if grep -q "message_follower_ids\|message_ids\|activity_ids" "$xml_file" 2>/dev/null; then
            # Extract model name from the XML
            local model_name=$(grep -o 'model="[^"]*"' "$xml_file" | head -1 | sed 's/model="\([^"]*\)"/\1/')
            if [ ! -z "$model_name" ]; then
                # Check if corresponding Python model has mail.thread inheritance
                local model_file=$(find $module_path -name "*.py" -exec grep -l "class.*models\.Model" {} \; | xargs grep -l "_name.*=.*'$model_name'" 2>/dev/null | head -1)
                if [ ! -z "$model_file" ] && ! grep -q "_inherit.*mail\.thread\|_inherit.*=.*\[.*mail\.thread" "$model_file" 2>/dev/null; then
                    echo "⚠️  Chatter fields without mail.thread in model '$model_name': $xml_file" | tee -a $LOG_FILE
                    chatter_errors=$((chatter_errors + 1))
                fi
            fi
        fi
    done

    # Check Python syntax
    local python_errors=0
    for py_file in $(find $module_path -name "*.py" 2>/dev/null); do
        if ! python3 -m py_compile "$py_file" 2>/dev/null; then
            echo "❌ Python Syntax Error in: $py_file" | tee -a $LOG_FILE
            python3 -m py_compile "$py_file" 2>&1 | tee -a $LOG_FILE
            python_errors=$((python_errors + 1))
        fi
    done

    # Check for missing files referenced in manifest
    local missing_files=0
    if [ -f "$module_path/__manifest__.py" ]; then
        cd "$module_path"
        missing_list=$(python3 -c "
import os
exec(open('__manifest__.py').read())
missing = []
for file_path in locals().get('__data__', locals().get('data', [])):
    if not os.path.exists(file_path):
        missing.append(file_path)
        print(file_path)
" 2>/dev/null)

        if [ ! -z "$missing_list" ]; then
            echo "❌ Missing files in $module_name manifest:" | tee -a $LOG_FILE
            echo "$missing_list" | while read missing_file; do
                echo "  - $missing_file" | tee -a $LOG_FILE
                missing_files=$((missing_files + 1))
            done
        fi
    fi

    local total_errors=$((xml_errors + ampersand_errors + tree_errors + chatter_errors + python_errors + missing_files))

    if [ $total_errors -eq 0 ]; then
        echo "✅ Module $module_name: VALID" | tee -a $LOG_FILE
        return 0
    else
        echo "❌ Module $module_name: $total_errors ERRORS" | tee -a $LOG_FILE
        return 1
    fi
}

# Main validation loop
valid_modules=0
invalid_modules=0

for module_dir in $BCM_ADDONS_PATH/bcm_*; do
    if [ -d "$module_dir" ] && [ -f "$module_dir/__manifest__.py" ]; then
        if validate_module "$module_dir"; then
            valid_modules=$((valid_modules + 1))
        else
            invalid_modules=$((invalid_modules + 1))
        fi
        echo "---" | tee -a $LOG_FILE
    fi
done

echo "📊 VALIDATION SUMMARY:" | tee -a $LOG_FILE
echo "✅ Valid modules: $valid_modules" | tee -a $LOG_FILE
echo "❌ Invalid modules: $invalid_modules" | tee -a $LOG_FILE

if [ $invalid_modules -eq 0 ]; then
    echo "🎉 ALL BCM MODULES ARE VALID!" | tee -a $LOG_FILE
    exit 0
else
    echo "🚨 FOUND $invalid_modules INVALID MODULES - FIX BEFORE INSTALLATION!" | tee -a $LOG_FILE
    exit 1
fi