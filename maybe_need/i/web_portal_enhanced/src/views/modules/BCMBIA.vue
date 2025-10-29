<template>
  <div class="bcm-bia-module">
    <!-- AI Assistant Integration -->
    <AssistantPanel
      :context="'bia'"
      :currentData="biaData"
      @ai-suggestion="handleAISuggestion"
      @ai-action="handleAIAction"
    />

    <!-- Page Header -->
    <div class="page-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Business Impact Analysis</h1>
            <p class="page-subtitle">AI-Enhanced BIA Engine v2.0</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-primary" @click="startNewAnalysis">
              <i class="fas fa-plus"></i> New Analysis
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- BIA Dashboard -->
    <div class="bia-dashboard">
      <div class="container-fluid">
        <!-- Status Cards -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="status-card critical">
              <div class="status-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="status-content">
                <h3>{{ biaMetrics.criticalProcesses }}</h3>
                <p>Critical Processes</p>
                <small>RTO less than 4h</small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="status-card financial">
              <div class="status-icon">
                <i class="fas fa-dollar-sign"></i>
              </div>
              <div class="status-content">
                <h3>${{ formatCurrency(biaMetrics.financialImpact) }}</h3>
                <p>Annual Risk Exposure</p>
                <small>ML calculated</small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="status-card optimization">
              <div class="status-icon">
                <i class="fas fa-brain"></i>
              </div>
              <div class="status-content">
                <h3>{{ biaMetrics.optimizationScore }}%</h3>
                <p>AI Optimization</p>
                <small>RTO/RPO efficiency</small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="status-card dependency">
              <div class="status-icon">
                <i class="fas fa-project-diagram"></i>
              </div>
              <div class="status-content">
                <h3>{{ biaMetrics.dependencyDepth }}</h3>
                <p>Max Dependency Depth</p>
                <small>Cascade analysis</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Grid -->
        <div class="row">
          <!-- Process Analysis Table -->
          <div class="col-md-8">
            <div class="analysis-card">
              <div class="card-header">
                <h3>Business Process Analysis</h3>
                <div class="header-actions">
                  <button class="btn btn-outline-primary btn-sm" @click="refreshAnalysis">
                    <i class="fas fa-sync"></i> Refresh
                  </button>
                  <button class="btn btn-success btn-sm" @click="runAIOptimization">
                    <i class="fas fa-brain"></i> AI Optimize
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Process Name</th>
                        <th>Criticality</th>
                        <th>RTO</th>
                        <th>RPO</th>
                        <th>Financial Impact</th>
                        <th>AI Confidence</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="process in businessProcesses" :key="process.id">
                        <td>
                          <div class="process-name">
                            {{ process.name }}
                            <small class="text-muted d-block">{{ process.description }}</small>
                          </div>
                        </td>
                        <td>
                          <span class="badge" :class="getCriticalityClass(process.criticality)">
                            {{ process.criticality }}
                          </span>
                        </td>
                        <td>
                          <span class="rto-value" :class="getRTOClass(process.rto)">
                            {{ process.rto }}h
                          </span>
                        </td>
                        <td>{{ process.rpo }}min</td>
                        <td>${{ formatCurrency(process.financialImpact) }}</td>
                        <td>
                          <div class="confidence-indicator">
                            <div class="confidence-bar">
                              <div class="confidence-fill" :style="{ width: process.aiConfidence + '%' }"></div>
                            </div>
                            <span class="confidence-text">{{ process.aiConfidence }}%</span>
                          </div>
                        </td>
                        <td>
                          <div class="action-buttons">
                            <button class="btn btn-sm btn-outline-primary" @click="editProcess(process)">
                              <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-info" @click="analyzeProcess(process)">
                              <i class="fas fa-chart-line"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Insights Panel -->
          <div class="col-md-4">
            <div class="insights-card">
              <div class="card-header">
                <h3>AI Insights</h3>
                <span class="ai-status">
                  <i class="fas fa-brain text-primary"></i> Active
                </span>
              </div>
              <div class="card-body">
                <!-- AI Recommendations -->
                <div class="recommendation-section">
                  <h5>Recommendations</h5>
                  <div class="recommendation-item" v-for="rec in aiRecommendations" :key="rec.id">
                    <div class="rec-icon" :class="rec.priority">
                      <i :class="rec.icon"></i>
                    </div>
                    <div class="rec-content">
                      <div class="rec-title">{{ rec.title }}</div>
                      <div class="rec-description">{{ rec.description }}</div>
                      <button class="btn btn-sm btn-outline-primary mt-2" @click="applyRecommendation(rec)">
                        Apply
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Risk Heatmap -->
                <div class="heatmap-section mt-4">
                  <h5>Risk Heat Map</h5>
                  <div class="heatmap-grid">
                    <div
                      v-for="cell in riskHeatmap"
                      :key="cell.id"
                      class="heatmap-cell"
                      :class="cell.level"
                      :title="cell.tooltip"
                    >
                      {{ cell.value }}
                    </div>
                  </div>
                </div>

                <!-- Quick Analysis -->
                <div class="quick-analysis mt-4">
                  <h5>Quick Analysis</h5>
                  <div class="analysis-controls">
                    <select v-model="selectedIndustry" class="form-select mb-3">
                      <option value="">Select Industry</option>
                      <option value="healthcare">Healthcare</option>
                      <option value="finance">Financial Services</option>
                      <option value="manufacturing">Manufacturing</option>
                      <option value="technology">Technology</option>
                    </select>
                    <button class="btn btn-warning w-100" @click="runQuickAnalysis">
                      <i class="fas fa-zap"></i> Quick AI Analysis
                    </button>
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
import { ref, reactive, onMounted, computed } from 'vue'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'
import bcmBIAService from '@/services/bcmBIA.js'

export default {
  name: 'BCMBIA',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive data
    const biaData = reactive({
      currentAnalysis: null,
      selectedProcesses: [],
      analysisProgress: 0
    })

    const biaMetrics = reactive({
      criticalProcesses: 12,
      financialImpact: 2450000,
      optimizationScore: 87,
      dependencyDepth: 4
    })

    const businessProcesses = ref([
      {
        id: 1,
        name: 'Payment Processing',
        description: 'Core payment system operations',
        criticality: 'Critical',
        rto: 2,
        rpo: 15,
        financialImpact: 50000,
        aiConfidence: 95
      },
      {
        id: 2,
        name: 'Customer Support',
        description: '24/7 customer service operations',
        criticality: 'High',
        rto: 4,
        rpo: 60,
        financialImpact: 15000,
        aiConfidence: 88
      },
      {
        id: 3,
        name: 'Data Backup',
        description: 'Daily backup procedures',
        criticality: 'Medium',
        rto: 8,
        rpo: 240,
        financialImpact: 5000,
        aiConfidence: 92
      }
    ])

    const aiRecommendations = ref([
      {
        id: 1,
        title: 'Optimize Payment RTO',
        description: 'AI suggests reducing RTO from 2h to 1.5h based on industry benchmarks',
        priority: 'high',
        icon: 'fas fa-clock'
      },
      {
        id: 2,
        title: 'Dependency Analysis',
        description: 'Customer Support depends on Payment - consider parallel recovery',
        priority: 'medium',
        icon: 'fas fa-project-diagram'
      }
    ])

    const riskHeatmap = ref([
      { id: 1, value: 'H', level: 'high', tooltip: 'High Impact, High Likelihood' },
      { id: 2, value: 'M', level: 'medium', tooltip: 'Medium Impact, Low Likelihood' },
      { id: 3, value: 'L', level: 'low', tooltip: 'Low Impact, Low Likelihood' },
      { id: 4, value: 'H', level: 'high', tooltip: 'High Impact, Medium Likelihood' }
    ])

    const selectedIndustry = ref('')

    // Methods
    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('en-US').format(amount)
    }

    const getCriticalityClass = (criticality) => {
      const classes = {
        'Critical': 'bg-danger',
        'High': 'bg-warning',
        'Medium': 'bg-info',
        'Low': 'bg-success'
      }
      return classes[criticality] || 'bg-secondary'
    }

    const getRTOClass = (rto) => {
      if (rto <= 2) return 'text-danger fw-bold'
      if (rto <= 4) return 'text-warning fw-bold'
      return 'text-success'
    }

    const startNewAnalysis = async () => {
      try {
        await bcmBIAService.startAnalysis()
        // Refresh data
        await loadBIAData()
      } catch (error) {
        console.error('Failed to start analysis:', error)
      }
    }

    const refreshAnalysis = async () => {
      await loadBIAData()
    }

    const runAIOptimization = async () => {
      try {
        const result = await bcmBIAService.runAIOptimization(businessProcesses.value)
        aiRecommendations.value = result.recommendations
      } catch (error) {
        console.error('AI optimization failed:', error)
      }
    }

    const runQuickAnalysis = async () => {
      if (!selectedIndustry.value) return

      try {
        const result = await bcmBIAService.quickAnalysis(selectedIndustry.value)
        businessProcesses.value = result.processes
        biaMetrics.criticalProcesses = result.metrics.critical
      } catch (error) {
        console.error('Quick analysis failed:', error)
      }
    }

    const editProcess = (process) => {
      console.log('Edit process:', process.name)
    }

    const analyzeProcess = async (process) => {
      try {
        await bcmBIAService.analyzeProcess(process.id)
      } catch (error) {
        console.error('Process analysis failed:', error)
      }
    }

    const applyRecommendation = async (recommendation) => {
      try {
        await bcmBIAService.applyRecommendation(recommendation.id)
        await refreshAnalysis()
      } catch (error) {
        console.error('Failed to apply recommendation:', error)
      }
    }

    const handleAISuggestion = (suggestion) => {
      console.log('AI Suggestion:', suggestion)
    }

    const handleAIAction = (action) => {
      console.log('AI Action:', action)
    }

    const loadBIAData = async () => {
      try {
        const [processes, metrics, recommendations] = await Promise.all([
          bcmBIAService.getBusinessProcesses(),
          bcmBIAService.getBIAMetrics(),
          bcmBIAService.getAIRecommendations()
        ])

        businessProcesses.value = processes
        Object.assign(biaMetrics, metrics)
        aiRecommendations.value = recommendations
      } catch (error) {
        console.error('Failed to load BIA data:', error)
      }
    }

    // Load data on mount
    onMounted(() => {
      loadBIAData()
    })

    return {
      biaData,
      biaMetrics,
      businessProcesses,
      aiRecommendations,
      riskHeatmap,
      selectedIndustry,
      formatCurrency,
      getCriticalityClass,
      getRTOClass,
      startNewAnalysis,
      refreshAnalysis,
      runAIOptimization,
      runQuickAnalysis,
      editProcess,
      analyzeProcess,
      applyRecommendation,
      handleAISuggestion,
      handleAIAction
    }
  }
}
</script>

<style scoped>
/* Anthropic colors for BIA module */
.bcm-bia-module {
  min-height: 100vh;
  background: linear-gradient(135deg, #F8F9FA 0%, #E3F2FD 100%);
}

.page-header {
  background: white;
  border-bottom: 3px solid #4A90E2;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.page-title {
  color: #1A1A1A;
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
}

.page-subtitle {
  color: #6C757D;
  font-size: 1.1rem;
  margin: 0.5rem 0 0 0;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border-left: 4px solid;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.2s ease;
}

.status-card:hover {
  transform: translateY(-2px);
}

.status-card.critical {
  border-left-color: #DC3545;
}

.status-card.financial {
  border-left-color: #28A745;
}

.status-card.optimization {
  border-left-color: #FF6B35;
}

.status-card.dependency {
  border-left-color: #4A90E2;
}

.status-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.status-card.critical .status-icon {
  background: #DC3545;
}

.status-card.financial .status-icon {
  background: #28A745;
}

.status-card.optimization .status-icon {
  background: #FF6B35;
}

.status-card.dependency .status-icon {
  background: #4A90E2;
}

.analysis-card, .insights-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 1.5rem;
}

.card-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #E9ECEF;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: #1A1A1A;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-bar {
  width: 60px;
  height: 8px;
  background: #E9ECEF;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B35, #4A90E2);
  transition: width 0.3s ease;
}

.confidence-text {
  font-size: 0.8rem;
  color: #6C757D;
}

.recommendation-item {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #F8F9FA;
}

.rec-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.rec-icon.high {
  background: #DC3545;
}

.rec-icon.medium {
  background: #FFC107;
}

.rec-title {
  font-weight: 500;
  color: #1A1A1A;
  margin-bottom: 0.25rem;
}

.rec-description {
  color: #6C757D;
  font-size: 0.9rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-top: 1rem;
}

.heatmap-cell {
  aspect-ratio: 1;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  cursor: pointer;
}

.heatmap-cell.high {
  background: #DC3545;
}

.heatmap-cell.medium {
  background: #FFC107;
}

.heatmap-cell.low {
  background: #28A745;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .status-card {
    margin-bottom: 1rem;
  }

  .table-responsive {
    font-size: 0.9rem;
  }
}
</style>