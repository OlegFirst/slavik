// Dependency Coordinator - управление зависимостями между компонентами

class DependencyCoordinator {
  constructor(config = {}) {
    this.config = config;

    // Граф зависимостей
    this.dependencyGraph = new Map(); // component -> {dependencies, dependents}

    // Резервные маршруты
    this.fallbackRoutes = new Map(); // component -> [fallback1, fallback2, ...]

    // Версии компонентов
    this.componentVersions = new Map(); // component -> {current, available, compatible}

    // Состояние компонентов
    this.componentHealth = new Map(); // component -> {status, lastCheck, metrics}

    // Стратегии разрешения конфликтов
    this.resolutionStrategies = {
      versionConflict: config.versionConflict || 'latest',
      unavailable: config.unavailable || 'fallback',
      circular: config.circular || 'break'
    };

    // Кэш разрешенных зависимостей
    this.resolutionCache = new Map();

    this.stats = {
      totalComponents: 0,
      healthyComponents: 0,
      failedComponents: 0,
      fallbacksUsed: 0,
      conflictsResolved: 0
    };
  }

  async initialize() {
    console.log('🔗 Initializing Dependency Coordinator...');

    // Сканируем все компоненты
    await this.scanComponents();

    // Строим граф зависимостей
    await this.buildDependencyGraph();

    // Проверяем на циклические зависимости
    this.detectCircularDependencies();

    // Начинаем мониторинг
    this.startHealthMonitoring();

    console.log('✅ Dependency Coordinator initialized');
    console.log(`   Total components: ${this.stats.totalComponents}`);
    console.log(`   Dependency graph built with ${this.dependencyGraph.size} nodes`);
  }

  // Сканирование компонентов
  async scanComponents() {
    const components = [
      // System Components
      { name: 'orchestrator', path: '../SYSTEM_COMPONENTS/1_ORCHESTRATION', type: 'system' },
      { name: 'event-bus', path: '../SYSTEM_COMPONENTS/2_EVENTS', type: 'system' },
      { name: 'workflow-engine', path: '../SYSTEM_COMPONENTS/3_PROCESSING', type: 'system' },
      { name: 'data-gateway', path: '../SYSTEM_COMPONENTS/4_STORAGE', type: 'system' },
      { name: 'ai-services', path: '../SYSTEM_COMPONENTS/5_INTELLIGENCE', type: 'system' },
      { name: 'monitoring', path: '../SYSTEM_COMPONENTS/6_TOOLS', type: 'system' },

      // Bridge Components
      { name: 'ai-bridge-manager', path: '../ai-bridge-manager', type: 'bridge' },
      { name: 'operational-brain', path: '../operational-brain', type: 'bridge' },
      { name: 'security-analyzer', path: '../security-analyzer', type: 'bridge' },

      // Program Components
      { name: 'bcm-domain', path: '../PROGRAM_COMPONENTS_NEW/DOMAIN_REGISTRY/bcm', type: 'program' },
      { name: 'bia-module', path: '../PROGRAM_COMPONENTS_NEW/MODULE_LIBRARY/business-impact-analysis', type: 'program' },
      { name: 'odoo-adapter', path: '../PROGRAM_COMPONENTS_NEW/INTEGRATION_LAYER/platform-adapters/odoo-adapter', type: 'program' }
    ];

    for (const component of components) {
      await this.registerComponent(component);
    }

    this.stats.totalComponents = components.length;
  }

  // Регистрация компонента
  async registerComponent(component) {
    const { name, path, type } = component;

    // Инициализируем структуру зависимостей
    if (!this.dependencyGraph.has(name)) {
      this.dependencyGraph.set(name, {
        dependencies: new Set(),
        dependents: new Set(),
        type: type,
        path: path,
        status: 'unknown'
      });
    }

    // Проверяем здоровье компонента
    const health = await this.checkComponentHealth(name);
    this.componentHealth.set(name, health);

    // Определяем версию
    const version = await this.getComponentVersion(name);
    this.componentVersions.set(name, version);

    return {
      name,
      registered: true,
      health: health.status,
      version: version.current
    };
  }

  // Построение графа зависимостей
  async buildDependencyGraph() {
    // Определяем зависимости между компонентами
    const dependencies = {
      // System dependencies
      'orchestrator': ['event-bus', 'data-gateway'],
      'event-bus': [],
      'workflow-engine': ['event-bus', 'data-gateway'],
      'data-gateway': [],
      'ai-services': ['data-gateway'],
      'monitoring': ['event-bus'],

      // Bridge dependencies
      'ai-bridge-manager': ['orchestrator', 'event-bus', 'ai-services'],
      'operational-brain': ['ai-services', 'data-gateway'],
      'security-analyzer': ['event-bus', 'monitoring'],

      // Program dependencies
      'bcm-domain': ['orchestrator', 'event-bus'],
      'bia-module': ['bcm-domain', 'odoo-adapter'],
      'odoo-adapter': ['data-gateway']
    };

    for (const [component, deps] of Object.entries(dependencies)) {
      if (this.dependencyGraph.has(component)) {
        const node = this.dependencyGraph.get(component);

        for (const dep of deps) {
          // Добавляем зависимость
          node.dependencies.add(dep);

          // Добавляем обратную связь
          if (this.dependencyGraph.has(dep)) {
            this.dependencyGraph.get(dep).dependents.add(component);
          }
        }
      }
    }

    // Определяем fallback маршруты
    this.defineFallbackRoutes();
  }

  // Определение резервных маршрутов
  defineFallbackRoutes() {
    // Fallback стратегии для критических компонентов
    this.fallbackRoutes.set('odoo-adapter', [
      'standalone-adapter',
      'cache-adapter',
      'mock-adapter'
    ]);

    this.fallbackRoutes.set('ai-services', [
      'local-ai',
      'cached-predictions',
      'rule-based-fallback'
    ]);

    this.fallbackRoutes.set('data-gateway', [
      'cache-layer',
      'read-replicas',
      'backup-storage'
    ]);

    this.fallbackRoutes.set('event-bus', [
      'in-memory-queue',
      'file-based-queue',
      'direct-calls'
    ]);
  }

  // Обнаружение циклических зависимостей
  detectCircularDependencies() {
    const visited = new Set();
    const recursionStack = new Set();
    const cycles = [];

    const dfs = (node, path = []) => {
      visited.add(node);
      recursionStack.add(node);
      path.push(node);

      const deps = this.dependencyGraph.get(node)?.dependencies || new Set();

      for (const dep of deps) {
        if (!visited.has(dep)) {
          dfs(dep, [...path]);
        } else if (recursionStack.has(dep)) {
          // Циклическая зависимость найдена
          const cycleStart = path.indexOf(dep);
          const cycle = path.slice(cycleStart).concat(dep);
          cycles.push(cycle);
          console.warn(`⚠️ Circular dependency detected: ${cycle.join(' -> ')}`);
        }
      }

      recursionStack.delete(node);
    };

    // Проверяем каждый компонент
    for (const component of this.dependencyGraph.keys()) {
      if (!visited.has(component)) {
        dfs(component);
      }
    }

    if (cycles.length > 0) {
      console.warn(`Found ${cycles.length} circular dependencies`);
      // Применяем стратегию разрешения
      this.resolveCircularDependencies(cycles);
    }

    return cycles;
  }

  // Разрешение циклических зависимостей
  resolveCircularDependencies(cycles) {
    for (const cycle of cycles) {
      if (this.resolutionStrategies.circular === 'break') {
        // Разрываем самую слабую связь
        const weakestLink = this.findWeakestLink(cycle);
        if (weakestLink) {
          const [from, to] = weakestLink;
          this.dependencyGraph.get(from).dependencies.delete(to);
          console.log(`Breaking circular dependency: ${from} -> ${to}`);
        }
      }
    }
  }

  // Поиск самой слабой связи в цикле
  findWeakestLink(cycle) {
    let weakestLink = null;
    let minImportance = Infinity;

    for (let i = 0; i < cycle.length - 1; i++) {
      const from = cycle[i];
      const to = cycle[i + 1];

      // Определяем важность связи
      const importance = this.calculateLinkImportance(from, to);

      if (importance < minImportance) {
        minImportance = importance;
        weakestLink = [from, to];
      }
    }

    return weakestLink;
  }

  // Расчет важности связи
  calculateLinkImportance(from, to) {
    // System components более важны
    const fromNode = this.dependencyGraph.get(from);
    const toNode = this.dependencyGraph.get(to);

    let importance = 50;

    if (fromNode?.type === 'system') importance += 30;
    if (toNode?.type === 'system') importance += 30;
    if (fromNode?.type === 'bridge') importance += 20;
    if (toNode?.type === 'bridge') importance += 20;

    // Если есть fallback - связь менее важна
    if (this.fallbackRoutes.has(from)) importance -= 10;
    if (this.fallbackRoutes.has(to)) importance -= 10;

    return importance;
  }

  // Разрешение зависимостей для компонента
  async resolveDependencies(componentName, context = {}) {
    // Проверяем кэш
    const cacheKey = `${componentName}:${JSON.stringify(context)}`;
    if (this.resolutionCache.has(cacheKey)) {
      return this.resolutionCache.get(cacheKey);
    }

    const resolution = {
      component: componentName,
      resolved: [],
      failed: [],
      fallbacks: [],
      order: []
    };

    // Получаем все зависимости (рекурсивно)
    const allDeps = await this.getAllDependencies(componentName);

    // Проверяем доступность каждой зависимости
    for (const dep of allDeps) {
      const health = this.componentHealth.get(dep);

      if (health?.status === 'healthy') {
        resolution.resolved.push(dep);
      } else {
        // Пробуем fallback
        const fallback = await this.findFallback(dep);
        if (fallback) {
          resolution.fallbacks.push({ original: dep, fallback });
          resolution.resolved.push(fallback);
          this.stats.fallbacksUsed++;
        } else {
          resolution.failed.push(dep);
        }
      }
    }

    // Определяем порядок инициализации (топологическая сортировка)
    resolution.order = this.topologicalSort(resolution.resolved);

    // Кэшируем результат
    this.resolutionCache.set(cacheKey, resolution);

    return resolution;
  }

  // Получение всех зависимостей (рекурсивно)
  async getAllDependencies(componentName, visited = new Set()) {
    if (visited.has(componentName)) {
      return [];
    }

    visited.add(componentName);
    const deps = [];

    const node = this.dependencyGraph.get(componentName);
    if (node) {
      for (const dep of node.dependencies) {
        deps.push(dep);
        const subDeps = await this.getAllDependencies(dep, visited);
        deps.push(...subDeps);
      }
    }

    return [...new Set(deps)]; // Уникальные зависимости
  }

  // Топологическая сортировка
  topologicalSort(components) {
    const sorted = [];
    const visited = new Set();

    const visit = (component) => {
      if (visited.has(component)) return;

      visited.add(component);

      const node = this.dependencyGraph.get(component);
      if (node) {
        for (const dep of node.dependencies) {
          if (components.includes(dep)) {
            visit(dep);
          }
        }
      }

      sorted.push(component);
    };

    for (const component of components) {
      visit(component);
    }

    return sorted;
  }

  // Поиск fallback для компонента
  async findFallback(componentName) {
    const fallbacks = this.fallbackRoutes.get(componentName) || [];

    for (const fallback of fallbacks) {
      // Проверяем доступность fallback
      const health = await this.checkComponentHealth(fallback);
      if (health.status === 'healthy') {
        console.log(`✅ Using fallback ${fallback} for ${componentName}`);
        return fallback;
      }
    }

    return null;
  }

  // Проверка здоровья компонента
  async checkComponentHealth(componentName) {
    // Симуляция проверки здоровья
    // В реальности здесь должен быть HTTP health check или другая проверка

    const node = this.dependencyGraph.get(componentName);
    const isHealthy = Math.random() > 0.1; // 90% healthy для демо

    const health = {
      status: isHealthy ? 'healthy' : 'unhealthy',
      lastCheck: new Date(),
      responseTime: Math.floor(Math.random() * 100),
      metrics: {
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        requests: Math.floor(Math.random() * 1000)
      }
    };

    if (isHealthy) {
      this.stats.healthyComponents++;
    } else {
      this.stats.failedComponents++;
    }

    return health;
  }

  // Получение версии компонента
  async getComponentVersion(componentName) {
    // Симуляция получения версии
    return {
      current: '1.0.0',
      available: ['1.0.0', '1.1.0', '2.0.0'],
      compatible: ['1.0.0', '1.1.0']
    };
  }

  // Мониторинг здоровья компонентов
  startHealthMonitoring() {
    setInterval(async () => {
      for (const component of this.dependencyGraph.keys()) {
        const health = await this.checkComponentHealth(component);
        this.componentHealth.set(component, health);

        // Обновляем статус в графе
        const node = this.dependencyGraph.get(component);
        if (node) {
          node.status = health.status;
        }
      }

      // Очищаем кэш разрешений если что-то изменилось
      this.resolutionCache.clear();
    }, this.config.scanInterval || 60000);
  }

  // Получение статистики
  getStats() {
    return {
      ...this.stats,
      cacheSize: this.resolutionCache.size,
      fallbackRoutes: this.fallbackRoutes.size,
      dependencyGraph: {
        nodes: this.dependencyGraph.size,
        edges: Array.from(this.dependencyGraph.values())
          .reduce((sum, node) => sum + node.dependencies.size, 0)
      }
    };
  }

  // Визуализация графа зависимостей
  exportGraph() {
    const nodes = [];
    const edges = [];

    for (const [name, node] of this.dependencyGraph) {
      nodes.push({
        id: name,
        label: name,
        type: node.type,
        status: node.status
      });

      for (const dep of node.dependencies) {
        edges.push({
          from: name,
          to: dep
        });
      }
    }

    return { nodes, edges };
  }

  // Health check
  async healthCheck() {
    const healthy = this.stats.healthyComponents;
    const total = this.stats.totalComponents;
    const ratio = total > 0 ? healthy / total : 0;

    return {
      status: ratio > 0.8 ? 'healthy' : ratio > 0.5 ? 'degraded' : 'unhealthy',
      healthyComponents: healthy,
      totalComponents: total,
      fallbacksActive: this.stats.fallbacksUsed,
      stats: this.getStats()
    };
  }
}

module.exports = DependencyCoordinator;