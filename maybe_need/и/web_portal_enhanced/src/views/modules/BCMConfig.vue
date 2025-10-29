<template>
  <div class="bcm-config">
    <!-- Header Section -->
    <div class="config-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Configuration Management</h1>
            <p class="page-subtitle">System Settings & Module Configuration</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-success me-2" @click="saveAllConfigs" :disabled="saving">
              <i class="fas fa-save"></i> {{ saving ? 'Saving...' : 'Save All' }}
            </button>
            <button class="btn btn-outline-primary" @click="loadConfigs">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- System Status Overview -->
    <div class="status-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ systemStatus.modulesActive }}</h3>
                <p class="metric-label">Active Modules</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card primary">
              <div class="metric-icon">
                <i class="fas fa-plug"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ systemStatus.integrations }}</h3>
                <p class="metric-label">Integrations</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ systemStatus.alerts }}</h3>
                <p class="metric-label">Config Alerts</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-history"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ formatDate(systemStatus.lastBackup) }}</h3>
                <p class="metric-label">Last Backup</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Tabs -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="config-tabs">
                  <button
                    v-for="tab in configTabs"
                    :key="tab.id"
                    class="tab-btn"
                    :class="{ active: activeTab === tab.id }"
                    @click="activeTab = tab.id"
                  >
                    <i :class="tab.icon"></i>
                    {{ tab.name }}
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- General Settings Tab -->
                <div v-if="activeTab === 'general'" class="config-tab-content">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>System Settings</h4>
                        <div class="mb-3">
                          <label class="form-label">Organization Name</label>
                          <input
                            type="text"
                            class="form-control"
                            v-model="configs.general.organization_name"
                          >
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Time Zone</label>
                          <select class="form-select" v-model="configs.general.timezone">
                            <option v-for="tz in timezones" :key="tz.value" :value="tz.value">
                              {{ tz.label }}
                            </option>
                          </select>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Default Language</label>
                          <select class="form-select" v-model="configs.general.default_language">
                            <option value="en_US">English (US)</option>
                            <option value="en_GB">English (UK)</option>
                            <option value="fr_FR">French</option>
                            <option value="de_DE">German</option>
                            <option value="es_ES">Spanish</option>
                          </select>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Date Format</label>
                          <select class="form-select" v-model="configs.general.date_format">
                            <option value="MM/dd/yyyy">MM/dd/yyyy</option>
                            <option value="dd/MM/yyyy">dd/MM/yyyy</option>
                            <option value="yyyy-MM-dd">yyyy-MM-dd</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>BCMS Settings</h4>
                        <div class="mb-3">
                          <label class="form-label">BCMS Scope</label>
                          <textarea
                            class="form-control"
                            rows="3"
                            v-model="configs.general.bcms_scope"
                            placeholder="Define the scope of your BCMS"
                          ></textarea>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Risk Tolerance Level</label>
                          <select class="form-select" v-model="configs.general.risk_tolerance">
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                          </select>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Default RTO (hours)</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.general.default_rto"
                            min="1"
                          >
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Default RPO (hours)</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.general.default_rpo"
                            min="1"
                          >
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Notifications Tab -->
                <div v-if="activeTab === 'notifications'" class="config-tab-content">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>Email Notifications</h4>
                        <div class="mb-3">
                          <div class="form-check form-switch">
                            <input
                              class="form-check-input"
                              type="checkbox"
                              v-model="configs.notifications.email_enabled"
                            >
                            <label class="form-check-label">Enable Email Notifications</label>
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">SMTP Server</label>
                          <input
                            type="text"
                            class="form-control"
                            v-model="configs.notifications.smtp_server"
                          >
                        </div>
                        <div class="mb-3">
                          <label class="form-label">SMTP Port</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.notifications.smtp_port"
                          >
                        </div>
                        <div class="mb-3">
                          <label class="form-label">From Email</label>
                          <input
                            type="email"
                            class="form-control"
                            v-model="configs.notifications.from_email"
                          >
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>Notification Rules</h4>
                        <div class="notification-rules">
                          <div
                            v-for="rule in configs.notifications.rules"
                            :key="rule.id"
                            class="notification-rule"
                          >
                            <div class="rule-header">
                              <strong>{{ rule.name }}</strong>
                              <div class="form-check form-switch">
                                <input
                                  class="form-check-input"
                                  type="checkbox"
                                  v-model="rule.enabled"
                                >
                              </div>
                            </div>
                            <div class="rule-content">
                              <small class="text-muted">{{ rule.description }}</small>
                              <div class="mt-2">
                                <label class="form-label">Recipients</label>
                                <input
                                  type="text"
                                  class="form-control form-control-sm"
                                  v-model="rule.recipients"
                                  placeholder="Enter email addresses separated by commas"
                                >
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Integrations Tab -->
                <div v-if="activeTab === 'integrations'" class="config-tab-content">
                  <div class="row">
                    <div class="col-12">
                      <div class="integration-grid">
                        <div
                          v-for="integration in integrations"
                          :key="integration.id"
                          class="integration-card"
                          :class="{ active: integration.enabled }"
                        >
                          <div class="integration-header">
                            <div class="integration-logo">
                              <i :class="integration.icon"></i>
                            </div>
                            <div class="integration-info">
                              <h5>{{ integration.name }}</h5>
                              <p>{{ integration.description }}</p>
                            </div>
                            <div class="integration-toggle">
                              <div class="form-check form-switch">
                                <input
                                  class="form-check-input"
                                  type="checkbox"
                                  v-model="integration.enabled"
                                  @change="toggleIntegration(integration)"
                                >
                              </div>
                            </div>
                          </div>
                          <div v-if="integration.enabled" class="integration-config">
                            <div class="row">
                              <div
                                v-for="field in integration.config_fields"
                                :key="field.name"
                                class="col-md-6"
                              >
                                <div class="mb-3">
                                  <label class="form-label">{{ field.label }}</label>
                                  <input
                                    :type="field.type"
                                    class="form-control form-control-sm"
                                    v-model="integration.config[field.name]"
                                    :placeholder="field.placeholder"
                                  >
                                </div>
                              </div>
                            </div>
                            <button
                              class="btn btn-outline-primary btn-sm"
                              @click="testIntegration(integration)"
                              :disabled="integration.testing"
                            >
                              <i class="fas fa-vial"></i>
                              {{ integration.testing ? 'Testing...' : 'Test Connection' }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Security Tab -->
                <div v-if="activeTab === 'security'" class="config-tab-content">
                  <div class="row">
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>Authentication Settings</h4>
                        <div class="mb-3">
                          <div class="form-check form-switch">
                            <input
                              class="form-check-input"
                              type="checkbox"
                              v-model="configs.security.two_factor_enabled"
                            >
                            <label class="form-check-label">Enable Two-Factor Authentication</label>
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Session Timeout (minutes)</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.security.session_timeout"
                            min="5"
                            max="1440"
                          >
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Password Policy</label>
                          <select class="form-select" v-model="configs.security.password_policy">
                            <option value="basic">Basic</option>
                            <option value="standard">Standard</option>
                            <option value="strict">Strict</option>
                          </select>
                        </div>
                        <div class="mb-3">
                          <div class="form-check form-switch">
                            <input
                              class="form-check-input"
                              type="checkbox"
                              v-model="configs.security.ip_restriction_enabled"
                            >
                            <label class="form-check-label">IP Restriction Enabled</label>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="config-section">
                        <h4>Data Protection</h4>
                        <div class="mb-3">
                          <div class="form-check form-switch">
                            <input
                              class="form-check-input"
                              type="checkbox"
                              v-model="configs.security.data_encryption_enabled"
                            >
                            <label class="form-check-label">Data Encryption at Rest</label>
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Backup Retention (days)</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.security.backup_retention"
                            min="30"
                          >
                        </div>
                        <div class="mb-3">
                          <div class="form-check form-switch">
                            <input
                              class="form-check-input"
                              type="checkbox"
                              v-model="configs.security.audit_logging_enabled"
                            >
                            <label class="form-check-label">Audit Logging Enabled</label>
                          </div>
                        </div>
                        <div class="mb-3">
                          <label class="form-label">Log Retention (days)</label>
                          <input
                            type="number"
                            class="form-control"
                            v-model="configs.security.log_retention"
                            min="90"
                          >
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Modules Tab -->
                <div v-if="activeTab === 'modules'" class="config-tab-content">
                  <div class="row">
                    <div class="col-12">
                      <div class="modules-grid">
                        <div
                          v-for="module in modules"
                          :key="module.id"
                          class="module-card"
                          :class="{ active: module.enabled }"
                        >
                          <div class="module-header">
                            <div class="module-icon">
                              <i :class="module.icon"></i>
                            </div>
                            <div class="module-info">
                              <h5>{{ module.name }}</h5>
                              <p>{{ module.description }}</p>
                              <span class="version-badge">v{{ module.version }}</span>
                            </div>
                            <div class="module-toggle">
                              <div class="form-check form-switch">
                                <input
                                  class="form-check-input"
                                  type="checkbox"
                                  v-model="module.enabled"
                                  @change="toggleModule(module)"
                                  :disabled="module.required"
                                >
                              </div>
                            </div>
                          </div>
                          <div class="module-stats">
                            <div class="stat">
                              <small>Last Updated</small>
                              <strong>{{ formatDate(module.last_updated) }}</strong>
                            </div>
                            <div class="stat">
                              <small>Status</small>
                              <strong :class="module.status">{{ module.status }}</strong>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Configuration Backup & Restore -->
        <div class="row mt-4">
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>Configuration Backup</h3>
                <button class="btn btn-outline-primary btn-sm" @click="createBackup" :disabled="backingUp">
                  <i class="fas fa-download"></i>
                  {{ backingUp ? 'Creating...' : 'Create Backup' }}
                </button>
              </div>
              <div class="card-body">
                <div class="backup-list">
                  <div
                    v-for="backup in backups"
                    :key="backup.id"
                    class="backup-item"
                  >
                    <div class="backup-info">
                      <strong>{{ backup.name }}</strong>
                      <small class="text-muted d-block">{{ formatDateTime(backup.created_date) }}</small>
                    </div>
                    <div class="backup-actions">
                      <button class="btn btn-sm btn-outline-success" @click="restoreBackup(backup)">
                        Restore
                      </button>
                      <button class="btn btn-sm btn-outline-danger" @click="deleteBackup(backup)">
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>System Health</h3>
                <button class="btn btn-outline-primary btn-sm" @click="checkSystemHealth">
                  <i class="fas fa-heartbeat"></i> Check Health
                </button>
              </div>
              <div class="card-body">
                <div class="health-checks">
                  <div
                    v-for="check in healthChecks"
                    :key="check.name"
                    class="health-check-item"
                  >
                    <div class="health-check-info">
                      <strong>{{ check.name }}</strong>
                      <small class="text-muted d-block">{{ check.description }}</small>
                    </div>
                    <div class="health-check-status">
                      <span class="status-indicator" :class="check.status">
                        <i :class="getHealthIcon(check.status)"></i>
                        {{ check.status }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import bcmConfigService from '@/services/bcmConfig'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMConfig',
  setup() {
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const backingUp = ref(false)
    const activeTab = ref('general')

    const systemStatus = reactive({
      modulesActive: 0,
      integrations: 0,
      alerts: 0,
      lastBackup: null
    })

    const configs = reactive({
      general: {
        organization_name: '',
        timezone: 'UTC',
        default_language: 'en_US',
        date_format: 'MM/dd/yyyy',
        bcms_scope: '',
        risk_tolerance: 'medium',
        default_rto: 24,
        default_rpo: 4
      },
      notifications: {
        email_enabled: true,
        smtp_server: '',
        smtp_port: 587,
        from_email: '',
        rules: []
      },
      security: {
        two_factor_enabled: false,
        session_timeout: 60,
        password_policy: 'standard',
        ip_restriction_enabled: false,
        data_encryption_enabled: true,
        backup_retention: 90,
        audit_logging_enabled: true,
        log_retention: 365
      }
    })

    const configTabs = ref([
      { id: 'general', name: 'General', icon: 'fas fa-cog' },
      { id: 'notifications', name: 'Notifications', icon: 'fas fa-bell' },
      { id: 'integrations', name: 'Integrations', icon: 'fas fa-plug' },
      { id: 'security', name: 'Security', icon: 'fas fa-shield-alt' },
      { id: 'modules', name: 'Modules', icon: 'fas fa-puzzle-piece' }
    ])

    const timezones = ref([
      { value: 'UTC', label: 'UTC' },
      { value: 'America/New_York', label: 'Eastern Time' },
      { value: 'America/Chicago', label: 'Central Time' },
      { value: 'America/Denver', label: 'Mountain Time' },
      { value: 'America/Los_Angeles', label: 'Pacific Time' },
      { value: 'Europe/London', label: 'London' },
      { value: 'Europe/Paris', label: 'Paris' },
      { value: 'Europe/Berlin', label: 'Berlin' },
      { value: 'Asia/Tokyo', label: 'Tokyo' },
      { value: 'Asia/Shanghai', label: 'Shanghai' }
    ])

    const integrations = ref([])
    const modules = ref([])
    const backups = ref([])
    const healthChecks = ref([])

    // Methods
    const loadConfigs = async () => {
      loading.value = true
      try {
        const data = await bcmConfigService.getConfigurations()
        Object.assign(configs.general, data.general)
        Object.assign(configs.notifications, data.notifications)
        Object.assign(configs.security, data.security)

        integrations.value = data.integrations || []
        modules.value = data.modules || []

        systemStatus.modulesActive = data.system_status.modules_active || 0
        systemStatus.integrations = data.system_status.integrations || 0
        systemStatus.alerts = data.system_status.alerts || 0
        systemStatus.lastBackup = data.system_status.last_backup
      } catch (error) {
        toast.error('Failed to load configurations')
      } finally {
        loading.value = false
      }
    }

    const saveAllConfigs = async () => {
      saving.value = true
      try {
        await bcmConfigService.saveConfigurations({
          general: configs.general,
          notifications: configs.notifications,
          security: configs.security,
          integrations: integrations.value,
          modules: modules.value
        })
        toast.success('Configurations saved successfully')
      } catch (error) {
        toast.error('Failed to save configurations')
      } finally {
        saving.value = false
      }
    }

    const toggleIntegration = async (integration) => {
      try {
        await bcmConfigService.toggleIntegration(integration.id, integration.enabled)
        if (integration.enabled) {
          toast.success(`${integration.name} integration enabled`)
        } else {
          toast.info(`${integration.name} integration disabled`)
        }
      } catch (error) {
        integration.enabled = !integration.enabled
        toast.error(`Failed to toggle ${integration.name} integration`)
      }
    }

    const testIntegration = async (integration) => {
      integration.testing = true
      try {
        const result = await bcmConfigService.testIntegration(integration.id)
        if (result.success) {
          toast.success(`${integration.name} connection test successful`)
        } else {
          toast.error(`${integration.name} connection test failed: ${result.error}`)
        }
      } catch (error) {
        toast.error(`Failed to test ${integration.name} connection`)
      } finally {
        integration.testing = false
      }
    }

    const toggleModule = async (module) => {
      if (module.required) {
        toast.warning('This module is required and cannot be disabled')
        return
      }

      try {
        await bcmConfigService.toggleModule(module.id, module.enabled)
        if (module.enabled) {
          toast.success(`${module.name} module enabled`)
        } else {
          toast.info(`${module.name} module disabled`)
        }
      } catch (error) {
        module.enabled = !module.enabled
        toast.error(`Failed to toggle ${module.name} module`)
      }
    }

    const createBackup = async () => {
      backingUp.value = true
      try {
        const backup = await bcmConfigService.createBackup()
        backups.value.unshift(backup)
        toast.success('Configuration backup created successfully')
      } catch (error) {
        toast.error('Failed to create backup')
      } finally {
        backingUp.value = false
      }
    }

    const restoreBackup = async (backup) => {
      if (confirm(`Are you sure you want to restore configuration from ${backup.name}? This will overwrite current settings.`)) {
        try {
          await bcmConfigService.restoreBackup(backup.id)
          toast.success('Configuration restored successfully')
          loadConfigs()
        } catch (error) {
          toast.error('Failed to restore backup')
        }
      }
    }

    const deleteBackup = async (backup) => {
      if (confirm(`Are you sure you want to delete backup ${backup.name}?`)) {
        try {
          await bcmConfigService.deleteBackup(backup.id)
          backups.value = backups.value.filter(b => b.id !== backup.id)
          toast.success('Backup deleted successfully')
        } catch (error) {
          toast.error('Failed to delete backup')
        }
      }
    }

    const loadBackups = async () => {
      try {
        backups.value = await bcmConfigService.getBackups()
      } catch (error) {
        console.error('Failed to load backups:', error)
      }
    }

    const checkSystemHealth = async () => {
      try {
        healthChecks.value = await bcmConfigService.getSystemHealth()
      } catch (error) {
        toast.error('Failed to check system health')
      }
    }

    const getHealthIcon = (status) => {
      const icons = {
        healthy: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle',
        unknown: 'fas fa-question-circle'
      }
      return icons[status] || icons.unknown
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    // Lifecycle
    onMounted(() => {
      loadConfigs()
      loadBackups()
      checkSystemHealth()
    })

    return {
      // Data
      loading,
      saving,
      backingUp,
      activeTab,
      systemStatus,
      configs,
      configTabs,
      timezones,
      integrations,
      modules,
      backups,
      healthChecks,

      // Methods
      loadConfigs,
      saveAllConfigs,
      toggleIntegration,
      testIntegration,
      toggleModule,
      createBackup,
      restoreBackup,
      deleteBackup,
      checkSystemHealth,
      getHealthIcon,
      formatDate,
      formatDateTime
    }
  }
}
</script>

<style scoped>
/* Anthropic Color Palette */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #F8F9FA;
  --anthropic-success: #28A745;
  --anthropic-warning: #FFC107;
  --anthropic-danger: #DC3545;
}

.bcm-config {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.config-header {
  background: white;
  border-bottom: 2px solid var(--anthropic-blue);
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.page-title {
  color: var(--anthropic-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
}

.page-subtitle {
  color: #6C757D;
  font-size: 1.1rem;
  margin: 0.5rem 0 0 0;
}

.status-section {
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-left: 4px solid;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.metric-card.primary {
  border-left-color: var(--anthropic-blue);
}

.metric-card.success {
  border-left-color: var(--anthropic-success);
}

.metric-card.warning {
  border-left-color: var(--anthropic-warning);
}

.metric-card.info {
  border-left-color: var(--anthropic-orange);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.metric-card.primary .metric-icon {
  background: var(--anthropic-blue);
}

.metric-card.success .metric-icon {
  background: var(--anthropic-success);
}

.metric-card.warning .metric-icon {
  background: var(--anthropic-warning);
}

.metric-card.info .metric-icon {
  background: var(--anthropic-orange);
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthropic-dark);
  margin: 0;
}

.metric-label {
  color: #6C757D;
  margin: 0;
  font-size: 0.9rem;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 1.5rem;
}

.card-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  border-bottom: 1px solid #E9ECEF;
}

.card-body {
  padding: 1.5rem;
}

.config-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: #F8F9FA;
  color: #6C757D;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab-btn:hover {
  background: #E9ECEF;
  color: var(--anthropic-dark);
}

.tab-btn.active {
  background: var(--anthropic-blue);
  color: white;
}

.config-tab-content {
  margin-top: 1rem;
}

.config-section {
  background: #F8F9FA;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.config-section h4 {
  color: var(--anthropic-dark);
  margin-bottom: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.form-label {
  color: var(--anthropic-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 1px solid #DEE2E6;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.95rem;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--anthropic-blue);
  box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25);
}

.form-check-input:checked {
  background-color: var(--anthropic-blue);
  border-color: var(--anthropic-blue);
}

.notification-rules {
  max-height: 400px;
  overflow-y: auto;
}

.notification-rule {
  background: white;
  border: 1px solid #E9ECEF;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.integration-grid,
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
}

.integration-card,
.module-card {
  background: #F8F9FA;
  border: 2px solid #E9ECEF;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.2s ease;
}

.integration-card.active,
.module-card.active {
  border-color: var(--anthropic-blue);
  background: white;
}

.integration-header,
.module-header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.integration-logo,
.module-icon {
  width: 48px;
  height: 48px;
  background: var(--anthropic-blue);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.integration-info,
.module-info {
  flex: 1;
}

.integration-info h5,
.module-info h5 {
  color: var(--anthropic-dark);
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.integration-info p,
.module-info p {
  color: #6C757D;
  margin: 0;
  font-size: 0.9rem;
}

.version-badge {
  background: var(--anthropic-orange);
  color: white;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-top: 0.5rem;
  display: inline-block;
}

.integration-config {
  border-top: 1px solid #E9ECEF;
  padding-top: 1rem;
}

.module-stats {
  display: flex;
  gap: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #E9ECEF;
}

.stat {
  text-align: center;
}

.stat small {
  color: #6C757D;
  display: block;
  margin-bottom: 0.25rem;
}

.stat strong {
  color: var(--anthropic-dark);
  font-size: 0.9rem;
}

.stat strong.healthy {
  color: var(--anthropic-success);
}

.stat strong.error {
  color: var(--anthropic-danger);
}

.backup-list {
  max-height: 300px;
  overflow-y: auto;
}

.backup-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #E9ECEF;
}

.backup-item:last-child {
  border-bottom: none;
}

.backup-actions {
  display: flex;
  gap: 0.5rem;
}

.health-checks {
  max-height: 300px;
  overflow-y: auto;
}

.health-check-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #E9ECEF;
}

.health-check-item:last-child {
  border-bottom: none;
}

.status-indicator {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.status-indicator.healthy {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.status-indicator.warning {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.status-indicator.error {
  background: #F8D7DA;
  color: var(--anthropic-danger);
}

.status-indicator.unknown {
  background: #E9ECEF;
  color: #6C757D;
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: none;
}

.btn-primary {
  background: var(--anthropic-blue);
  color: white;
}

.btn-success {
  background: var(--anthropic-success);
  color: white;
}

.btn-outline-primary {
  border: 1px solid var(--anthropic-blue);
  color: var(--anthropic-blue);
}

.btn-outline-success {
  border: 1px solid var(--anthropic-success);
  color: var(--anthropic-success);
}

.btn-outline-danger {
  border: 1px solid var(--anthropic-danger);
  color: var(--anthropic-danger);
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .config-tabs {
    flex-direction: column;
  }

  .tab-btn {
    justify-content: center;
  }

  .integration-grid,
  .modules-grid {
    grid-template-columns: 1fr;
  }

  .integration-header,
  .module-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>