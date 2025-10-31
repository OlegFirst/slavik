const { EventEmitter } = require('events');
const { v4: uuidv4 } = require('uuid');

class AIBridgeManager extends EventEmitter {
  constructor() {
    super();
    this.moduleAdapters = new Map();
    this.contextProviders = new Map();
    this.translationRules = new Map();
    this.knowledgeBase = {
      systemConcepts: new Map(),
      domainConcepts: new Map(),
      mappings: new Map()
    };
    this.learningHistory = [];
  }

  // Регистрация модуля в системе через мост
  async registerModule(moduleConfig) {
    const adapterId = uuidv4();

    // Создаем адаптер для модуля
    const adapter = {
      id: adapterId,
      moduleName: moduleConfig.name,
      moduleType: moduleConfig.type,
      domain: moduleConfig.domain || 'bcm',

      // Системные интерфейсы которые предоставляет мост
      systemInterfaces: {
        eventBus: this.createEventInterface(moduleConfig),
        dataGateway: this.createDataInterface(moduleConfig),
        workflowEngine: this.createWorkflowInterface(moduleConfig),
        aiServices: this.createAIInterface(moduleConfig)
      },

      // Контекст модуля
      context: {
        permissions: moduleConfig.permissions || [],
        dataSources: moduleConfig.dataSources || [],
        workflows: moduleConfig.workflows || [],
        events: moduleConfig.events || []
      },

      registeredAt: new Date(),
      status: 'active'
    };

    this.moduleAdapters.set(moduleConfig.name, adapter);

    // Обучаем систему новым концепциям модуля
    await this.learnModuleConcepts(moduleConfig);

    this.emit('module:registered', {
      moduleName: moduleConfig.name,
      adapterId
    });

    return adapter;
  }

  // Создаем интерфейс событий для модуля
  createEventInterface(moduleConfig) {
    return {
      // Модуль публикует domain-specific событие
      publish: async (domainEvent) => {
        // AI переводит в системное событие
        const systemEvent = await this.translateToSystemEvent(domainEvent, moduleConfig.domain);

        // Публикуем в системную шину
        this.emit('system:event', systemEvent);

        // Логируем для обучения
        this.logTranslation(domainEvent, systemEvent, 'event');

        return systemEvent;
      },

      // Модуль подписывается на события
      subscribe: (eventPattern, handler) => {
        // Создаем обертку которая переводит системные события в domain-specific
        const wrappedHandler = async (systemEvent) => {
          const domainEvent = await this.translateToDomainEvent(systemEvent, moduleConfig.domain);
          if (domainEvent) {
            handler(domainEvent);
          }
        };

        this.on(eventPattern, wrappedHandler);
        return () => this.off(eventPattern, wrappedHandler);
      }
    };
  }

  // Создаем интерфейс данных для модуля
  createDataInterface(moduleConfig) {
    return {
      // Сохранение domain-specific данных
      save: async (domainData) => {
        // Маппим на универсальную схему
        const systemData = await this.mapToSystemSchema(domainData, moduleConfig.domain);

        // Добавляем метаданные
        systemData._metadata = {
          source: moduleConfig.name,
          domain: moduleConfig.domain,
          timestamp: new Date(),
          version: moduleConfig.version
        };

        // Сохраняем через системный gateway
        this.emit('data:save', systemData);

        return systemData;
      },

      // Поиск данных с domain-specific запросом
      find: async (domainQuery) => {
        // Переводим запрос в системный формат
        const systemQuery = await this.translateQuery(domainQuery, moduleConfig.domain);

        // Запрашиваем через системный gateway
        return new Promise((resolve) => {
          this.emit('data:query', {
            query: systemQuery,
            callback: async (results) => {
              // Маппим результаты обратно в domain format
              const domainResults = await Promise.all(
                results.map(r => this.mapToDomainSchema(r, moduleConfig.domain))
              );
              resolve(domainResults);
            }
          });
        });
      }
    };
  }

  // Создаем интерфейс workflow для модуля
  createWorkflowInterface(moduleConfig) {
    return {
      // Запуск domain-specific процесса
      startProcess: async (processName, processData) => {
        // Находим подходящий BPMN workflow
        const workflow = await this.findOrCreateWorkflow(processName, moduleConfig.domain);

        // Маппим данные процесса
        const systemProcessData = await this.mapProcessData(processData, moduleConfig.domain);

        // Запускаем через системный engine
        this.emit('workflow:start', {
          workflow,
          data: systemProcessData,
          context: {
            module: moduleConfig.name,
            domain: moduleConfig.domain
          }
        });

        return { processId: uuidv4(), status: 'started' };
      },

      // Регистрация domain-specific задачи
      registerTask: (taskName, handler) => {
        const systemTaskName = `${moduleConfig.domain}.${taskName}`;

        // Оборачиваем handler для перевода данных
        const wrappedHandler = async (systemData) => {
          const domainData = await this.mapToDomainSchema(systemData, moduleConfig.domain);
          const result = await handler(domainData);
          return await this.mapToSystemSchema(result, moduleConfig.domain);
        };

        this.emit('task:register', {
          name: systemTaskName,
          handler: wrappedHandler
        });
      }
    };
  }

  // Создаем AI интерфейс для модуля
  createAIInterface(moduleConfig) {
    return {
      // Предсказание с domain context
      predict: async (input, modelType) => {
        // Добавляем domain context
        const enrichedInput = {
          ...input,
          _context: {
            domain: moduleConfig.domain,
            module: moduleConfig.name,
            concepts: await this.getDomainConcepts(moduleConfig.domain)
          }
        };

        // Вызываем системный AI
        return new Promise((resolve) => {
          this.emit('ai:predict', {
            input: enrichedInput,
            modelType,
            callback: resolve
          });
        });
      },

      // Анализ с domain knowledge
      analyze: async (data, analysisType) => {
        // Обогащаем domain знаниями
        const context = await this.buildDomainContext(moduleConfig.domain);

        return new Promise((resolve) => {
          this.emit('ai:analyze', {
            data,
            type: analysisType,
            context,
            callback: resolve
          });
        });
      }
    };
  }

  // AI переводит domain событие в системное
  async translateToSystemEvent(domainEvent, domain) {
    // Ищем правило перевода
    let rule = this.translationRules.get(`${domain}:${domainEvent.type}`);

    if (!rule) {
      // AI создает новое правило на основе обучения
      rule = await this.learnTranslationRule(domainEvent, domain);
    }

    return {
      id: uuidv4(),
      type: rule.systemType || 'domain.event',
      source: domain,
      originalType: domainEvent.type,
      data: domainEvent.data,
      timestamp: new Date(),
      metadata: {
        domain,
        confidence: rule.confidence || 0.8
      }
    };
  }

  // AI переводит системное событие в domain
  async translateToDomainEvent(systemEvent, domain) {
    // Проверяем релевантность для домена
    if (!this.isRelevantForDomain(systemEvent, domain)) {
      return null;
    }

    // Находим обратное правило
    const rule = this.findReverseRule(systemEvent.type, domain);

    if (!rule) {
      return null;
    }

    return {
      type: rule.domainType,
      data: systemEvent.data,
      systemEventId: systemEvent.id
    };
  }

  // Обучаем систему концепциям модуля
  async learnModuleConcepts(moduleConfig) {
    const { domain, concepts = {} } = moduleConfig;

    // Сохраняем domain концепции
    this.knowledgeBase.domainConcepts.set(domain, concepts);

    // Создаем маппинги на системные концепции
    for (const [domainConcept, definition] of Object.entries(concepts)) {
      const systemConcept = this.findSimilarSystemConcept(definition);

      if (systemConcept) {
        this.knowledgeBase.mappings.set(
          `${domain}:${domainConcept}`,
          systemConcept
        );
      } else {
        // Новая концепция - добавляем в систему
        this.knowledgeBase.systemConcepts.set(domainConcept, {
          origin: domain,
          definition,
          createdAt: new Date()
        });
      }
    }

    this.emit('knowledge:updated', { domain, conceptsCount: Object.keys(concepts).length });
  }

  // AI учится на переводах
  logTranslation(source, target, type) {
    this.learningHistory.push({
      source,
      target,
      type,
      timestamp: new Date(),
      success: true
    });

    // Периодически анализируем и улучшаем правила
    if (this.learningHistory.length % 100 === 0) {
      this.optimizeTranslationRules();
    }
  }

  // Оптимизация правил на основе истории
  async optimizeTranslationRules() {
    const patterns = this.analyzePatterns(this.learningHistory.slice(-1000));

    for (const pattern of patterns) {
      if (pattern.confidence > 0.9) {
        this.translationRules.set(pattern.key, {
          systemType: pattern.systemType,
          domainType: pattern.domainType,
          confidence: pattern.confidence,
          optimizedAt: new Date()
        });
      }
    }

    this.emit('rules:optimized', {
      rulesCount: this.translationRules.size,
      avgConfidence: this.calculateAverageConfidence()
    });
  }

  // Анализ паттернов в истории
  analyzePatterns(history) {
    const patterns = new Map();

    for (const entry of history) {
      const key = `${entry.source.type}:${entry.target.type}`;

      if (!patterns.has(key)) {
        patterns.set(key, {
          count: 0,
          successes: 0,
          key
        });
      }

      const pattern = patterns.get(key);
      pattern.count++;
      if (entry.success) pattern.successes++;
    }

    return Array.from(patterns.values()).map(p => ({
      ...p,
      confidence: p.successes / p.count,
      systemType: p.key.split(':')[1],
      domainType: p.key.split(':')[0]
    }));
  }

  // Проверка релевантности события для домена
  isRelevantForDomain(event, domain) {
    // Проверяем прямое указание
    if (event.targetDomains && event.targetDomains.includes(domain)) {
      return true;
    }

    // Проверяем по правилам
    const rules = Array.from(this.translationRules.entries())
      .filter(([k]) => k.endsWith(`:${event.type}`));

    return rules.some(([k]) => k.startsWith(`${domain}:`));
  }

  // Поиск похожей системной концепции
  findSimilarSystemConcept(definition) {
    for (const [concept, def] of this.knowledgeBase.systemConcepts) {
      if (this.calculateSimilarity(definition, def.definition) > 0.8) {
        return concept;
      }
    }
    return null;
  }

  // Расчет схожести концепций
  calculateSimilarity(def1, def2) {
    // Простая реализация - можно заменить на embeddings
    const words1 = new Set(String(def1).toLowerCase().split(/\s+/));
    const words2 = new Set(String(def2).toLowerCase().split(/\s+/));

    const intersection = new Set([...words1].filter(x => words2.has(x)));
    const union = new Set([...words1, ...words2]);

    return intersection.size / union.size;
  }

  calculateAverageConfidence() {
    const rules = Array.from(this.translationRules.values());
    if (rules.length === 0) return 0;

    const sum = rules.reduce((acc, rule) => acc + (rule.confidence || 0), 0);
    return sum / rules.length;
  }

  // Построение контекста домена
  async buildDomainContext(domain) {
    return {
      concepts: this.knowledgeBase.domainConcepts.get(domain) || {},
      mappings: Array.from(this.knowledgeBase.mappings.entries())
        .filter(([k]) => k.startsWith(`${domain}:`))
        .map(([k, v]) => ({ domain: k, system: v })),
      rules: Array.from(this.translationRules.entries())
        .filter(([k]) => k.startsWith(`${domain}:`))
        .map(([k, v]) => ({ key: k, ...v }))
    };
  }

  // Получение статистики моста
  getStats() {
    return {
      registeredModules: this.moduleAdapters.size,
      translationRules: this.translationRules.size,
      domainConcepts: this.knowledgeBase.domainConcepts.size,
      systemConcepts: this.knowledgeBase.systemConcepts.size,
      mappings: this.knowledgeBase.mappings.size,
      learningHistory: this.learningHistory.length,
      avgConfidence: this.calculateAverageConfidence()
    };
  }
}

// API endpoints
const express = require('express');
const app = express();
app.use(express.json());

const bridgeManager = new AIBridgeManager();

app.post('/register', async (req, res) => {
  const adapter = await bridgeManager.registerModule(req.body);
  res.json({
    status: 'registered',
    adapterId: adapter.id
  });
});

app.get('/stats', (req, res) => {
  res.json(bridgeManager.getStats());
});

app.get('/context/:domain', async (req, res) => {
  const context = await bridgeManager.buildDomainContext(req.params.domain);
  res.json(context);
});

const PORT = process.env.PORT || 3010;
app.listen(PORT, () => {
  console.log(`AI Bridge Manager running on port ${PORT}`);
});

module.exports = AIBridgeManager;