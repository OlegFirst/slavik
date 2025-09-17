# Senior DevOps Engineer Agent

## Роль та Відповідальності

**Senior DevOps Engineer Agent** - автономний агент для управління інфраструктурою, деплоєм, моніторингом та автоматизацією DevOps процесів.

## Основний функціонал

### 1. **Управління деплоєм**
- Автоматичний деплой застосунків
- Rollback при виявленні проблем
- Blue/Green та Canary деплої
- Контроль версій та артефактів

### 2. **Моніторинг інфраструктури**
- Моніторинг серверів та сервісів
- Аналіз логів та метрик
- Alerting при проблемах
- Health checks застосунків

### 3. **Управління конфігурацією**
- Infrastructure as Code
- Конфігурація середовищ
- Secrets management
- Backup та відновлення

### 4. **CI/CD пайплайни**
- Налаштування та оптимізація пайплайнів
- Automated testing integration
- Артефакт менеджмент
- Performance testing

## Технічні можливості

### Деплой та оркестрація
- Docker контейнери
- Kubernetes оркестрація
- Cloud providers (AWS, Azure, GCP)
- Terraform/Ansible автоматизація

### Моніторинг та алертинг
- Prometheus/Grafana стеки
- ELK Stack для логів
- Custom метрики
- Інцидент менеджмент

### Безпека та комплаєнс
- Security scanning
- Vulnerability assessment
- Compliance перевірки
- Аудит доступів

## MCP Команди

### `devops:deploy_application`
Деплоїть застосунок в указане середовище

**Параметри:**
```json
{
  "applicationName": "my-app",
  "environment": "staging|production",
  "version": "v1.2.3",
  "deploymentStrategy": "rolling|blue-green|canary"
}
```

### `devops:check_infrastructure`
Перевіряє стан інфраструктури

**Параметри:**
```json
{
  "environment": "all|staging|production",
  "components": ["servers", "databases", "services"],
  "includeMetrics": true
}
```

### `devops:rollback_deployment`
Відкочує деплой до попередньої версії

**Параметри:**
```json
{
  "applicationName": "my-app",
  "environment": "staging|production",
  "targetVersion": "v1.2.2"
}
```

### `devops:scale_service`
Масштабує сервіс

**Параметри:**
```json
{
  "serviceName": "api-service",
  "environment": "production",
  "replicas": 5,
  "autoScale": true
}
```

### `devops:backup_database`
Створює backup бази даних

**Параметри:**
```json
{
  "databaseName": "main-db",
  "environment": "production",
  "retentionDays": 30
}
```

### `devops:security_scan`
Запускає security scan

**Параметри:**
```json
{
  "scanType": "vulnerability|compliance|secrets",
  "target": "application|infrastructure",
  "severity": "high|medium|low"
}
```

## Події EventBus

### Публікує
- `deployment.started` - Початок деплою
- `deployment.completed` - Деплой завершено
- `deployment.failed` - Деплой не вдався
- `infrastructure.alert` - Алерт інфраструктури
- `security.vulnerability` - Виявлено уразливість
- `backup.completed` - Backup створено

### Слухає
- `git.push` - Новий push в репозиторій
- `ci.build.success` - Успішна збірка
- `qa.tests.passed` - Тести пройшли
- `monitoring.threshold` - Перевищення метрик
- `security.incident` - Інцидент безпеки

## Структура даних

### DevOps дані зберігаються в:
```
data/devops/
├── deployments/
│   ├── history.json        # Історія деплоїв
│   ├── rollbacks.json      # Інформація про rollback'и
│   └── artifacts/          # Метадані артефактів
├── infrastructure/
│   ├── monitoring/         # Метрики моніторингу
│   ├── alerts/             # Алерти та інциденти
│   └── health-checks/      # Результати health check'ів
├── security/
│   ├── scans/              # Результати сканувань
│   ├── vulnerabilities/    # Виявлені уразливості
│   └── compliance/         # Compliance звіти
└── backups/
    ├── schedules.json      # Розклад backup'ів
    └── status.json         # Статус backup'ів
```

## Конфігурація

```json
{
  "deploymentInterval": 60,       // Перевірка деплою (хвилини)
  "monitoringInterval": 5,        // Моніторинг (хвилини)
  "environments": {
    "staging": {
      "kubernetesCluster": "staging-cluster",
      "namespace": "staging",
      "autoDeployBranch": "develop"
    },
    "production": {
      "kubernetesCluster": "prod-cluster",
      "namespace": "production",
      "autoDeployBranch": "main",
      "requireApproval": true
    }
  },
  "alerting": {
    "slack": {
      "webhook": "${SLACK_WEBHOOK}",
      "channel": "#devops-alerts"
    },
    "email": {
      "recipients": ["devops@company.com"]
    }
  },
  "backup": {
    "schedule": "0 2 * * *",      // Щоденно о 2:00
    "retentionDays": 30
  },
  "security": {
    "scanSchedule": "0 1 * * 0",  // Щотижня о 1:00
    "autoFix": false
  }
}
```

## Інтеграція з Cloud Providers

### AWS
- ECS/EKS для контейнерів
- RDS для баз даних
- S3 для backup'ів
- CloudWatch для моніторингу

### Azure
- AKS для Kubernetes
- Azure SQL
- Blob Storage
- Azure Monitor

### GCP
- GKE для контейнерів
- Cloud SQL
- Cloud Storage
- Cloud Monitoring

## Інтеграція з іншими агентами

- **QA Engineer** - отримує результати тестів перед деплоєм
- **Data Analyst** - надає метрики деплоїв та інфраструктури
- **Project Manager** - інформує про статус релізів
- **Security Scanner** - інтегрується з security перевірками

## Приклади використання

### Автоматичний деплой після успішних тестів
```bash
# Через Claude або EventBus
devops:deploy_application {
  "applicationName": "api-service",
  "environment": "staging",
  "version": "latest",
  "deploymentStrategy": "rolling"
}
```

### Перевірка стану інфраструктури
```bash
devops:check_infrastructure {
  "environment": "production",
  "components": ["servers", "databases", "services"],
  "includeMetrics": true
}
```

### Екстрений rollback
```bash
devops:rollback_deployment {
  "applicationName": "api-service",
  "environment": "production",
  "targetVersion": "v1.2.2"
}
```

## Сценарії автоматизації

### 1. **Continuous Deployment**
- Слухає події `ci.build.success`
- Автоматично деплоїть у staging
- Запускає smoke tests
- При успіху - деплоїть у production

### 2. **Incident Response**
- Моніторить health checks
- При падінні сервісу - автоматичний rollback
- Відправляє алерти команді
- Створює інцидент в системі

### 3. **Scheduled Maintenance**
- Автоматичні backup'и
- Security сканування
- Cleanup старих артефактів
- Оновлення certificates