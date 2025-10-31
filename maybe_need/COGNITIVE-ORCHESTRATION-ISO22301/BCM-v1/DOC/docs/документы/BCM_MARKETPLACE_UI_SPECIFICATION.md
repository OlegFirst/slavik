# Техническое задание на интерфейсы BCM Community Marketplace

## 📋 Содержание
1. [Общие требования к UI/UX](#общие-требования)
2. [Интерфейс специалиста](#интерфейс-специалиста)
3. [Интерфейс клиента](#интерфейс-клиента)
4. [Маркетплейс](#маркетплейс)
5. [Система управления проектами](#система-управления-проектами)
6. [Мобильное приложение](#мобильное-приложение)

---

## 🎨 Общие требования к UI/UX

### Дизайн-система

#### Цветовая схема
```css
:root {
  /* Основные цвета */
  --primary: #1976D2;      /* Синий - основной бренд */
  --secondary: #FF6B35;    /* Оранжевый - акценты */
  --success: #4CAF50;      /* Зеленый - успех */
  --danger: #F44336;       /* Красный - ошибки/риски */
  --warning: #FFA726;      /* Желтый - предупреждения */
  --info: #29B6F6;        /* Голубой - информация */
  
  /* Нейтральные */
  --dark: #1A1A2E;        /* Темный фон */
  --light: #F7F9FC;       /* Светлый фон */
  --gray-100: #F5F5F5;
  --gray-300: #E0E0E0;
  --gray-500: #9E9E9E;
  --gray-700: #616161;
  --gray-900: #212121;
}
```

#### Типографика
```css
/* Заголовки */
h1 { font-size: 32px; font-weight: 600; }
h2 { font-size: 24px; font-weight: 600; }
h3 { font-size: 20px; font-weight: 500; }
h4 { font-size: 18px; font-weight: 500; }

/* Текст */
body { font-size: 14px; line-height: 1.5; }
.text-small { font-size: 12px; }
.text-large { font-size: 16px; }
```

#### Компоненты
- **Кнопки**: Primary, Secondary, Danger, Ghost, Link
- **Формы**: Input, Select, Textarea, Checkbox, Radio, Switch
- **Карточки**: Standard, Elevated, Outlined
- **Модальные окна**: Dialog, Drawer, Notification
- **Навигация**: Header, Sidebar, Tabs, Breadcrumbs

### Адаптивность
- Desktop: 1920px, 1440px, 1366px
- Tablet: 768px - 1024px
- Mobile: 320px - 767px

### Доступность (A11y)
- WCAG 2.1 Level AA соответствие
- Keyboard navigation
- Screen reader support
- High contrast mode

---

## 👨‍💼 Интерфейс специалиста

### 1. Дашборд специалиста

```
┌─────────────────────────────────────────────────────────────┐
│  Header                                                     │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌─────────────┐ │
│  │   Logo   │ │  Поиск     │ │ Сообщения│ │  Профиль    │ │
│  └──────────┘ └────────────┘ └──────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌────────────────────────────────────┐  │
│  │             │  │  Статистика                        │  │
│  │  Sidebar    │  │  ┌──────┐ ┌──────┐ ┌──────┐      │  │
│  │             │  │  │Доход │ │Проекты│ │Рейтинг│     │  │
│  │  • Dashboard │  │  │$12.5k│ │  23   │ │ 4.8★ │     │  │
│  │  • Запросы   │  │  └──────┘ └──────┘ └──────┘      │  │
│  │  • Проекты   │  └────────────────────────────────────┘  │
│  │  • Профиль   │                                          │
│  │  • Финансы   │  ┌────────────────────────────────────┐  │
│  │  • Сообщения │  │  Активные проекты                 │  │
│  │  • Настройки │  │  ┌──────────────────────────────┐ │  │
│  │             │  │  │ Project 1 - 75% complete    │ │  │
│  └─────────────┘  │  │ Deadline: 25 Sep            │ │  │
│                   │  └──────────────────────────────┘ │  │
│                   └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Функциональные элементы:

**Виджет статистики**
- Доход за период (день/неделя/месяц/год)
- Количество активных проектов
- Средний рейтинг
- Просмотры профиля
- Конверсия предложений

**График доходов**
- Line chart с выбором периода
- Сравнение с предыдущим периодом
- Экспорт в CSV/PDF

**Список активных проектов**
- Название и клиент
- Прогресс-бар
- Дедлайн с цветовой индикацией
- Быстрые действия (открыть, сообщение клиенту)

**Новые запросы**
- Карточки с кратким описанием
- Теги навыков
- Бюджет и сроки
- Кнопка "Подать предложение"

### 2. Профиль специалиста

#### Структура профиля:

```vue
<template>
  <div class="specialist-profile">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <img :src="specialist.avatar" class="avatar" />
        <div class="info">
          <h1>{{ specialist.name }}</h1>
          <p class="title">{{ specialist.title }}</p>
          <div class="badges">
            <Badge v-if="specialist.isVerified" type="verified" />
            <Badge v-for="badge in specialist.badges" :key="badge.id" />
          </div>
          <div class="stats">
            <div class="stat">
              <span class="value">{{ specialist.rating }}</span>
              <span class="label">Рейтинг</span>
            </div>
            <div class="stat">
              <span class="value">{{ specialist.projectsCount }}</span>
              <span class="label">Проектов</span>
            </div>
            <div class="stat">
              <span class="value">{{ specialist.yearsExperience }}</span>
              <span class="label">Лет опыта</span>
            </div>
          </div>
        </div>
        <div class="actions">
          <Button variant="primary">Предложить проект</Button>
          <Button variant="secondary">Сообщение</Button>
        </div>
      </div>
    </section>

    <!-- Tabs Navigation -->
    <Tabs v-model="activeTab">
      <Tab name="about">О себе</Tab>
      <Tab name="services">Услуги</Tab>
      <Tab name="portfolio">Портфолио</Tab>
      <Tab name="certifications">Сертификаты</Tab>
      <Tab name="reviews">Отзывы</Tab>
    </Tabs>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- About Tab -->
      <div v-if="activeTab === 'about'">
        <Card>
          <h3>Обо мне</h3>
          <p>{{ specialist.bio }}</p>
          
          <h4>Специализации</h4>
          <TagList :tags="specialist.specializations" />
          
          <h4>Индустрии</h4>
          <TagList :tags="specialist.industries" />
          
          <h4>Языки</h4>
          <ul class="languages">
            <li v-for="lang in specialist.languages">
              {{ lang.name }} - {{ lang.level }}
            </li>
          </ul>
        </Card>
      </div>

      <!-- Services Tab -->
      <div v-if="activeTab === 'services'">
        <ServiceCard 
          v-for="service in specialist.services"
          :key="service.id"
          :service="service"
        />
      </div>

      <!-- Portfolio Tab -->
      <div v-if="activeTab === 'portfolio'">
        <PortfolioGrid :items="specialist.portfolio" />
      </div>
    </div>
  </div>
</template>
```

### 3. Создание/редактирование предложения

#### Форма предложения:

```typescript
interface ProposalForm {
  // Основное
  coverLetter: string;           // Rich text editor
  proposedApproach: string;       // Textarea
  
  // Сроки
  startDate: Date;               // Date picker
  duration: number;              // Number input + select (часы/дни)
  endDate: Date;                 // Auto-calculated
  
  // Ценообразование
  pricingType: 'hourly' | 'fixed' | 'milestone';
  hourlyRate?: number;           // If hourly
  fixedPrice?: number;           // If fixed
  milestones?: Milestone[];      // If milestone
  
  // Дополнительно
  relevantExperience: string;    // Textarea
  portfolioItems: string[];       // Multi-select
  attachments: File[];           // File upload
}
```

#### UI компоненты формы:

- **Rich Text Editor** для cover letter
  - Форматирование текста
  - Списки
  - Ссылки
  - Автосохранение черновиков

- **Timeline Builder** для планирования
  - Визуальный таймлайн
  - Drag & drop для вех
  - Автоматический расчет дат

- **Price Calculator**
  - Динамический расчет итоговой стоимости
  - Конвертер валют
  - Включение/исключение налогов

---

## 🏢 Интерфейс клиента

### 1. Создание запроса на услуги

#### Мастер создания запроса (Wizard):

```
Шаг 1: Тип услуги
┌─────────────────────────────────────────────────────┐
│  Какой тип услуги вам нужен?                       │
│                                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │    📊   │ │    🔍   │ │    📋   │ │    🎓   │ │
│  │   BIA   │ │  Risk   │ │Planning │ │Training │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
│                                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │    ✅   │ │    🚨   │ │    💼   │ │    ⚙️   │ │
│  │  Audit  │ │ Crisis  │ │Consult  │ │ Other   │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
└─────────────────────────────────────────────────────┘

Шаг 2: Описание проекта
┌─────────────────────────────────────────────────────┐
│  Опишите ваш проект                                │
│                                                     │
│  Название проекта *                                │
│  ┌─────────────────────────────────────────────┐  │
│  │                                              │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  Детальное описание *                              │
│  ┌─────────────────────────────────────────────┐  │
│  │                                              │  │
│  │  Rich text editor с подсказками             │  │
│  │                                              │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  Цели и ожидаемые результаты                       │
│  ┌─────────────────────────────────────────────┐  │
│  │  • Цель 1                                   │  │
│  │  • Цель 2                                   │  │
│  │  [+ Добавить цель]                          │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

Шаг 3: Требования к специалисту
┌─────────────────────────────────────────────────────┐
│  Требования к специалисту                          │
│                                                     │
│  Необходимые навыки                                │
│  [Risk Assessment] [ISO 22301] [+]                 │
│                                                     │
│  Опыт работы (лет)                                 │
│  [0-2] [3-5] [5-10] [10+]                         │
│                                                     │
│  Сертификации                                      │
│  ☐ ISO 22301 Lead Implementer                     │
│  ☐ CBCP (Certified Business Continuity Professional)│
│  ☐ MBCI (Member of the BCI)                       │
│                                                     │
│  Языки                                             │
│  [Русский] [English] [+]                          │
└─────────────────────────────────────────────────────┘

Шаг 4: Бюджет и сроки
┌─────────────────────────────────────────────────────┐
│  Бюджет и сроки                                    │
│                                                     │
│  Бюджет                                            │
│  ○ Почасовая оплата                                │
│     Min: [___] Max: [___] USD/час                  │
│  ● Фиксированный бюджет                            │
│     Сумма: [_______] USD                           │
│  ○ Обсуждаемый                                     │
│                                                     │
│  Сроки                                             │
│  Начало: [📅 15 окт 2025]                          │
│  Окончание: [📅 15 дек 2025]                       │
│                                                     │
│  Срочность                                         │
│  [Низкая] [Средняя] [Высокая] [ASAP]              │
└─────────────────────────────────────────────────────┘
```

### 2. Управление предложениями

#### Таблица предложений:

```
┌───────────────────────────────────────────────────────────────────┐
│  Предложения по проекту "BCM Assessment for Manufacturing"       │
│                                                                   │
│  Фильтры: [Все] [Новые] [В обзоре] [Отклоненные]                │
│  Сортировка: [Рейтинг ↓] [Цена] [Опыт] [Дата]                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ⭐ John Smith                           $150/час | 3 дня    │ │
│  │ Senior BCM Consultant | 4.9★ | 15 лет опыта               │ │
│  │ "I have extensive experience in manufacturing sector..."   │ │
│  │ [Портфолио] [Интервью] [Принять] [Отклонить]             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Sarah Johnson                          $12,000 fixed       │ │
│  │ Risk Management Expert | 4.7★ | 10 лет опыта              │ │
│  │ "My approach includes comprehensive risk assessment..."    │ │
│  │ [Портфолио] [Интервью] [Принять] [Отклонить]             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

#### Детальный просмотр предложения:

- **Сравнительная таблица** (до 3 предложений)
- **Чат с специалистом** (встроенный)
- **Планирование интервью** (календарь)
- **Просмотр портфолио** (галерея/слайдер)

---

## 🛍️ Маркетплейс

### 1. Главная страница маркетплейса

```
┌────────────────────────────────────────────────────────┐
│  BCM Marketplace - Найдите идеального специалиста     │
│                                                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  🔍 Поиск специалистов или услуг...           │  │
│  │     [Поиск]                                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  Популярные категории                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐      │
│  │ BIA  │ │Risk  │ │Audit │ │Train │ │Crisis│      │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘      │
│                                                        │
│  Топ специалисты                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ [Avatar] Name | Title | ⭐4.9 | $150/час       │  │
│  │ [Avatar] Name | Title | ⭐4.8 | $120/час       │  │
│  │ [Avatar] Name | Title | ⭐4.8 | $100/час       │  │
│  └────────────────────────────────────────────────┘  │
│                                                        │
│  Последние проекты                                    │
│  ┌────────────────────────────────────────────────┐  │
│  │ • BCM Assessment - Manufacturing - $10-15k     │  │
│  │ • Risk Analysis - Healthcare - $5-8k          │  │
│  │ • Training Program - Finance - $3-5k          │  │
│  └────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 2. Поиск и фильтрация

#### Фильтры поиска:

```javascript
const searchFilters = {
  // Текстовый поиск
  query: string,
  
  // Категории
  serviceTypes: string[],
  specializations: string[],
  industries: string[],
  
  // Параметры специалиста
  rating: { min: number, max: number },
  experience: { min: number, max: number },
  hourlyRate: { min: number, max: number },
  
  // Локация
  location: {
    country: string,
    city: string,
    remote: boolean
  },
  
  // Доступность
  availability: 'available' | 'busy' | 'all',
  
  // Верификация
  verifiedOnly: boolean,
  
  // Языки
  languages: string[],
  
  // Сортировка
  sortBy: 'relevance' | 'rating' | 'price_low' | 'price_high' | 'experience'
};
```

### 3. Карточка специалиста в результатах

```vue
<template>
  <div class="specialist-card">
    <div class="card-header">
      <img :src="specialist.avatar" class="avatar" />
      <div class="availability-indicator" :class="specialist.availability" />
    </div>
    
    <div class="card-body">
      <h3>{{ specialist.name }}</h3>
      <p class="title">{{ specialist.title }}</p>
      
      <div class="rating">
        <StarRating :value="specialist.rating" />
        <span>({{ specialist.reviewsCount }} отзывов)</span>
      </div>
      
      <div class="info">
        <div class="info-item">
          <Icon name="briefcase" />
          <span>{{ specialist.experience }} лет</span>
        </div>
        <div class="info-item">
          <Icon name="dollar" />
          <span>${{ specialist.hourlyRate }}/час</span>
        </div>
        <div class="info-item">
          <Icon name="check-circle" />
          <span>{{ specialist.completedProjects }} проектов</span>
        </div>
      </div>
      
      <div class="skills">
        <Tag v-for="skill in specialist.topSkills" :key="skill">
          {{ skill }}
        </Tag>
      </div>
      
      <p class="bio">{{ specialist.shortBio }}</p>
    </div>
    
    <div class="card-footer">
      <Button variant="primary" @click="viewProfile">
        Посмотреть профиль
      </Button>
      <Button variant="ghost" @click="sendMessage">
        <Icon name="message" />
      </Button>
      <Button variant="ghost" @click="saveSpecialist">
        <Icon name="heart" />
      </Button>
    </div>
  </div>
</template>
```

---

## 📊 Система управления проектами

### 1. Канбан-доска проекта

```
┌──────────────────────────────────────────────────────────┐
│  Проект: BCM Implementation - ABC Corp                  │
│  Progress: 65% | Budget: $8,500/$12,000 | Due: 15 Oct  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  To Do              In Progress        Done             │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │ Task 1   │      │ Task 3   │      │ Task 5   │     │
│  │ 2 days   │      │ 75%      │      │ ✓ Compl. │     │
│  └──────────┘      └──────────┘      └──────────┘     │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │ Task 2   │      │ Task 4   │      │ Task 6   │     │
│  │ 3 days   │      │ 30%      │      │ ✓ Compl. │     │
│  └──────────┘      └──────────┘      └──────────┘     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 2. Трекинг времени

#### Интерфейс таймера:

```vue
<template>
  <div class="time-tracker">
    <div class="timer-display">
      <h1>{{ formatTime(elapsedTime) }}</h1>
      <p>{{ currentTask }}</p>
    </div>
    
    <div class="controls">
      <Button 
        v-if="!isRunning" 
        @click="startTimer"
        variant="success"
        size="large"
      >
        <Icon name="play" /> Начать
      </Button>
      
      <Button 
        v-else
        @click="pauseTimer"
        variant="warning"
        size="large"
      >
        <Icon name="pause" /> Пауза
      </Button>
      
      <Button 
        @click="stopTimer"
        variant="danger"
        size="large"
      >
        <Icon name="stop" /> Стоп
      </Button>
    </div>
    
    <div class="task-selector">
      <Select 
        v-model="currentTask"
        placeholder="Выберите задачу"
      >
        <Option 
          v-for="task in tasks" 
          :key="task.id"
          :value="task.id"
        >
          {{ task.name }}
        </Option>
      </Select>
    </div>
    
    <div class="quick-notes">
      <Textarea 
        v-model="notes"
        placeholder="Заметки о работе..."
      />
    </div>
  </div>
</template>
```

### 3. Вехи проекта (Milestones)

```
┌──────────────────────────────────────────────────────────┐
│  Вехи проекта                                           │
│                                                          │
│  ━━━━━●━━━━━━━━━○━━━━━━━━━○━━━━━━━━━○━━━━━             │
│      25%        50%        75%       100%               │
│                                                          │
│  ✅ Веха 1: Initial Assessment                          │
│     Завершено: 10 Sep | Оплачено: $3,000               │
│                                                          │
│  🔄 Веха 2: Risk Analysis                               │
│     Прогресс: 60% | Дедлайн: 25 Sep                    │
│     [Загрузить результаты] [Запросить проверку]         │
│                                                          │
│  ⏳ Веха 3: Implementation Plan                         │
│     Начало: 26 Sep | Бюджет: $3,000                    │
│                                                          │
│  ⏳ Веха 4: Training & Handover                         │
│     Начало: 10 Oct | Бюджет: $3,000                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📱 Мобильное приложение

### Основные экраны

#### 1. Мобильный дашборд
```
┌─────────────────┐
│ 9:41 AM     🔋 │
├─────────────────┤
│ Привет, Иван!   │
│                 │
│ ┌─────┬─────┐  │
│ │$2.5k│ 4.8★│  │
│ │Месяц│Рейт.│  │
│ └─────┴─────┘  │
│                 │
│ Новые запросы   │
│ ┌─────────────┐ │
│ │ BIA для     │ │
│ │ Retail      │ │
│ │ $5-8k       │ │
│ └─────────────┘ │
│                 │
│ Активные (3)    │
│ • Project 1 75% │
│ • Project 2 30% │
│ • Project 3 10% │
│                 │
│ [▦][👤][💬][⚙] │
└─────────────────┘
```

#### 2. Быстрое создание предложения
```
┌─────────────────┐
│ ← Предложение   │
├─────────────────┤
│                 │
│ Cover Letter    │
│ ┌─────────────┐ │
│ │             │ │
│ │ Текст...    │ │
│ │             │ │
│ └─────────────┘ │
│                 │
│ Цена            │
│ [150] $/час     │
│                 │
│ Сроки           │
│ [3] дня         │
│                 │
│ Портфолио       │
│ ☑ Project A     │
│ ☐ Project B     │
│ ☑ Project C     │
│                 │
│ [Отправить]     │
└─────────────────┘
```

#### 3. Чат с клиентом
```
┌─────────────────┐
│ ← John Smith    │
├─────────────────┤
│                 │
│ ┌─────────────┐ │
│ │ Привет!     │ │
│ │ Как проект? │ │
│ └─────────────┘ │
│                 │
│     ┌─────────┐ │
│     │ Отлично!│ │
│     │ 75%     │ │
│     └─────────┘ │
│                 │
│ ┌─────────────┐ │
│ │ 📎 report.pdf│ │
│ └─────────────┘ │
│                 │
│ [📎][📷][Отпр.] │
└─────────────────┘
```

### Специфичные мобильные функции

1. **Push-уведомления**
   - Новые запросы по вашим навыкам
   - Сообщения от клиентов
   - Изменения статуса предложений
   - Приближающиеся дедлайны
   - Подтверждения оплат

2. **Offline режим**
   - Просмотр активных проектов
   - Черновики предложений
   - Кэшированные сообщения
   - Синхронизация при подключении

3. **Quick Actions (3D Touch / Long Press)**
   - Быстрый ответ на сообщение
   - Старт/стоп таймера
   - Создание заметки
   - Смена статуса доступности

4. **Биометрическая аутентификация**
   - Face ID / Touch ID
   - Fingerprint
   - PIN-код как fallback

---

## 🎯 Метрики успеха интерфейса

### UX метрики
- Time to complete task < 3 минуты
- Error rate < 5%
- User satisfaction score > 4.5/5
- Task success rate > 90%

### Производительность
- First Contentful Paint < 1.5s
- Time to Interactive < 3.5s
- Lighthouse score > 90
- Bundle size < 500KB

### Конверсии
- Регистрация специалиста: 40%
- Создание первого запроса: 60%
- Принятие предложения: 25%
- Завершение проекта: 85%

---

## 🛠️ Технологический стек Frontend

### Основной стек
```json
{
  "framework": "Vue.js 3.4",
  "language": "TypeScript 5.0",
  "build": "Vite 5.0",
  "state": "Pinia 2.1",
  "router": "Vue Router 4.3",
  "ui": "PrimeVue 3.40",
  "css": "Tailwind CSS 3.4",
  "charts": "Chart.js 4.4",
  "forms": "VeeValidate 4.12",
  "http": "Axios 1.6",
  "websocket": "Socket.io 4.6",
  "i18n": "Vue I18n 9.8",
  "testing": "Vitest 1.0 + Cypress 13"
}
```

### Мобильное приложение
```json
{
  "framework": "React Native 0.73",
  "navigation": "React Navigation 6",
  "state": "Redux Toolkit 2.0",
  "ui": "React Native Elements 3.4",
  "notifications": "React Native Push Notifications",
  "storage": "AsyncStorage + SQLite"
}
```

---

*Документ создан: 16 сентября 2025*
*Версия: 1.0*
*Автор: BCM Platform Team*