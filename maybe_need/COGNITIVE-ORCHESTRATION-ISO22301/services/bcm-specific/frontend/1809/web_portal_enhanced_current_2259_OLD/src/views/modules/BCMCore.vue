<template>
  <div class="bcm-core-dashboard">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="dashboard-title">BCM Core Dashboard</h1>
            <p class="dashboard-subtitle">Business Continuity Foundation Layer</p>
          </div>
          <div class="col-md-4 text-end">
            <div class="status-indicator">
              <span class="status-dot" :class="systemStatus"></span>
              <span class="status-text">{{ systemStatusText }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Overview -->
    <div class="metrics-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card primary">
              <div class="metric-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.riskScore }}%</h3>
                <p class="metric-label">Risk Coverage</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.complianceLevel }}%</h3>
                <p class="metric-label">ISO 22301 Compliance</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-clock"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.avgRTO }}h</h3>
                <p class="metric-label">Average RTO</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-building"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.activeProcesses }}</h3>
                <p class="metric-label">Critical Processes</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <!-- Organization Context -->
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>Organization Context</h3>
                <button class="btn btn-outline-primary btn-sm" @click="refreshContext">
                  <i class="fas fa-sync"></i> Refresh
                </button>
              </div>
              <div class="card-body">
                <div class="context-item" v-for="item in organizationContext" :key="item.id">
                  <div class="context-title">{{ item.name }}</div>
                  <div class="context-value">{{ item.value }}</div>
                  <div class="context-status" :class="item.status">{{ item.statusText }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Activities -->
          <div class="col-md-6">
            <div class="content-card">
              <div class="card-header">
                <h3>Recent Activities</h3>
                <router-link to="/activities" class="btn btn-outline-primary btn-sm">
                  View All
                </router-link>
              </div>
              <div class="card-body">
                <div class="activity-timeline">
                  <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
                    <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
                    <div class="activity-icon" :class="activity.type">
                      <i :class="activity.icon"></i>
                    </div>
                    <div class="activity-content">
                      <div class="activity-title">{{ activity.title }}</div>
                      <div class="activity-description">{{ activity.description }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="row mt-4">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <h3>Quick Actions</h3>
              </div>
              <div class="card-body">
                <div class="quick-actions-grid">
                  <button class="action-btn primary" @click="startBIA">
                    <i class="fas fa-chart-line"></i>
                    <span>Start BIA</span>
                  </button>
                  <button class="action-btn success" @click="createIncident">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Report Incident</span>
                  </button>
                  <button class="action-btn warning" @click="scheduleTraining">
                    <i class="fas fa-graduation-cap"></i>
                    <span>Schedule Training</span>
                  </button>
                  <button class="action-btn info" @click="generateReport">
                    <i class="fas fa-file-alt"></i>
                    <span>Generate Report</span>
                  </button>
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
import { useRouter } from 'vue-router'

export default {
  name: 'BCMCore',
  setup() {
    const router = useRouter()

    // Reactive data
    const systemStatus = ref('healthy')
    const systemStatusText = ref('All Systems Operational')

    const metrics = reactive({
      riskScore: 87,
      complianceLevel: 92,
      avgRTO: 4.2,
      activeProcesses: 23
    })

    const organizationContext = ref([
      {
        id: 1,
        name: 'BCMS Scope',
        value: 'Global Operations',
        status: 'approved',
        statusText: 'Approved'
      },
      {
        id: 2,
        name: 'Risk Appetite',
        value: 'Moderate',
        status: 'current',
        statusText: 'Current'
      },
      {
        id: 3,
        name: 'Last Review',
        value: '2025-09-01',
        status: 'pending',
        statusText: 'Pending Update'
      }
    ])

    const recentActivities = ref([
      {
        id: 1,
        title: 'BIA Analysis Completed',
        description: 'Payment Processing critical analysis updated',
        timestamp: new Date(Date.now() - 1000 * 60 * 30),
        type: 'success',
        icon: 'fas fa-check'
      },
      {
        id: 2,
        title: 'Risk Assessment Updated',
        description: 'IT Infrastructure risk level modified',
        timestamp: new Date(Date.now() - 1000 * 60 * 120),
        type: 'warning',
        icon: 'fas fa-exclamation-triangle'
      },
      {
        id: 3,
        title: 'Training Session Scheduled',
        description: 'BCM Awareness training for Q4',
        timestamp: new Date(Date.now() - 1000 * 60 * 180),
        type: 'info',
        icon: 'fas fa-calendar'
      }
    ])

    // Methods
    const refreshContext = async () => {
      try {
        const response = await fetch('/api/bcm/context')
        const data = await response.json()
        organizationContext.value = data.context
      } catch (error) {
        console.error('Failed to refresh context:', error)
      }
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / (1000 * 60))

      if (minutes < 60) return `${minutes}m ago`
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `${hours}h ago`
      const days = Math.floor(hours / 24)
      return `${days}d ago`
    }

    const startBIA = () => {
      router.push('/bia')
    }

    const createIncident = () => {
      router.push('/incidents/new')
    }

    const scheduleTraining = () => {
      router.push('/training/schedule')
    }

    const generateReport = () => {
      router.push('/reports/generate')
    }

    // Load data on mount
    onMounted(() => {
      refreshContext()
    })

    return {
      systemStatus,
      systemStatusText,
      metrics,
      organizationContext,
      recentActivities,
      refreshContext,
      formatTime,
      startBIA,
      createIncident,
      scheduleTraining,
      generateReport
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

.bcm-core-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.dashboard-header {
  background: white;
  border-bottom: 2px solid var(--anthropic-blue);
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.dashboard-title {
  color: var(--anthropic-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
}

.dashboard-subtitle {
  color: #6C757D;
  font-size: 1.1rem;
  margin: 0.5rem 0 0 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.healthy {
  background: var(--anthropic-success);
}

.metrics-section {
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
  display: flex;
  justify-content: between;
  align-items: center;
  border-bottom: 1px solid #E9ECEF;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: var(--anthropic-dark);
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.card-body {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.context-item {
  display: flex;
  justify-content: between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #F8F9FA;
}

.context-item:last-child {
  border-bottom: none;
}

.context-title {
  font-weight: 500;
  color: var(--anthropic-dark);
}

.context-value {
  color: #6C757D;
}

.context-status {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.context-status.approved {
  background: #D4EDDA;
  color: var(--anthropic-success);
}

.context-status.current {
  background: #D1ECF1;
  color: var(--anthropic-blue);
}

.context-status.pending {
  background: #FFF3CD;
  color: var(--anthropic-warning);
}

.activity-timeline {
  position: relative;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #F8F9FA;
  position: relative;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  min-width: 80px;
  font-size: 0.8rem;
  color: #6C757D;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.9rem;
}

.activity-icon.success {
  background: var(--anthropic-success);
}

.activity-icon.warning {
  background: var(--anthropic-warning);
}

.activity-icon.info {
  background: var(--anthropic-blue);
}

.activity-title {
  font-weight: 500;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.activity-description {
  color: #6C757D;
  font-size: 0.9rem;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  border: 2px solid;
  border-radius: 12px;
  background: white;
  transition: all 0.2s ease;
  text-decoration: none;
  cursor: pointer;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.action-btn.primary {
  border-color: var(--anthropic-blue);
  color: var(--anthropic-blue);
}

.action-btn.primary:hover {
  background: var(--anthropic-blue);
  color: white;
}

.action-btn.success {
  border-color: var(--anthropic-success);
  color: var(--anthropic-success);
}

.action-btn.success:hover {
  background: var(--anthropic-success);
  color: white;
}

.action-btn.warning {
  border-color: var(--anthropic-warning);
  color: var(--anthropic-warning);
}

.action-btn.warning:hover {
  background: var(--anthropic-warning);
  color: white;
}

.action-btn.info {
  border-color: var(--anthropic-orange);
  color: var(--anthropic-orange);
}

.action-btn.info:hover {
  background: var(--anthropic-orange);
  color: white;
}

.action-btn i {
  font-size: 1.5rem;
}

.action-btn span {
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-title {
    font-size: 2rem;
  }

  .metric-card {
    margin-bottom: 0.5rem;
  }

  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>