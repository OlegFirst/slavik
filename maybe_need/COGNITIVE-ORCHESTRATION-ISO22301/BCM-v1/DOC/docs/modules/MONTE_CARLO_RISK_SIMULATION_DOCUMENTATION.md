# 📊 Monte Carlo Risk Simulation - Техническая документация

## Обзор

Monte Carlo симуляции интегрированы в модуль Risk Management BCM платформы для вероятностного моделирования рисков. Система позволяет проводить 10,000 симуляций для точной оценки распределения рисков и их потенциального влияния на организацию.

**Дата внедрения**: 17 сентября 2025
**Версия**: 1.0.0
**Статус**: ✅ Production Ready

## 🎯 Ключевые возможности

### 1. Симуляция одного риска
- **10,000 итераций** для статистической точности
- **Нормальное распределение** с Box-Muller трансформацией
- **Расчет VaR** (Value at Risk) на уровне доверия 95%
- **CVaR** (Conditional Value at Risk) для хвостовых рисков

### 2. Портфельная симуляция
- Анализ **всего портфеля рисков** организации
- **Матрица корреляций** между рисками
- Идентификация **топ-контрибьюторов** в общий риск
- **Агрегированные метрики** с доверительными интервалами

### 3. Интеграция с Exercise Simulators
- Подключение к **JaamSim** для сложных симуляций
- REST API интеграция с внешними симуляторами
- Fallback на локальные вычисления при недоступности

## 📁 Структура файлов

```
/Users/MD/ISO-22301/frontend/unified-bcm-platform/
├── services/
│   ├── monte-carlo-simulation.ts     # Основной сервис симуляций
│   └── risk-management-api.ts        # API интеграция
└── components/
    └── modules/
        └── RiskManagement.tsx         # UI компонент с визуализацией
```

## 🔧 Техническая реализация

### Основные интерфейсы

```typescript
// Параметры симуляции
interface MonteCarloParameters {
  simulations: number        // Количество итераций (10000)
  confidenceLevel: number    // Уровень доверия (0.95 = 95%)
  timeHorizon: number       // Временной горизонт в месяцах
  correlationMatrix?: number[][] // Опциональная матрица корреляций
}

// Результат симуляции одного риска
interface SimulationResult {
  riskId: string
  simulations: number
  statistics: {
    mean: number              // Среднее значение
    median: number           // Медиана
    standardDeviation: number // Стандартное отклонение
    min: number              // Минимум
    max: number              // Максимум
    percentiles: {           // Перцентили
      p5: number
      p25: number
      p50: number
      p75: number
      p95: number
      p99: number
    }
  }
  distribution: Array<{      // Распределение для гистограммы
    value: number
    frequency: number
    probability: number
  }>
  valueAtRisk: number        // VaR на уровне доверия
  conditionalValueAtRisk: number // CVaR/Expected Shortfall
  probabilityOfOccurrence: number // Вероятность наступления
}

// Результат портфельной симуляции
interface AggregatedSimulationResult {
  totalSimulations: number
  timeHorizon: number
  aggregatedLoss: {
    mean: number
    median: number
    standardDeviation: number
    percentiles: { /* ... */ }
  }
  topRiskContributors: Array<{
    riskId: string
    riskTitle: string
    contribution: number     // % вклада в общий риск
  }>
  correlationImpact: number  // Влияние корреляций
  confidence: {
    level: number
    lowerBound: number
    upperBound: number
  }
  recommendations: string[]  // AI рекомендации
}
```

### Основные методы

#### 1. Симуляция одного риска

```typescript
async runSimulation(
  risk: Risk,
  parameters: MonteCarloParameters
): Promise<SimulationResult>
```

**Алгоритм**:
1. Генерация 10,000 случайных значений probability и impact
2. Использование нормального распределения (μ = текущее значение, σ = 20-25%)
3. Расчет risk score для каждой итерации
4. Статистический анализ результатов
5. Построение распределения для визуализации

#### 2. Портфельная симуляция

```typescript
async runPortfolioSimulation(
  risks: Risk[],
  parameters: MonteCarloParameters
): Promise<AggregatedSimulationResult>
```

**Алгоритм**:
1. Генерация/использование матрицы корреляций
2. Создание коррелированных случайных чисел
3. Симуляция всех рисков с учетом корреляций
4. Агрегация результатов
5. Идентификация топ-контрибьюторов
6. Генерация AI рекомендаций

### Математические методы

#### Box-Muller Transform
Для генерации нормально распределенных случайных чисел:

```typescript
const u1 = Math.random()
const u2 = Math.random()
const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2)
```

#### Value at Risk (VaR)
Расчет максимальной потери с заданной вероятностью:

```typescript
const varIndex = Math.floor(results.length * (1 - confidenceLevel))
const valueAtRisk = results[results.length - varIndex - 1]
```

#### Conditional VaR (CVaR)
Средняя потеря в худших случаях:

```typescript
const tailResults = results.slice(results.length - varIndex)
const cVaR = tailResults.reduce((sum, val) => sum + val, 0) / tailResults.length
```

## 🎨 UI/UX компоненты

### FAIR Analysis Tab
Вкладка в модуле Risk Management с функционалом симуляций:

1. **Кнопки запуска**:
   - "Simulate Selected Risk" - для выбранного риска
   - "Simulate Full Portfolio" - для всех рисков

2. **Визуализация результатов**:
   - **Статистические карточки**: Mean, VaR, Probability, Std Dev
   - **Гистограмма распределения**: 20 bins с интерактивными подсказками
   - **Перцентили**: P5, P50, P95 для быстрой оценки
   - **Топ-контрибьюторы**: График с процентами вклада
   - **AI рекомендации**: Автоматические советы по митигации

### Цветовая схема
- **Синяя палитра** (blue-50 to indigo-50) - для single risk
- **Фиолетовая палитра** (purple-50 to pink-50) - для portfolio
- **Красный** - для критических значений (VaR)
- **Оранжевый** - для предупреждений
- **Зеленый** - для безопасных значений

## 🔌 API интеграция

### Внешние симуляторы

```typescript
async function integrateWithExerciseSimulators(
  risks: Risk[],
  simulatorEndpoint?: string
): Promise<any>
```

**Endpoint**: `POST /api/risk-simulation`

**Payload**:
```json
{
  "risks": [...],
  "simulationType": "monte_carlo",
  "parameters": {
    "iterations": 10000,
    "engine": "jaamsim"
  }
}
```

### Fallback стратегия
При недоступности внешних симуляторов автоматически используется локальная реализация без прерывания работы пользователя.

## 📊 Метрики и рекомендации

### Автоматические рекомендации генерируются на основе:

1. **Уровня среднего риска**:
   - `> 7.0` - "Critical risk level detected. Immediate mitigation actions required."
   - `> 5.0` - "Elevated risk level. Review and strengthen existing controls."

2. **Волатильности** (Coefficient of Variation > 0.5):
   - "High risk volatility detected. Consider implementing stabilizing controls."

3. **Топ-контрибьюторов** (> 30% вклада):
   - "Focus on [Risk Name] which contributes X% to total risk."

4. **Влияния корреляций** (|impact| > 20%):
   - "Risk correlations amplify/reduce total exposure by X%."

## 🚀 Использование

### Пример запуска симуляции в коде:

```typescript
import { monteCarloSimulation } from '@/services/monte-carlo-simulation'

// Для одного риска
const result = await monteCarloSimulation.runSimulation(
  selectedRisk,
  {
    simulations: 10000,
    confidenceLevel: 0.95,
    timeHorizon: 12
  }
)

// Для портфеля
const portfolioResult = await monteCarloSimulation.runPortfolioSimulation(
  risks,
  {
    simulations: 10000,
    confidenceLevel: 0.95,
    timeHorizon: 12
  }
)
```

## 🔐 Безопасность и производительность

### Оптимизации:
- **Асинхронное выполнение** для не-блокирующего UI
- **Web Workers** готовность для тяжелых вычислений
- **Кеширование результатов** в React Query (staleTime: 5 минут)
- **Progressive enhancement** - работает даже без backend

### Ограничения:
- Максимум **100,000 симуляций** для предотвращения зависания
- Значения риска ограничены диапазоном **[1, 10]**
- Матрица корреляций до **50x50** рисков

## 📈 Будущие улучшения

### Запланировано в v2.0:
1. **Web Workers** для параллельных вычислений
2. **GPU ускорение** через WebGL для больших портфелей
3. **Экспорт результатов** в PDF/Excel отчеты
4. **Исторический анализ** симуляций
5. **Машинное обучение** для предсказания корреляций
6. **Real-time симуляции** при изменении параметров

## 🔗 Связанная документация

- [Risk Management Module Overview](./BCM_RISK_MANAGEMENT_TECHNICAL_DOCUMENTATION.md)
- [FAIR Methodology Implementation](./FAIR_ANALYSIS_DOCUMENTATION.md)
- [BCM Platform Architecture](./BCM_PLATFORM_ARCHITECTURE_MAP.md)
- [API Integration Guide](./BCM_COMPONENT_INTEGRATION_GUIDE.md)

## 📝 Changelog

### v1.0.0 (17.09.2025)
- ✅ Initial implementation с 10,000 симуляциями
- ✅ Интеграция с FAIR Analysis
- ✅ Визуализация результатов
- ✅ Портфельная симуляция с корреляциями
- ✅ AI рекомендации
- ✅ Интеграция с JaamSim

---

**Автор**: BCM Development Team
**Контакт**: bcm-platform@organization.com
**Лицензия**: Proprietary