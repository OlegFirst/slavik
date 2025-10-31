<template>
  <div class="bcm-intelligent-base">
    <!-- Header Section -->
    <div class="header-section">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">
              <i class="fas fa-brain me-2"></i>
              AI Intelligence Base
            </h1>
            <p class="page-subtitle">
              AI-powered insights, automation, and intelligent analysis for Business Continuity Management
            </p>
          </div>
          <div class="col-md-4 text-end">
            <div class="header-actions">
              <button class="btn btn-outline-primary me-2" @click="refreshAiInsights">
                <i class="fas fa-sync me-1"></i>
                Refresh Insights
              </button>
              <button class="btn btn-primary" @click="showConfigModal = true">
                <i class="fas fa-cog me-1"></i>
                AI Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Dashboard Overview -->
    <div class="dashboard-section">
      <div class="container-fluid">
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-chart-line"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ aiMetrics.analysisCount || 0 }}</div>
                <div class="metric-label">AI Analyses</div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-lightbulb"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ aiMetrics.recommendations || 0 }}</div>
                <div class="metric-label">Recommendations</div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-robot"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ aiMetrics.automationTasks || 0 }}</div>
                <div class="metric-label">Automation Tasks</div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card">
              <div class="metric-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <div class="metric-content">
                <div class="metric-value">{{ aiMetrics.riskScore || 0 }}%</div>
                <div class="metric-label">Risk Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <!-- Left Panel - AI Insights -->
          <div class="col-md-8">
            <!-- AI Recommendations -->
            <div class="content-card mb-4">
              <div class="card-header">
                <h5>
                  <i class="fas fa-lightbulb me-2"></i>
                  AI Recommendations
                </h5>
                <div class="card-actions">
                  <button class="btn btn-outline-secondary btn-sm" @click="loadRecommendations">
                    <i class="fas fa-sync"></i>
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div v-if="loading.recommendations" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else-if="recommendations.length === 0" class="text-center py-4 text-muted">
                  <i class="fas fa-lightbulb mb-2" style="font-size: 2rem; opacity: 0.5;"></i>
                  <p>No AI recommendations available at this time</p>
                </div>
                <div v-else>
                  <div
                    v-for="recommendation in recommendations"
                    :key="recommendation.id"
                    class="recommendation-item"
                    :class="recommendation.priority"
                  >
                    <div class="recommendation-header">
                      <div class="recommendation-type">
                        <span class="badge" :class="getRecommendationTypeBadge(recommendation.type)">
                          {{ formatRecommendationType(recommendation.type) }}
                        </span>
                      </div>
                      <div class="recommendation-priority">
                        <span class="priority-badge" :class="recommendation.priority">
                          {{ recommendation.priority }}
                        </span>
                      </div>
                    </div>
                    <div class="recommendation-content">
                      <h6 class="recommendation-title">{{ recommendation.title }}</h6>
                      <p class="recommendation-description">{{ recommendation.description }}</p>
                      <div class="recommendation-actions">
                        <button
                          class="btn btn-primary btn-sm me-2"
                          @click="implementRecommendation(recommendation.id)"
                        >
                          <i class="fas fa-check me-1"></i>
                          Implement
                        </button>
                        <button
                          class="btn btn-outline-secondary btn-sm"
                          @click="dismissRecommendation(recommendation.id)"
                        >
                          <i class="fas fa-times me-1"></i>
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Risk Analysis -->
            <div class="content-card mb-4">
              <div class="card-header">
                <h5>
                  <i class="fas fa-exclamation-triangle me-2"></i>
                  AI Risk Analysis
                </h5>
              </div>
              <div class="card-body">
                <div v-if="loading.riskAnalysis" class="text-center py-4">
                  <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else-if="!riskAnalysis" class="text-center py-4 text-muted">
                  <i class="fas fa-chart-bar mb-2" style="font-size: 2rem; opacity: 0.5;"></i>
                  <p>No risk analysis data available</p>
                </div>
                <div v-else class="risk-analysis-content">
                  <div class="risk-summary mb-4">
                    <div class="row">
                      <div class="col-md-4">
                        <div class="risk-metric">
                          <div class="risk-value" :class="getRiskLevelClass(riskAnalysis.overall_risk)">
                            {{ riskAnalysis.overall_risk || 'N/A' }}
                          </div>
                          <div class="risk-label">Overall Risk Level</div>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="risk-metric">
                          <div class="risk-value">{{ riskAnalysis.critical_risks || 0 }}</div>
                          <div class="risk-label">Critical Risks</div>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="risk-metric">
                          <div class="risk-value">{{ riskAnalysis.mitigation_actions || 0 }}</div>
                          <div class="risk-label">Mitigation Actions</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="risk-categories">
                    <h6 class="mb-3">Risk Categories</h6>
                    <div
                      v-for="category in riskAnalysis.categories || []"
                      :key="category.name"
                      class="risk-category"
                    >
                      <div class="category-header">
                        <span class="category-name">{{ category.name }}</span>
                        <span class="category-score" :class="getRiskLevelClass(category.level)">
                          {{ category.level }}
                        </span>
                      </div>
                      <div class="progress">
                        <div
                          class="progress-bar"
                          :class="getRiskProgressClass(category.level)"
                          :style="{ width: category.score + '%' }"
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Panel - AI Assistant & Tools -->
          <div class="col-md-4">
            <!-- AI Chat Assistant -->
            <div class="content-card mb-4">
              <div class="card-header">
                <h5>
                  <i class="fas fa-comments me-2"></i>
                  AI Assistant
                </h5>
              </div>
              <div class="card-body p-0">
                <div class="chat-container">
                  <div class="chat-messages" ref="chatMessages">
                    <div v-if="chatMessages.length === 0" class="text-center py-4 text-muted">
                      <i class="fas fa-robot mb-2" style="font-size: 2rem; opacity: 0.5;"></i>
                      <p>Ask me anything about BCM!</p>
                    </div>
                    <div
                      v-for="message in chatMessages"
                      :key="message.id"
                      class="chat-message"
                      :class="message.type"
                    >
                      <div class="message-content">
                        <div class="message-text">{{ message.text }}</div>
                        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                      </div>
                    </div>
                  </div>
                  <div class="chat-input">
                    <div class="input-group">
                      <input
                        v-model="newMessage"
                        type="text"
                        class="form-control"
                        placeholder="Type your question..."
                        @keypress.enter="sendMessage"
                        :disabled="loading.chat"
                      >
                      <button
                        class="btn btn-primary"
                        @click="sendMessage"
                        :disabled="loading.chat || !newMessage.trim()"
                      >
                        <i v-if="loading.chat" class="fas fa-spinner fa-spin"></i>
                        <i v-else class="fas fa-paper-plane"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick AI Tools -->
            <div class="content-card">
              <div class="card-header">
                <h5>
                  <i class="fas fa-tools me-2"></i>
                  AI Tools
                </h5>
              </div>
              <div class="card-body">
                <div class="ai-tools-grid">
                  <button
                    class="ai-tool-btn"
                    @click="runTool('risk-assessment')"
                    :disabled="loading.tools"
                  >
                    <i class="fas fa-shield-alt"></i>
                    <span>Risk Assessment</span>
                  </button>
                  <button
                    class="ai-tool-btn"
                    @click="runTool('scenario-generator')"
                    :disabled="loading.tools"
                  >
                    <i class="fas fa-random"></i>
                    <span>Scenario Generator</span>
                  </button>
                  <button
                    class="ai-tool-btn"
                    @click="runTool('plan-optimizer')"
                    :disabled="loading.tools"
                  >
                    <i class="fas fa-optimize"></i>
                    <span>Plan Optimizer</span>
                  </button>
                  <button
                    class="ai-tool-btn"
                    @click="runTool('compliance-checker')"
                    :disabled="loading.tools"
                  >
                    <i class="fas fa-clipboard-check"></i>
                    <span>Compliance Check</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Configuration Modal -->
    <div class="modal fade" id="aiConfigModal" tabindex="-1" v-if="showConfigModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">AI Configuration</h5>
            <button type="button" class="btn-close" @click="showConfigModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveAiConfig">
              <div class="mb-3">
                <label class="form-label">AI Model Provider</label>
                <select v-model="aiConfig.provider" class="form-select">
                  <option value="openai">OpenAI GPT</option>
                  <option value="anthropic">Anthropic Claude</option>
                  <option value="azure">Azure OpenAI</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Analysis Frequency</label>
                <select v-model="aiConfig.analysis_frequency" class="form-select">
                  <option value="realtime">Real-time</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Risk Threshold</label>
                <input v-model="aiConfig.risk_threshold" type="range" class="form-range" min="0" max="100">
                <div class="d-flex justify-content-between">
                  <small>Low ({{ aiConfig.risk_threshold }}%)</small>
                  <small>High</small>
                </div>
              </div>
              <div class="mb-3">
                <div class="form-check">
                  <input
                    v-model="aiConfig.auto_recommendations"
                    class="form-check-input"
                    type="checkbox"
                    id="autoRecommendations"
                  >
                  <label class="form-check-label" for="autoRecommendations">
                    Enable automatic recommendations
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showConfigModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveAiConfig" :disabled="loading.config">
              <i v-if="loading.config" class="fas fa-spinner fa-spin me-1"></i>
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'

export default {
  name: 'BcmIntelligentBase',
  setup() {
    // Loading states
    const loading = reactive({
      recommendations: false,
      riskAnalysis: false,
      chat: false,
      tools: false,
      config: false
    })

    // Data
    const aiMetrics = reactive({
      analysisCount: 47,
      recommendations: 12,
      automationTasks: 8,
      riskScore: 73
    })

    const recommendations = ref([
      {
        id: 1,
        type: 'risk_mitigation',
        priority: 'high',
        title: 'Update Incident Response Procedures',
        description: 'AI detected gaps in your current incident response procedures. Consider updating contact lists and escalation protocols.'
      },
      {
        id: 2,
        type: 'training',
        priority: 'medium',
        title: 'Schedule BCP Training',
        description: 'Based on staff turnover analysis, 23% of your team needs refresher training on business continuity procedures.'
      }
    ])

    const riskAnalysis = reactive({
      overall_risk: 'Medium',
      critical_risks: 3,
      mitigation_actions: 8,
      categories: [
        { name: 'IT Infrastructure', level: 'High', score: 85 },
        { name: 'Supply Chain', level: 'Medium', score: 60 },
        { name: 'Human Resources', level: 'Low', score: 30 }
      ]
    })

    const chatMessages = ref([
      {
        id: 1,
        type: 'assistant',
        text: 'Hello! I\'m your AI assistant for Business Continuity Management. How can I help you today?',
        timestamp: new Date()
      }
    ])

    const newMessage = ref('')

    // Modals
    const showConfigModal = ref(false)

    // Configuration
    const aiConfig = reactive({
      provider: 'anthropic',
      analysis_frequency: 'daily',
      risk_threshold: 70,
      auto_recommendations: true
    })

    // Methods
    const refreshAiInsights = async () => {
      loading.recommendations = true
      loading.riskAnalysis = true

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500))

        // Update metrics
        aiMetrics.analysisCount += Math.floor(Math.random() * 5)
        aiMetrics.recommendations = recommendations.value.length

      } catch (error) {
        console.error('Failed to refresh AI insights:', error)
      } finally {
        loading.recommendations = false
        loading.riskAnalysis = false
      }
    }

    const loadRecommendations = async () => {
      loading.recommendations = true
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        console.error('Failed to load recommendations:', error)
      } finally {
        loading.recommendations = false
      }
    }

    const implementRecommendation = async (id) => {
      const index = recommendations.value.findIndex(r => r.id === id)
      if (index > -1) {
        recommendations.value.splice(index, 1)
        aiMetrics.recommendations = recommendations.value.length

        // Add success message to chat
        chatMessages.value.push({
          id: Date.now(),
          type: 'system',
          text: 'Recommendation implemented successfully!',
          timestamp: new Date()
        })
      }
    }

    const dismissRecommendation = async (id) => {
      const index = recommendations.value.findIndex(r => r.id === id)
      if (index > -1) {
        recommendations.value.splice(index, 1)
        aiMetrics.recommendations = recommendations.value.length
      }
    }

    const sendMessage = async () => {
      if (!newMessage.value.trim()) return

      // Add user message
      const userMessage = {
        id: Date.now(),
        type: 'user',
        text: newMessage.value,
        timestamp: new Date()
      }
      chatMessages.value.push(userMessage)

      const messageText = newMessage.value
      newMessage.value = ''
      loading.chat = true

      try {
        // Simulate AI response
        await new Promise(resolve => setTimeout(resolve, 2000))

        const aiResponse = {
          id: Date.now() + 1,
          type: 'assistant',
          text: generateAiResponse(messageText),
          timestamp: new Date()
        }
        chatMessages.value.push(aiResponse)

        // Scroll to bottom
        await nextTick()
        const chatContainer = document.querySelector('.chat-messages')
        if (chatContainer) {
          chatContainer.scrollTop = chatContainer.scrollHeight
        }

      } catch (error) {
        console.error('Failed to send message:', error)
      } finally {
        loading.chat = false
      }
    }

    const generateAiResponse = (userMessage) => {
      const responses = [
        'Based on industry best practices, I recommend reviewing your risk assessment annually.',
        'That\'s a great question! Let me analyze your current BCM setup and provide insights.',
        'I can help you optimize your business continuity plans. Would you like me to run a compliance check?',
        'Your incident response time looks good, but there are opportunities for improvement in communication protocols.',
        'I notice some gaps in your training records. Shall I generate a training schedule for your team?'
      ]
      return responses[Math.floor(Math.random() * responses.length)]
    }

    const runTool = async (toolName) => {
      loading.tools = true

      try {
        await new Promise(resolve => setTimeout(resolve, 2000))

        // Add result to chat
        const toolResults = {
          'risk-assessment': 'Risk assessment completed. Found 3 high-priority risks that need immediate attention.',
          'scenario-generator': 'Generated 5 new scenarios based on your industry profile and risk factors.',
          'plan-optimizer': 'BCP optimization complete. Identified 12 areas for improvement.',
          'compliance-checker': 'Compliance check finished. 94% compliant with ISO 22301 requirements.'
        }

        chatMessages.value.push({
          id: Date.now(),
          type: 'system',
          text: toolResults[toolName] || 'Tool execution completed.',
          timestamp: new Date()
        })

      } catch (error) {
        console.error('Failed to run AI tool:', error)
      } finally {
        loading.tools = false
      }
    }

    const saveAiConfig = async () => {
      loading.config = true

      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        showConfigModal.value = false

        chatMessages.value.push({
          id: Date.now(),
          type: 'system',
          text: 'AI configuration updated successfully!',
          timestamp: new Date()
        })

      } catch (error) {
        console.error('Failed to save AI config:', error)
      } finally {
        loading.config = false
      }
    }

    // Utility functions
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const getRecommendationTypeBadge = (type) => {
      const badges = {
        risk_mitigation: 'bg-danger',
        training: 'bg-warning',
        compliance: 'bg-info',
        optimization: 'bg-success'
      }
      return badges[type] || 'bg-secondary'
    }

    const formatRecommendationType = (type) => {
      const types = {
        risk_mitigation: 'Risk Mitigation',
        training: 'Training',
        compliance: 'Compliance',
        optimization: 'Optimization'
      }
      return types[type] || type
    }

    const getRiskLevelClass = (level) => {
      const classes = {
        'Low': 'text-success',
        'Medium': 'text-warning',
        'High': 'text-danger'
      }
      return classes[level] || 'text-secondary'
    }

    const getRiskProgressClass = (level) => {
      const classes = {
        'Low': 'bg-success',
        'Medium': 'bg-warning',
        'High': 'bg-danger'
      }
      return classes[level] || 'bg-secondary'
    }

    // Lifecycle
    onMounted(() => {
      loadRecommendations()
    })

    return {
      // State
      loading,
      aiMetrics,
      recommendations,
      riskAnalysis,
      chatMessages,
      newMessage,
      showConfigModal,
      aiConfig,

      // Methods
      refreshAiInsights,
      loadRecommendations,
      implementRecommendation,
      dismissRecommendation,
      sendMessage,
      runTool,
      saveAiConfig,

      // Utilities
      formatTime,
      getRecommendationTypeBadge,
      formatRecommendationType,
      getRiskLevelClass,
      getRiskProgressClass
    }
  }
}
</script>

<style scoped>
/* Variables */
:root {
  --ai-primary: #667eea;
  --ai-secondary: #764ba2;
  --ai-accent: #f093fb;
  --ai-success: #4facfe;
  --ai-warning: #ffeaa7;
  --ai-danger: #fd79a8;
  --ai-dark: #2d3436;
  --ai-light: #f8f9fa;
}

/* Main Layout */
.bcm-intelligent-base {
  background: linear-gradient(135deg, var(--ai-light) 0%, #ffffff 100%);
  min-height: 100vh;
}

/* Header */
.header-section {
  background: linear-gradient(135deg, var(--ai-primary) 0%, var(--ai-secondary) 100%);
  color: white;
  padding: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0.5rem 0 0 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Dashboard Section */
.dashboard-section {
  padding: 2rem 0;
  background: white;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--ai-primary), var(--ai-accent));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--ai-dark);
  margin: 0;
}

.metric-label {
  font-size: 0.875rem;
  color: #657786;
  margin: 0.25rem 0 0 0;
}

/* Content Section */
.content-section {
  padding: 2rem 0;
}

.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid #e1e8ed;
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e1e8ed;
  background: var(--ai-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h5 {
  margin: 0;
  color: var(--ai-dark);
  font-weight: 600;
  display: flex;
  align-items: center;
}

.card-body {
  padding: 1.5rem;
}

/* Recommendations */
.recommendation-item {
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background: white;
}

.recommendation-item.high {
  border-color: var(--ai-danger);
  background: rgba(253, 121, 168, 0.05);
}

.recommendation-item.medium {
  border-color: var(--ai-warning);
  background: rgba(255, 234, 167, 0.05);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.recommendation-title {
  font-weight: 600;
  color: var(--ai-dark);
  margin: 0.5rem 0 0.25rem 0;
}

.recommendation-description {
  color: #657786;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.recommendation-actions {
  display: flex;
  gap: 0.5rem;
}

.priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.priority-badge.high { background: #fee2e2; color: #dc2626; }
.priority-badge.medium { background: #fef3c7; color: #d97706; }
.priority-badge.low { background: #dcfce7; color: #166534; }

/* Risk Analysis */
.risk-summary {
  background: var(--ai-light);
  padding: 1.5rem;
  border-radius: 8px;
}

.risk-metric {
  text-align: center;
}

.risk-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.risk-label {
  font-size: 0.875rem;
  color: #657786;
}

.risk-categories {
  margin-top: 1.5rem;
}

.risk-category {
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--ai-light);
  border-radius: 8px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.category-name {
  font-weight: 600;
  color: var(--ai-dark);
}

.category-score {
  font-weight: 600;
}

.progress {
  height: 8px;
  border-radius: 4px;
  background: #e1e8ed;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Chat */
.chat-container {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: var(--ai-light);
}

.chat-message {
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-message.user .message-content {
  background: var(--ai-primary);
  color: white;
  margin-left: 2rem;
}

.chat-message.assistant .message-content {
  background: white;
  border: 1px solid #e1e8ed;
  margin-right: 2rem;
}

.chat-message.system .message-content {
  background: var(--ai-success);
  color: white;
  margin: 0 2rem;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message-text {
  font-size: 0.875rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.chat-input {
  padding: 1rem;
  border-top: 1px solid #e1e8ed;
  background: white;
}

/* AI Tools */
.ai-tools-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.ai-tool-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--ai-light);
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  color: var(--ai-dark);
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.ai-tool-btn:hover:not(:disabled) {
  background: var(--ai-primary);
  color: white;
  border-color: var(--ai-primary);
  transform: translateY(-2px);
}

.ai-tool-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-tool-btn i {
  font-size: 1.5rem;
}

.ai-tool-btn span {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}

/* Scrollbar Styling */
.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #e1e8ed;
  border-radius: 2px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #657786;
}

/* Responsive */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .metric-card {
    margin-bottom: 1rem;
  }

  .ai-tools-grid {
    grid-template-columns: 1fr;
  }

  .chat-container {
    height: 300px;
  }

  .recommendation-actions {
    flex-direction: column;
  }

  .recommendation-actions .btn {
    margin-bottom: 0.5rem;
  }
}

/* Loading States */
.spinner-border {
  color: var(--ai-primary) !important;
}

/* Badge Colors */
.badge.bg-danger { background-color: var(--ai-danger) !important; }
.badge.bg-warning { background-color: var(--ai-warning) !important; color: var(--ai-dark) !important; }
.badge.bg-info { background-color: var(--ai-primary) !important; }
.badge.bg-success { background-color: var(--ai-success) !important; }
</style>