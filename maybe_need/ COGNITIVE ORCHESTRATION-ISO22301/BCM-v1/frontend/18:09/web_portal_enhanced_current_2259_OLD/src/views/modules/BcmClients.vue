<template>
  <div class="bcm-clients">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1>Multi-Tenant Client Management</h1>
        <p>Manage clients, subscriptions, users, and monitor resource usage</p>
      </div>
      <div class="header-actions">
        <button @click="showCreateClient = true" class="btn-primary">
          <i class="icon-plus"></i>
          New Client
        </button>
        <button @click="showAssistant = true" class="btn-secondary">
          <i class="icon-ai"></i>
          AI Insights
        </button>
      </div>
    </div>

    <!-- Analytics Dashboard -->
    <div class="analytics-dashboard">
      <div class="metric-card">
        <div class="metric-icon total">
          <i class="icon-clients"></i>
        </div>
        <div class="metric-content">
          <h3>{{ analytics.total_clients || 0 }}</h3>
          <p>Total Clients</p>
          <span class="metric-trend positive">+{{ analytics.new_clients_this_month || 0 }} this month</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon active">
          <i class="icon-active"></i>
        </div>
        <div class="metric-content">
          <h3>{{ analytics.active_clients || 0 }}</h3>
          <p>Active Clients</p>
          <span class="metric-percentage">{{ getActivePercentage() }}% of total</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon revenue">
          <i class="icon-revenue"></i>
        </div>
        <div class="metric-content">
          <h3>${{ formatCurrency(analytics.monthly_revenue) }}</h3>
          <p>Monthly Revenue</p>
          <span class="metric-trend positive">+{{ analytics.revenue_growth || 0 }}%</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon churn">
          <i class="icon-warning"></i>
        </div>
        <div class="metric-content">
          <h3>{{ analytics.churn_risk || 0 }}</h3>
          <p>At-Risk Clients</p>
          <span class="metric-percentage">{{ getChurnPercentage() }}% churn risk</span>
        </div>
      </div>
    </div>

    <!-- Filters & Controls -->
    <div class="controls-section">
      <div class="filters-group">
        <div class="search-box">
          <input
            v-model="filters.search"
            type="text"
            placeholder="Search clients..."
            class="search-input"
          />
        </div>
        <select v-model="filters.client_type" class="filter-select">
          <option value="">All Types</option>
          <option value="enterprise">Enterprise</option>
          <option value="business">Business</option>
          <option value="startup">Startup</option>
          <option value="nonprofit">Non-Profit</option>
        </select>
        <select v-model="filters.status" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="trial">Trial</option>
          <option value="suspended">Suspended</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="filters.subscription_plan" class="filter-select">
          <option value="">All Plans</option>
          <option v-for="plan in subscriptionPlans" :key="plan.id" :value="plan.id">
            {{ plan.name }}
          </option>
        </select>
      </div>
      <div class="action-group">
        <button @click="viewMode = 'cards'" :class="['view-btn', { active: viewMode === 'cards' }]">
          <i class="icon-grid"></i>
        </button>
        <button @click="viewMode = 'table'" :class="['view-btn', { active: viewMode === 'table' }]">
          <i class="icon-list"></i>
        </button>
        <button @click="exportClients" class="btn-outline">
          <i class="icon-download"></i>
          Export
        </button>
        <button @click="refreshData" class="btn-outline">
          <i class="icon-refresh"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="content-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- Clients Cards View -->
    <div v-if="activeTab === 'clients' && viewMode === 'cards'" class="clients-grid">
      <div
        v-for="client in filteredClients"
        :key="client.id"
        class="client-card"
        @click="viewClient(client)"
      >
        <div class="client-header">
          <div class="client-avatar">
            {{ getClientInitials(client.name) }}
          </div>
          <div class="client-status">
            <span :class="['status-indicator', client.subscription_status]"></span>
          </div>
        </div>

        <div class="client-info">
          <h4>{{ client.name }}</h4>
          <p class="client-code">{{ client.code }}</p>
          <p class="client-type">{{ formatClientType(client.client_type) }} • {{ client.industry }}</p>
        </div>

        <div class="subscription-info">
          <div class="subscription-plan">
            <i class="icon-plan"></i>
            <span>{{ getSubscriptionPlanName(client.subscription_plan) }}</span>
          </div>
          <div class="subscription-dates">
            <span>{{ formatDate(client.subscription_start) }} - {{ formatDate(client.subscription_end) }}</span>
          </div>
        </div>

        <div class="usage-metrics">
          <div class="usage-item">
            <div class="usage-header">
              <span>Users</span>
              <span>{{ client.user_count }}/{{ client.user_limit }}</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${calculateUsagePercentage(client.user_count, client.user_limit)}%` }"
              ></div>
            </div>
          </div>
          <div class="usage-item">
            <div class="usage-header">
              <span>Storage</span>
              <span>{{ formatStorage(client.storage_used) }}/{{ formatStorage(client.storage_limit) }}</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${calculateUsagePercentage(client.storage_used, client.storage_limit)}%` }"
              ></div>
            </div>
          </div>
        </div>

        <div class="client-actions">
          <button @click.stop="viewClient(client)" class="btn-sm">
            <i class="icon-view"></i>
            View
          </button>
          <button @click.stop="manageUsers(client)" class="btn-sm">
            <i class="icon-users"></i>
            Users
          </button>
          <button @click.stop="editClient(client)" class="btn-sm btn-primary">
            <i class="icon-edit"></i>
            Edit
          </button>
        </div>
      </div>
    </div>

    <!-- Clients Table View -->
    <div v-if="activeTab === 'clients' && viewMode === 'table'" class="clients-table">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Client</th>
              <th>Type</th>
              <th>Subscription</th>
              <th>Status</th>
              <th>Users</th>
              <th>Storage</th>
              <th>Last Activity</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="client in filteredClients" :key="client.id">
              <td>
                <div class="client-name-cell">
                  <div class="client-avatar small">
                    {{ getClientInitials(client.name) }}
                  </div>
                  <div>
                    <strong>{{ client.name }}</strong>
                    <span class="client-code">{{ client.code }}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="client-type-badge">{{ formatClientType(client.client_type) }}</span>
              </td>
              <td>
                <div class="subscription-cell">
                  <span>{{ getSubscriptionPlanName(client.subscription_plan) }}</span>
                  <span class="subscription-end">Ends {{ formatDate(client.subscription_end) }}</span>
                </div>
              </td>
              <td>
                <span :class="['status-badge', client.subscription_status]">
                  {{ formatSubscriptionStatus(client.subscription_status) }}
                </span>
              </td>
              <td>
                <div class="usage-cell">
                  <span>{{ client.user_count }}/{{ client.user_limit }}</span>
                  <div class="mini-progress">
                    <div
                      class="mini-progress-fill"
                      :style="{ width: `${calculateUsagePercentage(client.user_count, client.user_limit)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td>
                <div class="usage-cell">
                  <span>{{ formatStorage(client.storage_used) }}</span>
                  <div class="mini-progress">
                    <div
                      class="mini-progress-fill"
                      :style="{ width: `${calculateUsagePercentage(client.storage_used, client.storage_limit)}%` }"
                    ></div>
                  </div>
                </div>
              </td>
              <td>{{ formatDate(client.last_login) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="viewClient(client)" class="btn-icon" title="View">
                    <i class="icon-view"></i>
                  </button>
                  <button @click="manageUsers(client)" class="btn-icon" title="Users">
                    <i class="icon-users"></i>
                  </button>
                  <button @click="generateInvoice(client)" class="btn-icon" title="Invoice">
                    <i class="icon-invoice"></i>
                  </button>
                  <button @click="editClient(client)" class="btn-icon" title="Edit">
                    <i class="icon-edit"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="analytics-section">
      <div class="analytics-charts">
        <div class="chart-container">
          <h3>Revenue Trends</h3>
          <canvas ref="revenueChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Client Growth</h3>
          <canvas ref="growthChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Subscription Distribution</h3>
          <canvas ref="subscriptionChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Usage Patterns</h3>
          <canvas ref="usageChart"></canvas>
        </div>
      </div>

      <div class="insights-section">
        <div class="insight-card">
          <h4>Churn Analysis</h4>
          <div class="churn-metrics">
            <div class="churn-item">
              <span class="churn-risk high">High Risk</span>
              <span>{{ churnAnalysis.high_risk || 0 }} clients</span>
            </div>
            <div class="churn-item">
              <span class="churn-risk medium">Medium Risk</span>
              <span>{{ churnAnalysis.medium_risk || 0 }} clients</span>
            </div>
            <div class="churn-item">
              <span class="churn-risk low">Low Risk</span>
              <span>{{ churnAnalysis.low_risk || 0 }} clients</span>
            </div>
          </div>
        </div>

        <div class="insight-card">
          <h4>Resource Utilization</h4>
          <div class="resource-metrics">
            <div class="resource-item">
              <span>Average Storage Usage</span>
              <div class="resource-bar">
                <div class="resource-fill" :style="{ width: '65%' }"></div>
              </div>
              <span>65%</span>
            </div>
            <div class="resource-item">
              <span>Average User Utilization</span>
              <div class="resource-bar">
                <div class="resource-fill" :style="{ width: '78%' }"></div>
              </div>
              <span>78%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Billing Tab -->
    <div v-if="activeTab === 'billing'" class="billing-section">
      <div class="billing-summary">
        <div class="billing-card">
          <h4>Monthly Recurring Revenue</h4>
          <div class="billing-amount">${{ formatCurrency(billing.mrr) }}</div>
          <div class="billing-change positive">+{{ billing.mrr_growth }}% from last month</div>
        </div>
        <div class="billing-card">
          <h4>Outstanding Invoices</h4>
          <div class="billing-amount">{{ billing.outstanding_count }}</div>
          <div class="billing-value">${{ formatCurrency(billing.outstanding_amount) }}</div>
        </div>
        <div class="billing-card">
          <h4>Overdue Payments</h4>
          <div class="billing-amount">{{ billing.overdue_count }}</div>
          <div class="billing-value">${{ formatCurrency(billing.overdue_amount) }}</div>
        </div>
      </div>

      <div class="recent-invoices">
        <div class="section-header">
          <h3>Recent Invoices</h3>
          <button @click="generateBulkInvoices" class="btn-primary">
            <i class="icon-invoice"></i>
            Generate Invoices
          </button>
        </div>

        <div class="invoices-table">
          <table class="data-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Client</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="invoice in recentInvoices" :key="invoice.id">
                <td>{{ invoice.invoice_number }}</td>
                <td>{{ invoice.client_name }}</td>
                <td>${{ formatCurrency(invoice.amount) }}</td>
                <td>
                  <span :class="['invoice-status', invoice.status]">
                    {{ formatInvoiceStatus(invoice.status) }}
                  </span>
                </td>
                <td>{{ formatDate(invoice.due_date) }}</td>
                <td>
                  <div class="action-buttons">
                    <button @click="viewInvoice(invoice)" class="btn-icon">
                      <i class="icon-view"></i>
                    </button>
                    <button @click="downloadInvoice(invoice)" class="btn-icon">
                      <i class="icon-download"></i>
                    </button>
                    <button @click="sendInvoice(invoice)" class="btn-icon">
                      <i class="icon-send"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Assistant Panel -->
    <AssistantPanel
      v-if="showAssistant"
      @close="showAssistant = false"
      :context="assistantContext"
      module="clients"
    />

    <!-- Create Client Modal -->
    <div v-if="showCreateClient" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Client</h3>
          <button @click="closeCreateModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createClient">
            <div class="form-grid">
              <div class="form-group">
                <label>Client Name</label>
                <input v-model="newClient.name" type="text" required />
              </div>
              <div class="form-group">
                <label>Client Code</label>
                <input v-model="newClient.code" type="text" required />
              </div>
              <div class="form-group">
                <label>Client Type</label>
                <select v-model="newClient.client_type" required>
                  <option value="enterprise">Enterprise</option>
                  <option value="business">Business</option>
                  <option value="startup">Startup</option>
                  <option value="nonprofit">Non-Profit</option>
                </select>
              </div>
              <div class="form-group">
                <label>Industry</label>
                <input v-model="newClient.industry" type="text" required />
              </div>
              <div class="form-group">
                <label>Contact Name</label>
                <input v-model="newClient.contact_name" type="text" required />
              </div>
              <div class="form-group">
                <label>Contact Email</label>
                <input v-model="newClient.contact_email" type="email" required />
              </div>
              <div class="form-group">
                <label>Contact Phone</label>
                <input v-model="newClient.contact_phone" type="tel" />
              </div>
              <div class="form-group">
                <label>Subscription Plan</label>
                <select v-model="newClient.subscription_plan" required>
                  <option v-for="plan in subscriptionPlans" :key="plan.id" :value="plan.id">
                    {{ plan.name }} - ${{ plan.price_monthly }}/month
                  </option>
                </select>
              </div>
              <div class="form-group full-width">
                <label>Address</label>
                <textarea v-model="newClient.address" rows="3"></textarea>
              </div>
              <div class="form-group full-width">
                <label>Description</label>
                <textarea v-model="newClient.description" rows="2"></textarea>
              </div>
            </div>
            <div class="modal-actions">
              <button type="button" @click="closeCreateModal" class="btn-secondary">Cancel</button>
              <button type="submit" class="btn-primary">Create Client</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Client Detail Modal -->
    <div v-if="showClientDetail && selectedClient" class="modal-overlay" @click="closeDetailModal">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedClient.name }}</h3>
          <button @click="closeDetailModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="client-detail-tabs">
            <button
              v-for="detailTab in detailTabs"
              :key="detailTab.id"
              @click="activeDetailTab = detailTab.id"
              :class="['detail-tab', { active: activeDetailTab === detailTab.id }]"
            >
              {{ detailTab.label }}
            </button>
          </div>

          <!-- Overview Tab -->
          <div v-if="activeDetailTab === 'overview'" class="detail-section">
            <div class="detail-grid">
              <div class="detail-item">
                <label>Client Type</label>
                <span>{{ formatClientType(selectedClient.client_type) }}</span>
              </div>
              <div class="detail-item">
                <label>Industry</label>
                <span>{{ selectedClient.industry }}</span>
              </div>
              <div class="detail-item">
                <label>Status</label>
                <span :class="['status-badge', selectedClient.subscription_status]">
                  {{ formatSubscriptionStatus(selectedClient.subscription_status) }}
                </span>
              </div>
              <div class="detail-item">
                <label>Contact</label>
                <div>
                  <div>{{ selectedClient.contact_name }}</div>
                  <div>{{ selectedClient.contact_email }}</div>
                  <div>{{ selectedClient.contact_phone }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Usage Tab -->
          <div v-if="activeDetailTab === 'usage'" class="detail-section">
            <div class="usage-overview">
              <div class="usage-card">
                <h4>Users</h4>
                <div class="usage-value">{{ selectedClient.user_count }}/{{ selectedClient.user_limit }}</div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: `${calculateUsagePercentage(selectedClient.user_count, selectedClient.user_limit)}%` }"
                  ></div>
                </div>
              </div>
              <div class="usage-card">
                <h4>Storage</h4>
                <div class="usage-value">{{ formatStorage(selectedClient.storage_used) }}/{{ formatStorage(selectedClient.storage_limit) }}</div>
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: `${calculateUsagePercentage(selectedClient.storage_used, selectedClient.storage_limit)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { bcmClientsService } from '../services/bcmClients'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BcmClients',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const clients = ref([])
    const subscriptionPlans = ref([])
    const analytics = ref({})
    const churnAnalysis = ref({})
    const billing = ref({})
    const recentInvoices = ref([])
    const loading = ref(false)
    const showAssistant = ref(false)
    const showCreateClient = ref(false)
    const showClientDetail = ref(false)
    const selectedClient = ref(null)
    const activeTab = ref('clients')
    const activeDetailTab = ref('overview')
    const viewMode = ref('cards')

    // Filters
    const filters = reactive({
      search: '',
      client_type: '',
      status: '',
      subscription_plan: '',
      industry: ''
    })

    // Form data
    const newClient = reactive({
      name: '',
      code: '',
      client_type: 'business',
      industry: '',
      contact_name: '',
      contact_email: '',
      contact_phone: '',
      address: '',
      description: '',
      subscription_plan: ''
    })

    // Tabs configuration
    const tabs = [
      { id: 'clients', label: 'Clients', icon: 'icon-clients' },
      { id: 'analytics', label: 'Analytics', icon: 'icon-chart' },
      { id: 'billing', label: 'Billing', icon: 'icon-invoice' }
    ]

    const detailTabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'usage', label: 'Usage' },
      { id: 'users', label: 'Users' },
      { id: 'billing', label: 'Billing' }
    ]

    // Computed properties
    const filteredClients = computed(() => {
      return clients.value.filter(client => {
        const matchesSearch = !filters.search ||
          client.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          client.code.toLowerCase().includes(filters.search.toLowerCase())
        const matchesType = !filters.client_type ||
          client.client_type === filters.client_type
        const matchesStatus = !filters.status ||
          client.subscription_status === filters.status
        const matchesPlan = !filters.subscription_plan ||
          client.subscription_plan === filters.subscription_plan

        return matchesSearch && matchesType && matchesStatus && matchesPlan
      })
    })

    const assistantContext = computed(() => ({
      module: 'clients',
      totalClients: clients.value.length,
      activeClients: clients.value.filter(c => c.subscription_status === 'active').length,
      trialClients: clients.value.filter(c => c.subscription_status === 'trial').length,
      churnRisk: analytics.value.churn_risk || 0,
      monthlyRevenue: analytics.value.monthly_revenue || 0,
      filters: filters
    }))

    // Methods
    const loadData = async () => {
      loading.value = true
      try {
        const [
          clientsData,
          plansData,
          analyticsData,
          churnData,
          billingData,
          invoicesData
        ] = await Promise.all([
          bcmClientsService.getClients(filters),
          bcmClientsService.getSubscriptionPlans(),
          bcmClientsService.getClientAnalytics(filters),
          bcmClientsService.getChurnAnalysis(),
          bcmClientsService.getRevenueAnalytics(),
          []  // Placeholder for recent invoices
        ])

        clients.value = clientsData || []
        subscriptionPlans.value = plansData || []
        analytics.value = analyticsData || {}
        churnAnalysis.value = churnData || {}
        billing.value = billingData || {}
        recentInvoices.value = invoicesData || []
      } catch (error) {
        console.error('Error loading client data:', error)
      } finally {
        loading.value = false
      }
    }

    const createClient = async () => {
      try {
        loading.value = true
        await bcmClientsService.createClient(newClient)
        await loadData()
        closeCreateModal()
        resetNewClient()
      } catch (error) {
        console.error('Error creating client:', error)
      } finally {
        loading.value = false
      }
    }

    const viewClient = (client) => {
      selectedClient.value = client
      showClientDetail.value = true
      activeDetailTab.value = 'overview'
    }

    const editClient = (client) => {
      console.log('Edit client:', client)
      // Open edit modal
    }

    const manageUsers = (client) => {
      console.log('Manage users for client:', client)
      // Navigate to user management
    }

    const generateInvoice = async (client) => {
      try {
        loading.value = true
        await bcmClientsService.generateInvoice(client.id, new Date().toISOString().substring(0, 7))
        await loadData()
      } catch (error) {
        console.error('Error generating invoice:', error)
      } finally {
        loading.value = false
      }
    }

    const generateBulkInvoices = async () => {
      try {
        loading.value = true
        // Generate invoices for all active clients
        const activeClients = clients.value.filter(c => c.subscription_status === 'active')
        for (const client of activeClients) {
          await bcmClientsService.generateInvoice(client.id, new Date().toISOString().substring(0, 7))
        }
        await loadData()
      } catch (error) {
        console.error('Error generating bulk invoices:', error)
      } finally {
        loading.value = false
      }
    }

    const exportClients = () => {
      console.log('Export clients')
      // Implement export functionality
    }

    const refreshData = () => {
      loadData()
    }

    const closeCreateModal = () => {
      showCreateClient.value = false
    }

    const closeDetailModal = () => {
      showClientDetail.value = false
      selectedClient.value = null
    }

    const resetNewClient = () => {
      Object.keys(newClient).forEach(key => {
        newClient[key] = key === 'client_type' ? 'business' : ''
      })
    }

    // Utility functions
    const formatDate = (date) => {
      return date ? new Date(date).toLocaleDateString() : ''
    }

    const formatCurrency = (amount) => {
      return amount ? parseFloat(amount).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }) : '0.00'
    }

    const formatStorage = (bytes) => {
      return bcmClientsService.formatStorageSize(bytes)
    }

    const formatClientType = (type) => {
      return bcmClientsService.formatClientType(type)
    }

    const formatSubscriptionStatus = (status) => {
      return bcmClientsService.formatSubscriptionStatus(status)
    }

    const formatInvoiceStatus = (status) => {
      const statuses = {
        draft: 'Draft',
        sent: 'Sent',
        paid: 'Paid',
        overdue: 'Overdue',
        cancelled: 'Cancelled'
      }
      return statuses[status] || status
    }

    const getClientInitials = (name) => {
      return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2)
    }

    const getSubscriptionPlanName = (planId) => {
      const plan = subscriptionPlans.value.find(p => p.id === planId)
      return plan ? plan.name : 'Unknown'
    }

    const calculateUsagePercentage = (used, limit) => {
      return bcmClientsService.calculateUsagePercentage(used, limit)
    }

    const getActivePercentage = () => {
      const total = analytics.value.total_clients || 0
      const active = analytics.value.active_clients || 0
      return total > 0 ? Math.round((active / total) * 100) : 0
    }

    const getChurnPercentage = () => {
      const total = analytics.value.total_clients || 0
      const atRisk = analytics.value.churn_risk || 0
      return total > 0 ? Math.round((atRisk / total) * 100) : 0
    }

    const viewInvoice = (invoice) => {
      console.log('View invoice:', invoice)
    }

    const downloadInvoice = (invoice) => {
      console.log('Download invoice:', invoice)
    }

    const sendInvoice = (invoice) => {
      console.log('Send invoice:', invoice)
    }

    // Watchers
    watch(filters, () => {
      loadData()
    }, { deep: true })

    // Lifecycle
    onMounted(() => {
      loadData()
    })

    return {
      // Data
      clients,
      subscriptionPlans,
      analytics,
      churnAnalysis,
      billing,
      recentInvoices,
      loading,
      showAssistant,
      showCreateClient,
      showClientDetail,
      selectedClient,
      activeTab,
      activeDetailTab,
      viewMode,
      filters,
      newClient,
      tabs,
      detailTabs,

      // Computed
      filteredClients,
      assistantContext,

      // Methods
      loadData,
      createClient,
      viewClient,
      editClient,
      manageUsers,
      generateInvoice,
      generateBulkInvoices,
      exportClients,
      refreshData,
      closeCreateModal,
      closeDetailModal,
      resetNewClient,
      formatDate,
      formatCurrency,
      formatStorage,
      formatClientType,
      formatSubscriptionStatus,
      formatInvoiceStatus,
      getClientInitials,
      getSubscriptionPlanName,
      calculateUsagePercentage,
      getActivePercentage,
      getChurnPercentage,
      viewInvoice,
      downloadInvoice,
      sendInvoice
    }
  }
}
</script>

<style scoped>
.bcm-clients {
  padding: 24px;
  background: #f8f9fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  color: #1A1A1A;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.header-content p {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary, .btn-secondary, .btn-outline {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #FF6B35;
  color: white;
}

.btn-primary:hover {
  background: #e55a2b;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #4A90E2;
  color: white;
}

.btn-secondary:hover {
  background: #357abd;
  transform: translateY(-1px);
}

.btn-outline {
  background: white;
  color: #666;
  border: 2px solid #e1e5e9;
}

.btn-outline:hover {
  border-color: #4A90E2;
  color: #4A90E2;
  transform: translateY(-1px);
}

.analytics-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.metric-icon.total {
  background: linear-gradient(135deg, #1A1A1A, #4A90E2);
}

.metric-icon.active {
  background: linear-gradient(135deg, #4caf50, #81c784);
}

.metric-icon.revenue {
  background: linear-gradient(135deg, #FF6B35, #ff9800);
}

.metric-icon.churn {
  background: linear-gradient(135deg, #f44336, #e57373);
}

.metric-icon i {
  font-size: 24px;
  color: white;
}

.metric-content h3 {
  margin: 0 0 4px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1A1A1A;
}

.metric-content p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.metric-trend, .metric-percentage {
  font-size: 12px;
  font-weight: 500;
}

.metric-trend.positive {
  color: #4caf50;
}

.metric-percentage {
  color: #4A90E2;
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filters-group {
  display: flex;
  gap: 16px;
  flex: 1;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #4A90E2;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  background: white;
  font-size: 14px;
  min-width: 150px;
}

.action-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

.view-btn {
  width: 40px;
  height: 40px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.view-btn.active {
  border-color: #4A90E2;
  background: #4A90E2;
  color: white;
}

.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  background: white;
  padding: 8px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  transition: all 0.2s;
}

.tab-button.active {
  background: #FF6B35;
  color: white;
}

.clients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.client-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s;
}

.client-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.client-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.client-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.client-avatar.small {
  width: 32px;
  height: 32px;
  font-size: 14px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.active { background: #4caf50; }
.status-indicator.trial { background: #ff9800; }
.status-indicator.suspended { background: #f44336; }
.status-indicator.cancelled { background: #666; }

.client-info h4 {
  margin: 0 0 8px 0;
  color: #1A1A1A;
  font-weight: 600;
  font-size: 18px;
}

.client-code {
  color: #666;
  font-size: 14px;
  margin-bottom: 4px;
}

.client-type {
  color: #4A90E2;
  font-size: 14px;
  font-weight: 500;
}

.subscription-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.subscription-plan {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #1A1A1A;
}

.subscription-dates {
  color: #666;
  font-size: 14px;
}

.usage-metrics {
  margin-bottom: 20px;
}

.usage-item {
  margin-bottom: 16px;
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #81c784);
  border-radius: 4px;
  transition: width 0.3s;
}

.client-actions {
  display: flex;
  gap: 12px;
}

.btn-sm {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 2px solid #e1e5e9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-sm:hover {
  border-color: #4A90E2;
  color: #4A90E2;
}

.btn-sm.btn-primary {
  background: #FF6B35;
  border-color: #FF6B35;
  color: white;
}

.btn-sm.btn-primary:hover {
  background: #e55a2b;
}

.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f8f9fa;
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: #1A1A1A;
  border-bottom: 1px solid #e1e5e9;
}

.data-table td {
  padding: 16px;
  border-bottom: 1px solid #e1e5e9;
}

.client-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.client-name-cell strong {
  display: block;
  color: #1A1A1A;
  margin-bottom: 4px;
}

.client-type-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  background: #e3f2fd;
  color: #1976d2;
}

.subscription-cell span:first-child {
  display: block;
  font-weight: 500;
  color: #1A1A1A;
}

.subscription-end {
  color: #666;
  font-size: 14px;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active { background: #e8f5e8; color: #4caf50; }
.status-badge.trial { background: #fff3e0; color: #ff9800; }
.status-badge.suspended { background: #ffebee; color: #f44336; }
.status-badge.cancelled { background: #f5f5f5; color: #666; }

.usage-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mini-progress {
  width: 60px;
  height: 4px;
  background: #e1e5e9;
  border-radius: 2px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  background: #4caf50;
  border-radius: 2px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: #f8f9fa;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #4A90E2;
  color: white;
  transform: translateY(-1px);
}

.analytics-charts {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.chart-container canvas {
  width: 100%;
  height: 300px;
  background: #f8f9fa;
  border-radius: 8px;
}

.insights-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.insight-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.insight-card h4 {
  margin: 0 0 20px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.churn-metrics, .resource-metrics {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.churn-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.churn-risk {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.churn-risk.high { background: #ffebee; color: #f44336; }
.churn-risk.medium { background: #fff3e0; color: #ff9800; }
.churn-risk.low { background: #e8f5e8; color: #4caf50; }

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.resource-bar {
  flex: 1;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B35, #4A90E2);
  border-radius: 4px;
}

.billing-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px;
}

.billing-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.billing-card {
  text-align: center;
  padding: 24px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
}

.billing-card h4 {
  margin: 0 0 16px 0;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.billing-amount {
  font-size: 32px;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 8px;
}

.billing-change {
  font-size: 14px;
  font-weight: 500;
}

.billing-change.positive {
  color: #4caf50;
}

.billing-value {
  color: #666;
  font-size: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.invoice-status {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.invoice-status.draft { background: #f5f5f5; color: #666; }
.invoice-status.sent { background: #e3f2fd; color: #1976d2; }
.invoice-status.paid { background: #e8f5e8; color: #4caf50; }
.invoice-status.overdue { background: #ffebee; color: #f44336; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content.large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #1A1A1A;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4A90E2;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e1e5e9;
}

.client-detail-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e1e5e9;
}

.detail-tab {
  padding: 12px 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.detail-tab.active {
  color: #FF6B35;
  border-bottom-color: #FF6B35;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

.usage-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.usage-card {
  padding: 24px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  text-align: center;
}

.usage-card h4 {
  margin: 0 0 16px 0;
  color: #1A1A1A;
  font-weight: 600;
}

.usage-value {
  font-size: 24px;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 16px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e1e5e9;
  border-top: 4px solid #FF6B35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .bcm-clients {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: center;
  }

  .analytics-dashboard {
    grid-template-columns: 1fr;
  }

  .controls-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .filters-group {
    flex-direction: column;
  }

  .clients-grid {
    grid-template-columns: 1fr;
  }

  .analytics-charts {
    grid-template-columns: 1fr;
  }

  .insights-section {
    grid-template-columns: 1fr;
  }

  .billing-summary {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .usage-overview {
    grid-template-columns: 1fr;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>