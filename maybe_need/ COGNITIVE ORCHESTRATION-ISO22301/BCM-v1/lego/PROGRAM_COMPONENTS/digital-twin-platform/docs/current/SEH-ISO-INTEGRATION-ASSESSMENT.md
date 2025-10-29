# Оценка интеграции ISO-сценариев и AI оркестрации в Digital Twin

## 1. СОВМЕСТИМОСТЬ: ✅ ВЫСОКАЯ (85%)

### Что уже есть в системе:
- ✅ **BCM scenarios** - таблица `bcm_scenarios` с RTO/RPO
- ✅ **Simulations** - таблица `simulations` готова для новых типов
- ✅ **Service deliveries** - поддержка arrival_rate, service_time
- ✅ **Measurements** - для KPI tracking
- ✅ **Grant management** - disbursements, milestones

### Что легко добавить:
- ✅ Capacity sweep симуляции (через существующий simulation-engine.js)
- ✅ Routing optimization (новый модуль)
- ✅ Grant-KPI оптимизацию
- ✅ Outage симуляции BCM

## 2. СЛОЖНОСТЬ ВНЕДРЕНИЯ: СРЕДНЯЯ

### Фаза 1 (1 неделя) - Базовые сценарии:
```javascript
// Расширение simulation-engine.js
class ISOScenarioEngine extends SimulationEngine {
    // Capacity Sweep
    async runCapacitySweep(params) {
        const { arrival_rate, service_time, capacity_agents } = params;
        // Monte Carlo по агентам
        return optimal_shifts;
    }
    
    // BCM Outage
    async simulateOutage(params) {
        const { rto_hours, rpo_hours, dependencies } = params;
        // Симуляция каскадных отказов
        return contingency_plan;
    }
}
```

### Фаза 2 (1 неделя) - AI Оркестрация:
```javascript
// AI Orchestrator
class AIOrchestrator {
    agents = {
        etl: new ETLAgent(),
        crm: new SalesforceAgent(),
        sim: new SimulationAgent(),
        bi: new BIAgent()
    };
    
    async processScenario(type, params) {
        // Governance rules check
        await this.validateRequest(params);
        
        // Run workflow
        const enriched = await this.agents.etl.enrich(params);
        const results = await this.agents.sim.run(type, enriched);
        const explained = await this.explainResults(results);
        
        // Commit to systems
        await this.agents.crm.update(results);
        return explained;
    }
}
```

### Фаза 3 (3-5 дней) - UI интеграция:
```javascript
// Новый компонент для существующего интерфейса
class ISOScenarioPanel {
    scenarios = [
        'IT Service Loss',
        'Site Loss', 
        'Staff Shortage',
        'Supplier Failure',
        'Cyber Incident',
        'Demand Surge'
    ];
    
    renderScenarioCards() {
        // Cards как в demo-seh-standalone.html
    }
    
    async runScenario(type) {
        const params = this.collectParams();
        const results = await orchestrator.processScenario(type, params);
        this.displayResults(results);
    }
}
```

## 3. ПОТЯНЕТ ЛИ ИНТЕРФЕЙС: ✅ ДА

### Текущий интерфейс поддерживает:
- Chart.js для графиков ✅
- D3.js для сложных визуализаций ✅
- Vis-network для зависимостей ✅
- Карточки метрик (как в demo) ✅

### Что нужно добавить:
1. **Табы для сценариев** (простой HTML/CSS)
2. **Параметры симуляций** (формы ввода)
3. **Результаты в реальном времени** (WebSocket уже есть)
4. **Экспорт отчетов** (PDF/Excel)

## 4. ПЛАН ИНТЕГРАЦИИ

### Быстрый старт (2-3 дня):
```sql
-- Новая таблица для ISO сценариев
CREATE TABLE iso_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_type VARCHAR(50), -- capacity, routing, grant_kpi, outage
    name VARCHAR(255),
    parameters JSONB,
    guardrails JSONB, -- limits, roles, constraints
    prompt_template TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Результаты оркестрации
CREATE TABLE orchestration_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id UUID REFERENCES iso_scenarios(id),
    input_params JSONB,
    simulation_results JSONB,
    decisions JSONB,
    applied_at TIMESTAMP,
    status VARCHAR(50)
);
```

### API endpoints:
```javascript
// Добавить в api/seh-endpoints.js
router.post('/iso-scenarios/run', async (req, res) => {
    const { scenario_type, params } = req.body;
    
    // Запуск через оркестратор
    const orchestrator = new AIOrchestrator();
    const results = await orchestrator.processScenario(scenario_type, params);
    
    // Сохранение результатов
    await supabase.from('orchestration_results').insert({
        scenario_id: scenario_type,
        input_params: params,
        simulation_results: results,
        status: 'completed'
    });
    
    res.json({ success: true, results });
});

router.get('/iso-scenarios/catalog', async (req, res) => {
    const scenarios = [
        {
            type: 'capacity',
            name: 'Capacity & Staffing Optimization',
            params: ['arrival_rate', 'service_time', 'agents'],
            metrics: ['wait_time', 'sla', 'throughput']
        },
        {
            type: 'outage',
            name: 'BCM Outage Simulation',
            params: ['rto', 'rpo', 'dependencies'],
            metrics: ['downtime', 'recovery_time', 'impact']
        }
        // ... остальные сценарии
    ];
    res.json(scenarios);
});
```

## 5. ВИЗУАЛИЗАЦИЯ В ТЕКУЩЕМ ИНТЕРФЕЙСЕ

### Добавить секцию в web-interface/templates/index.html:
```html
<!-- ISO Scenarios Section -->
<div class="iso-scenarios-panel">
    <h2>ISO 22301 Scenarios</h2>
    
    <!-- Scenario Cards Grid -->
    <div class="scenario-grid">
        <div class="scenario-card" data-type="capacity">
            <h3>Capacity Planning</h3>
            <div class="params">
                <input type="number" id="arrival_rate" placeholder="Arrival rate">
                <input type="number" id="agents" placeholder="Agents">
            </div>
            <button onclick="runISOScenario('capacity')">Run Simulation</button>
        </div>
        
        <div class="scenario-card" data-type="outage">
            <h3>BCM Outage</h3>
            <div class="params">
                <input type="number" id="rto" placeholder="RTO (hours)">
                <input type="number" id="rpo" placeholder="RPO (hours)">
            </div>
            <button onclick="runISOScenario('outage')">Simulate</button>
        </div>
    </div>
    
    <!-- Results Display -->
    <div id="iso-results">
        <canvas id="scenarioChart"></canvas>
    </div>
</div>

<script>
async function runISOScenario(type) {
    const params = collectScenarioParams(type);
    
    const response = await fetch('/api/seh/iso-scenarios/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_type: type, params })
    });
    
    const { results } = await response.json();
    displayScenarioResults(results);
}

function displayScenarioResults(results) {
    // Использовать существующие Chart.js графики
    const ctx = document.getElementById('scenarioChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: formatResultsForChart(results)
    });
}
</script>
```

## 6. ОЦЕНКА ГОТОВНОСТИ

| Компонент | Готовность | Сложность внедрения |
|-----------|------------|-------------------|
| База данных | 90% | Низкая |
| API | 70% | Средняя |
| Simulation Engine | 60% | Средняя |
| AI Orchestrator | 0% | Высокая (но модульно) |
| UI визуализация | 80% | Низкая |
| Промпты/Guardrails | 0% | Средняя |

## 7. РЕКОМЕНДАЦИИ

### Приоритет 1 (Быстрые победы):
1. **Capacity Sweep** - самый простой, высокая ценность
2. **BCM Outage** - уже есть таблицы, добавить симуляцию
3. **Визуализация** - использовать существующие компоненты

### Приоритет 2 (Средний срок):
1. **Routing VRP** - требует геоданных
2. **Grant-KPI optimization** - связать с существующими grants
3. **AI Orchestrator** - базовая версия без ML

### Приоритет 3 (Долгосрочно):
1. **Полная AI оркестрация** с обучением
2. **Интеграция с AnyLogic Cloud API**
3. **Real-time streaming от IoT датчиков**

## ВЫВОД

✅ **Система готова принять ISO-сценарии**
- Архитектура совместима
- UI справится с визуализацией  
- База данных расширяема
- API модульное

⏱️ **Время внедрения: 2-3 недели для базовой версии**
- Неделя 1: Сценарии + симуляции
- Неделя 2: AI оркестратор
- Неделя 3: UI интеграция + тесты

💡 **Рекомендация: Начать с 2-3 ключевых сценариев (Capacity, BCM, Grant-KPI) и постепенно расширять**