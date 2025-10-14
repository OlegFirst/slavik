// Module Wrapper - обертка для любых модулей чтобы они работали с системой

class ModuleWrapper {
  constructor(module, bridge) {
    this.module = module;
    this.bridge = bridge;
    this.name = module.name || 'unknown_module';
    this.version = module.version || '1.0.0';
    this.status = 'initialized';
  }

  // Оборачиваем модуль для работы с системой
  async wrap() {
    const wrappedModule = {
      // Метаданные
      id: this.generateModuleId(),
      name: this.name,
      version: this.version,
      type: this.detectModuleType(),

      // Жизненный цикл
      start: async () => {
        this.status = 'starting';

        // Регистрируем в системе
        await this.bridge.registerModule(this.getModuleConfig());

        // Инициализируем модуль
        if (this.module.init) await this.module.init();

        // Подписываемся на события
        this.subscribeToEvents();

        this.status = 'running';
        return true;
      },

      stop: async () => {
        this.status = 'stopping';

        // Отписываемся от событий
        this.unsubscribeFromEvents();

        // Останавливаем модуль
        if (this.module.shutdown) await this.module.shutdown();

        // Дерегистрируем из системы
        await this.bridge.deregisterModule(this.name);

        this.status = 'stopped';
        return true;
      },

      // Интерфейсы
      handleEvent: async (event) => {
        // Транслируем системное событие в модульное
        const moduleEvent = await this.bridge.translateEvent(event, this.name);

        if (this.module.handleEvent) {
          return await this.module.handleEvent(moduleEvent);
        }
      },

      executeAction: async (action, params) => {
        // Валидируем действие
        const validation = await this.bridge.validateAction(action, this.name);
        if (!validation.valid) throw new Error(validation.error);

        // Выполняем действие модуля
        if (this.module[action]) {
          const result = await this.module[action](params);

          // Логируем для обучения
          await this.bridge.logExecution(this.name, action, params, result);

          return result;
        }

        throw new Error(`Action ${action} not found in module ${this.name}`);
      },

      // Данные
      getData: async (query) => {
        if (this.module.query) {
          return await this.module.query(query);
        }
        return null;
      },

      saveData: async (data) => {
        if (this.module.save) {
          return await this.module.save(data);
        }
        return null;
      }
    };

    return wrappedModule;
  }

  // Генерация уникального ID модуля
  generateModuleId() {
    return `${this.name}_${this.version}_${Date.now()}`;
  }

  // Определение типа модуля
  detectModuleType() {
    if (this.name.includes('bcm')) return 'business_continuity';
    if (this.name.includes('risk')) return 'risk_management';
    if (this.name.includes('incident')) return 'incident_management';
    if (this.name.includes('cyber')) return 'cybersecurity';
    return 'general';
  }

  // Получение конфигурации модуля
  getModuleConfig() {
    return {
      name: this.name,
      version: this.version,
      type: this.detectModuleType(),
      capabilities: this.detectCapabilities(),
      requirements: this.detectRequirements(),
      events: this.detectEvents()
    };
  }

  // Определение возможностей модуля
  detectCapabilities() {
    const capabilities = [];

    if (this.module.assess) capabilities.push('assessment');
    if (this.module.analyze) capabilities.push('analysis');
    if (this.module.predict) capabilities.push('prediction');
    if (this.module.report) capabilities.push('reporting');
    if (this.module.workflow) capabilities.push('workflow');

    return capabilities;
  }

  // Определение требований модуля
  detectRequirements() {
    return {
      database: this.module.requiresDB !== false,
      events: this.module.requiresEvents !== false,
      ai: this.module.requiresAI === true,
      storage: this.module.requiresStorage === true
    };
  }

  // Определение событий модуля
  detectEvents() {
    return {
      subscribes: this.module.subscribes || [],
      publishes: this.module.publishes || []
    };
  }

  // Подписка на события
  subscribeToEvents() {
    const events = this.module.subscribes || [];

    for (const eventPattern of events) {
      this.bridge.subscribe(eventPattern, async (event) => {
        await this.handleEvent(event);
      });
    }
  }

  // Отписка от событий
  unsubscribeFromEvents() {
    const events = this.module.subscribes || [];

    for (const eventPattern of events) {
      this.bridge.unsubscribe(eventPattern);
    }
  }
}

module.exports = ModuleWrapper;