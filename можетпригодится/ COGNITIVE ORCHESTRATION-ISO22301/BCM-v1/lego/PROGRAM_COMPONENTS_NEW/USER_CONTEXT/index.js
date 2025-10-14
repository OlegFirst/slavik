// USER_CONTEXT - персонализированный контекст пользователя для интеллектуальных решений

class UserContextManager {
  constructor() {
    this.userProfiles = new Map();
    this.organizationTwins = new Map();
    this.behaviorPatterns = new Map();
    this.preferences = new Map();
  }

  // Создание и управление Digital Twin организации пользователя
  async createOrganizationTwin(userId, orgData) {
    const twin = {
      id: `org_twin_${userId}`,
      organization: {
        name: orgData.name,
        industry: orgData.industry,
        size: orgData.size,
        locations: orgData.locations,
        critical_processes: orgData.processes,
        dependencies: orgData.dependencies,
        risk_appetite: orgData.riskAppetite
      },

      // Динамические характеристики
      current_state: {
        operational_status: 'normal',
        active_incidents: [],
        risk_levels: {},
        performance_metrics: {},
        last_updated: new Date()
      },

      // Исторические данные для AI
      historical_data: {
        incidents: [],
        risk_assessments: [],
        exercise_results: [],
        performance_trends: []
      },

      // AI модели специфичные для организации
      ai_models: {
        risk_predictor: null,
        incident_classifier: null,
        performance_forecaster: null
      }
    };

    this.organizationTwins.set(userId, twin);
    return twin;
  }

  // Профиль пользователя с контекстом
  async buildUserProfile(userId, userData) {
    const profile = {
      basic: {
        id: userId,
        name: userData.name,
        role: userData.role,
        department: userData.department,
        experience_level: userData.experienceLevel
      },

      // Контекст работы
      work_context: {
        responsibilities: userData.responsibilities,
        decision_authority: userData.authority,
        typical_tasks: userData.tasks,
        work_patterns: await this.analyzeWorkPatterns(userId)
      },

      // BCM специфичный контекст
      bcm_context: {
        certification_level: userData.bcmCertification,
        areas_of_expertise: userData.expertise,
        training_history: userData.training,
        previous_incidents: userData.incidentHistory
      },

      // Персональные настройки
      preferences: {
        communication_style: userData.commStyle || 'detailed',
        notification_frequency: userData.notifFreq || 'normal',
        dashboard_layout: userData.dashboardPrefs,
        report_formats: userData.reportPrefs
      },

      // Адаптивные характеристики (обучаются на основе поведения)
      adaptive: {
        learning_style: 'visual', // visual, text, interactive
        decision_speed: 'deliberate', // quick, deliberate, consultative
        risk_tolerance: 'moderate', // low, moderate, high
        detail_preference: 'comprehensive' // summary, balanced, comprehensive
      }
    };

    this.userProfiles.set(userId, profile);
    return profile;
  }

  // Анализ паттернов поведения пользователя
  async analyzeWorkPatterns(userId) {
    const behaviors = this.behaviorPatterns.get(userId) || [];

    const patterns = {
      peak_activity_hours: this.findPeakHours(behaviors),
      common_workflows: this.identifyWorkflows(behaviors),
      decision_patterns: this.analyzeDecisions(behaviors),
      collaboration_style: this.analyzeCollaboration(behaviors)
    };

    return patterns;
  }

  // Персонализированная выдача результатов
  async personalizeResults(userId, baseResults, context) {
    const userProfile = this.userProfiles.get(userId);
    const orgTwin = this.organizationTwins.get(userId);

    if (!userProfile || !orgTwin) {
      return baseResults; // Возвращаем базовые результаты
    }

    const personalized = {
      // Адаптируем под роль пользователя
      role_specific: this.adaptForRole(baseResults, userProfile.basic.role),

      // Учитываем контекст организации
      org_contextualized: this.addOrgContext(baseResults, orgTwin),

      // Персонализируем презентацию
      presentation: this.customizePresentation(baseResults, userProfile.preferences),

      // Добавляем рекомендации
      recommendations: await this.generatePersonalizedRecommendations(
        baseResults, userProfile, orgTwin, context
      ),

      // Контекстные действия
      suggested_actions: this.suggestActions(baseResults, userProfile, context)
    };

    // Логируем для обучения
    this.logInteraction(userId, baseResults, personalized, context);

    return personalized;
  }

  // Адаптация под роль пользователя
  adaptForRole(results, role) {
    const roleAdaptations = {
      'bcm_manager': {
        focus: ['strategic_overview', 'compliance_status', 'resource_planning'],
        detail_level: 'executive_summary',
        metrics: ['program_maturity', 'risk_trends', 'exercise_effectiveness']
      },

      'risk_analyst': {
        focus: ['risk_details', 'analytical_data', 'trend_analysis'],
        detail_level: 'detailed_analysis',
        metrics: ['risk_scores', 'probability_distributions', 'impact_assessments']
      },

      'incident_coordinator': {
        focus: ['operational_status', 'response_procedures', 'communication'],
        detail_level: 'operational_detail',
        metrics: ['response_times', 'escalation_status', 'resource_allocation']
      },

      'executive': {
        focus: ['business_impact', 'financial_implications', 'strategic_alignment'],
        detail_level: 'high_level_summary',
        metrics: ['business_continuity_score', 'financial_exposure', 'reputation_risk']
      }
    };

    const adaptation = roleAdaptations[role] || roleAdaptations['bcm_manager'];

    return {
      filtered_data: this.filterForRole(results, adaptation.focus),
      summary_level: adaptation.detail_level,
      key_metrics: this.extractMetrics(results, adaptation.metrics),
      role_specific_insights: this.generateRoleInsights(results, role)
    };
  }

  // Добавление контекста организации
  addOrgContext(results, orgTwin) {
    return {
      // Сравнение с историческими данными организации
      historical_comparison: this.compareWithHistory(results, orgTwin.historical_data),

      // Учет специфики индустрии
      industry_benchmarks: this.addIndustryContext(results, orgTwin.organization.industry),

      // Учет размера и сложности организации
      scale_adjustments: this.adjustForScale(results, orgTwin.organization),

      // Текущее состояние организации
      current_state_impact: this.considerCurrentState(results, orgTwin.current_state)
    };
  }

  // Кастомизация презентации
  customizePresentation(results, preferences) {
    return {
      format: this.selectFormat(results, preferences.report_formats),
      visualization: this.createVisualizations(results, preferences.dashboard_layout),
      communication_style: this.adjustCommunicationStyle(results, preferences.communication_style),
      notification_settings: this.configureNotifications(results, preferences.notification_frequency)
    };
  }

  // Генерация персонализированных рекомендаций
  async generatePersonalizedRecommendations(results, userProfile, orgTwin, context) {
    const recommendations = [];

    // На основе роли пользователя
    const roleRecs = this.getRoleSpecificRecommendations(results, userProfile.basic.role);
    recommendations.push(...roleRecs);

    // На основе опыта пользователя
    const experienceRecs = this.getExperienceBasedRecommendations(
      results, userProfile.basic.experience_level
    );
    recommendations.push(...experienceRecs);

    // На основе контекста организации
    const orgRecs = this.getOrganizationalRecommendations(results, orgTwin);
    recommendations.push(...orgRecs);

    // На основе текущего контекста
    const contextRecs = this.getContextualRecommendations(results, context);
    recommendations.push(...contextRecs);

    // Приоритизируем рекомендации
    return this.prioritizeRecommendations(recommendations, userProfile, orgTwin);
  }

  // Предложение действий
  suggestActions(results, userProfile, context) {
    const actions = [];

    // Немедленные действия
    const immediateActions = this.identifyImmediateActions(results, context);
    actions.push(...immediateActions.map(a => ({ ...a, priority: 'immediate' })));

    // Краткосрочные действия
    const shortTermActions = this.identifyShortTermActions(results, userProfile);
    actions.push(...shortTermActions.map(a => ({ ...a, priority: 'short_term' })));

    // Долгосрочные действия
    const longTermActions = this.identifyLongTermActions(results, userProfile);
    actions.push(...longTermActions.map(a => ({ ...a, priority: 'long_term' })));

    return this.personalizeActions(actions, userProfile);
  }

  // Логирование взаимодействий для обучения
  logInteraction(userId, baseResults, personalizedResults, context) {
    const interaction = {
      user_id: userId,
      timestamp: new Date(),
      context: context,
      base_results: this.summarizeResults(baseResults),
      personalization_applied: this.summarizePersonalization(personalizedResults),
      user_reaction: null // Будет обновлено при получении обратной связи
    };

    // Добавляем в паттерны поведения
    if (!this.behaviorPatterns.has(userId)) {
      this.behaviorPatterns.set(userId, []);
    }
    this.behaviorPatterns.get(userId).push(interaction);

    // Ограничиваем размер истории
    const patterns = this.behaviorPatterns.get(userId);
    if (patterns.length > 1000) {
      this.behaviorPatterns.set(userId, patterns.slice(-500));
    }
  }

  // Обновление профиля на основе обратной связи
  async updateProfileFromFeedback(userId, feedback) {
    const profile = this.userProfiles.get(userId);
    if (!profile) return;

    // Обновляем адаптивные характеристики
    if (feedback.detail_preference) {
      profile.adaptive.detail_preference = feedback.detail_preference;
    }

    if (feedback.communication_style) {
      profile.adaptive.learning_style = feedback.communication_style;
    }

    // Обновляем предпочтения
    if (feedback.dashboard_feedback) {
      profile.preferences.dashboard_layout = {
        ...profile.preferences.dashboard_layout,
        ...feedback.dashboard_feedback
      };
    }

    this.userProfiles.set(userId, profile);

    // Обновляем последнее взаимодействие
    const patterns = this.behaviorPatterns.get(userId) || [];
    if (patterns.length > 0) {
      patterns[patterns.length - 1].user_reaction = feedback;
    }
  }

  // Получение контекста для принятия решений
  getDecisionContext(userId, decisionType) {
    const profile = this.userProfiles.get(userId);
    const orgTwin = this.organizationTwins.get(userId);

    if (!profile || !orgTwin) return null;

    return {
      user_authority: profile.work_context.decision_authority,
      org_constraints: orgTwin.organization.risk_appetite,
      historical_decisions: this.getHistoricalDecisions(userId, decisionType),
      current_org_state: orgTwin.current_state,
      stakeholder_considerations: this.getStakeholderContext(userId, decisionType)
    };
  }

  // Адаптивное обучение моделей пользователя
  async adaptUserModels(userId) {
    const patterns = this.behaviorPatterns.get(userId) || [];
    if (patterns.length < 10) return; // Недостаточно данных

    const profile = this.userProfiles.get(userId);

    // Анализируем паттерны предпочтений
    const preferencePatterns = this.analyzePreferencePatterns(patterns);

    // Обновляем адаптивные характеристики
    profile.adaptive = {
      ...profile.adaptive,
      ...preferencePatterns
    };

    // Обновляем модели предсказания для пользователя
    await this.updateUserPredictionModels(userId, patterns);

    this.userProfiles.set(userId, profile);
  }
}

module.exports = UserContextManager;