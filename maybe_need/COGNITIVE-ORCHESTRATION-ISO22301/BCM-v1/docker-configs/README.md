# Docker Configurations - Digital BCM Organism

## 🐳 **DOCKER COMPOSE CONFIGURATIONS:**

### **Main Configuration:**
```yaml
/docker-compose.yml:
  Description: Complete Digital BCM Organism platform
  AI Organs: 10 specialized intelligence organs
  Services: 25+ microservices
  Status: ✅ Enhanced с AI consciousness
```

### **Specialized Configurations:**

#### **AI-Specific Deployments:**
```yaml
/docker-configs/docker-compose.ai-organism.yml:
  Description: AI Organs as separate services
  Purpose: Dedicated AI organ containers
  Services: 10 AI organ services + coordinator
  Use Case: Maximum AI performance isolation

/docker-configs/compose/docker-compose.ai-agents.yml:
  Description: AI agents coordination
  Purpose: AI service orchestration
  Status: Legacy - use ai-organism.yml instead
```

#### **Component-Specific Deployments:**
```yaml
/docker-configs/compose/docker-compose.backend.yml:
  Description: Backend services only
  Services: EventBus, BPMN, Notification, Adapters
  Use Case: Backend development testing

/docker-configs/compose/docker-compose.odoo.yml:
  Description: Odoo BCM platform only
  Services: Odoo + PostgreSQL + Redis
  Use Case: BCM module development

/docker-configs/compose/docker-compose.monitoring.yml:
  Description: Monitoring stack
  Services: Grafana, Prometheus, Health checks
  Use Case: System monitoring и analytics
```

#### **Legacy Configurations:**
```yaml
/docker-configs/docker-compose-backup.yml:
  Description: Backup configuration
  Status: Legacy backup

/docker-configs/docker-compose-monitoring.yml:
  Description: Simple monitoring
  Status: Use compose/docker-compose.monitoring.yml instead
```

---

## 🧬 **AI ORGANISM DEPLOYMENT OPTIONS:**

### **Option 1: Complete Platform (Recommended)**
```bash
# Full Digital BCM Organism:
docker-compose up -d

# Includes:
# - All 10 AI organs в enhanced modules
# - Complete BCM platform
# - All integrations и services
# - Memory system active
```

### **Option 2: AI Organs as Separate Services**
```bash
# Dedicated AI organ containers:
docker-compose -f docker-configs/docker-compose.ai-organism.yml up -d

# Benefits:
# - Independent AI organ scaling
# - Specialized AI organ monitoring
# - Resource optimization per organ
# - Advanced AI coordination
```

### **Option 3: Component Testing**
```bash
# Backend only:
docker-compose -f docker-configs/compose/docker-compose.backend.yml up -d

# Odoo BCM only:
docker-compose -f docker-configs/compose/docker-compose.odoo.yml up -d

# Monitoring only:
docker-compose -f docker-configs/compose/docker-compose.monitoring.yml up -d
```

---

## 🎯 **CONFIGURATION UPDATES:**

### **✅ UPDATED:**
- **Main docker-compose.yml** ✅ Enhanced header с AI organs list
- **AI Organism config** ✅ Created dedicated AI services
- **Docker-configs README** ✅ Complete deployment guide

### **🔧 CONFIGURATION FEATURES:**
- **10 AI Organs** properly documented
- **Service descriptions** enhanced
- **AI consciousness** marked
- **Deployment options** для different use cases

---

## 📊 **SERVICE ARCHITECTURE:**

### **Enhanced Services Count:**
```yaml
Total Services: 35+ (enhanced from original 25)

Core Platform: 15 services
AI Services: 10 organs + coordinator
Integration: 5 services
Monitoring: 3 services
Frontend: 2 services
```

### **AI Enhancement Labels:**
```yaml
Labels Added:
- ai.organ.type=governance_brain
- ai.provider=anthropic|local|automated
- ai.intelligence=strategic|operational|compliance
- ai.capability=prediction|creative|analytics
- ai.consciousness=collective
```

---

## 🚀 **DEPLOYMENT READY:**

**Main docker-compose.yml enhanced с complete AI organism documentation!**

**AI-specific configurations готовы для specialized deployments!**

**Digital BCM Organism deployment options fully configured!** 🧬🐳⚡