# ЭТАП 3: Interface Requirements - ТЗ для команды интерфейсов

## 🎯 Scope of Interface Changes - ЭТАП 3

### **Затронутые модули с новым функционалом:**

```yaml
bcm_templates:     ✅ ENHANCED - добавлен BPMN workflow support
bcm_exercise:      ✅ ENHANCED - добавлена template integration
bcm_scenario_hub:  ✅ ENHANCED - добавлена template compatibility
```

---

## 🎨 **НОВЫЕ ИНТЕРФЕЙСЫ ДЛЯ РАЗРАБОТКИ**

### **ИНТЕРФЕЙС 1: BPMN Template Management (Odoo)**

#### **Location**: bcm_templates module views
```yaml
Файлы для создания:
  - views/bcm_template_views.xml        # Template management interface
  - views/bpmn_workflow_views.xml       # BPMN workflow designer
  - views/template_wizard_views.xml     # Template creation wizard

NEW Odoo Views Required:
  - Template Library (list view с categories)
  - BPMN Template Designer (form view с XML editor)
  - Template Preview (custom view с BPMN visualization)
  - Usage Analytics (graph view с statistics)
```

#### **Template Management Interface Spec**:
```xml
<!-- NEW: Enhanced Template Form View -->
<record id="view_bcm_template_form_enhanced" model="ir.ui.view">
    <field name="name">bcm.template.form.enhanced</field>
    <field name="model">bcm.template</field>
    <field name="arch" type="xml">
        <form string="BCM Template">
            <header>
                <!-- Action Buttons -->
                <button name="action_generate_with_ai" type="object"
                        string="🤖 Generate with AI" class="btn-primary"
                        attrs="{'invisible': [('category', '!=', 'workflow')]}"/>

                <button name="action_preview_template" type="object"
                        string="👁️ Preview" class="btn-secondary"/>

                <button name="action_use_template" type="object"
                        string="🚀 Use Template" class="btn-success"
                        attrs="{'invisible': [('category', '!=', 'workflow')]}"/>

                <field name="active" widget="boolean_toggle"/>
            </header>

            <sheet>
                <div class="oe_title">
                    <h1><field name="name" placeholder="Template Name"/></h1>
                </div>

                <group>
                    <group string="Template Configuration">
                        <field name="category" widget="radio"/>
                        <field name="template_type"/>
                        <field name="iso_clause"/>
                        <field name="sequence"/>
                    </group>
                    <group string="Usage Statistics">
                        <field name="usage_count" readonly="1"/>
                        <field name="last_used" readonly="1"/>
                        <field name="is_ai_enhanced"/>
                    </group>
                </group>

                <group string="Content">
                    <field name="description"/>
                    <field name="notes"/>
                </group>

                <!-- BPMN Workflow Section -->
                <group string="BPMN Workflow" attrs="{'invisible': [('category', '!=', 'workflow')]}">
                    <field name="bpmn_xml" widget="ace" options="{'mode': 'xml'}"
                           placeholder="Paste BPMN 2.0 XML definition here..."/>
                </group>

                <!-- AI Enhancement Section -->
                <group string="AI Enhancement" attrs="{'invisible': [('is_ai_enhanced', '=', False)]}">
                    <field name="ai_prompt" placeholder="Describe what this template should generate..."/>
                </group>

                <!-- Document Template Section -->
                <group string="Document Content" attrs="{'invisible': [('category', '!=', 'document')]}">
                    <field name="content" widget="html"/>
                </group>

                <!-- Form Schema Section -->
                <group string="Form Schema" attrs="{'invisible': [('category', '!=', 'form')]}">
                    <field name="form_schema" widget="ace" options="{'mode': 'json'}"
                           placeholder="JSON schema for form validation..."/>
                </group>

                <!-- Scenario Compatibility -->
                <group string="Scenario Compatibility">
                    <field name="scenario_types" widget="many2many_tags"/>
                </group>
            </sheet>

            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

---

### **ИНТЕРФЕЙС 2: Enhanced Exercise Management (Odoo)**

#### **bcm_exercise Form View Updates**:
```xml
<!-- UPDATED: Exercise Form with Template Integration -->
<record id="view_bcm_exercise_form_enhanced" model="ir.ui.view">
    <field name="name">bcm.exercise.form.enhanced</field>
    <field name="model">bcm.exercise</field>
    <field name="arch" type="xml">
        <form string="BCM Exercise">
            <header>
                <!-- NEW Action Buttons -->
                <button name="action_start_exercise_workflow" type="object"
                        string="🚀 Start Workflow" class="btn-primary"
                        attrs="{'invisible': ['|', ('template_id', '=', False), ('workflow_status', 'in', ['running', 'completed'])]}"/>

                <button name="action_sync_workflow_tasks" type="object"
                        string="🔄 Sync Tasks" class="btn-secondary"
                        attrs="{'invisible': [('bpmn_process_id', '=', False)]}"/>

                <!-- Workflow Status Badge -->
                <field name="workflow_status" widget="badge"
                       decoration-info="workflow_status == 'draft'"
                       decoration-warning="workflow_status == 'running'"
                       decoration-success="workflow_status == 'completed'"
                       decoration-danger="workflow_status == 'failed'"/>
            </header>

            <sheet>
                <div class="oe_title">
                    <h1><field name="name"/></h1>
                </div>

                <!-- NEW: Template and Scenario Integration -->
                <group>
                    <group string="Exercise Configuration">
                        <field name="exercise_type"/>
                        <field name="template_id" options="{'no_create': True}"/>
                        <field name="scenario_id" options="{'no_create': True}"/>
                        <field name="ai_generated" readonly="1"/>
                    </group>
                    <group string="BPMN Workflow">
                        <field name="bpmn_process_id" readonly="1"/>
                        <field name="workflow_status" readonly="1"/>
                    </group>
                </group>

                <group string="Scheduling">
                    <group>
                        <field name="state"/>
                        <field name="planned_date"/>
                    </group>
                    <group>
                        <field name="requested_by"/>
                        <field name="assigned_facilitator"/>
                    </group>
                </group>

                <!-- Participants -->
                <group string="Participants">
                    <field name="participant_ids" widget="many2many_tags"/>
                </group>

                <!-- Exercise Content -->
                <group string="Exercise Content">
                    <field name="scenario" widget="html"/>
                </group>

                <!-- NEW: Current Workflow Tasks -->
                <group string="Current Tasks" attrs="{'invisible': [('current_tasks', '=', False)]}">
                    <field name="current_tasks" widget="ace" options="{'mode': 'json'}" readonly="1"/>
                </group>

                <!-- Feedback -->
                <group string="Feedback" attrs="{'invisible': [('feedback_submitted', '=', False)]}">
                    <field name="feedback_data"/>
                    <field name="feedback_date"/>
                </group>
            </sheet>

            <div class="oe_chatter">
                <field name="message_follower_ids"/>
                <field name="activity_ids"/>
                <field name="message_ids"/>
            </div>
        </form>
    </field>
</record>
```

---

### **ИНТЕРФЕЙС 3: Scenario to Exercise Wizard (Odoo)**

#### **Exercise Creation Wizard**:
```xml
<!-- NEW: Exercise Creation Wizard -->
<record id="view_exercise_creation_wizard" model="ir.ui.view">
    <field name="name">exercise.creation.wizard.form</field>
    <field name="model">bcm.exercise.creation.wizard</field>
    <field name="arch" type="xml">
        <form string="Create Exercise from Scenario">
            <div class="oe_title">
                <h1>🎯 Create Exercise from Scenario</h1>
            </div>

            <!-- Scenario Information -->
            <group string="Based on Scenario">
                <field name="scenario_id" readonly="1"/>
                <field name="scenario_title" readonly="1"/>
                <field name="scenario_category" readonly="1"/>
                <field name="scenario_level" readonly="1"/>
            </group>

            <!-- Exercise Configuration -->
            <group string="Exercise Configuration">
                <field name="exercise_name"/>
                <field name="exercise_type"/>
                <field name="planned_date"/>
                <field name="assigned_facilitator"/>
            </group>

            <!-- Template Selection -->
            <group string="Workflow Template">
                <field name="template_id" domain="[('id', 'in', available_template_ids)]"/>
                <field name="available_template_ids" invisible="1"/>

                <!-- Template Preview -->
                <div class="template-preview" attrs="{'invisible': [('template_id', '=', False)]}">
                    <h6>Template Preview:</h6>
                    <field name="template_description" readonly="1"/>
                    <field name="template_activities" readonly="1"/>
                </div>
            </group>

            <!-- Participants -->
            <group string="Participants">
                <field name="participant_ids" widget="many2many_tags"/>
                <field name="auto_notify_participants"/>
            </group>

            <!-- Actions -->
            <footer>
                <button string="Create Exercise" name="action_create_exercise"
                        type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

### **ИНТЕРФЕЙС 4: Enhanced Scenario Hub (Vue.js)**

#### **bcm_scenario_hub View Updates**:
```vue
<!-- UPDATE: BCMScenarioHub.vue with Template Integration -->
<template>
  <div class="bcm-scenario-hub">
    <!-- Existing content -->

    <!-- NEW: Template Integration Section -->
    <div class="template-integration-panel">
      <h6><i class="fas fa-cogs"></i> Exercise Templates</h6>

      <!-- Compatible Templates Display -->
      <div v-if="scenario.available_templates && scenario.available_templates.length > 0"
           class="compatible-templates">
        <div class="template-list">
          <div v-for="template in scenario.available_templates"
               :key="template.id"
               class="template-card">
            <div class="template-header">
              <h6>{{ template.name }}</h6>
              <span class="badge badge-workflow">{{ template.template_type }}</span>
            </div>
            <p class="template-description">{{ template.description }}</p>
            <div class="template-actions">
              <button @click="previewTemplate(template.id)"
                      class="btn btn-sm btn-outline-info">
                <i class="fas fa-eye"></i> Preview
              </button>
              <button @click="createExerciseWithTemplate(scenario.id, template.id)"
                      class="btn btn-sm btn-success">
                <i class="fas fa-play"></i> Create Exercise
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Exercise Creation -->
      <div class="quick-exercise-creation">
        <button @click="createExerciseFromScenario(scenario.id)"
                class="btn btn-primary btn-block">
          <i class="fas fa-plus-circle"></i> Create Exercise from Scenario
        </button>
      </div>

      <!-- Exercise History -->
      <div v-if="scenario.exercise_count > 0" class="exercise-history">
        <h6><i class="fas fa-history"></i> Exercise History</h6>
        <div class="exercise-stats">
          <span class="stat-badge">
            {{ scenario.exercise_count }} exercises created
          </span>
        </div>
        <button @click="viewExerciseHistory(scenario.id)"
                class="btn btn-link btn-sm">
          View Exercise History →
        </button>
      </div>
    </div>

    <!-- NEW: Workflow Progress Indicator -->
    <div v-if="activeExercises.length > 0" class="active-exercises-panel">
      <h6><i class="fas fa-play-circle"></i> Active Exercises</h6>
      <div class="exercise-list">
        <div v-for="exercise in activeExercises"
             :key="exercise.id"
             class="exercise-item">
          <div class="exercise-info">
            <h6>{{ exercise.name }}</h6>
            <div class="workflow-status">
              <span class="status-badge" :class="getStatusClass(exercise.workflow_status)">
                {{ exercise.workflow_status }}
              </span>
            </div>
          </div>
          <div class="exercise-actions">
            <button @click="openExerciseMonitoring(exercise.id)"
                    class="btn btn-sm btn-outline-primary">
              <i class="fas fa-chart-line"></i> Monitor
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BCMScenarioHub',
  data() {
    return {
      activeExercises: []
    }
  },
  methods: {
    async createExerciseFromScenario(scenarioId) {
      try {
        // Open Odoo wizard for exercise creation
        const wizardUrl = `http://localhost:8069/web#model=bcm.exercise.creation.wizard&scenario_id=${scenarioId}`;
        window.open(wizardUrl, '_blank');

      } catch (error) {
        this.$toast.error('Failed to open exercise creation wizard');
      }
    },

    async createExerciseWithTemplate(scenarioId, templateId) {
      try {
        // Direct exercise creation with specific template
        const response = await this.$http.post('/api/exercises/create-from-scenario', {
          scenario_id: scenarioId,
          template_id: templateId
        });

        if (response.data.success) {
          this.$toast.success('Exercise created successfully!');
          this.openExerciseMonitoring(response.data.exercise_id);
        }

      } catch (error) {
        this.$toast.error('Failed to create exercise: ' + error.message);
      }
    },

    async previewTemplate(templateId) {
      try {
        // Open template preview in new window
        const previewUrl = `http://localhost:8069/web/preview/template/${templateId}`;
        window.open(previewUrl, '_blank');

      } catch (error) {
        this.$toast.error('Failed to open template preview');
      }
    },

    openExerciseMonitoring(exerciseId) {
      // Open exercise monitoring dashboard
      const monitorUrl = `http://localhost:8069/web#id=${exerciseId}&model=bcm.exercise&view_type=form`;
      window.open(monitorUrl, '_blank');
    },

    getStatusClass(status) {
      return {
        'draft': 'badge-secondary',
        'running': 'badge-warning',
        'completed': 'badge-success',
        'failed': 'badge-danger'
      }[status] || 'badge-light';
    },

    async loadActiveExercises() {
      try {
        const response = await this.$http.get('/api/exercises/active');
        this.activeExercises = response.data.exercises || [];
      } catch (error) {
        console.error('Failed to load active exercises:', error);
      }
    }
  },

  async mounted() {
    await this.loadActiveExercises();
    // Set up real-time updates for exercise status
    this.setupExerciseStatusUpdates();
  }
}
</script>

<style scoped>
.template-integration-panel {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.template-card {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: #4A90E2;
  box-shadow: 0 2px 4px rgba(74, 144, 226, 0.1);
}

.badge-workflow {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.exercise-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.workflow-status .status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
```

---

### **ИНТЕРФЕЙС 5: Workflow Monitoring Dashboard (React Admin)**

#### **Real-time Exercise Monitoring**:
```jsx
// NEW: WorkflowMonitoringDashboard.jsx
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Progress, Timeline } from 'react-bootstrap';

const WorkflowMonitoringDashboard = () => {
  const [activeWorkflows, setActiveWorkflows] = useState([]);
  const [workflowTasks, setWorkflowTasks] = useState({});

  useEffect(() => {
    loadActiveWorkflows();
    const interval = setInterval(loadActiveWorkflows, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadActiveWorkflows = async () => {
    try {
      const response = await fetch('/api/exercises?workflow_status=running');
      const data = await response.json();
      setActiveWorkflows(data.exercises || []);

      // Load tasks for each workflow
      for (const exercise of data.exercises) {
        if (exercise.bpmn_process_id) {
          loadWorkflowTasks(exercise.id, exercise.bpmn_process_id);
        }
      }
    } catch (error) {
      console.error('Failed to load active workflows:', error);
    }
  };

  const loadWorkflowTasks = async (exerciseId, processId) => {
    try {
      const response = await fetch(`/api/bpmn/process-instances/${processId}/tasks`);
      const tasks = await response.json();
      setWorkflowTasks(prev => ({ ...prev, [exerciseId]: tasks }));
    } catch (error) {
      console.error(`Failed to load tasks for exercise ${exerciseId}:`, error);
    }
  };

  return (
    <div className="workflow-monitoring-dashboard">
      <Row>
        <Col md={12}>
          <Card>
            <Card.Header>
              <h5><i className="fas fa-chart-line"></i> Active Exercise Workflows</h5>
            </Card.Header>
            <Card.Body>
              {activeWorkflows.length === 0 ? (
                <div className="text-center text-muted">
                  <i className="fas fa-sleep fa-2x mb-2"></i>
                  <p>No active exercise workflows</p>
                </div>
              ) : (
                <Row>
                  {activeWorkflows.map((exercise, index) => (
                    <Col md={6} lg={4} key={index} className="mb-3">
                      <Card className="exercise-workflow-card">
                        <Card.Header className="d-flex justify-content-between">
                          <span>{exercise.name}</span>
                          <Badge variant={getWorkflowStatusVariant(exercise.workflow_status)}>
                            {exercise.workflow_status}
                          </Badge>
                        </Card.Header>
                        <Card.Body>
                          <div className="workflow-info">
                            <div className="info-row">
                              <span>Template:</span>
                              <span>{exercise.template_name || 'N/A'}</span>
                            </div>
                            <div className="info-row">
                              <span>Participants:</span>
                              <span>{exercise.participant_count} people</span>
                            </div>
                            <div className="info-row">
                              <span>Started:</span>
                              <span>{formatTime(exercise.started_at)}</span>
                            </div>
                          </div>

                          {/* Current Tasks */}
                          <div className="current-tasks mt-3">
                            <h6>Current Tasks:</h6>
                            {workflowTasks[exercise.id] ? (
                              <div className="task-list">
                                {workflowTasks[exercise.id].map((task, i) => (
                                  <div key={i} className="task-item">
                                    <div className="task-name">{task.name}</div>
                                    <div className="task-assignee">
                                      👤 {task.assignee_name || 'Unassigned'}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-muted">Loading tasks...</div>
                            )}
                          </div>

                          {/* Progress Indicator */}
                          <div className="workflow-progress mt-3">
                            <Progress
                              variant="info"
                              now={calculateWorkflowProgress(exercise)}
                              label={`${calculateWorkflowProgress(exercise)}%`}
                            />
                          </div>
                        </Card.Body>
                        <Card.Footer>
                          <div className="workflow-actions">
                            <button
                              className="btn btn-sm btn-outline-primary me-2"
                              onClick={() => openWorkflowDetail(exercise.id)}
                            >
                              <i className="fas fa-chart-gantt"></i> Details
                            </button>
                            <button
                              className="btn btn-sm btn-outline-warning"
                              onClick={() => pauseWorkflow(exercise.bpmn_process_id)}
                            >
                              <i className="fas fa-pause"></i> Pause
                            </button>
                          </div>
                        </Card.Footer>
                      </Card>
                    </Col>
                  ))}
                </Row>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Workflow Timeline */}
      <Row className="mt-4">
        <Col md={12}>
          <Card>
            <Card.Header>
              <h5><i className="fas fa-timeline"></i> Workflow Timeline</h5>
            </Card.Header>
            <Card.Body>
              <WorkflowTimelineComponent workflows={activeWorkflows} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default WorkflowMonitoringDashboard;
```

---

## 📋 **Technical Requirements для Interface Team**

### **API Endpoints для Integration:**

```javascript
// NEW APIs для ЭТАП 3:

// Template Management
GET    /api/templates                    # Get all templates
GET    /api/templates/workflow           # Get workflow templates only
POST   /api/templates/{id}/preview       # Preview template
POST   /api/templates/{id}/generate-ai   # AI template generation

// Exercise Management
POST   /api/exercises/create-from-scenario  # Create exercise from scenario
GET    /api/exercises/{id}/workflow-tasks   # Get current workflow tasks
POST   /api/exercises/{id}/start-workflow   # Start BPMN workflow
GET    /api/exercises/active                # Get active exercises

// BPMN Integration
GET    /api/bpmn/process-instances/{id}/status  # Get workflow status
GET    /api/bpmn/process-instances/{id}/tasks   # Get workflow tasks
POST   /api/bpmn/tasks/{id}/complete           # Complete task
```

### **Environment Variables:**
```env
# NEW for ЭТАП 3:
VUE_APP_TEMPLATES_URL=http://localhost:8069/api/templates
VUE_APP_BPMN_URL=http://localhost:8005
VUE_APP_EXERCISE_URL=http://localhost:8069/api/exercises
```

---

## 🎯 **Priority для Interface Team:**

### **ПРИОРИТЕТ 1**: Template Integration в BCMScenarioHub.vue
- **Время**: 1-2 дня
- **Функции**: Compatible templates display, exercise creation buttons

### **ПРИОРИТЕТ 2**: Exercise Creation Wizard (Odoo)
- **Время**: 2-3 дня
- **Функции**: Template selection, participant assignment, workflow configuration

### **ПРИОРИТЕТ 3**: Workflow Monitoring Dashboard (React)
- **Время**: 2-3 дня
- **Функции**: Real-time exercise monitoring, task tracking, progress indicators

---

## ✅ **ЭТАП 3: Complete Implementation + Interface Specs Ready!**

**Вся backend логика реализована + детальное ТЗ для интерфейсов готово!** 🎨🚀

**Документация сохранена в:**
- `/docs/PHASE_3_IMPLEMENTATION_COMPLETE.md`
- `/docs/frontend/PHASE_3_INTERFACE_REQUIREMENTS.md`

**Переходим к ЭТАП 4 или есть вопросы по ЭТАП 3?** 🤔