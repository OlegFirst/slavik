# QA Engineer Agent

## Роль та Відповідальності

**QA Engineer Agent** - автономний агент для забезпечення якості продукту через автоматизоване тестування, аналіз якості коду та координацію QA процесів.

## Основний функціонал

### 1. **Автоматизоване тестування**
- Запуск unit, integration та e2e тестів
- Генерація та виконання тест-кейсів
- Performance та load тестування
- Security тестування

### 2. **Аналіз якості коду**
- Static code analysis
- Code coverage аналіз
- Code smell detection
- Dependency vulnerability scanning

### 3. **Test Management**
- Планування тестових циклів
- Трекінг дефектів та їх життєвого циклу
- Test case management
- Test data generation

### 4. **Continuous Testing Integration**
- CI/CD pipeline integration
- Automated test execution
- Test results reporting
- Quality gates enforcement

## Технічні можливості

### Тестування
- Jest, Mocha, Pytest runners
- Selenium, Playwright для UI тестів
- Postman/Newman для API тестів
- JMeter для performance тестів

### Аналіз якості
- SonarQube integration
- ESLint, Pylint, RuboCop
- Security scanners (OWASP ZAP, Snyk)
- Custom quality metrics

### Автоматизація
- Test case генерація
- Test data factories
- Automated bug reporting
- Flaky test detection

## MCP Команди

### `qa:run_test_suite`
Запускає набір тестів

**Параметри:**
```json
{
  "projectPath": "./path/to/project",
  "testType": "unit|integration|e2e|performance|security",
  "environment": "local|staging|production",
  "parallel": true,
  "coverage": true
}
```

### `qa:analyze_code_quality`
Аналізує якість коду

**Параметри:**
```json
{
  "projectPath": "./path/to/project",
  "analyzeTypes": ["complexity", "coverage", "security", "style"],
  "threshold": {
    "coverage": 80,
    "complexity": 10
  }
}
```

### `qa:generate_test_cases`
Генерує тест-кейси на основі коду

**Параметри:**
```json
{
  "sourceFile": "./src/UserService.ts",
  "testType": "unit|integration",
  "framework": "jest|mocha|pytest",
  "includeEdgeCases": true
}
```

### `qa:report_bug`
Автоматично створює звіт про баг

**Параметри:**
```json
{
  "title": "Login fails with special characters",
  "severity": "high|medium|low",
  "steps": ["Open login page", "Enter email with +", "Click login"],
  "expected": "User should be logged in",
  "actual": "Error message displayed",
  "environment": "staging",
  "assignee": "developer.name"
}
```

### `qa:performance_test`
Запускає performance тестування

**Параметри:**
```json
{
  "targetUrl": "https://api.example.com",
  "testType": "load|stress|spike|volume",
  "users": 100,
  "duration": "10m",
  "rampUp": "2m"
}
```

### `qa:security_scan`
Виконує security сканування

**Параметри:**
```json
{
  "target": "application|api|infrastructure",
  "scanType": "sast|dast|dependency",
  "severity": "high|medium|low|all"
}
```

## Події EventBus

### Публікує
- `qa.tests.started` - Тести розпочато
- `qa.tests.completed` - Тести завершено
- `qa.bug.found` - Знайдено баг
- `qa.coverage.updated` - Оновлено покриття
- `qa.quality.gate.passed` - Quality gate пройдено
- `qa.quality.gate.failed` - Quality gate не пройдено

### Слухає
- `git.commit` - Новий коміт для тестування
- `ci.build.completed` - Збірка завершена
- `deployment.started` - Початок деплою
- `project-manager.sprint.started` - Новий спринт
- `devops.deployment.completed` - Деплой завершено

## Структура даних

### QA дані зберігаються в:
```
data/qa/
├── test-results/
│   ├── unit/               # Unit тест результати
│   ├── integration/        # Integration тест результати
│   ├── e2e/               # End-to-end тест результати
│   ├── performance/       # Performance тест результати
│   └── security/          # Security scan результати
├── coverage/
│   ├── current.json       # Поточне покриття
│   ├── history.json       # Історія покриття
│   └── reports/           # Детальні звіти
├── quality-analysis/
│   ├── code-quality.json  # Метрики якості коду
│   ├── complexity.json    # Аналіз складності
│   └── tech-debt.json     # Технічний борг
├── bugs/
│   ├── active.json        # Активні баги
│   ├── resolved.json      # Вирішені баги
│   └── reports/           # Звіти по багах
└── test-cases/
    ├── generated/         # Автогенеровані тести
    ├── manual/           # Мануальні тест-кейси
    └── templates/        # Шаблони тестів
```

## Конфігурація

```json
{
  "testingInterval": 30,              // Інтервал тестування (хвилини)
  "qualityCheckInterval": 60,         // Перевірка якості (хвилини)
  "frameworks": {
    "unit": "jest",
    "e2e": "playwright",
    "api": "supertest",
    "performance": "k6"
  },
  "qualityGates": {
    "unitTestCoverage": 80,           // Мінімальне покриття %
    "codeComplexity": 10,             // Максимальна складність
    "duplicatedLines": 5,             // Максимум дублювання %
    "securityHotspots": 0             // Максимум security issues
  },
  "testEnvironments": {
    "local": {
      "baseUrl": "http://localhost:3000",
      "database": "test"
    },
    "staging": {
      "baseUrl": "https://staging.example.com",
      "database": "staging"
    }
  },
  "integrations": {
    "jira": {
      "enabled": true,
      "url": "${JIRA_URL}",
      "token": "${JIRA_TOKEN}",
      "autoBugReporting": true
    },
    "sonarqube": {
      "enabled": true,
      "url": "${SONAR_URL}",
      "token": "${SONAR_TOKEN}"
    },
    "slack": {
      "enabled": true,
      "webhook": "${SLACK_WEBHOOK}",
      "channel": "#qa-alerts"
    }
  },
  "notifications": {
    "testFailures": true,
    "qualityGateFailures": true,
    "newBugsFound": true,
    "coverageDrops": true
  }
}
```

## Типи тестів та стратегії

### 1. **Unit Testing Strategy**
```json
{
  "testPattern": "**/*.test.{js,ts}",
  "coverage": {
    "statements": 80,
    "branches": 75,
    "functions": 80,
    "lines": 80
  },
  "testData": "factories",
  "mocking": "automatic"
}
```

### 2. **Integration Testing Strategy**
```json
{
  "testPattern": "**/*.integration.{js,ts}",
  "database": "testcontainers",
  "apis": "wiremock",
  "environment": "docker-compose"
}
```

### 3. **E2E Testing Strategy**
```json
{
  "browser": ["chromium", "firefox", "webkit"],
  "viewport": ["desktop", "tablet", "mobile"],
  "testData": "fixtures",
  "parallelism": 4
}
```

### 4. **Performance Testing Strategy**
```json
{
  "loadPatterns": ["constant", "ramp-up", "spike"],
  "metrics": ["response-time", "throughput", "error-rate"],
  "sla": {
    "responseTime": "200ms",
    "errorRate": "1%"
  }
}
```

## Інтеграція з іншими агентами

- **DevOps Engineer** - інтеграція з CI/CD, результати тестів для деплою
- **Data Analyst** - метрики тестування та якості коду
- **Project Manager** - звітність по тестуванню, блокери
- **Development Team** - фідбек по якості коду, результати тестів

## Quality Gates

### 1. **Code Quality Gate**
```typescript
interface QualityGate {
  coverage: number;          // >= 80%
  complexity: number;        // <= 10
  duplicatedLines: number;   // <= 5%
  codeSmells: number;        // <= 5
  securityHotspots: number;  // = 0
  bugs: number;             // = 0
}
```

### 2. **Performance Gate**
```typescript
interface PerformanceGate {
  responseTime95: number;    // <= 500ms
  errorRate: number;         // <= 1%
  throughput: number;        // >= 100 rps
  cpuUsage: number;         // <= 80%
  memoryUsage: number;      // <= 80%
}
```

## Автоматичні сценарії

### 1. **Continuous Testing Pipeline**
```bash
# При кожному коміті:
1. Запуск unit тестів
2. Аналіз покриття коду
3. Static code analysis
4. Security scan
5. Звіт результатів
```

### 2. **Quality Gate Enforcement**
```bash
# Перед деплоєм:
1. Запуск повного набору тестів
2. Перевірка quality gates
3. Performance тестування
4. Security сканування
5. Блокування деплою при failure
```

### 3. **Automated Bug Reporting**
```bash
# При знаходженні проблем:
1. Збір контексту та логів
2. Створення детального bug report
3. Призначення відповідального
4. Нотифікація команди
5. Трекінг до вирішення
```

## Приклади використання

### Запуск повного набору тестів
```bash
qa:run_test_suite {
  "projectPath": "./my-project",
  "testType": "all",
  "environment": "staging",
  "parallel": true,
  "coverage": true
}
```

### Аналіз якості коду
```bash
qa:analyze_code_quality {
  "projectPath": "./my-project",
  "analyzeTypes": ["complexity", "coverage", "security"],
  "threshold": {
    "coverage": 85,
    "complexity": 8
  }
}
```

### Генерація тестів для нового модуля
```bash
qa:generate_test_cases {
  "sourceFile": "./src/PaymentService.ts",
  "testType": "unit",
  "framework": "jest",
  "includeEdgeCases": true
}
```