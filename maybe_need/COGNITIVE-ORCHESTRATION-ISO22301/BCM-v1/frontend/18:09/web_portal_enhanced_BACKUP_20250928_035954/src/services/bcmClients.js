import { odooService } from './odoo'
import { assistantService } from './assistant'

class BCMClientsService {
  constructor() {
    this.model = 'bcm.client'
  }

  // Client Management
  async getClients(filters = {}) {
    try {
      const domain = this.buildDomain(filters)
      return await odooService.searchRead(this.model, {
        domain,
        fields: [
          'id', 'name', 'code', 'client_type', 'status', 'industry',
          'contact_name', 'contact_email', 'contact_phone',
          'subscription_plan', 'subscription_status', 'subscription_start',
          'subscription_end', 'user_count', 'storage_used', 'storage_limit',
          'last_login', 'created_date', 'parent_id', 'child_ids',
          'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching clients:', error)
      throw error
    }
  }

  async getClientById(id) {
    try {
      const client = await odooService.read(this.model, [id], {
        fields: [
          'id', 'name', 'code', 'client_type', 'status', 'industry',
          'contact_name', 'contact_email', 'contact_phone', 'address',
          'website', 'description', 'subscription_plan', 'subscription_status',
          'subscription_start', 'subscription_end', 'billing_cycle',
          'user_count', 'user_limit', 'storage_used', 'storage_limit',
          'api_calls_used', 'api_calls_limit', 'last_login', 'created_date',
          'parent_id', 'child_ids', 'features_enabled', 'custom_settings',
          'integration_keys', 'create_date', 'write_date'
        ]
      })
      return client[0]
    } catch (error) {
      console.error('Error fetching client:', error)
      throw error
    }
  }

  async createClient(clientData) {
    try {
      const id = await odooService.create(this.model, clientData)

      // Get AI recommendations for client onboarding
      const onboardingPlan = await assistantService.generateClientOnboarding({
        clientType: clientData.client_type,
        industry: clientData.industry,
        subscriptionPlan: clientData.subscription_plan
      })

      if (onboardingPlan) {
        await odooService.write(this.model, [id], {
          onboarding_plan: onboardingPlan,
          onboarding_status: 'planned'
        })
      }

      return id
    } catch (error) {
      console.error('Error creating client:', error)
      throw error
    }
  }

  async updateClient(id, clientData) {
    try {
      return await odooService.write(this.model, [id], clientData)
    } catch (error) {
      console.error('Error updating client:', error)
      throw error
    }
  }

  async deleteClient(id) {
    try {
      return await odooService.unlink(this.model, [id])
    } catch (error) {
      console.error('Error deleting client:', error)
      throw error
    }
  }

  // Subscription Management
  async getSubscriptionPlans() {
    try {
      return await odooService.searchRead('bcm.subscription.plan', {
        domain: [['active', '=', true]],
        fields: [
          'id', 'name', 'code', 'description', 'plan_type', 'price_monthly',
          'price_yearly', 'user_limit', 'storage_limit', 'api_calls_limit',
          'features', 'support_level', 'trial_days'
        ]
      })
    } catch (error) {
      console.error('Error fetching subscription plans:', error)
      throw error
    }
  }

  async updateSubscription(clientId, planId, billingCycle = 'monthly') {
    try {
      return await odooService.callMethod(this.model, 'update_subscription', [clientId, planId, billingCycle])
    } catch (error) {
      console.error('Error updating subscription:', error)
      throw error
    }
  }

  async cancelSubscription(clientId, reason = '') {
    try {
      return await odooService.callMethod(this.model, 'cancel_subscription', [clientId, reason])
    } catch (error) {
      console.error('Error cancelling subscription:', error)
      throw error
    }
  }

  async renewSubscription(clientId, duration = 12) {
    try {
      return await odooService.callMethod(this.model, 'renew_subscription', [clientId, duration])
    } catch (error) {
      console.error('Error renewing subscription:', error)
      throw error
    }
  }

  // User Management
  async getClientUsers(clientId) {
    try {
      return await odooService.searchRead('bcm.client.user', {
        domain: [['client_id', '=', clientId]],
        fields: [
          'id', 'name', 'email', 'role', 'status', 'last_login',
          'permissions', 'department', 'created_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching client users:', error)
      throw error
    }
  }

  async createClientUser(userData) {
    try {
      const id = await odooService.create('bcm.client.user', userData)

      // Send welcome email with onboarding
      await this.sendWelcomeEmail(id)

      return id
    } catch (error) {
      console.error('Error creating client user:', error)
      throw error
    }
  }

  async updateUserRole(userId, role, permissions = []) {
    try {
      return await odooService.write('bcm.client.user', [userId], {
        role,
        permissions
      })
    } catch (error) {
      console.error('Error updating user role:', error)
      throw error
    }
  }

  async deactivateUser(userId) {
    try {
      return await odooService.write('bcm.client.user', [userId], {
        status: 'inactive'
      })
    } catch (error) {
      console.error('Error deactivating user:', error)
      throw error
    }
  }

  // Tenant Isolation & Data Management
  async getClientData(clientId, dataType) {
    try {
      return await odooService.callMethod(this.model, 'get_client_data', [clientId, dataType])
    } catch (error) {
      console.error('Error fetching client data:', error)
      throw error
    }
  }

  async exportClientData(clientId, format = 'json') {
    try {
      return await odooService.callMethod(this.model, 'export_client_data', [clientId, format])
    } catch (error) {
      console.error('Error exporting client data:', error)
      throw error
    }
  }

  async purgeClientData(clientId, dataTypes = []) {
    try {
      return await odooService.callMethod(this.model, 'purge_client_data', [clientId, dataTypes])
    } catch (error) {
      console.error('Error purging client data:', error)
      throw error
    }
  }

  async cloneClientConfiguration(sourceClientId, targetClientId, configTypes = []) {
    try {
      return await odooService.callMethod(this.model, 'clone_configuration', [sourceClientId, targetClientId, configTypes])
    } catch (error) {
      console.error('Error cloning client configuration:', error)
      throw error
    }
  }

  // Billing & Usage Analytics
  async getClientUsage(clientId, timeframe = '30d') {
    try {
      return await odooService.callMethod(this.model, 'get_usage_analytics', [clientId, timeframe])
    } catch (error) {
      console.error('Error fetching client usage:', error)
      throw error
    }
  }

  async generateInvoice(clientId, billingPeriod) {
    try {
      return await odooService.callMethod(this.model, 'generate_invoice', [clientId, billingPeriod])
    } catch (error) {
      console.error('Error generating invoice:', error)
      throw error
    }
  }

  async getInvoiceHistory(clientId) {
    try {
      return await odooService.searchRead('bcm.client.invoice', {
        domain: [['client_id', '=', clientId]],
        fields: [
          'id', 'invoice_number', 'amount', 'status', 'due_date',
          'paid_date', 'billing_period', 'create_date'
        ],
        order: 'create_date desc'
      })
    } catch (error) {
      console.error('Error fetching invoice history:', error)
      throw error
    }
  }

  // Resource Monitoring
  async getResourceUsage(clientId) {
    try {
      return await odooService.callMethod(this.model, 'get_resource_usage', [clientId])
    } catch (error) {
      console.error('Error fetching resource usage:', error)
      throw error
    }
  }

  async setResourceLimits(clientId, limits) {
    try {
      return await odooService.write(this.model, [clientId], {
        user_limit: limits.users,
        storage_limit: limits.storage,
        api_calls_limit: limits.api_calls
      })
    } catch (error) {
      console.error('Error setting resource limits:', error)
      throw error
    }
  }

  async getResourceAlerts(clientId) {
    try {
      return await odooService.searchRead('bcm.client.alert', {
        domain: [['client_id', '=', clientId], ['status', '=', 'active']],
        fields: [
          'id', 'alert_type', 'message', 'severity', 'threshold',
          'current_value', 'created_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching resource alerts:', error)
      throw error
    }
  }

  // Client Analytics & Insights
  async getClientAnalytics(filters = {}) {
    try {
      return await odooService.callMethod(this.model, 'get_client_analytics', [filters])
    } catch (error) {
      console.error('Error fetching client analytics:', error)
      throw error
    }
  }

  async getChurnAnalysis() {
    try {
      return await odooService.callMethod(this.model, 'get_churn_analysis', [])
    } catch (error) {
      console.error('Error fetching churn analysis:', error)
      throw error
    }
  }

  async getRevenueAnalytics(timeframe = '12M') {
    try {
      return await odooService.callMethod(this.model, 'get_revenue_analytics', [timeframe])
    } catch (error) {
      console.error('Error fetching revenue analytics:', error)
      throw error
    }
  }

  async getUsagePatterns(clientId = null) {
    try {
      return await odooService.callMethod(this.model, 'get_usage_patterns', [clientId])
    } catch (error) {
      console.error('Error fetching usage patterns:', error)
      throw error
    }
  }

  // Support & Communication
  async createSupportTicket(clientId, ticketData) {
    try {
      return await odooService.create('bcm.client.support', {
        client_id: clientId,
        ...ticketData
      })
    } catch (error) {
      console.error('Error creating support ticket:', error)
      throw error
    }
  }

  async getSupportTickets(clientId) {
    try {
      return await odooService.searchRead('bcm.client.support', {
        domain: [['client_id', '=', clientId]],
        fields: [
          'id', 'subject', 'status', 'priority', 'category',
          'created_date', 'last_updated', 'assigned_to'
        ],
        order: 'created_date desc'
      })
    } catch (error) {
      console.error('Error fetching support tickets:', error)
      throw error
    }
  }

  async sendClientNotification(clientId, notification) {
    try {
      return await odooService.callMethod(this.model, 'send_notification', [clientId, notification])
    } catch (error) {
      console.error('Error sending client notification:', error)
      throw error
    }
  }

  async sendWelcomeEmail(userId) {
    try {
      return await odooService.callMethod('bcm.client.user', 'send_welcome_email', [userId])
    } catch (error) {
      console.error('Error sending welcome email:', error)
      throw error
    }
  }

  // Integration & API Management
  async getApiKeys(clientId) {
    try {
      return await odooService.searchRead('bcm.client.api_key', {
        domain: [['client_id', '=', clientId]],
        fields: [
          'id', 'name', 'key_prefix', 'permissions', 'status',
          'last_used', 'expires_at', 'created_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching API keys:', error)
      throw error
    }
  }

  async generateApiKey(clientId, keyData) {
    try {
      return await odooService.create('bcm.client.api_key', {
        client_id: clientId,
        ...keyData
      })
    } catch (error) {
      console.error('Error generating API key:', error)
      throw error
    }
  }

  async revokeApiKey(keyId) {
    try {
      return await odooService.write('bcm.client.api_key', [keyId], {
        status: 'revoked'
      })
    } catch (error) {
      console.error('Error revoking API key:', error)
      throw error
    }
  }

  async getIntegrationStatus(clientId) {
    try {
      return await odooService.callMethod(this.model, 'get_integration_status', [clientId])
    } catch (error) {
      console.error('Error fetching integration status:', error)
      throw error
    }
  }

  // AI-Powered Client Management
  async getClientInsights(clientId) {
    try {
      const client = await this.getClientById(clientId)
      const usage = await this.getClientUsage(clientId)

      const insights = await assistantService.analyzeClientBehavior({
        clientData: client,
        usagePatterns: usage,
        timeframe: '90d'
      })

      return {
        riskScore: insights.churnRisk,
        recommendations: insights.recommendations,
        upsellOpportunities: insights.upsellOpportunities,
        healthScore: insights.healthScore
      }
    } catch (error) {
      console.error('Error getting client insights:', error)
      throw error
    }
  }

  async predictChurn(clientId) {
    try {
      const analytics = await this.getClientAnalytics({ client_id: clientId })
      return await assistantService.predictClientChurn({
        clientId,
        analytics,
        timeframe: '6M'
      })
    } catch (error) {
      console.error('Error predicting churn:', error)
      throw error
    }
  }

  async generatePersonalizedRecommendations(clientId) {
    try {
      const insights = await this.getClientInsights(clientId)
      return await assistantService.generateClientRecommendations({
        clientId,
        insights,
        includeFeatures: true,
        includeOptimizations: true
      })
    } catch (error) {
      console.error('Error generating recommendations:', error)
      throw error
    }
  }

  // Utility Methods
  buildDomain(filters) {
    const domain = []

    if (filters.client_type) {
      domain.push(['client_type', '=', filters.client_type])
    }
    if (filters.status) {
      domain.push(['status', 'in', Array.isArray(filters.status) ? filters.status : [filters.status]])
    }
    if (filters.subscription_status) {
      domain.push(['subscription_status', '=', filters.subscription_status])
    }
    if (filters.industry) {
      domain.push(['industry', '=', filters.industry])
    }
    if (filters.subscription_plan) {
      domain.push(['subscription_plan', '=', filters.subscription_plan])
    }
    if (filters.search) {
      domain.push(['|', ['name', 'ilike', filters.search], ['code', 'ilike', filters.search]])
    }

    return domain
  }

  formatClientType(type) {
    const types = {
      enterprise: 'Enterprise',
      business: 'Business',
      startup: 'Startup',
      nonprofit: 'Non-Profit'
    }
    return types[type] || type
  }

  formatSubscriptionStatus(status) {
    const statuses = {
      active: 'Active',
      trial: 'Trial',
      expired: 'Expired',
      cancelled: 'Cancelled',
      suspended: 'Suspended'
    }
    return statuses[status] || status
  }

  formatStorageSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  calculateUsagePercentage(used, limit) {
    if (!limit) return 0
    return Math.min(100, Math.max(0, (used / limit) * 100))
  }

  getHealthScoreColor(score) {
    if (score >= 80) return '#4caf50'
    if (score >= 60) return '#ff9800'
    return '#f44336'
  }
}

export const bcmClientsService = new BCMClientsService()