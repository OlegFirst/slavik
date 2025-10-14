# Module Update Checklist - AI Organs Implementation

## 🎯 **МОДУЛИ ДЛЯ ОБНОВЛЕНИЯ В ODOO:**

### **✅ ENHANCED MODULES (нужно UPGRADE):**

#### **CRITICAL - Обновить обязательно:**

**1. bcm_governance** ⭐⭐⭐
```yaml
Current: Очень простой (name, description)
Enhanced: AI Governance Brain с Anthropic integration
Files Changed:
  ✅ /models/models.py - Complete AI Brain implementation
  ✅ Added: BCMGovernanceAIBrain + BCMPolicy models

Upgrade Method:
  Odoo → Apps → Search "bcm_governance" → Upgrade
```

**2. bcm_incident** ⭐⭐⭐
```yaml
Current: Basic с некоторой AI integration
Enhanced: AI Emergency Response System
Files Changed:
  ✅ /models/bcm_incident_actions.py - Enhanced с fast AI response

Upgrade Method:
  Odoo → Apps → Search "bcm_incident" → Upgrade
```

**3. bcm_core** ⭐⭐⭐
```yaml
Current: Foundation module
Enhanced: AI Lifecycle Monitor
Files Added:
  ✅ /models/ai_lifecycle_monitor.py - Complete organism monitoring

Upgrade Method:
  Odoo → Apps → Search "bcm_core" → Upgrade
```

#### **IMPORTANT - Обновить для полной функциональности:**

**4. bcm_bia** ⭐⭐
```yaml
Enhanced: AI Impact Oracle
Files Added:
  ✅ /models/ai_impact_oracle.py - Predictive impact intelligence
```

**5. bcm_scenario_hub** ⭐⭐
```yaml
Enhanced: AI Scenario Creator
Files Added:
  ✅ /models/ai_scenario_creator.py - Creative intelligence
```

**6. bcm_audit** ⭐⭐
```yaml
Enhanced: AI Compliance Guardian
Files Added:
  ✅ /models/ai_compliance_guardian.py - Automated compliance
```

**7. bcm_kpi** ⭐⭐
```yaml
Enhanced: AI Performance Analyst
Files Added:
  ✅ /models/ai_performance_analyst.py - KPI intelligence
```

**8. bcm_training** ⭐⭐
```yaml
Enhanced: AI Learning Coach
Files Added:
  ✅ /models/ai_learning_coach.py - Adaptive learning
```

---

## 🔧 **UPGRADE PROCEDURE:**

### **Method 1: Odoo UI (Recommended)**
```bash
1. Go to: http://localhost:8069
2. Login to bcm_auto database
3. Enable Developer Mode
4. Apps → Update Apps List
5. For each enhanced module:
   - Search module name
   - Click "Upgrade" button
   - Wait for completion
```

### **Method 2: CLI (если UI не работает)**
```bash
# Upgrade critical modules:
docker exec iso-22301-odoo-1 odoo -d bcm_auto \
  -u bcm_governance,bcm_incident,bcm_core,bcm_bia,bcm_scenario_hub,bcm_audit,bcm_kpi,bcm_training \
  --stop-after-init --no-http

# Restart Odoo after CLI upgrade:
docker-compose restart odoo
```

---

## 🚨 **CONTAINER ISSUES:**

### **Failed Container: simulation_adapter**
```yaml
Container ID: fb9dcf8d98e3a7fcc22c93b983813022f17e73468983c20cdf15b80bbf30ec56
Error: ModuleNotFoundError: No module named 'config'
Status: ✅ FIXED - config.py created

Fix Applied:
  ✅ Created: /adapters/simulation/config.py
  ✅ Restart container: docker-compose restart simulation_adapter
```

### **Other Potential Issues:**
```bash
# Check all container status:
docker-compose ps

# Check logs for any other failed containers:
docker-compose logs --tail=10 [service_name]
```

---

## 📋 **VERIFICATION CHECKLIST:**

### **After Module Updates:**
```yaml
✅ Check New Menus Appear:
  - bcm_governance: "AI Governance Brain" menu
  - bcm_core: "AI Lifecycle Monitor" menu
  - bcm_incident: Enhanced incident actions
  - bcm_bia: "AI Impact Oracle" features

✅ Test AI Functionality:
  - Create governance topic → Click "AI Analysis"
  - Create incident → Click "AI Emergency Response"
  - Check AI Lifecycle Monitor → View organs health

✅ Verify Integration:
  - AI Orchestrator (:8000) responding
  - Scenario Orchestrator (:8085) working
  - MCP Server (:8087) enhanced
```

### **Critical Success Indicators:**
```yaml
1. bcm_governance.brain model exists и functional
2. AI analysis buttons appear в enhanced modules
3. Lifecycle monitor shows AI organs health
4. MCP tools respond с organism data
5. No critical errors в Odoo logs
```

---

## 🎯 **PRIORITY UPDATES:**

### **MUST UPDATE (для AI organs):**
1. **bcm_governance** ⭐⭐⭐ - AI Governance Brain
2. **bcm_incident** ⭐⭐⭐ - AI Emergency Response
3. **bcm_core** ⭐⭐⭐ - AI Lifecycle Monitor

### **SHOULD UPDATE (для full functionality):**
4-8. **Remaining 5 enhanced modules** - AI organs

### **CONTAINER FIX:**
- **simulation_adapter** ✅ Fixed - restart container

---

## 🚀 **ГОТОВ К ORGANISM ACTIVATION!**

**Обновляй critical modules и тестируем Digital BCM Organism!** 🧬⚡