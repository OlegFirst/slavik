// Config Bridge - адаптирует системную конфигурацию для модулей

class ConfigBridge {
  constructor() {
    this.systemConfig = {};
    this.moduleConfigs = new Map();
    this.environmentMappings = {
      development: 'dev',
      staging: 'test',
      production: 'prod'
    };
  }

  // Адаптация системной конфигурации для BCM модуля
  adaptForModule(systemConfig, moduleName) {
    const moduleConfig = {
      // Базовые настройки из системы
      database: {
        host: systemConfig.db.host,
        port: systemConfig.db.port,
        name: `${systemConfig.db.prefix}_${moduleName}`,
        schema: moduleName.toLowerCase()
      },

      // Настройки событий для модуля
      events: {
        prefix: `${moduleName}.`,
        queue: systemConfig.messageQueue.url,
        topics: this.generateModuleTopics(moduleName)
      },

      // Настройки AI для модуля
      ai: {
        endpoint: systemConfig.ai.endpoint,
        models: this.selectModelsForModule(moduleName),
        context: this.generateAIContext(moduleName)
      },

      // Специфичные для модуля
      features: this.getModuleFeatures(moduleName),
      limits: this.getModuleLimits(moduleName),

      environment: this.environmentMappings[systemConfig.env] || 'dev'
    };

    this.moduleConfigs.set(moduleName, moduleConfig);
    return moduleConfig;
  }

  // Генерация топиков событий для модуля
  generateModuleTopics(moduleName) {
    const baseTopics = ['created', 'updated', 'deleted', 'processed'];

    if (moduleName === 'bcm_risk') {
      return [...baseTopics, 'risk.assessed', 'risk.mitigated', 'risk.escalated'];
    }

    if (moduleName === 'bcm_incident') {
      return [...baseTopics, 'incident.reported', 'incident.resolved', 'incident.escalated'];
    }

    return baseTopics;
  }

  // Выбор AI моделей для модуля
  selectModelsForModule(moduleName) {
    const models = [];

    if (moduleName.includes('risk')) {
      models.push('risk_prediction', 'impact_analysis');
    }

    if (moduleName.includes('incident')) {
      models.push('incident_classifier', 'response_recommender');
    }

    models.push('general_nlp', 'pattern_detector');
    return models;
  }

  // Генерация AI контекста
  generateAIContext(moduleName) {
    return {
      domain: 'business_continuity',
      module: moduleName,
      standards: ['ISO22301', 'ISO27031'],
      language: 'en',
      industryContext: this.systemConfig.industry || 'general'
    };
  }

  // Получение функций модуля
  getModuleFeatures(moduleName) {
    const features = {
      bcm_risk: ['assessment', 'matrix', 'heatmap', 'reporting', 'ai_prediction'],
      bcm_incident: ['reporting', 'tracking', 'escalation', 'communication'],
      bcm_bia: ['impact_analysis', 'dependency_mapping', 'rto_rpo'],
      bcm_exercise: ['scenario_planning', 'execution', 'evaluation']
    };

    return features[moduleName] || ['basic'];
  }

  // Получение лимитов для модуля
  getModuleLimits(moduleName) {
    return {
      maxRecords: 100000,
      maxFileSize: '10MB',
      apiRateLimit: 1000,
      concurrentUsers: 100,
      dataRetention: 365 // days
    };
  }

  // Валидация конфигурации модуля
  validateModuleConfig(moduleName) {
    const config = this.moduleConfigs.get(moduleName);
    if (!config) return { valid: false, errors: ['Module not configured'] };

    const errors = [];

    if (!config.database.host) errors.push('Database host missing');
    if (!config.events.queue) errors.push('Event queue missing');
    if (config.features.length === 0) errors.push('No features enabled');

    return {
      valid: errors.length === 0,
      errors
    };
  }

  // Hot reload конфигурации
  updateModuleConfig(moduleName, updates) {
    const currentConfig = this.moduleConfigs.get(moduleName);
    if (!currentConfig) return null;

    const updatedConfig = { ...currentConfig, ...updates };
    this.moduleConfigs.set(moduleName, updatedConfig);

    // Emit событие об изменении конфигурации
    this.emit('config:updated', {
      module: moduleName,
      changes: updates
    });

    return updatedConfig;
  }
}

module.exports = ConfigBridge;