# ISO 22301 Knowledge Base

## 🎯 Назначение

**Единый источник правды** для стандарта ISO 22301:2019 в рамках BCM Platform. Библиотека содержит структурированные требования стандарта, процессы, контроли и утилиты для автоматической проверки соответствия.

## 📁 Структура

```
knowledge-base/
├── iso-22301-standard.ts      # Основные определения и базовые требования
├── complete-requirements.ts   # Полный набор требований ISO 22301
├── hooks.ts                   # React hooks для интеграции
├── utils.ts                   # Утилиты для работы с стандартом  
├── templates/                 # Шаблоны документации
│   ├── policy-templates.ts
│   ├── procedure-templates.ts
│   └── plan-templates.ts
└── README.md                  # Этот файл
```

## 🏗️ Основные компоненты

### **ISO22301Requirement**
Базовая структура требования стандарта:
```typescript
interface ISO22301Requirement {
  id: string                    // "4.1", "5.2", etc.
  clause: string               // Номер пункта
  title: string                // Название требования
  description: string          // Детальное описание
  type: 'mandatory' | 'recommended' | 'guidance'
  category: string             // Категория (Context, Leadership, etc.)
  evidence: string[]           // Необходимые доказательства
  controls: string[]           // Связанные контроли
  relatedClauses: string[]     // Связанные требования
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  complianceLevel: 'none' | 'partial' | 'full'
}
```

### **MODULE_COMPLIANCE_MATRIX**
Матрица соответствия модулей требованиям:
```typescript
const MODULE_COMPLIANCE_MATRIX = {
  bcm_context: ['4.1', '4.2', '4.3', '4.4'],
  bcm_governance: ['5.1', '5.2', '5.3'],
  bcm_risk_management: ['6.1', '8.1.1', '8.1.2'],
  bcm_bia: ['8.1.3', '8.1.4'],
  // ... остальные модули
}
```

## 🔧 Использование

### В React компонентах
```typescript
import { useModuleRequirements, useComplianceAnalysis } from '@/knowledge-base/hooks'

function GovernanceModule() {
  const { requirements } = useModuleRequirements('bcm_governance')
  const compliance = useComplianceAnalysis('bcm_governance')

  return (
    <div>
      <h2>Governance Module - {compliance.coverage}% соответствие</h2>
      {requirements.map(req => (
        <RequirementCard key={req.id} requirement={req} />
      ))}
    </div>
  )
}
```

### Прямое использование класса
```typescript
import { ISO22301KnowledgeBase } from '@/knowledge-base/iso-22301-standard'

// Получить требования для модуля
const requirements = ISO22301KnowledgeBase.getRequirementsByModule('bcm_governance')

// Проверить соответствие
const compliance = ISO22301KnowledgeBase.validateModuleCompliance('bcm_governance')

// Получить пробелы в соответствии
const gaps = ISO22301KnowledgeBase.getComplianceGaps()
```

## 📊 Автоматическая проверка соответствия

### Анализ модуля
```typescript
const analysis = ISO22301KnowledgeBase.validateModuleCompliance('bcm_governance')
// Результат:
{
  compliant: false,
  coverage: 25,  // 25% требований выполнено
  missingRequirements: ['5.1', '5.2', '5.3']
}
```

### Дорожная карта внедрения
```typescript
const roadmap = ISO22301KnowledgeBase.getImplementationRoadmap()
// Результат: фазы внедрения с приоритизацией требований
```

## 🎯 Интеграция с Odoo Inspector

Knowledge Base можно использовать для автоматической генерации соответствующих компонентов:

```bash
# В Odoo Inspector можно добавить флаг для включения требований
python3 cli.py create bcm_governance --include-compliance -o generated/
```

### Расширение генератора
```typescript
// В generator.py можно добавить:
const requirements = ISO22301KnowledgeBase.getRequirementsByModule(moduleName)

// И генерировать дополнительные компоненты:
// - ComplianceChecker.tsx
// - RequirementsTracker.tsx  
// - EvidenceCollector.tsx
```

## 📋 Примеры применения

### 1. Governance Dashboard
```typescript
function GovernanceDashboard() {
  const compliance = useComplianceAnalysis('bcm_governance')
  const gaps = useComplianceGaps()
  
  return (
    <div>
      <ComplianceMetrics coverage={compliance.coverage} />
      <GapAnalysis gaps={gaps.filter(g => g.requirement.category === 'Leadership')} />
    </div>
  )
}
```

### 2. Автоматическая проверка при создании политики
```typescript
function PolicyCreator() {
  const [policy, setPolicy] = useState('')
  const requirements = useModuleRequirements('bcm_governance')
  
  const checkCompliance = () => {
    // Автоматически проверяем покрытие требований в тексте политики
    const covered = requirements.filter(req => 
      policy.includes(req.title) || 
      req.evidence.some(evidence => policy.includes(evidence))
    )
    return covered.length / requirements.length * 100
  }
}
```

### 3. Аудиторский трекер
```typescript
function AuditTracker() {
  const roadmap = useImplementationRoadmap()
  
  return (
    <div>
      {roadmap.map(phase => (
        <PhaseTracker 
          key={phase.phase}
          phase={phase.phase}
          requirements={phase.requirements}
        />
      ))}
    </div>
  )
}
```

## 🔄 Обновление статуса соответствия

```typescript
// Функция для обновления статуса соответствия
function updateComplianceStatus(requirementId: string, status: 'none' | 'partial' | 'full') {
  const requirement = ISO22301KnowledgeBase.getRequirementById(requirementId)
  if (requirement) {
    requirement.complianceLevel = status
    // Сохранить в базу данных через API
    saveTo
```

## 🚀 Планы развития

- [ ] **Автоматический анализ документов** - сканирование документов на соответствие требованиям
- [ ] **AI-помощник по стандарту** - чат-бот для вопросов по ISO 22301
- [ ] **Автоматическая генерация отчетов** - создание отчетов по соответствию
- [ ] **Integration с системами аудита** - экспорт данных для аудиторов
- [ ] **Многоязычная поддержка** - перевод требований на разные языки

## 📖 Справочная информация

### Основные разделы ISO 22301:2019

| Раздел | Название | Модули BCM |
|--------|----------|------------|
| 4 | Context of the organization | bcm_context |
| 5 | Leadership | bcm_governance |
| 6 | Planning | bcm_risk_management, bcm_bia |
| 7 | Support | bcm_training, bcm_resources |
| 8 | Operation | bcm_plans, bcm_incident_management |
| 9 | Performance evaluation | bcm_audit, bcm_monitoring |
| 10 | Improvement | bcm_improvement |

### Уровни зрелости контролей

1. **Initial (1)** - Процесс не определен
2. **Managed (2)** - Процесс управляется на уровне проекта
3. **Defined (3)** - Процесс стандартизирован на уровне организации
4. **Quantitatively Managed (4)** - Процесс измеряется и контролируется
5. **Optimizing (5)** - Процесс постоянно улучшается

## 🔗 Связанные файлы

- `/frontend/unified-bcm-platform/components/modules/` - React компоненты модулей
- `/sandbox/odoo-inspector/` - Генератор компонентов
- `/core/odoo-18.0/addons/bcm_*/` - Backend модули Odoo
