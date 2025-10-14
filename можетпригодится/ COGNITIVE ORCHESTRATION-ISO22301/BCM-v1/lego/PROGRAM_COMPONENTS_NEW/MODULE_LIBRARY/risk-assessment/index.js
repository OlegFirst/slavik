// Universal Risk Assessment Module - пассивный модуль для оценки любых рисков

class RiskAssessmentModule {
  constructor() {
    this.name = 'risk-assessment';
    this.version = '1.0.0';
    this.capabilities = [
      'assess_probability',
      'assess_impact',
      'calculate_risk_score',
      'generate_risk_matrix',
      'recommend_mitigation'
    ];

    // Модуль ПАССИВЕН - не имеет собственного состояния
    // Все данные передаются в параметрах
  }

  // Основной API модуля - оценка риска
  async assess(riskData, context = {}) {
    const {
      risk_description,
      risk_category,
      domain = 'general',
      assessment_method = 'qualitative_matrix',
      custom_scales = null
    } = riskData;

    // Получаем конфигурацию для домена
    const domainConfig = this.getDomainConfig(domain);

    // Выбираем шкалы оценки
    const scales = custom_scales || domainConfig.scales;

    // Оцениваем вероятность
    const probability = await this.assessProbability(riskData, scales, context);

    // Оцениваем воздействие
    const impact = await this.assessImpact(riskData, scales, context);

    // Рассчитываем итоговый риск
    const riskScore = this.calculateRiskScore(probability, impact, assessment_method);

    // Определяем уровень риска
    const riskLevel = this.determineRiskLevel(riskScore, scales);

    // Генерируем рекомендации
    const recommendations = await this.generateRecommendations(
      riskScore, riskLevel, riskData, context
    );

    return {
      risk_score: riskScore,
      probability_rating: probability.rating,
      probability_score: probability.score,
      impact_rating: impact.rating,
      impact_score: impact.score,
      risk_level: riskLevel,
      confidence_score: this.calculateConfidence(probability, impact, context),
      assessment_method: assessment_method,
      recommendations: recommendations,
      assessment_date: new Date(),
      context_used: this.summarizeContext(context)
    };
  }

  // Массовая оценка рисков
  async bulkAssess(risksArray, context = {}) {
    const results = [];

    for (const riskData of risksArray) {
      try {
        const assessment = await this.assess(riskData, context);
        results.push({
          id: riskData.id || `risk_${Date.now()}`,
          status: 'success',
          assessment
        });
      } catch (error) {
        results.push({
          id: riskData.id || `risk_${Date.now()}`,
          status: 'error',
          error: error.message
        });
      }
    }

    return {
      total: risksArray.length,
      successful: results.filter(r => r.status === 'success').length,
      failed: results.filter(r => r.status === 'error').length,
      results
    };
  }

  // Оценка вероятности
  async assessProbability(riskData, scales, context) {
    const factors = this.extractProbabilityFactors(riskData, context);

    // Используем разные методы в зависимости от доступных данных
    if (context.historical_data && context.historical_data.length > 0) {
      return this.assessProbabilityHistorical(factors, context.historical_data, scales);
    } else if (context.expert_judgment) {
      return this.assessProbabilityExpert(factors, context.expert_judgment, scales);
    } else {
      return this.assessProbabilityQualitative(factors, scales);
    }
  }

  // Историческая оценка вероятности
  assessProbabilityHistorical(factors, historicalData, scales) {
    // Анализируем исторические данные
    const similarEvents = historicalData.filter(event =>
      this.calculateSimilarity(factors, event.factors) > 0.7
    );

    if (similarEvents.length > 0) {
      const frequency = similarEvents.length / historicalData.length;
      const avgInterval = this.calculateAverageInterval(similarEvents);

      return {
        score: frequency,
        rating: this.mapToScale(frequency, scales.probability),
        method: 'historical_analysis',
        confidence: Math.min(0.9, similarEvents.length / 10),
        details: {
          similar_events: similarEvents.length,
          average_interval: avgInterval,
          trend: this.calculateTrend(similarEvents)
        }
      };
    }

    // Fallback к качественной оценке
    return this.assessProbabilityQualitative(factors, scales);
  }

  // Оценка воздействия
  async assessImpact(riskData, scales, context) {
    const impactCategories = this.getImpactCategories(context.domain || 'general');
    const impactAssessments = {};

    // Оцениваем воздействие по каждой категории
    for (const category of impactCategories) {
      impactAssessments[category] = this.assessCategoryImpact(
        riskData, category, scales, context
      );
    }

    // Вычисляем общее воздействие
    const totalImpact = this.aggregateImpacts(impactAssessments, scales);

    return {
      score: totalImpact.score,
      rating: totalImpact.rating,
      breakdown: impactAssessments,
      method: 'multi_category_assessment',
      confidence: this.calculateImpactConfidence(impactAssessments)
    };
  }

  // Расчет итогового риска
  calculateRiskScore(probability, impact, method = 'multiplication') {
    switch (method) {
      case 'multiplication':
        return probability.score * impact.score;

      case 'weighted_average':
        return (probability.score * 0.4) + (impact.score * 0.6);

      case 'geometric_mean':
        return Math.sqrt(probability.score * impact.score);

      case 'maximum':
        return Math.max(probability.score, impact.score);

      default:
        return probability.score * impact.score;
    }
  }

  // Генерация рекомендаций
  async generateRecommendations(riskScore, riskLevel, riskData, context) {
    const recommendations = [];

    // Базовые рекомендации по уровню риска
    const baseRecs = this.getBaseRecommendations(riskLevel);
    recommendations.push(...baseRecs);

    // Специфичные для домена рекомендации
    const domainRecs = this.getDomainSpecificRecommendations(
      riskData, context.domain, riskScore
    );
    recommendations.push(...domainRecs);

    // Контекстуальные рекомендации
    if (context.user_context) {
      const contextRecs = this.getContextualRecommendations(
        riskScore, context.user_context
      );
      recommendations.push(...contextRecs);
    }

    // Приоритизируем рекомендации
    return this.prioritizeRecommendations(recommendations, riskScore, context);
  }

  // Конфигурации для разных доменов
  getDomainConfig(domain) {
    const configs = {
      business_continuity: {
        scales: {
          probability: {
            'very_low': { min: 0, max: 0.1, label: 'Very Unlikely' },
            'low': { min: 0.1, max: 0.3, label: 'Unlikely' },
            'medium': { min: 0.3, max: 0.7, label: 'Possible' },
            'high': { min: 0.7, max: 0.9, label: 'Likely' },
            'very_high': { min: 0.9, max: 1.0, label: 'Very Likely' }
          },
          impact: {
            'very_low': { min: 0, max: 0.2, label: 'Minimal' },
            'low': { min: 0.2, max: 0.4, label: 'Minor' },
            'medium': { min: 0.4, max: 0.6, label: 'Moderate' },
            'high': { min: 0.6, max: 0.8, label: 'Major' },
            'very_high': { min: 0.8, max: 1.0, label: 'Catastrophic' }
          }
        },
        impact_categories: ['financial', 'operational', 'reputational', 'compliance']
      },

      cybersecurity: {
        scales: {
          probability: {
            'very_low': { min: 0, max: 0.15, label: 'Very Rare' },
            'low': { min: 0.15, max: 0.35, label: 'Rare' },
            'medium': { min: 0.35, max: 0.65, label: 'Occasional' },
            'high': { min: 0.65, max: 0.85, label: 'Frequent' },
            'very_high': { min: 0.85, max: 1.0, label: 'Very Frequent' }
          },
          impact: {
            'very_low': { min: 0, max: 0.2, label: 'Negligible' },
            'low': { min: 0.2, max: 0.4, label: 'Limited' },
            'medium': { min: 0.4, max: 0.6, label: 'Serious' },
            'high': { min: 0.6, max: 0.8, label: 'Severe' },
            'very_high': { min: 0.8, max: 1.0, label: 'Critical' }
          }
        },
        impact_categories: ['confidentiality', 'integrity', 'availability', 'privacy']
      },

      general: {
        scales: {
          probability: {
            'very_low': { min: 0, max: 0.2, label: 'Very Low' },
            'low': { min: 0.2, max: 0.4, label: 'Low' },
            'medium': { min: 0.4, max: 0.6, label: 'Medium' },
            'high': { min: 0.6, max: 0.8, label: 'High' },
            'very_high': { min: 0.8, max: 1.0, label: 'Very High' }
          },
          impact: {
            'very_low': { min: 0, max: 0.2, label: 'Very Low' },
            'low': { min: 0.2, max: 0.4, label: 'Low' },
            'medium': { min: 0.4, max: 0.6, label: 'Medium' },
            'high': { min: 0.6, max: 0.8, label: 'High' },
            'very_high': { min: 0.8, max: 1.0, label: 'Very High' }
          }
        },
        impact_categories: ['financial', 'operational', 'strategic', 'reputational']
      }
    };

    return configs[domain] || configs.general;
  }

  // Определение уровня риска
  determineRiskLevel(riskScore, scales) {
    if (riskScore >= 0.8) return 'critical';
    if (riskScore >= 0.6) return 'high';
    if (riskScore >= 0.4) return 'medium';
    if (riskScore >= 0.2) return 'low';
    return 'very_low';
  }

  // Расчет уверенности в оценке
  calculateConfidence(probability, impact, context) {
    let confidence = 0.5; // Базовая уверенность

    // Увеличиваем уверенность если есть исторические данные
    if (context.historical_data && context.historical_data.length > 10) {
      confidence += 0.2;
    }

    // Увеличиваем уверенность если есть экспертная оценка
    if (context.expert_judgment) {
      confidence += 0.1;
    }

    // Увеличиваем уверенность если оценки согласованы
    if (Math.abs(probability.confidence - impact.confidence) < 0.2) {
      confidence += 0.1;
    }

    // Снижаем уверенность если данных мало
    if (!context.historical_data || context.historical_data.length < 3) {
      confidence -= 0.2;
    }

    return Math.max(0.1, Math.min(0.9, confidence));
  }

  // API для получения доступных методов
  getMethods() {
    return {
      assessment_methods: [
        'qualitative_matrix',
        'quantitative_scoring',
        'monte_carlo',
        'historical_analysis',
        'expert_judgment'
      ],
      domains: [
        'business_continuity',
        'cybersecurity',
        'financial',
        'operational',
        'strategic',
        'compliance'
      ],
      capabilities: this.capabilities
    };
  }

  // Симуляция сценариев
  async simulate(riskData, scenarios, context = {}) {
    const results = [];

    for (const scenario of scenarios) {
      // Модифицируем данные риска согласно сценарию
      const modifiedRisk = this.applyScenario(riskData, scenario);

      // Оцениваем риск в этом сценарии
      const assessment = await this.assess(modifiedRisk, context);

      results.push({
        scenario: scenario.name,
        modifications: scenario.modifications,
        assessment: assessment,
        comparison: this.compareWithBaseline(assessment, riskData.baseline)
      });
    }

    return {
      base_scenario: riskData,
      scenario_results: results,
      summary: this.summarizeScenarios(results)
    };
  }
}

module.exports = RiskAssessmentModule;