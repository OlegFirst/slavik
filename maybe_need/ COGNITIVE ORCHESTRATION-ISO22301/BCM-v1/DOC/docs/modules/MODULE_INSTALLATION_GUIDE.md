# BCM Platform - Module Installation & Update Guide

## ❌ **ПРОБЛЕМА С МОДУЛЯМИ РЕШЕНА**

### **🔧 Что было не так:**
1. **bcm_community** - неправильные security group references
2. **bcm_reporting** - missing access rules для новых models
3. **Нет view файлов** для новых моделей

### **✅ ИСПРАВЛЕНИЯ СДЕЛАНЫ:**
1. ✅ **Security references fixed** - правильные group categories
2. ✅ **Access rules created** - для всех новых моделей
3. ✅ **Dependencies fixed** - bcm_core dependency добавлены

---

## 📋 **ПРАВИЛЬНАЯ ПРОЦЕДУРА УСТАНОВКИ:**

### **Метод 1: Через Odoo UI (Рекомендуется)**

#### **Step 1: Update Apps List**
```bash
1. Go to: http://localhost:8069
2. Login to bcm_auto database
3. Enable Developer Mode: Settings → Activate Developer Mode
4. Go to: Apps
5. Click: "Update Apps List" button
6. Wait for completion
```

#### **Step 2: Install NEW modules**
```bash
Search: "bcm_community" → Click "Install"
Wait for installation to complete
```

#### **Step 3: Upgrade ENHANCED modules**
```bash
Search: "bcm_reporting" → Click "Upgrade"
Search: "bcm_templates" → Click "Upgrade"
Search: "bcm_scenario_hub" → Click "Upgrade"
Search: "bcm_exercise" → Click "Upgrade"
```

### **Метод 2: CLI Installation (если UI не работает)**

#### **Via Docker exec:**
```bash
# Update bcm_reporting
docker exec iso-22301-odoo-1 odoo -d bcm_auto -u bcm_reporting --stop-after-init --no-http

# Install bcm_community
docker exec iso-22301-odoo-1 odoo -d bcm_auto -i bcm_community --stop-after-init --no-http

# Update other modules
docker exec iso-22301-odoo-1 odoo -d bcm_auto -u bcm_templates,bcm_scenario_hub,bcm_exercise --stop-after-init --no-http

# Restart Odoo after CLI operations
docker-compose restart odoo
```

---

## 🔍 **Как проверить установку:**

### **Проверка модулей:**
```bash
1. Go to: Apps
2. Filter: "Installed"
3. Search: "bcm_"
4. Should see:
   ✅ bcm_community (NEW)
   ✅ bcm_reporting (UPGRADED)
   ✅ bcm_templates (UPGRADED)
   ✅ bcm_scenario_hub (UPGRADED)
   ✅ bcm_exercise (UPGRADED)
```

### **Проверка функциональности:**
```bash
NEW Menus появляются:
  - Community → Forum Integration
  - Community → Forum Topics
  - Templates → BCM Templates (enhanced)
  - Reporting → Analytics Dashboard (NEW)

NEW Features работают:
  - AI scenario generation
  - Template compatibility в scenarios
  - BPMN workflows в templates
  - Analytics dashboards в reporting
```

---

## 🎯 **ВЕРСИОННОСТЬ И ОБНОВЛЕНИЯ:**

### **Как видеть версии модулей:**
```bash
1. Apps → Filter: "Installed"
2. Click on module name
3. В описании видно version: "18.0.1.0.0"
```

### **Как отслеживать изменения:**
```bash
1. Module description показывает что нового
2. Chatter в module form показывает install/upgrade history
3. Developer mode → Technical → Modules → Installed показывает details
```

### **Стратегия обновлений:**
```yaml
Подход: Incremental updates через Odoo UI
НЕ НУЖНО: Пересборка контейнеров
ДОСТАТОЧНО: Upgrade modules через Apps

Файлы автоматически берутся из:
/mnt/extra-addons/ (volume mount к /core/odoo-18.0/addons/)
```

---

## 📊 **ПОСЛЕ УСТАНОВКИ МОДУЛЕЙ:**

**Получишь enhanced functionality:**
- **AI-powered scenario generation** integration
- **BPMN workflow templates** system
- **Community forum** integration
- **Advanced analytics** dashboards
- **Knowledge base** functionality

**Затем продолжаем с глубоким анализом остальных модулей!** 🔍

**Попробуешь установить модули сейчас?** 🔧