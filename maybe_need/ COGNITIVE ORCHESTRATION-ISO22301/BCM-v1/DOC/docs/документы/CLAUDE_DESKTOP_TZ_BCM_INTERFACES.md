# 🎯 ТЗ для Claude Desktop - Генерация BCM Интерфейсов

## 📋 **ЗАДАЧА:**
Создать профессиональные интерфейсы для Business Continuity Management Platform через Claude Desktop с использованием доступных инструментов.

## 🏗️ **АРХИТЕКТУРА ПЛАТФОРМЫ:**

### **Backend (уже есть):**
- **Odoo 18.0** - основная BCM платформа (http://localhost:8069)
- **22 BCM модуля** - полный функционал ISO 22301
- **PostgreSQL** - база данных
- **API endpoints** - REST API для интеграции

### **Frontend (нужно доработать):**
- **Vue Portal v2** - пользовательский интерфейс (http://localhost:5173)
- **Odoo Website** - админ панель (проблемы с Owl errors)

## 🎯 **ЧТО НУЖНО СОЗДАТЬ:**

### **1. Incident Management Interface**
**Функционал:**
- Список всех инцидентов (список/карточки)
- Форма создания нового инцидента
- Детальный просмотр инцидента
- Фильтрация по статусу/важности
- AI рекомендации по реагированию

**Данные (модель `bcm.incident`):**
```python
- name (Incident Title) - string, required
- incident_type - selection (system_outage, data_breach, cyber_attack, etc.)
- severity - selection (low, medium, high, critical)
- status - selection (open, in_progress, resolved, closed)
- reported_date - datetime
- assigned_to - many2one res.users
- notes - text
```

### **2. Risk Management Interface**
**Функционал:**
- Risk assessment dashboard
- Risk register (список рисков)
- Risk matrix visualization
- Impact analysis tools

### **3. Business Impact Analysis (BIA)**
**Функционал:**
- Critical process identification
- RTO/RPO management
- Impact scoring
- Dependency mapping

## 🛠️ **ДОСТУПНЫЕ ИНСТРУМЕНТЫ:**

### **Option 1: B12.io (рекомендуемый)**
- **Доступ:** https://www.b12.io/ (работает в 2025)
- **Возможности:** AI website builder за 60 секунд
- **Процесс:**
  1. Регистрация на B12.io
  2. Указать: "Business Continuity Management Platform"
  3. Выбрать "Professional Services" категорию
  4. Генерация → кастомизация → экспорт кода

### **Option 2: Figma AI**
- **Доступ:** https://www.figma.com/make/
- **Возможности:** AI-powered design generation
- **Процесс:**
  1. Создать новый Figma проект
  2. Использовать "First Draft" feature
  3. Промпт: "BCM incident management dashboard"
  4. Итерации и улучшения
  5. Export to HTML/CSS

### **Option 3: MCP Server (внутренний)**
- **Доступ:** http://localhost:8087 (твой MCP сервер)
- **Возможности:** BCM Platform Chat Tools
- **Процесс:** Через MCP protocol генерация интерфейсов

## 📐 **ДИЗАЙН ТРЕБОВАНИЯ:**

### **Стиль:**
- **Цветовая схема:** Professional blue/white (#667eea, #764ba2)
- **Типографика:** Inter font family
- **Компоненты:** Modern cards, clean forms, responsive grid
- **БЕЗ эмодзи** - только иконки Font Awesome

### **Layout Pattern:**
```
Header (title + actions)
Stats Cards (4 колонки)
Main Content (list/form/dashboard)
Filters/Search (если нужно)
```

### **Responsive:**
- Desktop first
- Mobile-friendly cards
- Tablet optimization

## 🚀 **ПРОМПТЫ ДЛЯ AI ГЕНЕРАЦИИ:**

### **For B12.io:**
```
"Create a professional business continuity management platform for enterprise clients.
Include incident management, risk assessment, and business impact analysis modules.
Style: Corporate, clean, professional.
Features: Dashboard, forms, data tables, status tracking."
```

### **For Figma AI:**
```
"Design a modern enterprise dashboard for business continuity management.
Include: incident list, risk matrix, status cards, action buttons.
Style: Professional corporate interface, blue color scheme, clean typography."
```

## 📊 **ПРИОРИТЕТЫ:**

1. **Incident Management** - самый важный модуль
2. **Dashboard** - обзорная страница
3. **Risk Management** - оценка рисков
4. **BIA Module** - анализ воздействия

## 🎨 **РЕЗУЛЬТАТ:**

После генерации получим:
- **HTML/CSS/JS код** готовых интерфейсов
- **Design system** для всех BCM модулей
- **Responsive layouts** для всех устройств
- **Интеграцию** с Odoo API через готовые endpoints

## 📞 **ДАЛЕЕ:**

1. **Генерируем интерфейсы** через выбранный инструмент
2. **Интегрируем с Vue Portal** или создаем новый фронтенд
3. **Подключаем к Odoo API**
4. **Тестируем полную интеграцию**

**🎊 Цель: Профессиональные BCM интерфейсы за час вместо недель ручного кодинга!**