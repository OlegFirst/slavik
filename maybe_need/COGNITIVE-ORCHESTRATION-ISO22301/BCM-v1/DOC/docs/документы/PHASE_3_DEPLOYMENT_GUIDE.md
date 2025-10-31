# ЭТАП 3: Deployment Guide - BPMN Workflow Integration

## 🚀 Deployment Steps для ЭТАП 3

### **Prerequisites:**
- ✅ ЭТАП 1 и 2 завершены
- ✅ All services running (80%+ health)
- ✅ bcm_community module prepared

---

## 📋 **Deployment Checklist**

### **Step 1: Update Odoo Modules**

#### **1.1: Install Enhanced bcm_templates**
```bash
# Restart Odoo to load updated bcm_templates
docker-compose restart odoo

# Wait for Odoo startup
sleep 30

# Install/upgrade module via Odoo UI:
# 1. Go to http://localhost:8069
# 2. Apps → Update Apps List
# 3. Search: bcm_templates
# 4. Click: Upgrade (or Install if not installed)
```

#### **1.2: Install bcm_community Module**
```bash
# Install bcm_community module via Odoo UI:
# 1. Go to http://localhost:8069
# 2. Apps → Update Apps List
# 3. Search: bcm_community
# 4. Click: Install

# OR use CLI:
./install-bcm-community.sh
```

#### **1.3: Upgrade bcm_scenario_hub**
```bash
# Upgrade existing module to get new template integration:
# 1. Go to http://localhost:8069
# 2. Apps → Search: bcm_scenario_hub
# 3. Click: Upgrade
```

#### **1.4: Upgrade bcm_exercise**
```bash
# Upgrade existing module to get template integration:
# 1. Go to http://localhost:8069
# 2. Apps → Search: bcm_exercise
# 3. Click: Upgrade
```

---

### **Step 2: Verify Service Integration**

#### **2.1: Test BPMN Service Connection**
```bash
# Check BPMN Service health
curl http://localhost:8005/health

# Expected response:
# {"status":"healthy","service":"bpmn_workflow"}
```

#### **2.2: Test Template System**
```bash
# After module installation, verify templates exist:
# 1. Go to http://localhost:8069
# 2. Menu: Templates → BCM Templates
# 3. Should see: 3 workflow templates (Tabletop, Full-Scale, Incident Response)
```

#### **2.3: Test Scenario-Template Integration**
```bash
# 1. Go to http://localhost:8069
# 2. Menu: Scenario Hub → Scenario Catalog
# 3. Open any published scenario
# 4. Should see: "Compatible Templates" field populated
# 5. Button: "Create Exercise from Scenario" should appear
```

---

### **Step 3: Test End-to-End Workflow**

#### **3.1: Create Exercise from AI Scenario**
```bash
# Test complete flow:
# 1. Generate AI scenario:
curl -X POST http://localhost:8085/scenarios/generate \
  -H "Content-Type: application/json" \
  -d '{"category": "cyber", "complexity": 3, "participants": 8}'

# 2. Go to Odoo: Scenario Hub → find AI scenario
# 3. Click: "Create Exercise from Scenario"
# 4. Select template: "Tabletop Exercise Workflow"
# 5. Click: "Create Exercise"
```

#### **3.2: Start BPMN Workflow**
```bash
# After exercise creation:
# 1. Go to: Exercises → [Created Exercise]
# 2. Add participants (select users)
# 3. Click: "Start Workflow" button
# 4. Should see: workflow_status = "running"
# 5. Check Slack for participant notifications
```

#### **3.3: Monitor Workflow Progress**
```bash
# Monitor workflow in real-time:
# 1. Exercise form should show: BPMN Process ID
# 2. Click: "Sync Tasks" to get current workflow tasks
# 3. Current Tasks field should populate with JSON
# 4. Participants should receive Odoo activities/tasks
```

---

### **Step 4: Configure External Integrations**

#### **4.1: Slack Notifications (if not configured)**
```bash
# Update .env with real Slack webhook:
SLACK_ENABLED=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/REAL/WEBHOOK
SLACK_CHANNEL_ALERTS=#bcm-alerts

# Restart notification service:
docker-compose restart notification_service
```

#### **4.2: Test Notification Flow**
```bash
# Test Slack integration:
curl -X POST http://localhost:8002/external/notify \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Exercise Notification",
    "message": "Testing BPMN workflow notifications",
    "channels": ["slack"],
    "severity": "info"
  }'
```

---

## 🧪 **Validation Tests**

### **Test 1: AI Scenario → Exercise Creation**
```yaml
Steps:
  1. Generate AI cyber scenario (complexity 4)
  2. Verify scenario has compatible templates
  3. Create exercise from scenario
  4. Verify exercise links to scenario and template

Expected Result:
  ✅ Exercise created with scenario_id and template_id populated
  ✅ Compatible templates include "Incident Response" для cyber scenarios
```

### **Test 2: BPMN Workflow Execution**
```yaml
Steps:
  1. Create exercise with "Tabletop Exercise" template
  2. Add 3-5 participants
  3. Click "Start Workflow"
  4. Check BPMN Service logs
  5. Verify participant notifications

Expected Result:
  ✅ workflow_status = "running"
  ✅ bpmn_process_id populated
  ✅ Slack notifications sent to participants
  ✅ Odoo activities created for participants
```

### **Test 3: Template Library**
```yaml
Steps:
  1. Go to Templates → BCM Templates
  2. Verify 3 workflow templates exist
  3. Open "Full-Scale Exercise" template
  4. Verify BPMN XML is populated
  5. Click "Preview Template"

Expected Result:
  ✅ 3 workflow templates visible
  ✅ BPMN XML valid и complete
  ✅ Template preview opens successfully
```

---

## 🔧 **Troubleshooting Guide**

### **Issue 1: Templates Not Appearing**
```bash
# Solution:
# 1. Check if bcm_templates module upgraded successfully
# 2. Verify data/bpmn_workflow_templates.xml loaded
# 3. Check logs: docker-compose logs odoo
```

### **Issue 2: BPMN Workflow Not Starting**
```bash
# Solution:
# 1. Check BPMN Service health: curl http://localhost:8005/health
# 2. Verify template has valid BPMN XML
# 3. Check exercise has template_id populated
# 4. Check logs: docker-compose logs bpmn_service
```

### **Issue 3: Notifications Not Sending**
```bash
# Solution:
# 1. Verify SLACK_WEBHOOK_URL in .env
# 2. Check notification service: curl http://localhost:8002/health
# 3. Test notification endpoint directly
# 4. Check logs: docker-compose logs notification_service
```

---

## 📊 **Deployment Success Metrics**

### **Module Installation:**
- ✅ bcm_templates module shows "Installed" в Apps
- ✅ bcm_community module shows "Installed" в Apps
- ✅ bcm_scenario_hub и bcm_exercise show "Upgraded" status

### **Template Library:**
- ✅ 3 BPMN workflow templates visible в Templates menu
- ✅ Templates have valid BPMN XML content
- ✅ Template types match scenario categories

### **Integration Working:**
- ✅ Scenarios show compatible templates
- ✅ "Create Exercise from Scenario" button appears
- ✅ Exercise creation wizard opens successfully
- ✅ BPMN workflows start without errors
- ✅ Participant notifications sent via Slack

### **Performance:**
- ✅ Template matching под 500ms
- ✅ Exercise creation под 2 seconds
- ✅ BPMN workflow start под 5 seconds
- ✅ Notification delivery под 3 seconds

---

**ЭТАП 3 deployment guide готов для production rollout!** 🚀

**Все компоненты протестированы и ready для interface team implementation!** 🎨✨