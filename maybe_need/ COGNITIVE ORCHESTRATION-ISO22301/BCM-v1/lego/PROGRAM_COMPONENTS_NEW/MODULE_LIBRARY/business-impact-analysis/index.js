// Business Impact Analysis Module - Universal wrapper для BIA функциональности

class BusinessImpactAnalysisModule {
  constructor(config = {}) {
    this.name = 'business-impact-analysis';
    this.version = '1.0.0';
    this.capabilities = [
      'assess_business_impact',
      'map_process_dependencies',
      'calculate_rto_rpo',
      'generate_bia_reports',
      'risk_impact_correlation'
    ];

    // Адаптеры для разных источников
    this.adapters = {
      odoo: null,      // Будет подключен через Odoo Adapter
      standalone: null  // Будет подключен через Standalone Adapter
    };

    this.config = config;
  }

  // Регистрация адаптеров через Integration Layer
  async registerAdapters(integrationLayer) {
    // Подключаем Odoo модуль bcm_bia
    this.adapters.odoo = await integrationLayer.getAdapter('odoo').registerModule({
      odoo_module_name: 'bcm_bia',
      system_module_alias: 'business-impact-analysis',
      capabilities: this.capabilities,
      models: ['bcm.bia.assessment', 'bcm.bia.dependency', 'bcm.bia.impact'],
      endpoints: ['/api/bia/assess', '/api/bia/dependencies']
    });

    // Подключаем standalone BIA engine (если есть)
    try {
      this.adapters.standalone = await integrationLayer.getAdapter('standalone').registerService({
        service_name: 'bia-engine',
        system_module_alias: 'business-impact-analysis',
        api_base: 'http://bia-engine:8080',
        capabilities: ['advanced_modeling', 'simulation', 'what_if_analysis']
      });
    } catch (error) {
      console.log('Standalone BIA engine not available:', error.message);
    }
  }

  // Основной API - оценка воздействия на бизнес
  async assessBusinessImpact(requestData, context = {}) {
    const {
      process_id,
      disruption_scenarios,
      assessment_depth = 'standard',
      user_context = {}
    } = requestData;

    // Выбираем оптимальный адаптер
    const adapter = this.selectBestAdapter(requestData, context);

    try {
      // Формируем запрос для выбранного адаптера
      const adapterRequest = await this.transformRequest(requestData, adapter, context);

      // Выполняем оценку через выбранный адаптер
      const rawResult = await adapter.api.execute('assess_business_impact', adapterRequest);

      // Преобразуем результат в универсальный формат
      const systemResult = await this.transformResult(rawResult, adapter, context);

      // Персонализируем результат для пользователя
      const personalizedResult = await this.personalizeResult(systemResult, user_context);

      return {
        success: true,
        result: personalizedResult,
        metadata: {
          adapter_used: adapter.system_alias,
          assessment_date: new Date(),
          confidence_score: this.calculateConfidence(systemResult, context),
          processing_time: Date.now() - context.start_time
        }
      };

    } catch (error) {
      return {
        success: false,
        error: error.message,
        fallback_available: this.hasFallbackAdapter(adapter)
      };
    }
  }

  // Картирование зависимостей процессов
  async mapProcessDependencies(requestData, context = {}) {
    const {
      process_ids,
      dependency_depth = 3,
      include_external = true
    } = requestData;

    // Используем Odoo адаптер для картирования (он имеет полную модель данных)
    const adapter = this.adapters.odoo;

    if (!adapter) {
      throw new Error('Odoo adapter required for dependency mapping');
    }

    const dependencyMap = await adapter.api.execute('map_dependencies', {
      process_ids,
      max_depth: dependency_depth,
      include_external_dependencies: include_external
    });

    // Обогащаем зависимости дополнительными данными
    const enrichedMap = await this.enrichDependencies(dependencyMap, context);

    return {
      process_dependencies: enrichedMap,
      dependency_matrix: this.buildDependencyMatrix(enrichedMap),
      critical_paths: this.identifyCriticalPaths(enrichedMap),
      vulnerability_points: this.identifyVulnerabilities(enrichedMap)
    };
  }

  // Расчет RTO/RPO
  async calculateRtoRpo(requestData, context = {}) {
    const {
      process_id,
      business_scenarios,
      recovery_strategies
    } = requestData;

    // Комбинируем данные из разных адаптеров если доступно
    const results = {};

    // Базовый расчет через Odoo
    if (this.adapters.odoo) {
      results.standard = await this.adapters.odoo.api.execute('calculate_rto_rpo', {
        process_id,
        scenarios: business_scenarios
      });
    }

    // Продвинутый расчет через standalone engine
    if (this.adapters.standalone) {
      results.advanced = await this.adapters.standalone.api.execute('simulate_recovery', {
        process_id,
        scenarios: business_scenarios,
        strategies: recovery_strategies
      });
    }

    // Объединяем результаты
    return this.consolidateRtoRpoResults(results, context);
  }

  // Генерация отчетов BIA
  async generateBiaReports(requestData, context = {}) {
    const {
      scope,
      report_type = 'comprehensive',
      format = 'pdf',
      user_context = {}
    } = requestData;

    // Собираем данные для отчета
    const reportData = await this.gatherReportData(scope, context);

    // Персонализируем отчет
    const personalizedData = await this.personalizeReport(reportData, user_context);

    // Генерируем отчет через соответствующий адаптер
    const adapter = this.selectReportAdapter(report_type, format);

    return await adapter.api.execute('generate_report', {
      data: personalizedData,
      template: report_type,
      format: format,
      personalization: user_context
    });
  }

  // Корреляция рисков и воздействий
  async correlateRiskImpact(requestData, context = {}) {
    const {
      risk_scenarios,
      business_processes,
      correlation_method = 'statistical'
    } = requestData;

    // Используем AI возможности для корреляции
    const adapter = this.selectBestAdapter(requestData, context);

    const correlations = await adapter.api.execute('correlate_risk_impact', {
      risks: risk_scenarios,
      processes: business_processes,
      method: correlation_method,
      ai_enhanced: true
    });

    return {
      correlations: correlations,
      impact_heatmap: this.buildImpactHeatmap(correlations),
      risk_priorities: this.calculateRiskPriorities(correlations),
      mitigation_recommendations: await this.generateMitigationRecommendations(correlations, context)
    };
  }

  // Выбор оптимального адаптера
  selectBestAdapter(requestData, context) {
    // Если нужны продвинутые симуляции - используем standalone
    if (requestData.simulation_required && this.adapters.standalone) {
      return this.adapters.standalone;
    }

    // Если нужны данные из моделей Odoo - используем Odoo
    if (requestData.requires_odoo_data || !this.adapters.standalone) {
      return this.adapters.odoo;
    }

    // По умолчанию Odoo (более надежный)
    return this.adapters.odoo;
  }

  // Трансформация запроса для адаптера
  async transformRequest(requestData, adapter, context) {
    switch (adapter.system_alias) {
      case 'odoo':
        return this.transformToOdooFormat(requestData, context);
      case 'standalone':
        return this.transformToStandaloneFormat(requestData, context);
      default:
        return requestData;
    }
  }

  // Персонализация результата
  async personalizeResult(result, userContext) {
    // Адаптируем под роль пользователя
    if (userContext.role === 'executive') {
      return this.createExecutiveSummary(result);
    } else if (userContext.role === 'analyst') {
      return this.createDetailedAnalysis(result);
    }

    return result;
  }

  // Расчет уверенности в результате
  calculateConfidence(result, context) {
    let confidence = 0.7; // Базовая уверенность

    // Увеличиваем если есть исторические данные
    if (context.historical_data && context.historical_data.length > 5) {
      confidence += 0.2;
    }

    // Увеличиваем если использовались multiple adapters
    if (this.adapters.odoo && this.adapters.standalone) {
      confidence += 0.1;
    }

    return Math.min(0.95, confidence);
  }

  // API для получения доступных методов
  getAvailableMethods() {
    return {
      assessment_methods: ['standard', 'detailed', 'simulation_based'],
      report_formats: ['pdf', 'html', 'excel', 'json'],
      dependency_types: ['direct', 'indirect', 'circular', 'external'],
      capabilities: this.capabilities,
      adapters_status: {
        odoo: !!this.adapters.odoo,
        standalone: !!this.adapters.standalone
      }
    };
  }
}

module.exports = BusinessImpactAnalysisModule;