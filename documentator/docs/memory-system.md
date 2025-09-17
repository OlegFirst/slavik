# Memory System Documentation

Digital Office включає потужну систему управління пам'яттю, що дозволяє агентам зберігати, отримувати та аналізувати дані через різні типи сховищ.

## Підтримувані Провайдери Пам'яті

### 🗃️ **Supabase**
Postgres-based БД як сервіс з real-time можливостями
```typescript
supabase: {
  enabled: true,
  url: "https://your-project.supabase.co",
  key: "your-anon-key",
  schema: "public"
}
```

### 🍃 **MongoDB**
NoSQL документна база даних
```typescript
mongodb: {
  enabled: true,
  uri: "mongodb://localhost:27017",
  database: "digital_office"
}
```

### 🚀 **Redis**
In-memory структури даних для кешування та швидкого доступу
```typescript
redis: {
  enabled: true,
  host: "localhost",
  port: 6379,
  password: "your-password",
  database: 0
}
```

### 🐘 **PostgreSQL**
Реляційна база даних з підтримкою JSON
```typescript
postgresql: {
  enabled: true,
  host: "localhost",
  port: 5432,
  database: "digital_office",
  username: "user",
  password: "password"
}
```

### 🔍 **Elasticsearch**
Повнотекстовий пошук та аналітика
```typescript
elasticsearch: {
  enabled: true,
  node: "http://localhost:9200",
  username: "elastic",
  password: "password"
}
```

### 📁 **File System**
Локальне зберігання файлів (за замовчуванням)
```typescript
file: {
  enabled: true,
  path: "./data/memory"
}
```

## Типи Пам'яті

### 🗣️ **Conversation**
Зберігання діалогів та взаємодій
```typescript
await agent.storeConversation({
  message: "Привіт! Як справи?",
  userId: "user123",
  timestamp: new Date()
});
```

### 🧠 **Knowledge**
База знань та навчальні дані
```typescript
await agent.storeKnowledge({
  topic: "машинне навчання",
  content: "ML алгоритми для класифікації",
  difficulty: "intermediate"
}, ['ml', 'classification']);
```

### 📊 **Analytics**
Метрики та аналітичні дані
```typescript
await agent.storeAnalytics({
  executionTime: 1500,
  success: true,
  resourcesUsed: { cpu: 45, memory: 128 }
});
```

### ⚙️ **Configuration**
Налаштування агентів
```typescript
await agent.storeMemory('configuration', {
  key: 'api_settings',
  data: { timeout: 30000, retries: 3 }
}, ['config', 'api']);
```

### 💾 **Cache**
Тимчасові дані для швидкого доступу
```typescript
await agent.storeMemory('cache', {
  result: processedData,
  expiresAt: new Date(Date.now() + 3600000)
}, ['cache', 'processed']);
```

## Використання в Агентах

### Базове Зберігання

```typescript
export class SmartAgent extends BaseAgent {
  protected async executeAutonomously(): Promise<void> {
    // Зберігаємо результат роботи
    const result = await this.performTask();

    const memoryId = await this.storeMemory('analytics', {
      task: 'data_processing',
      result,
      timestamp: new Date()
    }, ['task', 'processing']);

    this.log(`Результат збережено: ${memoryId}`);
  }
}
```

### Пошук та Аналіз

```typescript
// Пошук знань за тегами
const knowledge = await this.searchKnowledge(['machine-learning', 'classification'], 20);

// Запит за специфічними критеріями
const recentAnalytics = await this.queryMemory({
  type: 'analytics',
  dateRange: {
    from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // Останні 7 днів
    to: new Date()
  },
  limit: 50
});

// Аналіз паттернів
const patterns = this.analyzePatterns(recentAnalytics);
```

### Навчання та Адаптація

```typescript
protected async adaptBehavior(): Promise<void> {
  // Отримуємо історію виконання
  const history = await this.getExecutionHistory(100);

  // Аналізуємо успішність
  const successRate = history.filter(h => h.data.execution.success).length / history.length;

  if (successRate < 0.7) {
    // Аналізуємо помилки та зберігаємо інсайти
    const errorPatterns = this.analyzeErrorPatterns(history);

    await this.storeKnowledge({
      type: 'improvement_strategy',
      patterns: errorPatterns,
      recommendations: this.generateRecommendations(errorPatterns)
    }, ['improvement', 'learning']);
  }
}
```

## Конфігурація Memory Providers

### Environment Variables

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# MongoDB
MONGODB_URI=mongodb://localhost:27017/digital_office

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=digital_office
POSTGRES_USER=user
POSTGRES_PASSWORD=password

# Elasticsearch
ELASTICSEARCH_NODE=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=password
```

### Agent-Specific Configuration

```typescript
export class DataAnalystAgent extends BaseAgent {
  protected async onInitialize(): Promise<void> {
    // Конфігуруємо провайдери пам'яті для цього агента
    this.configureMemoryProviders({
      supabase: {
        enabled: true,
        url: process.env.SUPABASE_URL,
        key: process.env.SUPABASE_KEY
      },
      redis: {
        enabled: true,
        host: process.env.REDIS_HOST,
        port: parseInt(process.env.REDIS_PORT || '6379'),
        database: 1 // Окрема база для цього агента
      }
    });

    await this.initializeMemory();
  }
}
```

## Advanced Features

### Cross-Provider Replication

```typescript
// Зберігаємо в primary провайдері
const primaryId = await this.storeMemory('knowledge', data, tags, 'supabase');

// Резервна копія в іншому провайдері
await this.storeMemory('knowledge', {
  ...data,
  primaryId
}, [...tags, 'backup'], 'mongodb');
```

### Memory Migration

```typescript
// Міграція даних між провайдерами
async migrateMemoryData(fromProvider: string, toProvider: string): Promise<void> {
  const allData = await this.queryMemory({}, fromProvider);

  for (const record of allData) {
    await this.storeMemory(record.type, record.data, record.tags, toProvider);
  }

  this.log(`Перенесено ${allData.length} записів з ${fromProvider} до ${toProvider}`);
}
```

### Memory Analytics

```typescript
async analyzeMemoryUsage(): Promise<any> {
  const providers = await this.getMemoryProviders();
  const analysis: any = {};

  for (const provider of providers) {
    const data = await this.queryMemory({}, provider);

    analysis[provider] = {
      totalRecords: data.length,
      byType: this.groupByType(data),
      oldestRecord: data.reduce((oldest, current) =>
        oldest.metadata?.createdAt < current.metadata?.createdAt ? oldest : current
      ),
      storageSize: this.estimateStorageSize(data)
    };
  }

  return analysis;
}
```

## Best Practices

### 1. **Provider Selection**
- **Redis**: Для кешування та швидкого доступу
- **MongoDB/Supabase**: Для структурованих даних та складних запитів
- **Elasticsearch**: Для повнотекстового пошуку
- **File System**: Для розробки та невеликих проектів

### 2. **Memory Management**
```typescript
// Періодичне очищення старих даних
async cleanupOldMemories(): Promise<void> {
  const cutoffDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 днів

  const oldMemories = await this.queryMemory({
    type: 'cache',
    dateRange: { from: new Date(0), to: cutoffDate }
  });

  for (const memory of oldMemories) {
    await this.deleteMemory(memory.id);
  }
}
```

### 3. **Error Handling**
```typescript
async storeWithFallback(data: any, primaryProvider: string, fallbackProvider: string): Promise<string> {
  try {
    return await this.storeMemory('knowledge', data, [], primaryProvider);
  } catch (error) {
    this.log(`Primary provider failed, using fallback: ${error.message}`, 'warn');
    return await this.storeMemory('knowledge', data, ['fallback'], fallbackProvider);
  }
}
```

### 4. **Performance Optimization**
```typescript
// Використання кешування
async getCachedOrFetch(key: string, fetchFn: () => Promise<any>): Promise<any> {
  // Спробуємо знайти в кеші
  const cached = await this.queryMemory({
    type: 'cache',
    tags: [key]
  });

  if (cached.length > 0 && !this.isCacheExpired(cached[0])) {
    return cached[0].data;
  }

  // Якщо не знайдено, виконуємо функцію та кешуємо
  const result = await fetchFn();
  await this.storeMemory('cache', result, [key]);

  return result;
}
```

## Troubleshooting

### Provider Connection Issues
```typescript
async diagnoseMemoryProviders(): Promise<void> {
  const providers = await this.getMemoryProviders();

  for (const provider of providers) {
    const isHealthy = await this.testMemoryProvider(provider);

    if (!isHealthy) {
      this.log(`❌ Provider ${provider} не доступний`, 'error');

      // Спробуємо перевірити конкретні помилки
      try {
        await this.storeMemory('cache', { test: true }, ['diagnostic'], provider);
      } catch (error) {
        this.log(`Деталі помилки ${provider}: ${error.message}`, 'error');
      }
    } else {
      this.log(`✅ Provider ${provider} працює нормально`);
    }
  }
}
```

### Memory Debugging
```typescript
async debugMemoryState(): Promise<any> {
  return {
    providers: await this.getMemoryProviders(),
    totalRecords: (await this.queryMemory({})).length,
    recentActivity: await this.queryMemory({
      limit: 10
    }),
    cacheStatus: this.memoryManager['cache'].size,
    lastCleanup: new Date()
  };
}
```

## Приклади Використання

Дивіться файл `examples/memory-enhanced-agent.ts` для повного прикладу агента з розширеними можливостями пам'яті.

## Monitoring та Метрики

Memory система автоматично збирає метрики про використання, які можуть бути корисні для оптимізації:

- Кількість запитів до кожного провайдера
- Час відгуку запитів
- Розмір збережених даних
- Частота звернень до різних типів пам'яті
- Ефективність кешування

Ці дані допомагають у виборі оптимального провайдера для конкретних завдань та налаштуванні продуктивності системи.