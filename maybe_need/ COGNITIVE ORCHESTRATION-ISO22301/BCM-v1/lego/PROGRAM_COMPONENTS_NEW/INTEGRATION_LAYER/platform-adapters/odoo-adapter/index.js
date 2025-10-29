// Odoo Adapter - мост между системой и Odoo BCM модулями

const { bcmModulesConfig, transformationRules, monitoringConfig } = require('./bcm-modules-config');

class OdooAdapter {
  constructor(config = {}) {
    this.odooConfig = {
      host: config.odoo_host || 'localhost',
      port: config.odoo_port || 8069,
      database: config.odoo_database || 'bcm_platform',
      username: config.odoo_username || 'admin',
      password: config.odoo_password || 'admin',
      protocol: config.odoo_protocol || 'http'
    };

    this.moduleRegistry = new Map(); // Реестр Odoo модулей
    this.activeConnections = new Map(); // Активные соединения
    this.moduleAliases = new Map(); // Алиасы модулей для системы
    this.bcmConfig = bcmModulesConfig; // BCM модули конфигурация
    this.transformRules = transformationRules; // Правила трансформации
    this.monitoring = monitoringConfig; // Конфигурация мониторинга
  }

  // Регистрация Odoo модуля в системе
  async registerOdooModule(moduleConfig) {
    const {
      odoo_module_name,     // bcm_bia
      system_module_alias,  // business-impact-analysis
      capabilities,         // ['assess_impact', 'map_dependencies']
      models,              // ['bcm.bia.assessment', 'bcm.bia.dependency']
      endpoints,           // ['/api/bia/assess', '/api/bia/dependencies']
      dependencies         // ['bcm_core', 'bcm_base']
    } = moduleConfig;

    // Проверяем доступность модуля в Odoo
    const isAvailable = await this.checkOdooModuleAvailability(odoo_module_name);
    if (!isAvailable) {
      throw new Error(`Odoo module ${odoo_module_name} not available`);
    }

    // Создаем адаптер для модуля
    const adapter = {
      odoo_name: odoo_module_name,
      system_alias: system_module_alias,
      capabilities: capabilities,
      models: models,
      endpoints: endpoints,
      dependencies: dependencies,
      status: 'registered',
      registered_at: new Date(),

      // API методы для работы с модулем
      api: {
        // Выполнение метода модуля
        execute: async (method, params) => {
          return await this.executeOdooMethod(odoo_module_name, method, params);
        },

        // Запрос данных из модуля
        query: async (model, domain = [], fields = []) => {
          return await this.queryOdooModel(model, domain, fields);
        },

        // Создание записи в модуле
        create: async (model, values) => {
          return await this.createOdooRecord(model, values);
        },

        // Обновление записи в модуле
        update: async (model, ids, values) => {
          return await this.updateOdooRecord(model, ids, values);
        },

        // Удаление записи в модуле
        delete: async (model, ids) => {
          return await this.deleteOdooRecord(model, ids);
        }
      }
    };

    this.moduleRegistry.set(system_module_alias, adapter);
    this.moduleAliases.set(odoo_module_name, system_module_alias);

    return adapter;
  }

  // Автоматическая регистрация всех BCM модулей
  async registerAllBcmModules() {
    const registrationResults = [];

    for (const [odooModuleName, config] of Object.entries(this.bcmConfig)) {
      try {
        // Проверяем доступность модуля в Odoo
        const isAvailable = await this.checkOdooModuleAvailability(odooModuleName);

        if (isAvailable) {
          // Регистрируем модуль
          const adapter = await this.registerOdooModule({
            odoo_module_name: odooModuleName,
            system_module_alias: config.system_alias,
            capabilities: config.capabilities,
            models: config.models,
            endpoints: config.endpoints,
            dependencies: config.dependencies,
            bridge_config: config.bridge_integration
          });

          registrationResults.push({
            module: odooModuleName,
            alias: config.system_alias,
            status: 'registered',
            capabilities: config.capabilities.length,
            models: config.models.length
          });

          console.log(`✅ BCM Module registered: ${odooModuleName} -> ${config.system_alias}`);
        } else {
          registrationResults.push({
            module: odooModuleName,
            alias: config.system_alias,
            status: 'not_available',
            error: `Module ${odooModuleName} not found in Odoo`
          });

          console.log(`❌ BCM Module not available: ${odooModuleName}`);
        }
      } catch (error) {
        registrationResults.push({
          module: odooModuleName,
          alias: config.system_alias,
          status: 'error',
          error: error.message
        });

        console.error(`💥 Error registering ${odooModuleName}:`, error.message);
      }
    }

    return {
      total_modules: Object.keys(this.bcmConfig).length,
      registered: registrationResults.filter(r => r.status === 'registered').length,
      failed: registrationResults.filter(r => r.status !== 'registered').length,
      results: registrationResults
    };
  }

  // Выполнение системного запроса через Odoo модуль
  async executeSystemRequest(request) {
    const {
      module_alias,    // 'business-impact-analysis'
      action,          // 'assess_impact'
      data,           // { process_id: 123, criteria: {...} }
      context         // { user_id: 456, org_id: 789 }
    } = request;

    // Получаем адаптер модуля
    const adapter = this.moduleRegistry.get(module_alias);
    if (!adapter) {
      throw new Error(`Module ${module_alias} not registered`);
    }

    // Проверяем поддержку действия
    if (!adapter.capabilities.includes(action)) {
      throw new Error(`Action ${action} not supported by module ${module_alias}`);
    }

    try {
      // Преобразуем системный запрос в Odoo формат
      const odooRequest = await this.transformSystemToOdoo(request, adapter);

      // Устанавливаем контекст Odoo (пользователь, компания, etc)
      await this.setOdooContext(context);

      // Выполняем запрос в Odoo
      const odooResult = await adapter.api.execute(action, odooRequest.data);

      // Преобразуем результат Odoo в системный формат
      const systemResult = await this.transformOdooToSystem(odooResult, adapter);

      return {
        success: true,
        result: systemResult,
        module: module_alias,
        execution_time: new Date(),
        odoo_module: adapter.odoo_name
      };

    } catch (error) {
      return {
        success: false,
        error: error.message,
        module: module_alias,
        execution_time: new Date()
      };
    }
  }

  // Трансформация системного запроса в Odoo формат
  async transformSystemToOdoo(systemRequest, adapter) {
    const { data, context, action } = systemRequest;

    // Ищем правило трансформации для данного модуля и действия
    const moduleRules = this.transformRules.systemToOdoo[adapter.system_alias];

    if (moduleRules && moduleRules[action]) {
      // Используем специфичное правило трансформации
      return moduleRules[action](systemRequest);
    }

    // Базовая трансформация данных
    const odooData = {
      ...data,
      // Добавляем обязательные для Odoo поля
      company_id: context.org_id,
      create_uid: context.user_id,
      write_uid: context.user_id
    };

    // Fallback специфичные трансформации для разных модулей
    switch (adapter.system_alias) {
      case 'business-impact-analysis':
        return this.transformBIARequest(odooData);

      case 'incident-management':
        return this.transformIncidentRequest(odooData);

      case 'risk-assessment':
        return this.transformRiskRequest(odooData);

      default:
        return { data: odooData };
    }
  }

  // Трансформация результата Odoo в системный формат
  async transformOdooToSystem(odooResult, adapter, action) {
    // Ищем правило трансформации для данного модуля и действия
    const moduleRules = this.transformRules.odooToSystem[adapter.system_alias];

    if (moduleRules && moduleRules[action]) {
      // Используем специфичное правило трансформации
      const transformedResult = moduleRules[action](odooResult);

      // Добавляем системные метаданные
      transformedResult._metadata = {
        source: 'odoo',
        module: adapter.odoo_name,
        system_alias: adapter.system_alias,
        processed_at: new Date(),
        transformation_rule: `${adapter.system_alias}.${action}`
      };

      return transformedResult;
    }

    // Убираем Odoo-специфичные поля
    const systemResult = this.removeOdooFields(odooResult);

    // Добавляем системные метаданные
    systemResult._metadata = {
      source: 'odoo',
      module: adapter.odoo_name,
      system_alias: adapter.system_alias,
      processed_at: new Date()
    };

    // Fallback специфичные трансформации для разных модулей
    switch (adapter.system_alias) {
      case 'business-impact-analysis':
        return this.transformBIAResult(systemResult);

      case 'incident-management':
        return this.transformIncidentResult(systemResult);

      default:
        return systemResult;
    }
  }

  // Установка контекста Odoo
  async setOdooContext(context) {
    // Аутентификация пользователя в Odoo
    if (context.user_id) {
      await this.authenticateOdooUser(context.user_id);
    }

    // Установка компании
    if (context.org_id) {
      await this.setOdooCompany(context.org_id);
    }

    // Установка языка
    if (context.language) {
      await this.setOdooLanguage(context.language);
    }
  }

  // Проверка доступности модуля в Odoo
  async checkOdooModuleAvailability(moduleName) {
    try {
      const modules = await this.callOdooAPI('ir.module.module', 'search_read', [
        [['name', '=', moduleName], ['state', '=', 'installed']],
        ['name', 'state']
      ]);

      return modules.length > 0;
    } catch (error) {
      console.error(`Error checking Odoo module ${moduleName}:`, error);
      return false;
    }
  }

  // Выполнение метода Odoo модуля
  async executeOdooMethod(moduleName, method, params) {
    // Находим главную модель модуля
    const mainModel = this.getMainModelForModule(moduleName);

    return await this.callOdooAPI(mainModel, method, params);
  }

  // Запрос к Odoo API
  async callOdooAPI(model, method, params = []) {
    const odooRpc = require('./odoo-rpc-client');

    const client = new odooRpc({
      host: this.odooConfig.host,
      port: this.odooConfig.port,
      database: this.odooConfig.database,
      username: this.odooConfig.username,
      password: this.odooConfig.password,
      protocol: this.odooConfig.protocol
    });

    try {
      await client.connect();
      const result = await client.call(model, method, params);
      return result;
    } finally {
      client.close();
    }
  }

  // Мониторинг состояния Odoo модулей
  async monitorOdooModules() {
    const monitoringResults = [];

    for (const [alias, adapter] of this.moduleRegistry) {
      try {
        // Проверяем доступность модуля
        const isAvailable = await this.checkOdooModuleAvailability(adapter.odoo_name);

        // Проверяем производительность
        const startTime = Date.now();
        await this.callOdooAPI('res.users', 'search_count', [[]]);
        const responseTime = Date.now() - startTime;

        monitoringResults.push({
          alias: alias,
          odoo_module: adapter.odoo_name,
          status: isAvailable ? 'healthy' : 'unavailable',
          response_time: responseTime,
          last_check: new Date()
        });

      } catch (error) {
        monitoringResults.push({
          alias: alias,
          odoo_module: adapter.odoo_name,
          status: 'error',
          error: error.message,
          last_check: new Date()
        });
      }
    }

    return monitoringResults;
  }

  // Синхронизация данных между системой и Odoo
  async syncData(direction = 'bidirectional') {
    const syncResults = [];

    for (const [alias, adapter] of this.moduleRegistry) {
      try {
        let result;

        switch (direction) {
          case 'to_system':
            result = await this.syncOdooToSystem(adapter);
            break;

          case 'to_odoo':
            result = await this.syncSystemToOdoo(adapter);
            break;

          case 'bidirectional':
            const toSystem = await this.syncOdooToSystem(adapter);
            const toOdoo = await this.syncSystemToOdoo(adapter);
            result = { to_system: toSystem, to_odoo: toOdoo };
            break;
        }

        syncResults.push({
          module: alias,
          status: 'success',
          result: result,
          synced_at: new Date()
        });

      } catch (error) {
        syncResults.push({
          module: alias,
          status: 'error',
          error: error.message,
          synced_at: new Date()
        });
      }
    }

    return syncResults;
  }

  // Получение статистики использования
  getUsageStatistics() {
    const stats = {
      registered_modules: this.moduleRegistry.size,
      active_connections: this.activeConnections.size,
      modules: []
    };

    for (const [alias, adapter] of this.moduleRegistry) {
      stats.modules.push({
        alias: alias,
        odoo_module: adapter.odoo_name,
        status: adapter.status,
        capabilities: adapter.capabilities.length,
        registered_at: adapter.registered_at
      });
    }

    return stats;
  }
}

module.exports = OdooAdapter;