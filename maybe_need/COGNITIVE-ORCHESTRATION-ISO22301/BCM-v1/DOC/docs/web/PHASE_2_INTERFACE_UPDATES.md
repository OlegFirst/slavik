# ЭТАП 2: Interface Updates - ТЗ для команды интерфейсов

## 🎯 Изменения архитектуры

**РЕШЕНИЕ**: Community Service **удаляется** как отдельный сервис!
**НОВОЕ**: bcm_community становится **Odoo website module**

## 📋 Изменения для интерфейсов

### **1. Odoo BCM Module Interfaces (NEW)**

#### **bcm_community Module - Website Integration**
```yaml
Локация: /core/odoo-18.0/addons/bcm_community/
Технология: Odoo Website + Portal framework
Статус: Модуль создан, нужна установка

NEW Website Pages:
  - /bcm/community                     # Community homepage
  - /bcm/community/scenarios           # Scenario discussions
  - /bcm/community/scenario/{id}/discuss # Specific scenario discussion
  - /my/bcm                           # User BCM portal
  - /my/bcm/scenarios                 # User's scenarios

NEW Odoo Menus:
  Community/
    ├── 🔧 Forum Integration
    ├── 📝 Forum Topics
    │   ├── All Topics
    │   └── Scenario Discussions
    ├── 📊 Community Analytics
    └── 📚 Knowledge Base
```

#### **bcm_scenario_hub Module Updates**
```yaml
Файл: /core/odoo-18.0/addons/bcm_scenario_hub/models/bcm_scenario.py

NEW Fields:
  - forum_topic_id: Many2one('bcm.forum.topic')  # Link to forum discussion

NEW Methods:
  - action_publish_scenario()           # Auto-creates forum topic
  - action_create_forum_discussion()    # Manual forum creation
  - _notify_community_service()         # Webhook notifications

NEW View Buttons:
  - "Create Forum Discussion" button
  - "View Discussion" button
  - Forum topic indicator in scenario form
```

---

### **2. Frontend Updates Required**

#### **Vue.js Web Portal Updates**
```yaml
Файлы для обновления:

/src/views/BCMScenarioHub.vue:
  UPDATE: Add forum discussion links
  UPDATE: Show AI-generated badge
  ADD: "Discuss in Community" button
  ADD: Forum activity indicators

NEW Components:
  /src/components/community/CommunityWidget.vue:
    - Recent forum activity widget
    - Quick discussion links
    - Community stats display

  /src/components/scenario/ScenarioForumLink.vue:
    - Forum discussion link component
    - Discussion participation indicators
    - Quick comment interface
```

#### **Admin Panel Updates (React)**
```yaml
NEW Components:

/src/components/community/CommunityManagement.jsx:
  - Forum integration status
  - Community analytics dashboard
  - Moderation tools

/src/components/monitoring/ServiceHealthDashboard.jsx:
  UPDATE: Remove Community Service monitoring
  ADD: bcm_community module status
  ADD: Website forum metrics
```

---

### **3. API Integration Changes**

#### **УДАЛЯЕТСЯ**:
```bash
# Community Service endpoints (больше не нужны):
❌ http://localhost:3000/api/topics
❌ http://localhost:3000/api/users
❌ http://localhost:3000/api/stats
❌ WebSocket ws://localhost:3000/ws/{user_id}
```

#### **ЗАМЕНЯЕТСЯ на Odoo endpoints**:
```bash
# NEW Odoo website endpoints:
✅ http://localhost:8069/bcm/community
✅ http://localhost:8069/bcm/community/api/stats
✅ http://localhost:8069/bcm/community/scenario/{id}/discuss
✅ http://localhost:8069/my/bcm  # Portal integration
```

#### **JavaScript API Integration**:
```javascript
// UPDATE: Remove Community Service calls
// OLD (удалить):
const communityService = {
  baseURL: 'http://localhost:3000',
  getTopics: () => axios.get('/api/topics'),
  createTopic: (data) => axios.post('/api/topics', data)
};

// NEW (использовать):
const odooWebsiteAPI = {
  baseURL: 'http://localhost:8069',
  getStats: () => axios.get('/bcm/community/api/stats'),
  createDiscussion: (scenarioId) =>
    axios.post(`/bcm/community/api/scenarios/${scenarioId}/create-discussion`)
};
```

---

### **4. Environment Variables Updates**

#### **УДАЛИТЬ из .env и docker-compose**:
```env
# Community Service vars (удалить):
❌ COMMUNITY_SERVICE_URL=http://localhost:3000
❌ FORUM_API_KEY=xxx
❌ FORUM_DB_PASSWORD=xxx
```

#### **ДОБАВИТЬ**:
```env
# Odoo website integration:
✅ ODOO_WEBSITE_FORUM_ENABLED=true
✅ BCM_COMMUNITY_MODULE_INSTALLED=true
```

---

## 🗑️ **Удаление Community Service из /services/**

### **Файлы для удаления**:
```bash
# Полностью удалить директорию:
rm -rf /Users/MD/ISO-22301/services/community/

# Эти файлы больше не нужны:
❌ forum_service.py
❌ worker.py
❌ docker-compose.yml
❌ Dockerfile
❌ requirements.txt
❌ sql/
```

### **Что сохранить (перенести в bcm_community)**:
```bash
# Логика которую можно переиспользовать:
✅ Real-time notification patterns → Odoo bus/longpolling
✅ Community analytics logic → Odoo computed fields
✅ Forum categorization → Forum categories data
```

---

## 📊 **Benefits новой архитектуры:**

### **✅ Преимущества**:
1. **Единая система** - все в Odoo
2. **Нет дублирования** - users, companies, auth
3. **Native integration** - scenarios ↔ forum seamless
4. **Portal ready** - external users из коробки
5. **Maintenance simplicity** - один codebase
6. **Performance** - нет network calls между сервисами

### **🔧 Implementation Steps**:
1. **Установить bcm_community** в Odoo
2. **Обновить frontend** - убрать Community Service calls
3. **Добавить website templates** в модуль
4. **Удалить /services/community** директорию
5. **Обновить документацию**

---

## 🎯 **Для команды интерфейсов:**

### **Immediate Actions**:
1. **Обновить BCMScenarioHub.vue** - убрать Community Service references
2. **Добавить Odoo website links** - /bcm/community URLs
3. **Создать CommunityWidget.vue** - показывать forum activity
4. **Обновить Admin Panel** - убрать Community Service monitoring

### **API Changes**:
```javascript
// OLD (удалить все references):
const COMMUNITY_API = 'http://localhost:3000';

// NEW (использовать):
const ODOO_COMMUNITY = 'http://localhost:8069/bcm/community';
```

## ✅ **Результат**:

**Community как часть Odoo** вместо отдельного проблемного сервиса!

**Переносим Community Service логику в bcm_community модуль и удаляем /services/community/?** 🗑️➡️🏛️