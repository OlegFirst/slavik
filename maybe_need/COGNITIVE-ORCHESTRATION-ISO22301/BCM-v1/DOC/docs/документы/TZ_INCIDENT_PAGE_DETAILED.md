# 📋 ТЗ: Страница Incident Management

## 🎯 **ЦЕЛЬ СТРАНИЦЫ:**
Создать профессиональную страницу управления инцидентами для BCM платформы.

## 📊 **СТРУКТУРА СТРАНИЦЫ:**

### **1. HEADER SECTION**
```
┌─────────────────────────────────────────────────────────────┐
│ [🔥] Incident Management          [🆘 Report] [⚙️ Settings] │
│ Manage and track business continuity incidents             │
└─────────────────────────────────────────────────────────────┘
```
**Элементы:**
- **Заголовок:** "Incident Management" (без эмодзи)
- **Подзаголовок:** "Manage and track business continuity incidents"
- **Кнопка справа:** "Report Incident" (красная, primary action)
- **Кнопка настроек:** "Settings" (серая, secondary)

### **2. STATS CARDS (4 карточки в ряд)**
```
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ OPEN    │ │ CRITICAL│ │ RESOLVED│ │ AVG TIME│
│   7     │ │    2    │ │    15   │ │  4.2h   │
│ Active  │ │ Urgent  │ │ Today   │ │Response │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```
**Спецификация карточек:**
- **Размер:** col-lg-3 col-md-6 (responsive)
- **Стиль:** Белые карточки с цветными левыми границами
- **Цвета:** Blue(#667eea), Red(#dc3545), Green(#28a745), Orange(#fd7e14)
- **Иконки:** FontAwesome (folder-open, fire, check-circle, clock)
- **Hover:** Поднятие на 2px, тень увеличивается

### **3. FILTERS BAR**
```
┌─────────────────────────────────────────────────────────────┐
│ [All] [Open] [Critical] [My Incidents]    [List] [Cards]   │
└─────────────────────────────────────────────────────────────┘
```
**Элементы:**
- **Filter buttons:** Toggle группа (Primary/Outline-secondary)
- **View switcher:** List/Cards иконки справа
- **Active state:** Blue background (#667eea)

### **4. MAIN CONTENT AREA**

#### **LIST VIEW:**
```
┌─────────────────────────────────────────────────────────────┐
│ Title               │ Type      │ Severity │ Status │ Date │
├─────────────────────────────────────────────────────────────┤
│ System Outage       │ Technical │ Critical │ Open   │ 2h   │
│ Network Issues      │ Technical │ High     │ Active │ 5h   │
│ Data Center Down    │ Technical │ Critical │ Resolved│ 1d  │
└─────────────────────────────────────────────────────────────┘
```

#### **CARD VIEW:**
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ [CRITICAL]      │ │ [HIGH]          │ │ [MEDIUM]        │
│ System Outage   │ │ Network Issues  │ │ Backup Failed   │
│ Reported: 2h ago│ │ Reported: 5h ago│ │ Reported: 1d ago│
│ [View] [Edit]   │ │ [View] [Edit]   │ │ [View] [Edit]   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 🎨 **ДЕТАЛЬНЫЙ СТИЛЬ:**

### **Цветовая палитра:**
```css
--primary: #667eea      /* Основной синий */
--secondary: #764ba2    /* Вторичный фиолетовый */
--success: #28a745      /* Зеленый для успеха */
--danger: #dc3545       /* Красный для критичного */
--warning: #ffc107      /* Желтый для предупреждений */
--info: #17a2b8         /* Голубой для информации */
--light: #f8f9fa        /* Светло-серый фон */
--dark: #343a40         /* Темно-серый текст */
```

### **Типографика:**
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
H1: 2rem, font-weight: 700
H2: 1.5rem, font-weight: 600
H3: 1.25rem, font-weight: 600
Body: 1rem, font-weight: 400
Small: 0.875rem, font-weight: 400
```

### **Spacing:**
```css
Grid: 8px base unit
Padding: 1rem (16px)
Margin: 1rem (16px)
Gap: 1rem (16px)
Border-radius: 8px
```

### **Cards Spec:**
```css
background: white
border: none
box-shadow: 0 2px 4px rgba(0,0,0,0.1)
border-radius: 8px
padding: 1.5rem
transition: all 0.2s ease

hover:
  transform: translateY(-2px)
  box-shadow: 0 4px 8px rgba(0,0,0,0.15)
```

### **Buttons:**
```css
Primary: Linear gradient(#667eea → #764ba2)
Secondary: Border #e2e8f0, color #718096
Danger: Solid #dc3545
Success: Solid #28a745

Размеры:
- Small: padding 0.375rem 0.75rem
- Normal: padding 0.5rem 1rem
- Large: padding 0.75rem 1.5rem
```

### **Table Style:**
```css
background: white
border: none
border-radius: 8px
thead: background #f8f9fa

Строки:
- hover: background #f8f9fa
- border-bottom: 1px solid #e9ecef
```

## 📱 **RESPONSIVE BREAKPOINTS:**
```css
Mobile: < 768px (стек карточек)
Tablet: 768px - 1024px (2 колонки)
Desktop: > 1024px (4 колонки)
```

## 🔧 **КОМПОНЕНТЫ:**

### **Status Badges:**
```html
<span class="badge bg-danger">Critical</span>
<span class="badge bg-warning">High</span>
<span class="badge bg-success">Low</span>
```

### **Action Buttons:**
```html
<div class="btn-group btn-group-sm">
  <button class="btn btn-outline-primary">View</button>
  <button class="btn btn-outline-secondary">Edit</button>
  <button class="btn btn-outline-danger">Delete</button>
</div>
```

## 📋 **КОНКРЕТНЫЕ РАЗМЕРЫ:**

- **Страница:** Full width container-fluid
- **Header:** Высота 120px, padding 2rem 0
- **Stats cards:** Высота 120px, минимальная ширина 250px
- **Filter bar:** Высота 60px
- **Main content:** Минимальная высота 400px
- **Cards:** Минимальная высота 200px

**🎯 Используй это ТЗ для генерации в B12.io, Figma AI или MCP!**