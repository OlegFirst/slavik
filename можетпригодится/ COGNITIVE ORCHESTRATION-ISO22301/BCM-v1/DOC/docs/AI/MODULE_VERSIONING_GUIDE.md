# Module Versioning Guide - AI Organisms Updates

## 🔢 **VERSION TRACKING SYSTEM:**

### **Version Format:** `18.0.X.Y.Z`
```yaml
18.0 - Odoo version
X - Major AI enhancement (0→1→2)
Y - Minor feature addition (0→1→2)
Z - Bug fixes (0→1→2)
```

---

## 📊 **MODULE VERSIONS BEFORE/AFTER:**

### **AI GOVERNANCE BRAIN (bcm_governance):**
```yaml
BEFORE: 18.0.1.0.0 (Basic governance)
AFTER:  18.0.2.0.0 (AI Governance Brain)

Changes:
  ✅ Added: BCMGovernanceAIBrain model
  ✅ Added: BCMPolicy model
  ✅ Added: Anthropic integration
  ✅ Summary: "🧠 AI Governance Brain - Strategic Intelligence"
  ✅ Description: Complete AI capabilities description
```

### **AI EMERGENCY RESPONSE (bcm_incident):**
```yaml
BEFORE: 18.0.1.0.0 (Basic incident + some AI)
AFTER:  18.0.2.0.0 (AI Emergency Response)

Changes Needed:
  - Version bump
  - Summary update
  - Description enhancement
  - New AI capabilities documentation
```

### **AI LIFECYCLE MONITOR (bcm_core):**
```yaml
BEFORE: 18.0.1.0.0 (Foundation)
AFTER:  18.0.2.0.0 (+ AI Lifecycle Monitor)

Changes Needed:
  - Version bump
  - Add AI monitoring capabilities
  - Description enhancement
```

---

## 🏷️ **METADATA ENHANCEMENT TEMPLATE:**

### **Для каждого AI-enhanced модуля:**

#### **Category Enhancement:**
```yaml
OLD: "Business Continuity"
NEW: "AI-Enhanced Business Continuity" 🤖
```

#### **Summary Enhancement Pattern:**
```yaml
OLD: "Basic [module function]"
NEW: "🧠 AI [Organ Name] - [AI Capability] with [AI Provider] Integration"

Examples:
  bcm_governance: "🧠 AI Governance Brain - Strategic Intelligence with Anthropic"
  bcm_incident: "🚨 AI Emergency Response - Fast Crisis Management with Local AI"
  bcm_bia: "🔮 AI Impact Oracle - Predictive Analysis with Digital Twin"
```

#### **Description Enhancement:**
```yaml
Structure:
  1. DIGITAL ORGANISM COMPONENT header
  2. AI capabilities overview
  3. Specific AI features
  4. Integration points
  5. Ecosystem role
  6. "PART OF DIGITAL BCM ORGANISM" footer
```

---

## 🔄 **HOW TO CHECK UPDATE SUCCESS:**

### **In Odoo Apps List:**
```yaml
✅ Version Changed: 18.0.1.0.0 → 18.0.2.0.0
✅ Summary Shows: "🧠 AI [Organ Name]"
✅ Category Shows: "AI-Enhanced Business Continuity"
✅ Status Shows: "Installed" (not "To Upgrade")
✅ Description Shows: AI capabilities
```

### **In Module Details:**
```yaml
✅ Latest Version: 18.0.2.0.0
✅ Dependencies: Shows new AI dependencies
✅ Created Menus: Shows new AI menus
✅ Created Views: Shows AI brain views
✅ Demo Data: AI examples available
```

### **Functional Verification:**
```yaml
✅ New Menu Appears: "AI Governance Brain"
✅ New Model Works: bcm.governance.brain
✅ AI Buttons Work: "AI Analysis", "Emergency Session"
✅ No Errors: Clean installation logs
```

---

## 📋 **QUICK VERSION UPDATE COMMANDS:**

### **Update Critical Modules:**
```bash
# 1. bcm_governance
# Version: 18.0.1.0.0 → 18.0.2.0.0 ✅ DONE

# 2. bcm_incident
# Version: 18.0.1.0.0 → 18.0.2.0.0 (needs update)

# 3. bcm_core
# Version: 18.0.1.0.0 → 18.0.2.0.0 (needs update)
```

### **After Version Updates:**
```bash
# Force Odoo to recognize version changes:
docker exec iso-22301-odoo-1 odoo -d bcm_auto \
  -u bcm_governance,bcm_incident,bcm_core \
  --stop-after-init --no-http

# Restart Odoo:
docker-compose restart odoo
```

---

## 🎯 **VERSION TRACKING BENEFITS:**

### **Easy Change Tracking:**
- **Version number** показывает AI enhancement level
- **Summary** immediately shows AI capabilities
- **Dependencies** показывает AI service requirements
- **Description** shows complete AI organism role

### **User Benefits:**
- **Clear AI capabilities** visibility
- **Version history** tracking
- **Feature evolution** понимание
- **Troubleshooting** easier с version info

---

## ✅ **ОБНОВЛЯЮ ОСТАЛЬНЫЕ VERSIONS:**

**Хочешь чтобы я обновил versions и metadata для всех AI-enhanced модулей сейчас?**

**Или сначала протестируем bcm_governance с новой версией?** 🔢⚡