# Knowledge Base Integration Guide

## 🎯 Цель документа

Руководство по интеграции существующих BCM модулей с новой системой **ISO 22301 Knowledge Base** для автоматического отслеживания соответствия стандарту.

## 📊 Текущий статус модулей

### ✅ Интегрированные модули:
- **Governance Module** - полная интеграция с requirements 5.1, 5.2
- **Compliance Dashboard** - центральный мониторинг соответствия

### 🔄 Требуют обновления:
- **Risk Management Module** - добавить ISO 22301 requirements 6.1, 8.1.1, 8.1.2
- **BIA Module** - добавить ISO 22301 requirement 8.1.3  
- **AI Control Center** - добавить cross-module compliance integration

### 📋 Планируется создать:
- **BCM Core Module** - requirements 4.3, 4.4
- **Context Module** - requirements 4.1, 4.2
- **Plans Module** - requirements 8.2.1, 8.2.2, 8.2.3
- **Incident Management** - requirement 8.3
- **Exercise Module** - requirements 8.4, 8.5
- **Audit Module** - requirement 9.2
- **Review Module** - requirement 9.3
- **Improvement Module** - requirements 10.1, 10.2

## 🔧 Как интегрировать существующий модуль

### Шаг 1: Добавить Knowledge Base импорты

```typescript
// В начало компонента добавить:
import {
  ISO22301KnowledgeBase,
  useModuleRequirements,
  useComplianceAnalysis,
  MODULE_COMPLIANCE_MATRIX
} from '@/lib/knowledge-base-embedded'
```

### Шаг 2: Определить соответствие модуля

```typescript
// Проверить в MODULE_COMPLIANCE_MATRIX какие требования покрывает модуль:
const MODULE_COMPLIANCE_MATRIX = {
  bcm_risk_management: ['6.1', '8.1.1', '8.1.2'],  // ← Для Risk Management
  bcm_bia: ['8.1.3', '8.1.4'],                    // ← Для BIA Module
  // ... другие модули
}
```

### Шаг 3: Добавить хуки в компонент

```typescript
export function RiskManagementModule() {
  // Добавить эти хуки:
  const { requirements } = useModuleRequirements('bcm_risk_management')
  const complianceAnalysis = useComplianceAnalysis('bcm_risk_management')
  
  // Остальной код модуля...
}
```

### Шаг 4: Добавить индикатор соответствия в заголовок

```typescript
<div className="flex items-center gap-4 mt-3">
  <div className="flex items-center gap-2">
    <div className={cn(
      "w-3 h-3 rounded-full",
      complianceAnalysis.coverage >= 80 ? "bg-green-500" :
      complianceAnalysis.coverage >= 60 ? "bg-yellow-500" : "bg-red-500"
    )} />
    <span className="text-sm text-gray-600">
      ISO 22301 Соответствие: {Math.round(complianceAnalysis.coverage)}%
    </span>
  </div>
  <div className="text-sm text-gray-500">
    {requirements.filter(req => req.complianceLevel === 'full').length}/{requirements.length} требований выполнено
  </div>
</div>
```

### Шаг 5: Добавить таб "Соответствие"

```typescript
// Добавить в табы:
{ id: 'compliance', label: 'Соответствие', icon: Shield }

// Добавить контент таба:
{activeTab === 'compliance' && (
  <div className="bg-white rounded-lg border shadow-sm">
    <div className="p-6 border-b">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Shield className="h-5 w-5" />
        Соответствие ISO 22301 - [Название раздела]
      </h3>
    </div>
    <div className="p-6">
      {/* Метрики соответствия */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(complianceAnalysis.coverage)}%
          </div>
          <div className="text-sm text-gray-500">Общее соответствие</div>
        </div>
        {/* Остальные метрики... */}
      </div>

      {/* Список требований */}
      <div className="space-y-4">
        <h4 className="font-medium">Требования стандарта:</h4>
        {requirements.map(req => (
          <RequirementCard key={req.id} requirement={req} />
        ))}
      </div>
    </div>
  </div>
)}
```

## 📋 Детальные инструкции по модулям

### Risk Management Module

**Файл:** `/components/modules/RiskManagement.tsx`

**Требования ISO 22301:**
- **6.1** - Actions to address risks and opportunities
- **8.1.1** - General operational planning
- **8.1.2** - Business impact analysis and risk assessment

**Что добавить:**
1. Import Knowledge Base hooks
2. Compliance indicator в заголовок  
3. Таб "Соответствие" с требованиями 6.1, 8.1.1, 8.1.2
4. Связь с BIA модулем через requirement 8.1.2

**Пример кода:**
```typescript
const { requirements } = useModuleRequirements('bcm_risk_management')
const complianceAnalysis = useComplianceAnalysis('bcm_risk_management')

// В описании модуля добавить:
<p className="text-gray-600 mt-2">
  Управление рисками непрерывности бизнеса согласно ISO 22301 (разделы 6.1, 8.1.1, 8.1.2)
</p>
```

### BIA Module

**Файл:** `/components/modules/BIAModule.tsx`

**Требования ISO 22301:**
- **8.1.3** - Business impact analysis
- **8.1.4** - Business continuity strategy

**Что добавить:**
1. Import Knowledge Base hooks
2. Compliance indicator
3. Таб "Соответствие" с требованием 8.1.3
4. Связь с Risk Management через shared requirement 8.1.2

**Особенность:** BIA модуль имеет критическое требование 8.1.3 - должно быть выделено в UI.

### AI Control Center

**Файл:** `/components/modules/AIControlCenter.tsx`

**Интеграция:** Cross-module compliance monitoring

**Что добавить:**
1. Compliance widget для мониторинга всех модулей
2. Alerts для критических пробелов в соответствии
3. Integration с Compliance Dashboard
4. Real-time notifications о изменениях compliance статуса

**Пример интеграции:**
```typescript
// Добавить в AI Control Center:
const overallCompliance = useQuery({
  queryKey: ['overall-compliance'],
  queryFn: () => ComplianceReportGenerator.generateFullComplianceReport()
})

// AI орган для соответствия:
{
  id: 'compliance-monitor',
  name: 'ISO 22301 Compliance Monitor',
  status: overallCompliance.data?.overallCompliance >= 80 ? 'optimal' : 'warning',
  metrics: {
    coverage: `${Math.round(overallCompliance.data?.overallCompliance || 0)}%`,
    criticalGaps: overallCompliance.data?.criticalGaps.length || 0
  }
}
```

## 🔄 Миграционный чек-лист

### Для каждого существующего модуля:

#### ✅ Технические изменения:
- [ ] Добавить импорты Knowledge Base
- [ ] Добавить хуки `useModuleRequirements` и `useComplianceAnalysis`  
- [ ] Добавить compliance indicator в заголовок
- [ ] Добавить таб "Соответствие"
- [ ] Обновить описание модуля с указанием разделов ISO 22301
- [ ] Тестирование интеграции

#### ✅ Контентные изменения:
- [ ] Определить mapping на требования стандарта
- [ ] Установить текущий статус соответствия (none/partial/full)
- [ ] Добавить связи с другими модулями через shared requirements
- [ ] Создать help text для требований
- [ ] Валидация корректности отображения

#### ✅ UX улучшения:
- [ ] Визуальные индикаторы статуса соответствия
- [ ] Tooltips с объяснением требований
- [ ] Связи между модулями через compliance
- [ ] Экспорт отчетов по соответствию
- [ ] Breadcrumbs с navigation по связанным модулям

## 🚀 Автоматизация обновлений

### С помощью Odoo Inspector:

```bash
# Обновить существующий модуль с Knowledge Base интеграцией
cd /Users/MD/ISO-22301/sandbox/odoo-inspector
python3 cli.py create bcm_risk_management --include-compliance -o ../frontend/unified-bcm-platform/generated/risk-updated/

# Сравнить с существующим и применить изменения
diff -u existing/RiskManagement.tsx generated/risk-updated/components/modules/RiskManagement.tsx
```

### Batch обновление:
```bash
#!/bin/bash
# update-modules.sh

MODULES=("bcm_risk_management" "bcm_bia" "bcm_incident_management")

for module in "${MODULES[@]}"; do
  echo "Updating $module with Knowledge Base integration..."
  python3 cli.py create $module --include-compliance -o "../frontend/unified-bcm-platform/generated/updated/$module"
done
```

## 📊 Мониторинг интеграции

### Compliance Dashboard покажет:
- ✅ **Зеленый статус** - модуль полностью интегрирован
- 🟡 **Желтый статус** - частичная интеграция  
- ❌ **Красный статус** - интеграция отсутствует

### Автоматические проверки:
```typescript
// В каждом модуле можно добавить проверку интеграции:
const integrationStatus = useMemo(() => {
  return {
    hasKnowledgeBase: !!requirements.length,
    hasComplianceTab: activeTab === 'compliance',
    hasIndicators: !!complianceAnalysis.coverage,
    integrationComplete: requirements.length > 0 && complianceAnalysis.coverage !== undefined
  }
}, [requirements, complianceAnalysis, activeTab])
```

## 🎯 Приоритеты внедрения

### Высокий приоритет (немедленно):
1. **Risk Management** - критический для compliance
2. **BIA Module** - связан с Risk Management

### Средний приоритет (в течение недели):
3. **AI Control Center** - cross-module monitoring
4. **Создание Context Module** - foundational requirements

### Низкий приоритет (по мере разработки):
5. Остальные модули по мере их создания

## 📞 Поддержка интеграции

### При вопросах:
- Проверить `/lib/knowledge-base-embedded.ts` - основные функции
- Посмотреть `GovernanceModule.tsx` - reference implementation
- Использовать `ComplianceDashboard.tsx` - для понимания cross-module связей
- Основная папка Knowledge Base: `/services/knowledge-base/`

### Troubleshooting:
- **Ошибка импорта** → проверить path к knowledge-base-embedded.ts
- **Пустые requirements** → проверить MODULE_COMPLIANCE_MATRIX
- **Неправильный coverage** → проверить complianceLevel в requirements
- **UI issues** → сравнить с GovernanceModule implementation

---

**Этот документ обновляется по мере интеграции модулей. Текущий статус см. в `/docs/integration-status.md`**