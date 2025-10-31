// BCM Modules Configuration for Odoo Adapter

const bcmModulesConfig = {
  // DOMAIN CORE MODULES
  'bcm_core': {
    system_alias: 'bcm-domain-core',
    type: 'domain_foundation',
    capabilities: [
      'organization_context',
      'business_unit_management',
      'stakeholder_management',
      'critical_function_registry',
      'ai_lifecycle_monitoring'
    ],
    models: [
      'bcm.plan',
      'bcm.incident',
      'bcm.business.process',
      'bcm.ai.lifecycle',
      'bcm.stakeholder',
      'bcm.critical.function'
    ],
    endpoints: [
      '/api/bcm/core/context',
      '/api/bcm/core/business-units',
      '/api/bcm/core/stakeholders'
    ],
    dependencies: ['base', 'mail', 'web'],
    bridge_integration: {
      event_mappings: {
        'organization.updated': 'bcm.context.sync',
        'user.role.changed': 'bcm.stakeholder.update',
        'ai.health.check': 'bcm.ai.lifecycle.monitor'
      },
      data_sync: ['organization', 'users', 'business_processes']
    }
  },

  // FUNCTIONAL MODULES
  'bcm_bia': {
    system_alias: 'business-impact-analysis',
    type: 'functional_module',
    capabilities: [
      'assess_business_impact',
      'map_process_dependencies',
      'calculate_rto_rpo',
      'generate_bia_reports'
    ],
    models: [
      'bcm.bia.assessment',
      'bcm.bia.dependency',
      'bcm.bia.impact',
      'bcm.bia.scenario'
    ],
    endpoints: [
      '/api/bia/assess',
      '/api/bia/dependencies',
      '/api/bia/rto-rpo',
      '/api/bia/reports'
    ],
    dependencies: ['bcm_core'],
    bridge_integration: {
      event_mappings: {
        'process.created': 'bia.process.register',
        'process.updated': 'bia.dependency.recalculate',
        'risk.assessed': 'bia.impact.correlate'
      },
      ai_enhancement: true,
      personalization: ['role_based_views', 'industry_templates']
    }
  },

  'bcm_incident': {
    system_alias: 'incident-management',
    type: 'functional_module',
    capabilities: [
      'incident_reporting',
      'incident_response',
      'escalation_management',
      'communication_coordination'
    ],
    models: [
      'bcm.incident',
      'bcm.incident.response',
      'bcm.incident.communication',
      'bcm.incident.escalation'
    ],
    endpoints: [
      '/api/incident/report',
      '/api/incident/respond',
      '/api/incident/escalate',
      '/api/incident/communicate'
    ],
    dependencies: ['bcm_core'],
    bridge_integration: {
      event_mappings: {
        'incident.detected': 'incident.create',
        'incident.escalated': 'incident.escalation.trigger',
        'recovery.completed': 'incident.close'
      },
      external_integrations: ['thehive', 'monitoring_systems'],
      real_time: true
    }
  },

  'bcm_incident_management': {
    system_alias: 'advanced-incident-management',
    type: 'functional_module',
    capabilities: [
      'advanced_incident_analysis',
      'automated_response',
      'predictive_escalation',
      'impact_simulation'
    ],
    models: [
      'bcm.incident.advanced',
      'bcm.incident.automation',
      'bcm.incident.prediction'
    ],
    endpoints: [
      '/api/incident/advanced/analyze',
      '/api/incident/advanced/automate',
      '/api/incident/advanced/predict'
    ],
    dependencies: ['bcm_core', 'bcm_incident'],
    bridge_integration: {
      ai_enhancement: true,
      machine_learning: ['pattern_recognition', 'prediction', 'automation'],
      external_integrations: ['ai_services', 'ml_models']
    }
  },

  'bcm_digital_twin_core': {
    system_alias: 'digital-twin-core',
    type: 'functional_module',
    capabilities: [
      'organization_modeling',
      'process_simulation',
      'scenario_testing',
      'digital_mirror'
    ],
    models: [
      'bcm.digital.twin',
      'bcm.twin.component',
      'bcm.twin.simulation',
      'bcm.twin.scenario'
    ],
    endpoints: [
      '/api/twin/model',
      '/api/twin/simulate',
      '/api/twin/test',
      '/api/twin/mirror'
    ],
    dependencies: ['bcm_core'],
    bridge_integration: {
      ai_enhancement: true,
      real_time_sync: true,
      data_intensive: true,
      external_integrations: ['simulation_engines', 'modeling_platforms']
    }
  },

  'bcm_corporate_twin': {
    system_alias: 'corporate-digital-twin',
    type: 'functional_module',
    capabilities: [
      'corporate_modeling',
      'enterprise_simulation',
      'strategic_planning',
      'corporate_intelligence'
    ],
    models: [
      'bcm.corporate.twin',
      'bcm.corporate.model',
      'bcm.corporate.intelligence'
    ],
    endpoints: [
      '/api/corporate-twin/model',
      '/api/corporate-twin/simulate',
      '/api/corporate-twin/intelligence'
    ],
    dependencies: ['bcm_core', 'bcm_digital_twin_core'],
    bridge_integration: {
      ai_enhancement: true,
      strategic_ai: true,
      executive_dashboard: true
    }
  },

  'bcm_ai_consultant': {
    system_alias: 'ai-advisor',
    type: 'ai_module',
    capabilities: [
      'intelligent_consultation',
      'recommendation_engine',
      'predictive_analysis',
      'automated_insights'
    ],
    models: [
      'bcm.ai.consultation',
      'bcm.ai.recommendation',
      'bcm.ai.insight'
    ],
    endpoints: [
      '/api/ai/consult',
      '/api/ai/recommend',
      '/api/ai/analyze',
      '/api/ai/insights'
    ],
    dependencies: ['bcm_core'],
    bridge_integration: {
      ai_native: true,
      learning_enabled: true,
      context_aware: true,
      personalization: ['adaptive_responses', 'learning_preferences']
    }
  }
};

// Дополнительные конфигурации трансформации
const transformationRules = {
  // Системный запрос -> Odoo формат
  systemToOdoo: {
    'business-impact-analysis': {
      'assess_impact': (systemRequest) => ({
        method: 'assess_business_impact',
        params: {
          process_ids: systemRequest.data.process_id ? [systemRequest.data.process_id] : systemRequest.data.process_ids,
          scenarios: systemRequest.data.disruption_scenarios || [],
          assessment_type: systemRequest.data.assessment_depth || 'standard',
          context: {
            company_id: systemRequest.context.org_id,
            user_id: systemRequest.context.user_id
          }
        }
      })
    },

    'incident-management': {
      'report_incident': (systemRequest) => ({
        method: 'create_incident',
        params: {
          incident_data: {
            name: systemRequest.data.title,
            description: systemRequest.data.description,
            severity: systemRequest.data.severity || 'medium',
            category: systemRequest.data.category,
            reporter_id: systemRequest.context.user_id
          }
        }
      })
    }
  },

  // Odoo результат -> Системный формат
  odooToSystem: {
    'business-impact-analysis': {
      'assess_business_impact': (odooResult) => ({
        impact_assessment: {
          overall_score: odooResult.impact_score,
          financial_impact: odooResult.financial_impact,
          operational_impact: odooResult.operational_impact,
          reputational_impact: odooResult.reputational_impact,
          rto: odooResult.recovery_time_objective,
          rpo: odooResult.recovery_point_objective
        },
        dependencies: odooResult.dependencies || [],
        recommendations: odooResult.recommendations || [],
        confidence: odooResult.confidence_level || 0.8
      })
    },

    'incident-management': {
      'create_incident': (odooResult) => ({
        incident: {
          id: odooResult.id,
          reference: odooResult.name,
          status: odooResult.state,
          severity: odooResult.severity,
          created_at: odooResult.create_date,
          assigned_to: odooResult.assigned_user_id
        },
        next_actions: odooResult.next_actions || [],
        escalation_required: odooResult.auto_escalate || false
      })
    }
  }
};

// Конфигурация мониторинга
const monitoringConfig = {
  health_checks: {
    interval: 60000, // 1 минута
    endpoints: [
      '/web/health',
      '/api/bcm/core/status',
      '/api/bia/health',
      '/api/incident/status'
    ],
    timeout: 5000
  },

  performance_metrics: {
    response_time_threshold: 2000, // 2 секунды
    error_rate_threshold: 0.05,    // 5%
    availability_threshold: 0.99   // 99%
  },

  alerts: {
    channels: ['system_events', 'monitoring_dashboard'],
    escalation: {
      critical: 'immediate',
      high: '5_minutes',
      medium: '15_minutes'
    }
  }
};

module.exports = {
  bcmModulesConfig,
  transformationRules,
  monitoringConfig
};