# Digital Twin с SEH Адаптерами - Развертывание

## Быстрый старт

### 1. Подготовка
```bash
# Клонируйте проект
git clone <your-repo>
cd digital-twin-standalone

# Настройте переменные окружения
cp config/environments/development.env .env
# Отредактируйте .env с вашими настройками Supabase
```

### 2. Развертывание с Docker Compose
```bash
# Соберите и запустите все сервисы
docker compose up --build -d

# Проверьте статус
docker compose ps
```

### 3. Проверка работы
```bash
# Основное приложение
curl http://localhost:3000/health

# SimPy адаптер
curl http://localhost:7001/docs

# Mesa адаптер  
curl http://localhost:7002/docs

# EpiNow2 адаптер
curl http://localhost:7003/__ping__
```

## Архитектура развертывания

```
digital-twin:3000 ←→ simpy-adapter:7001
                 ↙→ mesa-adapter:7002
                 ↘→ epinow2-adapter:7003
```

## Доступные эксперименты

### 🔬 **Внешние SEH адаптеры (3 эксперимента)**

#### 1. SimPy (Очереди/Capacity Planning)
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "simpy_queue",
    "params": {
      "arrival_rate": 12,
      "service_time": {"dist": "lognormal", "mu": "10m", "sigma": 0.5},
      "capacity_agents": [6, 8, 10],
      "targets": {"sla_target": 0.95, "wait_p50_min": "15m"}
    },
    "monte_carlo_runs": 50
  }'
```

#### 2. Mesa (Agent-Based Modeling)
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "mesa_abm",
    "params": {
      "steps": 200,
      "population_size": 2000,
      "policies": {"sms": 1.5, "vouchers": 1.1}
    },
    "monte_carlo_runs": 100
  }'
```

#### 3. EpiNow2 (Epidemiological Modeling)
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "epi_nowcasting_rt",
    "params": {
      "cases_ts": "supabase://bucket/path.csv",
      "generation_time": "dist_ref",
      "reporting_delay": "dist_ref"
    }
  }'
```

### 🏢 **Digital Twin организационные сценарии (22 эксперимента)**

#### Основные сценарии трансформации:
- `automation` - Автоматизация процессов
- `digital_transformation` - Цифровая трансформация
- `ai_implementation` - Внедрение ИИ
- `process_optimization` - Оптимизация процессов

#### Управление рисками и кризисами:
- `crisis` - Антикризисное управление
- `cybersecurity` - Кибербезопасность
- `compliance` - Соответствие требованиям

#### Развитие и расширение:
- `expansion` - Расширение деятельности
- `partnership_development` - Развитие партнерств
- `integration` - Интеграция систем
- `innovation_research` - Инновации и исследования

#### Управление персоналом и процессами:
- `staff_training` - Обучение персонала
- `capacity_building` - Наращивание потенциала
- `resource_allocation` - Распределение ресурсов
- `knowledge_management` - Управление знаниями

#### Взаимодействие с сообществом:
- `stakeholder_engagement` - Взаимодействие с заинтересованными сторонами
- `community_outreach` - Работа с сообществом
- `sustainability_planning` - Планирование устойчивости

#### Управление грантами и финансами:
- `grant_management` - Управление грантами
- `funding_diversification` - Диверсификация финансирования
- `impact_assessment` - Оценка воздействия

#### Мониторинг и оценка:
- `monitoring_evaluation` - Мониторинг и оценка

### ⚙️ **Внутренние движки симуляций (4 эксперимента)**

#### 4. Theory of Change
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "theory_of_change",
    "params": {
      "objective": "maximize_outcome_per_cost",
      "budget_cap": 50000,
      "decision_variables": ["outreach_sms", "transport_vouchers"]
    },
    "monte_carlo_runs": 1000
  }'
```

#### 5. Capacity Sweep
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "capacity_sweep",
    "params": {
      "min_capacity": 5,
      "max_capacity": 20,
      "step": 1
    },
    "monte_carlo_runs": 200
  }'
```

#### 6. BCM Outage Simulation
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "bcm_outage",
    "params": {
      "outage_duration": 24,
      "affected_systems": ["crm", "email"]
    }
  }'
```

#### 7. Budget Optimization
```bash
curl -X POST http://localhost:3000/api/simulations/run \
  -H "Content-Type: application/json" \
  -d '{
    "experiment": "budget_optimization",
    "params": {
      "total_budget": 100000,
      "priorities": ["staff", "technology", "outreach"]
    }
  }'
```

## 📊 **ИТОГО: 29 доступных экспериментов**
- 3 внешних SEH адаптера
- 22 Digital Twin сценария 
- 4 внутренних движка

## Fallback режим

Если внешние адаптеры недоступны, система автоматически переключается на fallback режим с предупреждениями.

## Логи и мониторинг

```bash
# Логи основного приложения
docker compose logs digital-twin

# Логи адаптеров
docker compose logs simpy-adapter mesa-adapter epinow2-adapter

# Живые логи
docker compose logs -f
```

## Остановка

```bash
# Остановить все сервисы
docker compose down

# Очистить данные и образы
docker compose down -v --rmi all
```

## Production настройки

1. Смените все секреты в .env
2. Настройте реальные URL Supabase
3. Используйте production.env вместо development.env
4. Настройте reverse proxy (nginx)
5. Добавьте SSL сертификаты