# UI/UX Technical Specification for AI-Enhanced BCM Platform

## 🎯 Scope of Interface Development

### **Затронутые модули и компоненты:**

#### **1. Odoo BCM Modules (Backend Interface Updates)**
```yaml
bcm_scenario_hub:
  - NEW: AI generation wizard
  - NEW: Forum discussion integration
  - UPDATE: Scenario catalog with AI metadata

bcm_community:
  - NEW: Complete module UI (созданный модуль)
  - NEW: Forum integration dashboard
  - NEW: Community statistics interface

bcm_exercise:
  - UPDATE: Exercise creation from AI scenarios
  - NEW: Real-time exercise monitoring dashboard
  - NEW: BPMN workflow progress tracking

bcm_notification:
  - NEW: Notification channel management
  - NEW: External integration configuration
  - UPDATE: Alert template designer
```

#### **2. Frontend Services (New Interface Development)**
```yaml
Web Portal (Vue.js) - Port 3002:
  - UPDATE: BCMScenarioHub.vue (уже обновлен)
  - NEW: AI Assistant integration components
  - NEW: Real-time scenario generation interface
  - NEW: Community forum integration

Web Portal v2 - Port 3002 (упомянут в docker-compose):
  - NEW: Modern BCM interface
  - NEW: AI-enhanced user experience
  - NEW: Real-time collaboration features

Admin Panel (React) - Port 3001:
  - NEW: AI service monitoring dashboard
  - NEW: System health monitoring interface
  - UPDATE: Service configuration panels
```

#### **3. AI Services (API Interface Requirements)**
```yaml
Scenario Orchestrator (Port 8085):
  - NEW: Scenario generation API interface
  - NEW: Template management interface
  - NEW: Generation history and analytics

AI Orchestrator (Port 8000):
  - UPDATE: Enhanced NLP query interface
  - NEW: AI capability management
  - NEW: Learning analytics dashboard

Notification Service (Port 8002):
  - NEW: External integration testing interface
  - NEW: Notification template management
  - NEW: Delivery status monitoring
```

---

## 🎨 UI/UX Requirements by Component

### **COMPONENT 1: AI Scenario Generation Interface**

#### **Location**: Web Portal (Vue.js) - `/frontend/web_portal/src/views/`

#### **Interface Requirements**:

1. **Scenario Generation Wizard**
```vue
<!-- NEW: AIScenarioGenerationWizard.vue -->
<template>
  <div class="ai-scenario-wizard">
    <!-- Step 1: Basic Parameters -->
    <div class="wizard-step" v-if="currentStep === 1">
      <h3>🤖 AI Scenario Generation</h3>

      <div class="form-group">
        <label>Scenario Category *</label>
        <select v-model="scenarioParams.category" class="form-select">
          <option value="cyber">🔒 Cyber Security Incident</option>
          <option value="epidemic">🦠 Epidemic/Pandemic</option>
          <option value="blackout">⚡ Power Blackout</option>
          <option value="supply">📦 Supply Chain Disruption</option>
          <option value="natural">🌪️ Natural Disaster</option>
          <option value="terrorism">🎯 Terrorism/Security</option>
          <option value="financial">💰 Financial Crisis</option>
        </select>
      </div>

      <div class="form-group">
        <label>Complexity Level *</label>
        <div class="complexity-slider">
          <input type="range" v-model="scenarioParams.complexity"
                 min="1" max="5" class="form-range">
          <div class="complexity-labels">
            <span>1 - Basic</span>
            <span>3 - Intermediate</span>
            <span>5 - Expert</span>
          </div>
        </div>
      </div>

      <div class="form-row">
        <div class="col-md-6">
          <label>Duration (hours) *</label>
          <input type="number" v-model="scenarioParams.duration_hours"
                 min="1" max="24" class="form-control">
        </div>
        <div class="col-md-6">
          <label>Participants *</label>
          <input type="number" v-model="scenarioParams.participants"
                 min="3" max="100" class="form-control">
        </div>
      </div>
    </div>

    <!-- Step 2: Organization Context -->
    <div class="wizard-step" v-if="currentStep === 2">
      <h3>🏢 Organization Context</h3>

      <div class="form-group">
        <label>Organization Type</label>
        <select v-model="scenarioParams.organization_context" class="form-select">
          <option value="healthcare">🏥 Healthcare</option>
          <option value="financial">🏦 Financial Services</option>
          <option value="manufacturing">🏭 Manufacturing</option>
          <option value="government">🏛️ Government</option>
          <option value="education">🎓 Education</option>
          <option value="retail">🛒 Retail</option>
          <option value="technology">💻 Technology</option>
        </select>
      </div>

      <div class="form-group">
        <label>Affected Systems</label>
        <div class="system-selector">
          <div v-for="system in availableSystems" :key="system">
            <input type="checkbox" :id="system"
                   v-model="scenarioParams.affected_systems"
                   :value="system">
            <label :for="system">{{ system }}</label>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>Custom Objectives</label>
        <div class="objectives-manager">
          <div v-for="(objective, index) in scenarioParams.custom_objectives"
               :key="index" class="objective-item">
            <input type="text" v-model="scenarioParams.custom_objectives[index]"
                   class="form-control" placeholder="Enter objective...">
            <button @click="removeObjective(index)" class="btn btn-sm btn-danger">
              <i class="fas fa-trash"></i>
            </button>
          </div>
          <button @click="addObjective" class="btn btn-sm btn-primary">
            <i class="fas fa-plus"></i> Add Objective
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: AI Generation & Preview -->
    <div class="wizard-step" v-if="currentStep === 3">
      <h3>🧠 AI Generation</h3>

      <div v-if="isGenerating" class="generation-progress">
        <div class="ai-animation">
          <div class="brain-icon">🧠</div>
          <div class="thinking-dots">
            <span>.</span><span>.</span><span>.</span>
          </div>
        </div>
        <p>AI is generating your scenario...</p>
        <div class="progress">
          <div class="progress-bar progress-bar-animated"
               :style="{width: generationProgress + '%'}"></div>
        </div>
      </div>

      <div v-if="generatedScenario" class="scenario-preview">
        <h4>📝 Generated Scenario Preview</h4>
        <div class="scenario-meta">
          <span class="badge badge-primary">{{ generatedScenario.category }}</span>
          <span class="badge badge-info">{{ generatedScenario.level }}</span>
          <span class="badge badge-warning">{{ generatedScenario.meta_duration }}h</span>
          <span class="badge badge-success">{{ generatedScenario.meta_participants }} participants</span>
        </div>

        <div class="scenario-content">
          <div v-html="renderMarkdown(generatedScenario.content_md)"></div>
        </div>

        <div v-if="generatedScenario.jaamsim_config" class="simulation-config">
          <h5>🎮 JaamSim Simulation Configuration</h5>
          <pre class="code-block">{{ generatedScenario.jaamsim_config }}</pre>
        </div>
      </div>
    </div>

    <!-- Wizard Navigation -->
    <div class="wizard-navigation">
      <button v-if="currentStep > 1" @click="previousStep"
              class="btn btn-outline-secondary">Previous</button>

      <button v-if="currentStep < 3" @click="nextStep"
              class="btn btn-primary">Next</button>

      <button v-if="currentStep === 2" @click="generateScenario"
              class="btn btn-success">🧠 Generate with AI</button>

      <button v-if="currentStep === 3 && generatedScenario"
              @click="saveScenario" class="btn btn-success">
        💾 Save Scenario
      </button>
    </div>
  </div>
</template>

<script>
// Implementation details for Vue.js component
export default {
  name: 'AIScenarioGenerationWizard',
  data() {
    return {
      currentStep: 1,
      isGenerating: false,
      generationProgress: 0,
      generatedScenario: null,
      scenarioParams: {
        category: 'cyber',
        complexity: 3,
        duration_hours: 4,
        participants: 8,
        affected_systems: [],
        custom_objectives: [],
        organization_context: 'healthcare'
      }
    }
  },
  methods: {
    async generateScenario() {
      this.currentStep = 3
      this.isGenerating = true

      // Simulate AI generation progress
      const progressInterval = setInterval(() => {
        this.generationProgress += 10
        if (this.generationProgress >= 100) {
          clearInterval(progressInterval)
        }
      }, 500)

      try {
        const response = await this.$http.post(
          'http://localhost:8085/scenarios/generate',
          this.scenarioParams
        )

        this.generatedScenario = response.data
        this.isGenerating = false

      } catch (error) {
        this.isGenerating = false
        this.$toast.error('AI generation failed: ' + error.message)
      }
    }
  }
}
</script>
```

---

### **COMPONENT 2: Community Forum Integration Interface**

#### **Location**: Odoo BCM Platform - bcm_community module

#### **Interface Requirements**:

1. **Forum Integration Dashboard** (`views/forum_integration_views.xml`):
```xml
<!-- NEW: Forum Integration Management Interface -->
<record id="view_forum_integration_dashboard" model="ir.ui.view">
    <field name="name">Forum Integration Dashboard</field>
    <field name="model">bcm.forum.integration</field>
    <field name="arch" type="xml">
        <form>
            <div class="o_form_sheet">
                <!-- Connection Status Dashboard -->
                <div class="o_group">
                    <div class="o_inner_group">
                        <div class="alert alert-success"
                             attrs="{'invisible': [('sync_status', '!=', 'success')]}">
                            <i class="fa fa-check-circle"/>
                            <strong>Forum Service Connected</strong>
                            <p>Last sync: <field name="last_sync" readonly="1"/></p>
                        </div>

                        <div class="alert alert-warning"
                             attrs="{'invisible': [('sync_status', '!=', 'idle')]}">
                            <i class="fa fa-clock-o"/>
                            <strong>Forum Service Idle</strong>
                            <p>Ready for synchronization</p>
                        </div>

                        <div class="alert alert-danger"
                             attrs="{'invisible': [('sync_status', '!=', 'error')]}">
                            <i class="fa fa-exclamation-triangle"/>
                            <strong>Forum Service Error</strong>
                            <p><field name="error_message" readonly="1"/></p>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions Panel -->
                <div class="o_group">
                    <div class="o_inner_group">
                        <button name="action_test_connection" type="object"
                                string="🔗 Test Connection" class="btn-primary"/>
                        <button name="action_sync_all" type="object"
                                string="🔄 Sync All Data" class="btn-success"/>
                    </div>
                </div>

                <!-- Statistics Dashboard -->
                <div class="o_group">
                    <h3>📊 Community Statistics</h3>
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="card-title text-primary">
                                        <field name="total_topics" readonly="1"/>
                                    </h4>
                                    <p class="card-text">Forum Topics</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="card-title text-success">
                                        <field name="active_users" readonly="1"/>
                                    </h4>
                                    <p class="card-text">Active Users</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="card-title text-info">
                                        <field name="scenario_discussions" readonly="1"/>
                                    </h4>
                                    <p class="card-text">Scenario Discussions</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body">
                                    <h4 class="card-title text-warning">
                                        <field name="knowledge_articles" readonly="1"/>
                                    </h4>
                                    <p class="card-text">Knowledge Articles</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    </field>
</record>
```

2. **Forum Topic Management Interface**:
```xml
<!-- NEW: Enhanced Forum Topic Interface -->
<record id="view_forum_topic_kanban" model="ir.ui.view">
    <field name="name">bcm.forum.topic.kanban</field>
    <field name="model">bcm.forum.topic</field>
    <field name="arch" type="xml">
        <kanban class="o_kanban_dashboard">
            <field name="name"/>
            <field name="category"/>
            <field name="post_count"/>
            <field name="score"/>
            <field name="is_synced"/>
            <field name="scenario_id"/>
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <div class="oe_kanban_content">
                            <!-- Topic Header -->
                            <div class="o_kanban_record_top">
                                <div class="o_kanban_record_headings">
                                    <strong class="o_kanban_record_title">
                                        <t t-esc="record.name.value"/>
                                    </strong>
                                    <div class="text-muted">
                                        <i class="fa fa-comments"/>
                                        <t t-esc="record.post_count.value"/> posts
                                        <span class="mx-2">•</span>
                                        <i class="fa fa-arrow-up"/>
                                        <t t-esc="record.score.value"/> score
                                    </div>
                                </div>
                            </div>

                            <!-- Category Badge -->
                            <div class="o_kanban_record_body">
                                <span class="badge badge-pill"
                                      t-attf-class="badge-#{record.category.raw_value}">
                                    <t t-esc="record.category.value"/>
                                </span>

                                <!-- Sync Status -->
                                <span t-if="record.is_synced.raw_value"
                                      class="badge badge-success">
                                    <i class="fa fa-check"/> Synced
                                </span>
                                <span t-if="!record.is_synced.raw_value"
                                      class="badge badge-warning">
                                    <i class="fa fa-clock-o"/> Local
                                </span>
                            </div>

                            <!-- Quick Actions -->
                            <div class="o_kanban_record_bottom">
                                <div class="oe_kanban_bottom_left">
                                    <a t-if="record.scenario_id.raw_value"
                                       type="object" name="open_scenario">
                                        <i class="fa fa-file-text"/> View Scenario
                                    </a>
                                </div>
                                <div class="oe_kanban_bottom_right">
                                    <a t-if="record.forum_url.value"
                                       type="object" name="action_view_in_forum">
                                        <i class="fa fa-external-link"/> Open Forum
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

### **COMPONENT 3: Real-time AI Assistant Panel**

#### **Location**: Web Portal - `/frontend/web_portal/src/components/ai/`

#### **Interface Requirements**:

1. **AI Assistant Chat Interface** (`AIAssistantPanel.vue`):
```vue
<!-- NEW: Real-time AI Assistant -->
<template>
  <div class="ai-assistant-panel">
    <!-- AI Status Indicator -->
    <div class="ai-status">
      <div class="status-indicator" :class="aiStatus">
        <i class="fas fa-robot"></i>
        <span>{{ aiStatusText }}</span>
      </div>
    </div>

    <!-- Chat Interface -->
    <div class="chat-container">
      <div class="chat-messages" ref="chatMessages">
        <div v-for="message in chatHistory" :key="message.id"
             class="message" :class="message.type">
          <div class="message-avatar">
            <i v-if="message.type === 'ai'" class="fas fa-robot"></i>
            <i v-else class="fas fa-user"></i>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(message.content)"></div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="chat-input">
        <div class="input-group">
          <input v-model="currentMessage"
                 @keypress.enter="sendMessage"
                 type="text"
                 class="form-control"
                 placeholder="Ask AI about BCM scenarios, exercises, or best practices..."
                 :disabled="isProcessing">

          <button @click="sendMessage"
                  class="btn btn-primary"
                  :disabled="isProcessing || !currentMessage.trim()">
            <i v-if="isProcessing" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h6>Quick Actions</h6>
      <div class="action-buttons">
        <button @click="askAI('Generate a cyber security scenario')"
                class="btn btn-sm btn-outline-primary">
          🔒 Generate Cyber Scenario
        </button>
        <button @click="askAI('Recommend exercise for our organization')"
                class="btn btn-sm btn-outline-success">
          🎯 Exercise Recommendation
        </button>
        <button @click="askAI('Analyze our BCM readiness')"
                class="btn btn-sm btn-outline-info">
          📊 Readiness Analysis
        </button>
      </div>
    </div>

    <!-- AI Recommendations -->
    <div v-if="recommendations.length > 0" class="ai-recommendations">
      <h6>🤖 AI Recommendations</h6>
      <div class="recommendation-list">
        <div v-for="rec in recommendations" :key="rec.id"
             class="recommendation-item" @click="applyRecommendation(rec)">
          <div class="rec-icon">
            <i :class="rec.icon"></i>
          </div>
          <div class="rec-content">
            <strong>{{ rec.title }}</strong>
            <p>{{ rec.description }}</p>
            <span class="confidence">{{ rec.confidence }}% confidence</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AIAssistantPanel',
  data() {
    return {
      aiStatus: 'online', // online, offline, processing
      chatHistory: [],
      currentMessage: '',
      isProcessing: false,
      recommendations: []
    }
  },
  computed: {
    aiStatusText() {
      return {
        'online': 'AI Assistant Ready',
        'offline': 'AI Assistant Offline',
        'processing': 'AI Thinking...'
      }[this.aiStatus] || 'Unknown'
    }
  },
  methods: {
    async sendMessage() {
      if (!this.currentMessage.trim()) return

      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: this.currentMessage,
        timestamp: new Date()
      }

      this.chatHistory.push(userMessage)
      const query = this.currentMessage
      this.currentMessage = ''
      this.isProcessing = true
      this.aiStatus = 'processing'

      try {
        const response = await this.$http.post('/api/ai/query', {
          query: query,
          context: this.getContext()
        })

        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: response.data.response,
          timestamp: new Date()
        }

        this.chatHistory.push(aiMessage)

        // Update recommendations if provided
        if (response.data.recommendations) {
          this.recommendations = response.data.recommendations
        }

      } catch (error) {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date()
        }
        this.chatHistory.push(errorMessage)
      } finally {
        this.isProcessing = false
        this.aiStatus = 'online'
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      }
    }
  }
}
</script>
```

---

### **COMPONENT 4: Service Health Monitoring Dashboard**

#### **Location**: Admin Panel (React) - `/frontend/admin_panel/src/components/`

#### **Interface Requirements**:

1. **Service Health Dashboard** (`ServiceHealthDashboard.jsx`):
```jsx
// NEW: Real-time Service Health Monitoring
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Progress, Alert } from 'react-bootstrap';

const ServiceHealthDashboard = () => {
  const [services, setServices] = useState([]);
  const [overallHealth, setOverallHealth] = useState(0);
  const [healthTrend, setHealthTrend] = useState([]);

  useEffect(() => {
    // Real-time health monitoring
    const healthInterval = setInterval(checkAllServices, 30000); // Every 30 seconds
    checkAllServices(); // Initial check

    return () => clearInterval(healthInterval);
  }, []);

  const checkAllServices = async () => {
    const serviceList = [
      { name: 'AI Orchestrator', port: 8000, critical: true },
      { name: 'Scenario Orchestrator', port: 8085, critical: true },
      { name: 'Odoo BCM Platform', port: 8069, critical: true },
      { name: 'PostgreSQL', port: 5432, critical: true },
      { name: 'Redis Cache', port: 6379, critical: true },
      { name: 'BIA Engine', port: 8082, critical: false },
      { name: 'Document Processor', port: 8083, critical: false },
      { name: 'Compliance Checker', port: 8084, critical: false },
      { name: 'MCP Server', port: 8087, critical: false },
      { name: 'EventBus', port: 8001, critical: false },
      { name: 'Notification Service', port: 8002, critical: false },
      { name: 'BPMN Service', port: 8005, critical: false }
    ];

    const healthResults = await Promise.allSettled(
      serviceList.map(async (service) => {
        try {
          const response = await fetch(`http://localhost:${service.port}/health`);
          const data = await response.json();

          return {
            ...service,
            status: 'healthy',
            responseTime: Date.now() - startTime,
            details: data
          };
        } catch (error) {
          return {
            ...service,
            status: 'unhealthy',
            error: error.message
          };
        }
      })
    );

    const updatedServices = healthResults.map(result => result.value);
    setServices(updatedServices);

    // Calculate overall health
    const healthyCount = updatedServices.filter(s => s.status === 'healthy').length;
    const healthPercentage = Math.round((healthyCount / updatedServices.length) * 100);
    setOverallHealth(healthPercentage);
  };

  const getStatusVariant = (status) => {
    return {
      'healthy': 'success',
      'unhealthy': 'danger',
      'warning': 'warning'
    }[status] || 'secondary';
  };

  const getHealthColor = (percentage) => {
    if (percentage >= 90) return 'success';
    if (percentage >= 70) return 'warning';
    return 'danger';
  };

  return (
    <div className="service-health-dashboard">
      {/* Overall Health Summary */}
      <Row className="mb-4">
        <Col md={12}>
          <Card>
            <Card.Header>
              <h5><i className="fas fa-heartbeat"></i> Platform Health Overview</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={3}>
                  <div className="text-center">
                    <h2 className={`text-${getHealthColor(overallHealth)}`}>
                      {overallHealth}%
                    </h2>
                    <p>Overall Health</p>
                  </div>
                </Col>
                <Col md={9}>
                  <Progress
                    variant={getHealthColor(overallHealth)}
                    now={overallHealth}
                    label={`${overallHealth}%`}
                  />
                  <div className="mt-2">
                    <small className="text-muted">
                      {services.filter(s => s.status === 'healthy').length} of {services.length} services healthy
                    </small>
                  </div>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Service Grid */}
      <Row>
        {services.map((service, index) => (
          <Col md={6} lg={4} key={index} className="mb-3">
            <Card className={`service-card ${service.status}`}>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <span>
                  <i className={service.critical ? 'fas fa-star text-warning' : 'fas fa-cog'}></i>
                  {service.name}
                </span>
                <Badge variant={getStatusVariant(service.status)}>
                  {service.status}
                </Badge>
              </Card.Header>
              <Card.Body>
                <div className="service-details">
                  <div className="detail-row">
                    <span>Port:</span>
                    <span>{service.port}</span>
                  </div>
                  {service.responseTime && (
                    <div className="detail-row">
                      <span>Response:</span>
                      <span>{service.responseTime}ms</span>
                    </div>
                  )}
                  {service.details && (
                    <div className="detail-row">
                      <span>Version:</span>
                      <span>{service.details.version || 'N/A'}</span>
                    </div>
                  )}
                </div>

                {service.error && (
                  <Alert variant="danger" className="mt-2">
                    <small>{service.error}</small>
                  </Alert>
                )}

                <div className="service-actions mt-2">
                  <button
                    className="btn btn-sm btn-outline-primary me-2"
                    onClick={() => window.open(`http://localhost:${service.port}`, '_blank')}
                  >
                    <i className="fas fa-external-link-alt"></i> Open
                  </button>
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => checkSingleService(service)}
                  >
                    <i className="fas fa-sync"></i> Refresh
                  </button>
                </div>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* AI Services Detailed Status */}
      <Row className="mt-4">
        <Col md={12}>
          <Card>
            <Card.Header>
              <h5><i className="fas fa-robot"></i> AI Services Status</h5>
            </Card.Header>
            <Card.Body>
              <AIServicesDetailPanel services={services.filter(s => s.name.includes('AI') || s.name.includes('Scenario'))} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ServiceHealthDashboard;
```

---

## 📋 Technical Requirements for Interface Team

### **1. Vue.js Frontend Updates** (Web Portal)

#### **New Components to Create**:
```yaml
/src/components/ai/:
  - AIScenarioGenerationWizard.vue     # Wizard для AI generation
  - AIAssistantPanel.vue               # Real-time AI chat
  - AIRecommendationsPanel.vue         # AI рекомендации
  - ScenarioAIMetadata.vue             # AI metadata display

/src/components/scenario-hub/:
  - ScenarioGenerationButton.vue       # Quick AI generation
  - AIScenarioPreview.vue              # Generated scenario preview
  - ScenarioDiscussionLink.vue         # Link to forum discussion

/src/views/:
  - AIScenarioDashboard.vue            # AI dashboard
  - CommunityForumIntegration.vue      # Forum integration page
```

#### **Existing Components to Update**:
```yaml
BCMScenarioHub.vue:
  - ADD: AI Assistant Panel integration
  - ADD: "Generate with AI" button
  - ADD: Real-time scenario updates
  - UPDATE: Search to include AI-generated scenarios

ScenarioCard.vue:
  - ADD: AI-generated badge
  - ADD: Complexity level indicator
  - ADD: Forum discussion link
  - UPDATE: Metadata display for AI params
```

#### **API Integration Requirements**:
```javascript
// NEW: AI Service Integration
export const aiService = {
  // Scenario generation
  generateScenario: (params) =>
    axios.post('http://localhost:8085/scenarios/generate', params),

  // AI chat
  queryAI: (query, context) =>
    axios.post('http://localhost:8000/nlp/query', { query, context }),

  // Get AI recommendations
  getRecommendations: (userContext) =>
    axios.get('http://localhost:8000/recommendations', { params: userContext }),

  // Health checks
  checkAIHealth: () =>
    axios.get('http://localhost:8000/health')
};
```

---

### **2. React Admin Panel Updates**

#### **New Components to Create**:
```yaml
/src/components/monitoring/:
  - ServiceHealthDashboard.jsx         # Complete health monitoring
  - AIServicesDetailPanel.jsx          # AI services специализированный panel
  - SystemMetricsPanel.jsx             # System performance metrics
  - AlertsManagementPanel.jsx          # Alert rules и notifications

/src/components/ai/:
  - AIModelConfiguration.jsx           # AI model settings
  - AILearningAnalytics.jsx            # AI learning progress
  - ScenarioGenerationStats.jsx       # AI generation analytics
```

#### **Dashboard Updates**:
```jsx
// UPDATE: Main Dashboard
const MainDashboard = () => {
  return (
    <div>
      {/* Existing dashboard content */}

      {/* NEW: AI Services Overview */}
      <Row>
        <Col md={8}>
          <ServiceHealthDashboard />
        </Col>
        <Col md={4}>
          <AIServicesDetailPanel />
        </Col>
      </Row>

      {/* NEW: Recent AI Activity */}
      <Row className="mt-4">
        <Col md={12}>
          <ScenarioGenerationStats />
        </Col>
      </Row>
    </div>
  );
};
```

---

### **3. Odoo Module Interface Updates**

#### **bcm_scenario_hub Module Updates**:
```yaml
NEW Views Required:
  - ai_scenario_wizard.xml             # AI generation wizard
  - scenario_ai_metadata_view.xml      # AI metadata display
  - community_integration_view.xml     # Forum integration

NEW Wizards:
  - ai_scenario_generation_wizard.py   # AI generation wizard logic
  - scenario_forum_creation_wizard.py  # Forum topic creation
```

#### **bcm_community Module (Complete UI)**:
```yaml
Views to Create:
  - forum_integration_dashboard.xml    # Integration dashboard
  - forum_topic_kanban.xml            # Topics kanban view
  - community_analytics_view.xml       # Community analytics
  - knowledge_base_view.xml           # Knowledge base management

Menu Structure:
  Community/
    ├── 🔧 Forum Integration
    ├── 📝 Forum Topics
    │   ├── All Topics
    │   └── Scenario Discussions
    ├── 📊 Community Analytics
    └── 📚 Knowledge Base
```

---

## 🎨 UI/UX Design Guidelines

### **Design System**:
```css
/* AI-Enhanced Component Styling */
.ai-component {
  --ai-primary: #6366f1;     /* Indigo for AI elements */
  --ai-secondary: #818cf8;   /* Light indigo */
  --ai-success: #10b981;     /* Emerald for success */
  --ai-warning: #f59e0b;     /* Amber for warnings */
  --ai-danger: #ef4444;      /* Red for errors */
}

.ai-badge {
  background: linear-gradient(135deg, var(--ai-primary), var(--ai-secondary));
  color: white;
  border-radius: 12px;
  padding: 4px 8px;
  font-size: 0.75rem;
}

.ai-animation {
  animation: pulse 2s infinite;
}

.scenario-card.ai-generated {
  border-left: 4px solid var(--ai-primary);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
}
```

### **Responsive Design Requirements**:
- **Mobile-first** approach for all new components
- **Touch-friendly** interface elements
- **Progressive disclosure** for complex AI features
- **Loading states** for AI operations
- **Error boundaries** for AI service failures

---

## 📋 Implementation Checklist for Interface Team

### **Phase 1: Foundation (Current)**
- [x] AI Scenario Generation API working
- [x] Service health monitoring system
- [x] Basic notification configuration
- [ ] **NEED**: AI generation wizard UI
- [ ] **NEED**: Service health dashboard UI
- [ ] **NEED**: bcm_community module installation

### **Phase 2: Community Integration (Next)**
- [ ] **NEED**: Community Service refactoring
- [ ] **NEED**: Forum integration interface
- [ ] **NEED**: Real-time WebSocket integration
- [ ] **NEED**: Knowledge base management UI

### **Priority Interface Development Order**:
1. **AI Scenario Generation Wizard** (высокий приоритет)
2. **Service Health Dashboard** (средний приоритет)
3. **Community Forum Integration** (средний приоритет)
4. **AI Assistant Chat Panel** (низкий приоритет)

---

**Complete interface specification ready for frontend development team with detailed component requirements and implementation guidelines.**