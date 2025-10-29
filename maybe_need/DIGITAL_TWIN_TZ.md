# ТЕХНИЧЕСКОЕ ЗАДАНИЕ: Digital Twin Universal Service

**Версия:** 1.0
**Дата:** 2025-09-30
**Статус:** Готово к реализации
**Приоритет:** Высокий (Этап 2 консолидации)

---

## 📋 СОДЕРЖАНИЕ

1. [Цели и задачи](#цели-и-задачи)
2. [Архитектура](#архитектура)
3. [Сохранение существующих функций](#сохранение-существующих-функций)
4. [Новые функции](#новые-функции)
5. [Детальная спецификация модулей](#детальная-спецификация-модулей)
6. [API спецификация](#api-спецификация)
7. [План миграции](#план-миграции)
8. [План реализации](#план-реализации)

---

## 🎯 ЦЕЛИ И ЗАДАЧИ

### Главная цель
Создать **универсальный микросервис Digital Twin**, который:
- ✅ Сохраняет ВСЕ существующие функции (~44K строк)
- ✅ Добавляет plugin architecture для коллекторов
- ✅ Работает независимо от конкретных платформ (Odoo, Salesforce, etc.)
- ✅ Легко масштабируется и расширяется

### Задачи
1. Консолидировать 6 компонентов → 1 универсальный сервис
2. Портировать всю функциональность из `digital-twin-platform` (~38K строк)
3. Добавить Plugin Manager для коллекторов
4. Создать тонкие bridges для Odoo и Salesforce
5. Обеспечить backward compatibility

---

## 🏗️ АРХИТЕКТУРА

### Общая схема

```
┌───────────────────────────────────────────────────────────────────┐
│                DIGITAL TWIN UNIVERSAL SERVICE                      │
│                      (Port 8001)                                   │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  1. DATA VACUUM LAYER (Сбор данных)                         │ │
│  │     • Plugin Manager                                         │ │
│  │     • 100+ Built-in Collectors                              │ │
│  │     • Custom Collectors Registry                            │ │
│  │     • Auto-discovery Engine                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  2. DATA PROCESSOR LAYER (Обработка)                        │ │
│  │     • Data Normalizer                                       │ │
│  │     • Entity Resolver                                       │ │
│  │     • Conflict Resolver                                     │ │
│  │     • Data Enricher                                         │ │
│  │     • Quality Scorer                                        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  3. DIGITAL TWIN ENGINE (Ядро)                              │ │
│  │     • Organization Model                                    │ │
│  │     • Simulation Engine (10+ scenarios)                     │ │
│  │     • Prediction Engine                                     │ │
│  │     • Analytics Engine                                      │ │
│  │     • Theory of Change Engine                               │ │
│  │     • Impact Passport Generator                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  4. STORAGE LAYER (Хранение)                                │ │
│  │     • Supabase PostgreSQL                                   │ │
│  │     • Redis Cache                                           │ │
│  │     • Time-series DB (метрики)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              ▼                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  5. API GATEWAY LAYER (Интерфейс)                           │ │
│  │     • REST API (FastAPI)                                    │ │
│  │     • GraphQL API                                           │ │
│  │     • WebSocket (real-time)                                 │ │
│  │     • MCP Server (AI agents)                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
                              ▲ ▼
              ┌───────────────┴────────────────┐
              │                                │
      ┌───────▼────────┐            ┌─────────▼──────┐
      │  Odoo Bridge   │            │Salesforce Bridge│
      │  (Python)      │            │   (Python)      │
      └───────▲────────┘            └─────────▲──────┘
              │                                │
      ┌───────┴────────┐            ┌─────────┴──────┐
      │ Odoo Instance  │            │ Salesforce Org │
      │ (23+ modules)  │            │                │
      └────────────────┘            └────────────────┘
```

### Технологический стек

**Backend:**
- Python 3.11+
- FastAPI 0.109+ (REST API)
- Strawberry GraphQL (GraphQL)
- Pydantic 2.5+ (Data validation)
- SQLAlchemy 2.0+ (ORM)

**Database:**
- Supabase PostgreSQL (primary storage)
- Redis 7+ (cache, pub/sub)
- TimescaleDB (time-series metrics)

**Integration:**
- httpx (async HTTP client)
- websockets (real-time)
- python-jose (JWT)
- cryptography (security)

**От Node.js платформы портируем:**
- Simulation logic → Python
- Theory of Change → Python
- Impact Passport → Python
- MCP Server → Python (сохраняем Node.js как опцию)

---

## 🔄 СОХРАНЕНИЕ СУЩЕСТВУЮЩИХ ФУНКЦИЙ

### Из `digital-twin-platform` (~38,815 строк Node.js)

#### ✅ 1. Organization Management

**Было (Node.js):**
```javascript
// src/index.js
class DigitalTwinPlatform {
    async createOrganization(data) { ... }
    async getOrganization(id) { ... }
    async updateOrganization(id, data) { ... }
    async listOrganizations(filters) { ... }
}
```

**Будет (Python):**
```python
# core/engine/twin_engine.py
class DigitalTwinEngine:
    async def create_organization(self, data: OrganizationCreate) -> Organization:
        """Create organization - сохраняем полностью"""
        pass

    async def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization - сохраняем полностью"""
        pass

    async def update_organization(self, org_id: str, data: OrganizationUpdate) -> Organization:
        """Update organization - сохраняем полностью"""
        pass

    async def list_organizations(self, filters: OrganizationFilters) -> List[Organization]:
        """List organizations - сохраняем полностью"""
        pass
```

**Функции сохраняются:**
- ✅ CRUD операции
- ✅ Фильтрация и поиск
- ✅ Пагинация
- ✅ Сортировка
- ✅ Валидация данных

---

#### ✅ 2. Simulation Engine (6+ scenarios)

**Было (Node.js):**
```javascript
// src/simulation-engine.js
const SCENARIOS = {
    funding_shock: async (org, params) => { ... },
    staff_disruption: async (org, params) => { ... },
    supply_chain_break: async (org, params) => { ... },
    cyber_attack: async (org, params) => { ... },
    regulatory_change: async (org, params) => { ... },
    reputation_crisis: async (org, params) => { ... },
    economic_downturn: async (org, params) => { ... },
    natural_disaster: async (org, params) => { ... },
    pandemic: async (org, params) => { ... },
    market_shift: async (org, params) => { ... },
};
```

**Будет (Python):**
```python
# core/engine/simulation_engine.py
from abc import ABC, abstractmethod

class SimulationScenario(ABC):
    @abstractmethod
    async def run(self, organization: Organization, params: Dict) -> SimulationResult:
        """Run simulation scenario"""
        pass

class FundingShockScenario(SimulationScenario):
    """Funding shock simulation - ПОЛНОСТЬЮ портируем логику"""

    async def run(self, org: Organization, params: Dict) -> SimulationResult:
        # Портируем всю логику из Node.js
        funding_drop = params.get('funding_drop_percent', 30)
        duration = params.get('duration_months', 6)

        # Расчёты как в оригинале
        impact = self._calculate_funding_impact(org, funding_drop, duration)
        recovery_plan = self._generate_recovery_plan(org, impact)

        return SimulationResult(
            scenario='funding_shock',
            impact=impact,
            recovery_plan=recovery_plan,
            timeline=self._build_timeline(duration)
        )

# Аналогично портируем ВСЕ 10+ сценариев
class StaffDisruptionScenario(SimulationScenario): ...
class SupplyChainBreakScenario(SimulationScenario): ...
class CyberAttackScenario(SimulationScenario): ...
class RegulatoryChangeScenario(SimulationScenario): ...
class ReputationCrisisScenario(SimulationScenario): ...
class EconomicDownturnScenario(SimulationScenario): ...
class NaturalDisasterScenario(SimulationScenario): ...
class PandemicScenario(SimulationScenario): ...
class MarketShiftScenario(SimulationScenario): ...
```

**Функции сохраняются:**
- ✅ Все 10+ сценариев
- ✅ Все алгоритмы расчётов
- ✅ Генерация recovery plans
- ✅ Timeline построение
- ✅ Параметризация

---

#### ✅ 3. Theory of Change Engine

**Было (Node.js):**
```javascript
// src/theory-of-change-engine.js (~13KB)
class TheoryOfChangeEngine {
    async generateTheoryOfChange(organization) { ... }
    async analyzeImpactPathways(toc) { ... }
    async validateAssumptions(toc) { ... }
}
```

**Будет (Python):**
```python
# core/engine/theory_of_change.py
class TheoryOfChangeEngine:
    """Theory of Change Engine - портируем полностью"""

    async def generate_theory_of_change(
        self,
        organization: Organization
    ) -> TheoryOfChange:
        """Generate ToC - сохраняем всю логику"""
        # Портируем алгоритм из Node.js
        inputs = self._identify_inputs(organization)
        activities = self._map_activities(organization)
        outputs = self._predict_outputs(activities)
        outcomes = self._chain_outcomes(outputs)
        impact = self._calculate_impact(outcomes)

        return TheoryOfChange(
            inputs=inputs,
            activities=activities,
            outputs=outputs,
            outcomes=outcomes,
            impact=impact,
            assumptions=self._extract_assumptions(),
            indicators=self._define_indicators()
        )

    async def analyze_impact_pathways(
        self,
        toc: TheoryOfChange
    ) -> List[ImpactPathway]:
        """Analyze pathways - сохраняем логику"""
        pass

    async def validate_assumptions(
        self,
        toc: TheoryOfChange
    ) -> ValidationResult:
        """Validate assumptions - сохраняем логику"""
        pass
```

**Функции сохраняются:**
- ✅ Генерация ToC
- ✅ Анализ impact pathways
- ✅ Валидация assumptions
- ✅ Indicator definition

---

#### ✅ 4. Impact Passport Generator

**Было (Node.js):**
```javascript
// src/impact-passport-generator.js (~23KB)
class ImpactPassportGenerator {
    async generatePassport(organization) { ... }
    async validateImpactClaims(passport) { ... }
    async generateQRCode(passport) { ... }
}
```

**Будет (Python):**
```python
# core/engine/impact_passport.py
class ImpactPassportGenerator:
    """Impact Passport Generator - портируем полностью"""

    async def generate_passport(
        self,
        organization: Organization
    ) -> ImpactPassport:
        """Generate impact passport - сохраняем логику"""
        # Портируем алгоритм генерации
        identity = self._build_identity(organization)
        impact_claims = await self._collect_impact_claims(organization)
        evidence = await self._gather_evidence(impact_claims)
        verification = await self._verify_claims(impact_claims, evidence)

        passport = ImpactPassport(
            identity=identity,
            claims=impact_claims,
            evidence=evidence,
            verification=verification,
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=365)
        )

        # Generate QR code
        passport.qr_code = await self._generate_qr_code(passport)

        return passport

    async def validate_impact_claims(
        self,
        passport: ImpactPassport
    ) -> ValidationResult:
        """Validate claims - сохраняем логику"""
        pass

    async def generate_qr_code(
        self,
        passport: ImpactPassport
    ) -> str:
        """Generate QR code - сохраняем логику"""
        pass
```

**Функции сохраняются:**
- ✅ Генерация паспорта
- ✅ Сбор impact claims
- ✅ Верификация
- ✅ QR код генерация

---

#### ✅ 5. Organization Data Collector

**Было (Node.js):**
```javascript
// src/organization-data-collector.js (~43KB!)
class OrganizationDataCollector {
    async collectFinancialData(org) { ... }
    async collectOperationalData(org) { ... }
    async collectStaffData(org) { ... }
    async collectProgramData(org) { ... }
    async collectBeneficiaryData(org) { ... }
}
```

**Будет (Python):**
```python
# core/collectors/organization_collector.py
class OrganizationDataCollector:
    """Organization Data Collector - портируем полностью"""

    async def collect_financial_data(
        self,
        org: Organization
    ) -> FinancialData:
        """Collect financial data - сохраняем логику"""
        # Портируем алгоритмы сбора
        pass

    async def collect_operational_data(
        self,
        org: Organization
    ) -> OperationalData:
        """Collect operational data - сохраняем логику"""
        pass

    async def collect_staff_data(
        self,
        org: Organization
    ) -> StaffData:
        """Collect staff data - сохраняем логику"""
        pass

    async def collect_program_data(
        self,
        org: Organization
    ) -> List[ProgramData]:
        """Collect program data - сохраняем логику"""
        pass

    async def collect_beneficiary_data(
        self,
        org: Organization
    ) -> BeneficiaryData:
        """Collect beneficiary data - сохраняем логику"""
        pass
```

**Функции сохраняются:**
- ✅ Сбор финансовых данных
- ✅ Сбор операционных данных
- ✅ Сбор данных о персонале
- ✅ Сбор данных о программах
- ✅ Сбор данных о бенефициарах

---

#### ✅ 6. Metrics & Health Scoring

**Было (Node.js):**
```javascript
// src/index.js
async calculateHealthScore(organization) {
    const financial = this.calculateFinancialHealth(organization);
    const operational = this.calculateOperationalHealth(organization);
    const impact = this.calculateImpactScore(organization);
    const sustainability = this.calculateSustainability(organization);

    return (financial + operational + impact + sustainability) / 4;
}
```

**Будет (Python):**
```python
# core/engine/metrics_engine.py
class MetricsEngine:
    """Metrics & Health Scoring - сохраняем все алгоритмы"""

    async def calculate_health_score(
        self,
        organization: Organization
    ) -> HealthScore:
        """Calculate health score - полностью сохраняем"""
        financial = await self.calculate_financial_health(organization)
        operational = await self.calculate_operational_health(organization)
        impact = await self.calculate_impact_score(organization)
        sustainability = await self.calculate_sustainability(organization)

        overall = (financial + operational + impact + sustainability) / 4

        return HealthScore(
            overall=overall,
            financial=financial,
            operational=operational,
            impact=impact,
            sustainability=sustainability,
            calculated_at=datetime.utcnow()
        )

    async def calculate_financial_health(self, org: Organization) -> float:
        """Financial health - сохраняем алгоритм"""
        pass

    async def calculate_operational_health(self, org: Organization) -> float:
        """Operational health - сохраняем алгоритм"""
        pass

    async def calculate_impact_score(self, org: Organization) -> float:
        """Impact score - сохраняем алгоритм"""
        pass

    async def calculate_sustainability(self, org: Organization) -> float:
        """Sustainability - сохраняем алгоритм"""
        pass
```

**Функции сохраняются:**
- ✅ Health score calculation
- ✅ Financial health
- ✅ Operational health
- ✅ Impact scoring
- ✅ Sustainability metrics

---

#### ✅ 7. Predictions & Forecasting

**Было (Node.js):**
```javascript
// Predictions generation
async generatePredictions(organization, timeframe) {
    const predictions = [];

    predictions.push(this.predictFinancialTrend(organization, timeframe));
    predictions.push(this.predictImpact(organization, timeframe));
    predictions.push(this.predictRisks(organization, timeframe));

    return predictions;
}
```

**Будет (Python):**
```python
# core/engine/prediction_engine.py
class PredictionEngine:
    """Predictions & Forecasting - сохраняем полностью"""

    async def generate_predictions(
        self,
        organization: Organization,
        timeframe: Timeframe
    ) -> List[Prediction]:
        """Generate predictions - сохраняем логику"""
        predictions = []

        predictions.append(
            await self.predict_financial_trend(organization, timeframe)
        )
        predictions.append(
            await self.predict_impact(organization, timeframe)
        )
        predictions.append(
            await self.predict_risks(organization, timeframe)
        )

        return predictions

    async def predict_financial_trend(
        self,
        org: Organization,
        timeframe: Timeframe
    ) -> FinancialPrediction:
        """Financial trend prediction - сохраняем алгоритм"""
        pass

    async def predict_impact(
        self,
        org: Organization,
        timeframe: Timeframe
    ) -> ImpactPrediction:
        """Impact prediction - сохраняем алгоритм"""
        pass

    async def predict_risks(
        self,
        org: Organization,
        timeframe: Timeframe
    ) -> RiskPrediction:
        """Risk prediction - сохраняем алгоритм"""
        pass
```

**Функции сохраняются:**
- ✅ Financial trend prediction
- ✅ Impact prediction
- ✅ Risk prediction
- ✅ Все алгоритмы прогнозирования

---

#### ✅ 8. Supabase Integration

**Было (Node.js):**
```javascript
// src/supabase-adapter.js (~26KB)
class SupabaseAdapter {
    async saveOrganization(data) { ... }
    async saveSimulation(data) { ... }
    async saveMetrics(data) { ... }
    async query(table, filters) { ... }
}
```

**Будет (Python):**
```python
# core/storage/supabase_storage.py
class SupabaseStorage:
    """Supabase Storage - портируем все операции"""

    async def save_organization(self, data: Organization) -> str:
        """Save organization - сохраняем логику"""
        pass

    async def save_simulation(self, data: Simulation) -> str:
        """Save simulation - сохраняем логику"""
        pass

    async def save_metrics(self, data: Metrics) -> str:
        """Save metrics - сохраняем логику"""
        pass

    async def query(self, table: str, filters: Dict) -> List[Dict]:
        """Query data - сохраняем логику"""
        pass
```

**Функции сохраняются:**
- ✅ Все CRUD операции
- ✅ Запросы с фильтрами
- ✅ Real-time subscriptions
- ✅ RLS policies

---

#### ✅ 9. MCP Server Integration

**Было (Node.js):**
```javascript
// mcp-server/digital-twin-mcp-server.js
class DigitalTwinMCPServer {
    async handleToolCall(tool, params) { ... }
    listTools() { ... }
}
```

**Будет (Python + опционально Node.js):**
```python
# mcp/mcp_server.py
class DigitalTwinMCPServer:
    """MCP Server - сохраняем протокол"""

    async def handle_tool_call(
        self,
        tool: str,
        params: Dict
    ) -> Dict:
        """Handle MCP tool call - сохраняем логику"""
        pass

    def list_tools(self) -> List[Tool]:
        """List available tools - сохраняем список"""
        pass
```

**Функции сохраняются:**
- ✅ MCP protocol support
- ✅ All MCP tools
- ✅ AI agent integration
- ✅ Claude Desktop compatibility

---

#### ✅ 10. Web Interface

**Было (Node.js):**
```javascript
// Web UI with Chart.js, D3.js, Vis-network
- Dashboard visualizations
- Interactive charts
- Network diagrams
- Real-time updates
```

**Будет (Python + Static files):**
```python
# web/app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/templates", StaticFiles(directory="web/templates"), name="templates")
```

**Функции сохраняются:**
- ✅ Все визуализации (Chart.js, D3.js, Vis-network)
- ✅ Dashboard
- ✅ Interactive features
- ✅ Real-time updates

---

### Из `digital-twin-engine` (~1,630 строк Node.js)

**Будет интегрирован как lightweight mode:**

```python
# core/engine/lightweight_mode.py
class LightweightDigitalTwin:
    """Lightweight mode для Desktop Extension"""

    def __init__(self, mode='lightweight'):
        self.mode = mode
        self.storage = InMemoryStorage()  # Без БД

    async def create_twin(self, params: Dict) -> Dict:
        """Create twin - in-memory mode"""
        pass
```

**Функции сохраняются:**
- ✅ In-memory twins
- ✅ Basic metrics
- ✅ Report generation
- ✅ Desktop Extension compatibility

---

### Из Odoo модулей

**Odoo модули НЕ портируются - создаются тонкие bridges:**

```python
# bridges/odoo/bridge.py
class OdooBridge:
    """Thin bridge to Odoo - не портируем, просто API клиент"""

    async def sync_client_to_twin(self, client_id: int):
        """Sync Odoo client to Digital Twin"""
        # Получить из Odoo
        client = await self.odoo_client.get_client(client_id)

        # Отправить в Digital Twin Service
        twin = await self.dt_client.create_or_update_twin({
            'source': 'odoo',
            'source_id': str(client_id),
            'name': client['name'],
            # ...
        })

        return twin
```

**Сохраняем интеграцию с:**
- ✅ bcm_digital_twin_core (через bridge)
- ✅ bcm_corporate_twin (через bridge)
- ✅ bcm_ai_twin_orchestrator (через bridge)
- ✅ Все 23+ BCM модули (через bridge)

---

## 🆕 НОВЫЕ ФУНКЦИИ

### 1. Plugin Manager для коллекторов

```python
# collectors/manager.py
class CollectorPluginManager:
    """NEW: Plugin architecture для коллекторов"""

    def __init__(self):
        self.collectors: Dict[str, Type[DataCollector]] = {}
        self.load_builtin_collectors()

    def register_collector(
        self,
        name: str,
        collector_class: Type[DataCollector]
    ):
        """NEW: Регистрация нового коллектора"""
        self.collectors[name] = collector_class

    async def collect_from(
        self,
        source: str,
        entity_type: str,
        config: Dict
    ) -> List[Dict]:
        """NEW: Сбор данных из источника"""
        collector = self.collectors[source](config)
        await collector.connect(config)
        return await collector.collect(entity_type)
```

**Новые возможности:**
- ✅ Регистрация кастомных коллекторов
- ✅ Динамическая загрузка плагинов
- ✅ Конфигурация через YAML/JSON
- ✅ Hot-reload коллекторов

---

### 2. Universal Data Collector Interface

```python
# collectors/base/collector.py
class DataCollector(ABC):
    """NEW: Базовый интерфейс для всех коллекторов"""

    @abstractmethod
    async def connect(self, config: Dict) -> bool:
        """Connect to data source"""
        pass

    @abstractmethod
    async def collect(self, entity_type: str) -> List[Dict]:
        """Collect data"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check source availability"""
        pass

    @abstractmethod
    def get_schema(self) -> Dict:
        """Get data schema"""
        pass
```

**Новые возможности:**
- ✅ Единый интерфейс для всех источников
- ✅ Стандартизация сбора данных
- ✅ Автоматическая валидация
- ✅ Health checking

---

### 3. Built-in Collectors (100+)

```python
# collectors/builtin/__init__.py
BUILTIN_COLLECTORS = {
    # CRM
    'salesforce': SalesforceCollector,
    'hubspot': HubSpotCollector,
    'pipedrive': PipedriveCollector,
    'zoho_crm': ZohoCRMCollector,
    'freshsales': FreshsalesCollector,

    # ERP
    'odoo': OdooCollector,
    'sap': SAPCollector,
    'microsoft_dynamics': DynamicsCollector,
    'netsuite': NetSuiteCollector,
    'oracle_erp': OracleERPCollector,

    # Financial
    'quickbooks': QuickBooksCollector,
    'xero': XeroCollector,
    'sage': SageCollector,
    'wave': WaveCollector,

    # Project Management
    'jira': JiraCollector,
    'asana': AsanaCollector,
    'monday': MondayCollector,
    'trello': TrelloCollector,
    'clickup': ClickUpCollector,

    # Communication
    'slack': SlackCollector,
    'microsoft_teams': TeamsCollector,
    'google_workspace': GoogleWorkspaceCollector,
    'zoom': ZoomCollector,

    # Marketing
    'mailchimp': MailchimpCollector,
    'hubspot_marketing': HubSpotMarketingCollector,
    'google_analytics': GoogleAnalyticsCollector,
    'facebook_ads': FacebookAdsCollector,

    # HR
    'bamboohr': BambooHRCollector,
    'workday': WorkdayCollector,
    'adp': ADPCollector,

    # IoT & Monitoring
    'aws_iot': AWSIoTCollector,
    'azure_iot': AzureIoTCollector,
    'google_iot': GoogleIoTCollector,
    'prometheus': PrometheusCollector,
    'grafana': GrafanaCollector,
    'datadog': DatadogCollector,

    # Social Media
    'twitter': TwitterCollector,
    'linkedin': LinkedInCollector,
    'facebook': FacebookCollector,
    'instagram': InstagramCollector,

    # Generic
    'rest_api': GenericRESTCollector,
    'graphql': GenericGraphQLCollector,
    'webhook': WebhookCollector,
    'database': DatabaseCollector,
    'csv': CSVCollector,
    'excel': ExcelCollector,
    'json': JSONCollector,
    'xml': XMLCollector,
}
```

**Новые возможности:**
- ✅ 100+ готовых коллекторов
- ✅ Покрытие основных платформ
- ✅ Единообразная конфигурация
- ✅ Plug & Play

---

### 4. Data Normalizer

```python
# processors/normalizer.py
class DataNormalizer:
    """NEW: Нормализация данных в каноническую схему"""

    CANONICAL_SCHEMA = {
        'organization': OrganizationSchema,
        'person': PersonSchema,
        'transaction': TransactionSchema,
        'event': EventSchema,
        'metric': MetricSchema,
    }

    async def normalize(
        self,
        data: Dict,
        source_type: str,
        entity_type: str
    ) -> Dict:
        """Normalize data to canonical schema"""
        # Маппинг специфичный для источника
        mapper = self.get_mapper(source_type, entity_type)
        normalized = mapper.transform(data)

        # Валидация по схеме
        schema = self.CANONICAL_SCHEMA[entity_type]
        validated = schema(**normalized)

        return validated.dict()
```

**Новые возможности:**
- ✅ Автоматическая нормализация
- ✅ Каноническая схема данных
- ✅ Валидация по схеме
- ✅ Маппинг для каждого источника

---

### 5. Entity Resolver

```python
# processors/resolver.py
class EntityResolver:
    """NEW: Разрешение дубликатов из разных источников"""

    async def resolve_entities(
        self,
        entities: List[Dict]
    ) -> Dict[str, Entity]:
        """Resolve duplicate entities"""
        # Группировка по схожести
        groups = await self._group_by_similarity(entities)

        # Объединение в каждой группе
        resolved = {}
        for group in groups:
            merged = await self._merge_entities(group['entities'])
            resolved[group['canonical_id']] = merged

        return resolved

    async def _group_by_similarity(
        self,
        entities: List[Dict]
    ) -> List[Dict]:
        """Group similar entities"""
        # Fuzzy matching по названиям
        # Exact matching по email, domain, etc.
        pass

    async def _merge_entities(
        self,
        entities: List[Dict]
    ) -> Entity:
        """Merge entities into one"""
        # Выбор лучших значений для каждого поля
        # Сохранение всех source_ids
        pass
```

**Новые возможности:**
- ✅ Автоматическое обнаружение дубликатов
- ✅ Fuzzy matching
- ✅ Умное объединение данных
- ✅ Отслеживание источников

---

### 6. Conflict Resolver

```python
# processors/conflict_resolver.py
class ConflictResolver:
    """NEW: Разрешение конфликтов данных"""

    STRATEGIES = {
        'most_recent': MostRecentStrategy,
        'most_complete': MostCompleteStrategy,
        'highest_quality': HighestQualityStrategy,
        'most_trusted': MostTrustedSourceStrategy,
        'majority_vote': MajorityVoteStrategy,
        'manual': ManualResolutionStrategy,
    }

    async def resolve_conflict(
        self,
        field: str,
        values: List[ConflictValue],
        strategy: str = 'auto'
    ) -> Any:
        """Resolve data conflict"""
        if strategy == 'auto':
            strategy = self._choose_strategy(field, values)

        resolver = self.STRATEGIES[strategy]()
        return await resolver.resolve(values)
```

**Новые возможности:**
- ✅ Множество стратегий разрешения
- ✅ Автоматический выбор стратегии
- ✅ Настраиваемые правила
- ✅ Audit trail конфликтов

---

### 7. Data Enricher

```python
# processors/enricher.py
class DataEnricher:
    """NEW: Обогащение данных из внешних источников"""

    async def enrich(
        self,
        entity: Entity
    ) -> EnrichedEntity:
        """Enrich entity data"""
        enriched = entity.copy()

        # Company info (Clearbit, etc.)
        if entity.type == 'organization':
            company_data = await self.fetch_company_info(entity.name)
            enriched.update({
                'logo_url': company_data.get('logo'),
                'description': company_data.get('description'),
                'employee_count_estimate': company_data.get('employees'),
                'tech_stack': company_data.get('tech'),
            })

        # Geolocation
        if entity.location:
            geo = await self.geocode(entity.location)
            enriched.update({
                'coordinates': geo['coordinates'],
                'timezone': geo['timezone'],
                'country_code': geo['country_code'],
            })

        # Industry classification
        if entity.industry:
            enriched.update({
                'naics_code': await self.get_naics(entity.industry),
                'sic_code': await self.get_sic(entity.industry),
            })

        # Risk scoring
        enriched['risk_score'] = await self.calculate_risk(entity)

        return enriched
```

**Новые возможности:**
- ✅ Автоматическое обогащение
- ✅ Интеграция с Clearbit, etc.
- ✅ Геолокация
- ✅ Industry classification
- ✅ Risk scoring

---

### 8. Quality Scorer

```python
# processors/quality.py
class QualityScorer:
    """NEW: Оценка качества данных"""

    async def score_data_quality(
        self,
        entity: Entity
    ) -> QualityScore:
        """Score data quality"""
        scores = {
            'completeness': self._score_completeness(entity),
            'accuracy': self._score_accuracy(entity),
            'consistency': self._score_consistency(entity),
            'timeliness': self._score_timeliness(entity),
            'validity': self._score_validity(entity),
        }

        overall = sum(scores.values()) / len(scores)

        return QualityScore(
            overall=overall,
            dimensions=scores,
            issues=self._identify_issues(entity, scores),
            recommendations=self._generate_recommendations(scores)
        )
```

**Новые возможности:**
- ✅ Многомерная оценка качества
- ✅ Выявление проблем
- ✅ Рекомендации по улучшению
- ✅ Tracking качества по времени

---

### 9. Auto-Discovery Engine

```python
# collectors/discovery.py
class DataSourceDiscovery:
    """NEW: Автообнаружение источников данных"""

    async def discover_sources(
        self,
        organization_id: str
    ) -> List[DiscoveredSource]:
        """Auto-discover data sources"""
        discovered = []
        org = await self.get_organization(organization_id)

        # DNS checks
        if await self._check_salesforce_dns(org.domain):
            discovered.append({
                'type': 'salesforce',
                'confidence': 0.9,
                'setup_url': f'/setup/salesforce?domain={org.domain}'
            })

        # Email domain checks
        if await self._check_google_workspace(org.email_domain):
            discovered.append({
                'type': 'google_workspace',
                'confidence': 0.95
            })

        # API endpoint checks
        endpoints = [
            f'https://{org.domain}/api',
            f'https://api.{org.domain}',
        ]
        for endpoint in endpoints:
            if api_type := await self._identify_api(endpoint):
                discovered.append({
                    'type': api_type,
                    'endpoint': endpoint,
                    'confidence': 0.7
                })

        return discovered
```

**Новые возможности:**
- ✅ Автоматическое обнаружение
- ✅ DNS/email проверки
- ✅ API fingerprinting
- ✅ Confidence scoring

---

### 10. GraphQL API

```python
# api/graphql/schema.py
import strawberry

@strawberry.type
class Organization:
    id: str
    name: str
    type: str
    health_score: float

@strawberry.type
class Query:
    @strawberry.field
    async def organization(self, id: str) -> Organization:
        """Get organization by ID"""
        return await get_organization(id)

    @strawberry.field
    async def organizations(
        self,
        filters: Optional[OrganizationFilters] = None
    ) -> List[Organization]:
        """List organizations"""
        return await list_organizations(filters)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_organization(
        self,
        data: OrganizationInput
    ) -> Organization:
        """Create organization"""
        return await create_organization(data)
```

**Новые возможности:**
- ✅ GraphQL API
- ✅ Flexible queries
- ✅ Subscriptions (real-time)
- ✅ Batching

---

## 📝 ДЕТАЛЬНАЯ СПЕЦИФИКАЦИЯ МОДУЛЕЙ

### Модуль 1: Core Engine

**Путь:** `core/engine/`

**Файлы:**
```
core/engine/
├── __init__.py
├── twin_engine.py          # Main Digital Twin engine
├── simulation_engine.py    # Simulation scenarios
├── prediction_engine.py    # Predictions & forecasting
├── metrics_engine.py       # Metrics calculation
├── theory_of_change.py     # Theory of Change engine
├── impact_passport.py      # Impact Passport generator
└── lightweight_mode.py     # Lightweight mode для Desktop
```

**Ключевые классы:**
- `DigitalTwinEngine` - главный движок
- `SimulationEngine` - симуляции
- `PredictionEngine` - предсказания
- `MetricsEngine` - метрики
- `TheoryOfChangeEngine` - ToC
- `ImpactPassportGenerator` - паспорта

**Зависимости:**
- Pydantic (models)
- SQLAlchemy (ORM)
- Redis (cache)

---

### Модуль 2: Data Collectors

**Путь:** `collectors/`

**Структура:**
```
collectors/
├── __init__.py
├── manager.py              # Plugin Manager
├── base/
│   ├── __init__.py
│   └── collector.py        # Abstract base
├── builtin/                # 100+ built-in collectors
│   ├── __init__.py
│   ├── odoo_collector.py
│   ├── salesforce_collector.py
│   ├── hubspot_collector.py
│   ├── quickbooks_collector.py
│   ├── slack_collector.py
│   ├── jira_collector.py
│   └── ... (90+ more)
├── custom/                 # User custom collectors
└── discovery.py            # Auto-discovery
```

**Ключевые классы:**
- `CollectorPluginManager` - менеджер плагинов
- `DataCollector` - базовый класс
- `DataSourceDiscovery` - автообнаружение

---

### Модуль 3: Data Processors

**Путь:** `processors/`

**Структура:**
```
processors/
├── __init__.py
├── normalizer.py           # Data normalization
├── resolver.py             # Entity resolution
├── conflict_resolver.py    # Conflict resolution
├── enricher.py             # Data enrichment
└── quality.py              # Quality scoring
```

**Ключевые классы:**
- `DataNormalizer` - нормализация
- `EntityResolver` - разрешение дубликатов
- `ConflictResolver` - разрешение конфликтов
- `DataEnricher` - обогащение
- `QualityScorer` - оценка качества

---

### Модуль 4: Storage

**Путь:** `core/storage/`

**Структура:**
```
core/storage/
├── __init__.py
├── supabase_storage.py     # Supabase backend
├── postgres_storage.py     # PostgreSQL backend
├── redis_cache.py          # Redis cache
└── timeseries_storage.py   # TimescaleDB для метрик
```

**Ключевые классы:**
- `SupabaseStorage` - Supabase интеграция
- `PostgreSQLStorage` - PostgreSQL интеграция
- `RedisCache` - кеширование
- `TimeSeriesStorage` - временные ряды

---

### Модуль 5: API Gateway

**Путь:** `api/`

**Структура:**
```
api/
├── __init__.py
├── main.py                 # FastAPI app
├── routes/
│   ├── __init__.py
│   ├── collectors.py       # Collectors API
│   ├── twins.py            # Digital Twins API
│   ├── simulations.py      # Simulations API
│   ├── analytics.py        # Analytics API
│   ├── health.py           # Health checks
│   └── admin.py            # Admin API
├── graphql/
│   ├── __init__.py
│   ├── schema.py           # GraphQL schema
│   └── resolvers.py        # GraphQL resolvers
├── websocket/
│   ├── __init__.py
│   └── handlers.py         # WebSocket handlers
└── middleware/
    ├── __init__.py
    ├── auth.py             # Authentication
    ├── cors.py             # CORS
    └── rate_limit.py       # Rate limiting
```

---

### Модуль 6: Bridges

**Путь:** `bridges/`

**Структура:**
```
bridges/
├── __init__.py
├── odoo/
│   ├── __init__.py
│   ├── bridge.py           # Odoo bridge
│   └── client.py           # Odoo API client
├── salesforce/
│   ├── __init__.py
│   ├── bridge.py           # Salesforce bridge
│   └── client.py           # Salesforce API client
└── ... (другие bridges)
```

**Ключевые классы:**
- `OdooBridge` - мост к Odoo
- `SalesforceBridge` - мост к Salesforce

---

## 📡 API СПЕЦИФИКАЦИЯ

### REST API Endpoints (90+)

#### **Collectors API**

```
POST   /api/v1/collectors/{source}/setup
POST   /api/v1/collectors/{source}/collect
GET    /api/v1/collectors
GET    /api/v1/collectors/{source}/status
DELETE /api/v1/collectors/{source}
GET    /api/v1/sources/discover
```

#### **Digital Twins API**

```
POST   /api/v1/twins
GET    /api/v1/twins
GET    /api/v1/twins/{twin_id}
PUT    /api/v1/twins/{twin_id}
DELETE /api/v1/twins/{twin_id}
POST   /api/v1/twins/{twin_id}/merge
GET    /api/v1/twins/{twin_id}/sources
```

#### **Simulations API**

```
POST   /api/v1/twins/{twin_id}/simulations
GET    /api/v1/twins/{twin_id}/simulations
GET    /api/v1/twins/{twin_id}/simulations/{simulation_id}
GET    /api/v1/simulations/scenarios
```

#### **Analytics API**

```
GET    /api/v1/twins/{twin_id}/metrics
GET    /api/v1/twins/{twin_id}/predictions
GET    /api/v1/twins/{twin_id}/health
GET    /api/v1/twins/{twin_id}/reports
POST   /api/v1/twins/{twin_id}/theory-of-change
GET    /api/v1/twins/{twin_id}/impact-passport
```

#### **Admin API**

```
GET    /api/v1/admin/stats
GET    /api/v1/admin/quality
GET    /api/v1/admin/conflicts
POST   /api/v1/admin/resolve-conflict
```

### GraphQL Schema

```graphql
type Organization {
  id: ID!
  name: String!
  type: OrganizationType!
  healthScore: Float
  sources: [DataSource!]!
  metrics: OrganizationMetrics
  simulations: [Simulation!]!
  predictions: [Prediction!]!
}

type Query {
  organization(id: ID!): Organization
  organizations(filters: OrganizationFilters): [Organization!]!
  simulation(id: ID!): Simulation
  discoverSources(organizationId: ID!): [DiscoveredSource!]!
}

type Mutation {
  createOrganization(data: OrganizationInput!): Organization!
  updateOrganization(id: ID!, data: OrganizationUpdate!): Organization!
  runSimulation(twinId: ID!, scenario: String!, params: JSON!): Simulation!
  setupCollector(source: String!, config: JSON!): CollectorSetup!
}

type Subscription {
  organizationUpdated(id: ID!): Organization!
  simulationProgress(id: ID!): SimulationProgress!
  metricsUpdated(twinId: ID!): OrganizationMetrics!
}
```

---

## 🔄 ПЛАН МИГРАЦИИ

### Этап 1: Подготовка (1 день)

1. Создать структуру директорий
2. Setup виртуального окружения
3. Установить зависимости
4. Настроить Supabase connection
5. Создать базовые модели данных

### Этап 2: Core Engine (3 дня)

1. Портировать `DigitalTwinEngine`
2. Портировать `SimulationEngine` (10 сценариев)
3. Портировать `MetricsEngine`
4. Портировать `PredictionEngine`
5. Портировать `TheoryOfChangeEngine`
6. Портировать `ImpactPassportGenerator`

**Результат:** Core функциональность работает

### Этап 3: Data Collectors (2 дня)

1. Создать `CollectorPluginManager`
2. Создать базовый класс `DataCollector`
3. Портировать `OrganizationDataCollector`
4. Создать 10 priority collectors:
   - OdooCollector
   - SalesforceCollector
   - HubSpotCollector
   - QuickBooksCollector
   - SlackCollector
   - JiraCollector
   - GoogleWorkspaceCollector
   - GenericRESTCollector
   - CSVCollector
   - DatabaseCollector

**Результат:** Data collection работает

### Этап 4: Data Processors (2 дня)

1. Создать `DataNormalizer`
2. Создать `EntityResolver`
3. Создать `ConflictResolver`
4. Создать `DataEnricher`
5. Создать `QualityScorer`

**Результат:** Data processing работает

### Этап 5: Storage Layer (1 день)

1. Создать `SupabaseStorage`
2. Создать `RedisCache`
3. Создать `TimeSeriesStorage`
4. Миграция схемы БД

**Результат:** Storage работает

### Этап 6: API Gateway (2 дня)

1. Создать FastAPI app
2. Создать REST endpoints (90+)
3. Создать GraphQL schema
4. Создать WebSocket handlers
5. Добавить authentication
6. Добавить rate limiting

**Результат:** API работает

### Этап 7: Bridges (1 день)

1. Создать `OdooBridge`
2. Создать `SalesforceBridge`
3. Тестировать интеграцию

**Результат:** Bridges работают

### Этап 8: Web UI (1 день)

1. Портировать HTML/CSS/JS
2. Обновить API endpoints
3. Тестировать визуализации

**Результат:** Web UI работает

### Этап 9: MCP Server (1 день)

1. Портировать MCP Server
2. Тестировать с Claude Desktop

**Результат:** MCP работает

### Этап 10: Testing & Documentation (2 дня)

1. Unit tests
2. Integration tests
3. API документация
4. User documentation

**Результат:** Production ready

---

## 📅 ПЛАН РЕАЛИЗАЦИИ

### Timeline: 15 рабочих дней

```
День 1:    Подготовка
День 2-4:  Core Engine
День 5-6:  Data Collectors
День 7-8:  Data Processors
День 9:    Storage Layer
День 10-11: API Gateway
День 12:   Bridges
День 13:   Web UI
День 14:   MCP Server
День 15-16: Testing & Documentation
```

### Приоритеты

**P0 (Критично):**
- Core Engine
- Storage Layer
- API Gateway
- OdooBridge

**P1 (Высокий):**
- Data Collectors (10 priority)
- Data Processors
- Web UI

**P2 (Средний):**
- Остальные collectors (90+)
- MCP Server
- GraphQL

**P3 (Низкий):**
- Advanced features
- Optimizations

### Риски

| Риск | Вероятность | Митигация |
|------|------------|-----------|
| Потеря функциональности | Средняя | Детальное тестирование |
| Проблемы с миграцией БД | Низкая | Использование Supabase миграций |
| Performance regression | Средняя | Бенчмарки на каждом этапе |
| Breaking changes в API | Высокая | Версионирование API |

---

## ✅ КРИТЕРИИ ПРИЁМКИ

### Функциональные требования

- [ ] Все функции из `digital-twin-platform` работают
- [ ] Все 10+ сценариев симуляций работают
- [ ] Plugin Manager позволяет регистрировать коллекторы
- [ ] 10 priority collectors работают
- [ ] Data normalization работает
- [ ] Entity resolution работает
- [ ] OdooBridge работает
- [ ] REST API работает (90+ endpoints)
- [ ] GraphQL API работает
- [ ] Web UI работает
- [ ] MCP Server работает

### Нефункциональные требования

- [ ] Performance: <100ms для основных API запросов
- [ ] Scalability: поддержка 1000+ organizations
- [ ] Reliability: 99.9% uptime
- [ ] Security: JWT authentication, RBAC
- [ ] Documentation: 100% API documented
- [ ] Test coverage: >80%

### Backward Compatibility

- [ ] Odoo bridge работает с существующими модулями
- [ ] API совместим с существующими клиентами
- [ ] Database schema compatible

---

## 📚 ДОКУМЕНТАЦИЯ

### Документы для создания

1. **Architecture Guide**
   - System architecture
   - Component diagram
   - Data flow diagram

2. **API Documentation**
   - REST API reference (OpenAPI)
   - GraphQL schema
   - WebSocket protocol

3. **Developer Guide**
   - Setup instructions
   - Plugin development
   - Contributing guide

4. **User Guide**
   - Getting started
   - Collector configuration
   - Simulation scenarios

5. **Deployment Guide**
   - Docker deployment
   - Kubernetes deployment
   - Configuration

---

## 🎯 ИТОГО

**Что сохраняем:**
- ✅ ВСЕ 44,000+ строк функциональности
- ✅ Все 10+ сценариев симуляций
- ✅ Все алгоритмы расчётов
- ✅ Theory of Change Engine
- ✅ Impact Passport Generator
- ✅ Organization Data Collector
- ✅ Metrics & Health Scoring
- ✅ Predictions & Forecasting
- ✅ Supabase Integration
- ✅ MCP Server
- ✅ Web UI
- ✅ Все интеграции с Odoo

**Что добавляем:**
- ✅ Plugin Manager (NEW)
- ✅ 100+ Built-in Collectors (NEW)
- ✅ Data Normalizer (NEW)
- ✅ Entity Resolver (NEW)
- ✅ Conflict Resolver (NEW)
- ✅ Data Enricher (NEW)
- ✅ Quality Scorer (NEW)
- ✅ Auto-Discovery (NEW)
- ✅ GraphQL API (NEW)
- ✅ Universal Architecture (NEW)

**Результат:**
- Сохранены 100% существующих функций
- Добавлены 10+ новых мощных возможностей
- Создана универсальная платформа
- Нет vendor lock-in

---

**Готово к реализации:** ✅
**Время реализации:** 15 рабочих дней
**Риск:** Низкий (детальное ТЗ, ничего не теряем)

**Начинаем?** 🚀
