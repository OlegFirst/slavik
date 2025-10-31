#!/bin/bash

# Обновление имен моделей на BCM префикс
echo "Updating model names to BCM prefix..."

# Замена в Python файлах
find . -name "*.py" -exec sed -i '' \
    -e "s/'digital\.twin\.organization'/'bcm.digital.twin.organization'/g" \
    -e "s/'digital\.twin\.simulation'/'bcm.digital.twin.simulation'/g" \
    -e "s/'digital\.twin\.config'/'bcm.digital.twin.config'/g" \
    -e "s/'digital\.twin\.bridge'/'bcm.digital.twin.bridge'/g" \
    -e "s/'digital\.twin\.settings'/'bcm.digital.twin.settings'/g" \
    -e "s/'ai\.twin\.orchestrator'/'bcm.ai.twin.orchestrator'/g" \
    -e 's/_name = "digital\.twin\./_name = "bcm.digital.twin./g' \
    -e 's/_name = "ai\.twin\./_name = "bcm.ai.twin./g' \
    {} \;

# Замена в XML файлах
find . -name "*.xml" -exec sed -i '' \
    -e "s/model=\"digital\.twin\./model=\"bcm.digital.twin./g" \
    -e "s/model=\"ai\.twin\./model=\"bcm.ai.twin./g" \
    -e "s/ref=\"model_digital_twin_/ref=\"model_bcm_digital_twin_/g" \
    -e "s/ref=\"model_ai_twin_/ref=\"model_bcm_ai_twin_/g" \
    {} \;

# Замена в CSV файлах
find . -name "*.csv" -exec sed -i '' \
    -e "s/model_digital_twin_/model_bcm_digital_twin_/g" \
    -e "s/model_ai_twin_/model_bcm_ai_twin_/g" \
    {} \;

echo "Model names updated to BCM prefix!"