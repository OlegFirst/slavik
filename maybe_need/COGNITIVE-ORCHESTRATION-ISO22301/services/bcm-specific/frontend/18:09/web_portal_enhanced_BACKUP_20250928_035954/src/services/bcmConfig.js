/**
 * BCM Configuration API Service
 * Handles communication with Odoo bcm_config module
 */

import apiClient from './apiClient'

class BCMConfigService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.config'
    this.moduleURL = '/web/dataset/call_kw/bcm.module'
    this.integrationURL = '/web/dataset/call_kw/bcm.integration'
    this.backupURL = '/web/dataset/call_kw/bcm.config.backup'
  }

  /**
   * Get all system configurations
   */
  async getConfigurations() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_all_configurations',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get configurations:', error)
      throw error
    }
  }

  /**
   * Save all configurations
   */
  async saveConfigurations(configs) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'save_all_configurations',
          args: [configs],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to save configurations:', error)
      throw error
    }
  }

  /**
   * Get general system settings
   */
  async getGeneralSettings() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_general_settings',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get general settings:', error)
      return {}
    }
  }

  /**
   * Update general settings
   */
  async updateGeneralSettings(settings) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'update_general_settings',
          args: [settings],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update general settings:', error)
      throw error
    }
  }

  /**
   * Get notification settings
   */
  async getNotificationSettings() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_notification_settings',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get notification settings:', error)
      return {}
    }
  }

  /**
   * Update notification settings
   */
  async updateNotificationSettings(settings) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'update_notification_settings',
          args: [settings],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update notification settings:', error)
      throw error
    }
  }

  /**
   * Test SMTP configuration
   */
  async testSMTP(smtpSettings) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'test_smtp_configuration',
          args: [smtpSettings],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to test SMTP:', error)
      throw error
    }
  }

  /**
   * Get security settings
   */
  async getSecuritySettings() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_security_settings',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get security settings:', error)
      return {}
    }
  }

  /**
   * Update security settings
   */
  async updateSecuritySettings(settings) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'update_security_settings',
          args: [settings],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update security settings:', error)
      throw error
    }
  }

  /**
   * Get available modules
   */
  async getModules() {
    try {
      const response = await apiClient.post(this.moduleURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.module',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'name', 'description', 'version', 'enabled', 'required',
              'status', 'last_updated', 'icon', 'dependencies', 'config_options'
            ],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get modules:', error)
      return []
    }
  }

  /**
   * Toggle module status
   */
  async toggleModule(moduleId, enabled) {
    try {
      const response = await apiClient.post(this.moduleURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.module',
          method: 'toggle_module',
          args: [moduleId, enabled],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to toggle module:', error)
      throw error
    }
  }

  /**
   * Install module
   */
  async installModule(moduleId) {
    try {
      const response = await apiClient.post(this.moduleURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.module',
          method: 'install_module',
          args: [moduleId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to install module:', error)
      throw error
    }
  }

  /**
   * Uninstall module
   */
  async uninstallModule(moduleId) {
    try {
      const response = await apiClient.post(this.moduleURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.module',
          method: 'uninstall_module',
          args: [moduleId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to uninstall module:', error)
      throw error
    }
  }

  /**
   * Update module
   */
  async updateModule(moduleId) {
    try {
      const response = await apiClient.post(this.moduleURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.module',
          method: 'update_module',
          args: [moduleId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update module:', error)
      throw error
    }
  }

  /**
   * Get available integrations
   */
  async getIntegrations() {
    try {
      const response = await apiClient.post(this.integrationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.integration',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: [
              'name', 'description', 'icon', 'enabled', 'status',
              'config', 'config_fields', 'last_sync', 'error_message'
            ],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get integrations:', error)
      return []
    }
  }

  /**
   * Toggle integration status
   */
  async toggleIntegration(integrationId, enabled) {
    try {
      const response = await apiClient.post(this.integrationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.integration',
          method: 'toggle_integration',
          args: [integrationId, enabled],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to toggle integration:', error)
      throw error
    }
  }

  /**
   * Test integration connection
   */
  async testIntegration(integrationId) {
    try {
      const response = await apiClient.post(this.integrationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.integration',
          method: 'test_connection',
          args: [integrationId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to test integration:', error)
      throw error
    }
  }

  /**
   * Update integration configuration
   */
  async updateIntegrationConfig(integrationId, config) {
    try {
      const response = await apiClient.post(this.integrationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.integration',
          method: 'update_config',
          args: [integrationId, config],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to update integration config:', error)
      throw error
    }
  }

  /**
   * Sync integration data
   */
  async syncIntegration(integrationId) {
    try {
      const response = await apiClient.post(this.integrationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.integration',
          method: 'sync_data',
          args: [integrationId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to sync integration:', error)
      throw error
    }
  }

  /**
   * Get system health status
   */
  async getSystemHealth() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_system_health',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get system health:', error)
      return []
    }
  }

  /**
   * Run system diagnostics
   */
  async runDiagnostics() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'run_diagnostics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to run diagnostics:', error)
      throw error
    }
  }

  /**
   * Get configuration backups
   */
  async getBackups() {
    try {
      const response = await apiClient.post(this.backupURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.backup',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'description', 'created_date', 'size', 'backup_type'],
            order: 'created_date desc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get backups:', error)
      return []
    }
  }

  /**
   * Create configuration backup
   */
  async createBackup(description = '') {
    try {
      const response = await apiClient.post(this.backupURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.backup',
          method: 'create_backup',
          args: [description],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to create backup:', error)
      throw error
    }
  }

  /**
   * Restore configuration from backup
   */
  async restoreBackup(backupId) {
    try {
      const response = await apiClient.post(this.backupURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.backup',
          method: 'restore_backup',
          args: [backupId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to restore backup:', error)
      throw error
    }
  }

  /**
   * Delete backup
   */
  async deleteBackup(backupId) {
    try {
      const response = await apiClient.post(this.backupURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.backup',
          method: 'unlink',
          args: [backupId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to delete backup:', error)
      throw error
    }
  }

  /**
   * Export configuration
   */
  async exportConfig(format = 'json') {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'export_configuration',
          args: [format],
          kwargs: {}
        }
      })

      // Handle file download
      if (response.data.result.file_data) {
        const link = document.createElement('a')
        link.href = `data:application/octet-stream;base64,${response.data.result.file_data}`
        link.download = response.data.result.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }

      return response.data.result
    } catch (error) {
      console.error('Failed to export configuration:', error)
      throw error
    }
  }

  /**
   * Import configuration
   */
  async importConfig(configData, format = 'json') {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'import_configuration',
          args: [configData, format],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to import configuration:', error)
      throw error
    }
  }

  /**
   * Get audit logs
   */
  async getAuditLogs(filters = {}) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.config.audit', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.audit',
          method: 'search_read',
          args: [this.buildAuditFilters(filters)],
          kwargs: {
            fields: [
              'action', 'model', 'res_id', 'user_id', 'user_name',
              'timestamp', 'old_values', 'new_values', 'description'
            ],
            order: 'timestamp desc',
            limit: filters.limit || 100
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get audit logs:', error)
      return []
    }
  }

  /**
   * Get system performance metrics
   */
  async getPerformanceMetrics(timeRange = '24h') {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'get_performance_metrics',
          args: [timeRange],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get performance metrics:', error)
      return {}
    }
  }

  /**
   * Reset to default configuration
   */
  async resetToDefaults(section = 'all') {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'reset_to_defaults',
          args: [section],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to reset to defaults:', error)
      throw error
    }
  }

  /**
   * Validate configuration
   */
  async validateConfig(config) {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config',
          method: 'validate_configuration',
          args: [config],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to validate configuration:', error)
      throw error
    }
  }

  /**
   * Get configuration history
   */
  async getConfigHistory(section, limit = 20) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.config.history', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.history',
          method: 'search_read',
          args: [['section', '=', section]],
          kwargs: {
            fields: [
              'section', 'change_date', 'changed_by', 'old_value',
              'new_value', 'change_reason', 'is_rollback'
            ],
            order: 'change_date desc',
            limit: limit
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get configuration history:', error)
      return []
    }
  }

  /**
   * Rollback configuration change
   */
  async rollbackChange(historyId) {
    try {
      const response = await apiClient.post('/web/dataset/call_kw/bcm.config.history', {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.config.history',
          method: 'rollback_change',
          args: [historyId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to rollback change:', error)
      throw error
    }
  }

  /**
   * Build audit filters
   */
  buildAuditFilters(filters) {
    const domain = []

    if (filters.user_id) {
      domain.push(['user_id', '=', filters.user_id])
    }

    if (filters.model) {
      domain.push(['model', '=', filters.model])
    }

    if (filters.action) {
      domain.push(['action', '=', filters.action])
    }

    if (filters.date_from) {
      domain.push(['timestamp', '>=', filters.date_from])
    }

    if (filters.date_to) {
      domain.push(['timestamp', '<=', filters.date_to])
    }

    return domain
  }

  /**
   * Format configuration value for display
   */
  formatConfigValue(value, type = 'string') {
    if (value === null || value === undefined) {
      return 'Not set'
    }

    switch (type) {
      case 'boolean':
        return value ? 'Enabled' : 'Disabled'
      case 'date':
        return new Date(value).toLocaleDateString()
      case 'datetime':
        return new Date(value).toLocaleString()
      case 'json':
        return JSON.stringify(value, null, 2)
      default:
        return value.toString()
    }
  }

  /**
   * Validate configuration field
   */
  validateField(value, field) {
    if (field.required && (!value || value.toString().trim() === '')) {
      return `${field.label} is required`
    }

    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(value)) {
        return `${field.label} must be a valid email address`
      }
    }

    if (field.type === 'number' && value) {
      if (isNaN(value)) {
        return `${field.label} must be a number`
      }
      if (field.min !== undefined && value < field.min) {
        return `${field.label} must be at least ${field.min}`
      }
      if (field.max !== undefined && value > field.max) {
        return `${field.label} must be at most ${field.max}`
      }
    }

    if (field.type === 'url' && value) {
      try {
        new URL(value)
      } catch {
        return `${field.label} must be a valid URL`
      }
    }

    return null
  }
}

export default new BCMConfigService()