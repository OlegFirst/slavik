# ЭТАП 4: Advanced Exercise Simulation - Interface Requirements

## 🎯 Scope of Interface Development - ЭТАП 4

### **Реализованные возможности симуляции:**

```yaml
Services Running:
  ✅ Exercise Simulators Bridge (:8094) - Unified API
  ✅ JaamSim Engine (:5900) - Discrete event simulation
  ✅ Simulation Adapter (:8012) - Coordination layer

Integration Complete:
  ✅ bcm_templates → JaamSim config generation
  ✅ bcm_exercise → BPMN workflow execution
  ✅ Real-time simulation monitoring
```

---

## 🎨 **НОВЫЕ ИНТЕРФЕЙСЫ ДЛЯ ЭТАП 4**

### **ИНТЕРФЕЙС 1: Simulation Control Panel (Vue.js)**

#### **Location**: Web Portal v2 - `/frontend/web_portal_v2/src/components/simulation/`

#### **SimulationControlPanel.vue**:
```vue
<template>
  <div class="simulation-control-panel">
    <!-- Simulation Status Header -->
    <div class="simulation-header">
      <div class="status-indicator" :class="simulationStatus">
        <i class="fas fa-play-circle" v-if="simulationStatus === 'running'"></i>
        <i class="fas fa-pause-circle" v-if="simulationStatus === 'paused'"></i>
        <i class="fas fa-stop-circle" v-if="simulationStatus === 'stopped'"></i>
        <span>{{ simulationStatusText }}</span>
      </div>

      <div class="simulation-controls">
        <button @click="startSimulation"
                :disabled="simulationStatus === 'running'"
                class="btn btn-success">
          <i class="fas fa-play"></i> Start
        </button>
        <button @click="pauseSimulation"
                :disabled="simulationStatus !== 'running'"
                class="btn btn-warning">
          <i class="fas fa-pause"></i> Pause
        </button>
        <button @click="stopSimulation"
                :disabled="simulationStatus === 'stopped'"
                class="btn btn-danger">
          <i class="fas fa-stop"></i> Stop
        </button>
      </div>
    </div>

    <!-- JaamSim Simulation Display -->
    <div class="simulation-display">
      <div class="row">
        <div class="col-md-8">
          <!-- JaamSim VNC Viewer -->
          <div class="jaamsim-viewer">
            <h6><i class="fas fa-desktop"></i> JaamSim Simulation View</h6>
            <div class="vnc-container">
              <iframe :src="vncViewerUrl"
                      width="100%" height="500px"
                      frameborder="0">
              </iframe>
              <div class="vnc-info">
                <small>VNC Access: vnc://localhost:5900</small>
                <button @click="openVNCExternal" class="btn btn-link btn-sm">
                  <i class="fas fa-external-link-alt"></i> Open in VNC Client
                </button>
              </div>
            </div>
          </div>

          <!-- Real-time Metrics -->
          <div class="simulation-metrics mt-4">
            <h6><i class="fas fa-chart-line"></i> Real-time Metrics</h6>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-value">{{ metrics.processedEvents || 0 }}</div>
                <div class="metric-label">Events Processed</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ metrics.activeEntities || 0 }}</div>
                <div class="metric-label">Active Entities</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ metrics.queueLength || 0 }}</div>
                <div class="metric-label">Queue Length</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">{{ metrics.utilization || 0 }}%</div>
                <div class="metric-label">Resource Utilization</div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <!-- Exercise Progress -->
          <div class="exercise-progress">
            <h6><i class="fas fa-tasks"></i> Exercise Progress</h6>

            <div class="progress-timeline">
              <div v-for="(phase, index) in exercisePhases"
                   :key="index"
                   class="timeline-item"
                   :class="{
                     'completed': phase.status === 'completed',
                     'active': phase.status === 'active',
                     'pending': phase.status === 'pending'
                   }">
                <div class="timeline-marker">
                  <i class="fas fa-check" v-if="phase.status === 'completed'"></i>
                  <i class="fas fa-clock" v-else-if="phase.status === 'active'"></i>
                  <i class="fas fa-circle" v-else></i>
                </div>
                <div class="timeline-content">
                  <h6>{{ phase.name }}</h6>
                  <p>{{ phase.description }}</p>
                  <small v-if="phase.completedAt">
                    Completed: {{ formatTime(phase.completedAt) }}
                  </small>
                </div>
              </div>
            </div>
          </div>

          <!-- Participant Activity -->
          <div class="participant-activity mt-4">
            <h6><i class="fas fa-users"></i> Participant Activity</h6>
            <div class="activity-list">
              <div v-for="activity in recentActivity"
                   :key="activity.id"
                   class="activity-item">
                <div class="activity-user">{{ activity.user_name }}</div>
                <div class="activity-action">{{ activity.action }}</div>
                <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
              </div>
            </div>
          </div>

          <!-- NICS Integration Panel -->
          <div class="nics-integration mt-4" v-if="nicsEnabled">
            <h6><i class="fas fa-sitemap"></i> NICS Command Structure</h6>
            <div class="nics-roles">
              <div v-for="role in nicsRoles" :key="role.code" class="role-assignment">
                <div class="role-title">{{ role.name }}</div>
                <div class="role-assignee">{{ role.assignee || 'Unassigned' }}</div>
              </div>
            </div>
            <button @click="openNICSPlatform" class="btn btn-outline-primary btn-sm mt-2">
              <i class="fas fa-external-link-alt"></i> Open NICS Platform
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Simulation Results Panel -->
    <div class="simulation-results mt-4" v-if="simulationResults">
      <h6><i class="fas fa-chart-bar"></i> Simulation Results</h6>
      <div class="results-tabs">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'summary' }"
               @click="activeTab = 'summary'">Summary</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'metrics' }"
               @click="activeTab = 'metrics'">Metrics</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'raw' }"
               @click="activeTab = 'raw'">Raw Data</a>
          </li>
        </ul>

        <div class="tab-content">
          <!-- Summary Tab -->
          <div v-if="activeTab === 'summary'" class="tab-pane">
            <SimulationSummaryChart :data="simulationResults.summary" />
          </div>

          <!-- Metrics Tab -->
          <div v-if="activeTab === 'metrics'" class="tab-pane">
            <SimulationMetricsTable :data="simulationResults.metrics" />
          </div>

          <!-- Raw Data Tab -->
          <div v-if="activeTab === 'raw'" class="tab-pane">
            <pre class="code-block">{{ JSON.stringify(simulationResults.raw, null, 2) }}</pre>
            <button @click="downloadResults" class="btn btn-outline-primary mt-2">
              <i class="fas fa-download"></i> Download CSV
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SimulationSummaryChart from './SimulationSummaryChart.vue';
import SimulationMetricsTable from './SimulationMetricsTable.vue';

export default {
  name: 'SimulationControlPanel',
  components: {
    SimulationSummaryChart,
    SimulationMetricsTable
  },
  props: {
    exerciseId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      simulationStatus: 'stopped',
      metrics: {},
      exercisePhases: [],
      recentActivity: [],
      nicsEnabled: false,
      nicsRoles: [],
      simulationResults: null,
      activeTab: 'summary',
      vncViewerUrl: 'http://localhost:5900'
    }
  },
  computed: {
    simulationStatusText() {
      return {
        'running': 'Simulation Running',
        'paused': 'Simulation Paused',
        'stopped': 'Simulation Stopped'
      }[this.simulationStatus] || 'Unknown'
    }
  },
  methods: {
    async startSimulation() {
      try {
        const response = await this.$http.post(
          `http://localhost:8094/api/simulations/${this.exerciseId}/start`
        );

        if (response.data.success) {
          this.simulationStatus = 'running';
          this.startRealTimeUpdates();
          this.$toast.success('Simulation started successfully');
        }
      } catch (error) {
        this.$toast.error('Failed to start simulation: ' + error.message);
      }
    },

    startRealTimeUpdates() {
      // WebSocket connection for real-time updates
      if (this.ws) {
        this.ws.close();
      }

      this.ws = new WebSocket(`ws://localhost:8094/ws/simulation/${this.exerciseId}`);

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'metrics_update') {
          this.metrics = data.metrics;
        } else if (data.type === 'phase_update') {
          this.updateExercisePhase(data.phase);
        } else if (data.type === 'participant_activity') {
          this.recentActivity.unshift(data.activity);
          if (this.recentActivity.length > 10) {
            this.recentActivity = this.recentActivity.slice(0, 10);
          }
        }
      };
    }
  },

  async mounted() {
    await this.loadExerciseData();
    this.checkNICSIntegration();
  },

  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  }
}
</script>
```

---

### **ИНТЕРФЕЙС 2: Exercise Monitoring Dashboard (Admin Panel)**

#### **Location**: Admin Panel - `/frontend/admin_panel/src/components/`

#### **ExerciseMonitoringDashboard.jsx**:
```jsx
// NEW: Real-time Exercise Monitoring
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Badge, Progress, Table } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';

const ExerciseMonitoringDashboard = () => {
  const [activeExercises, setActiveExercises] = useState([]);
  const [simulationMetrics, setSimulationMetrics] = useState({});
  const [exerciseTimeline, setExerciseTimeline] = useState([]);

  // Real-time simulation monitoring
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8094/ws/monitoring');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'exercise_started':
          loadActiveExercises();
          break;
        case 'simulation_metrics':
          setSimulationMetrics(prev => ({
            ...prev,
            [data.exercise_id]: data.metrics
          }));
          break;
        case 'exercise_completed':
          handleExerciseCompletion(data);
          break;
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="exercise-monitoring-dashboard">
      {/* Active Exercises Overview */}
      <Row className="mb-4">
        <Col md={12}>
          <Card>
            <Card.Header>
              <h5><i className="fas fa-play-circle"></i> Active Exercise Simulations</h5>
            </Card.Header>
            <Card.Body>
              {activeExercises.length === 0 ? (
                <div className="text-center text-muted">
                  <i className="fas fa-sleep fa-3x mb-3"></i>
                  <p>No active exercise simulations</p>
                  <button className="btn btn-primary" onClick={openExerciseCreation}>
                    <i className="fas fa-plus"></i> Start New Exercise
                  </button>
                </div>
              ) : (
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Exercise Name</th>
                      <th>Type</th>
                      <th>Simulation Status</th>
                      <th>Participants</th>
                      <th>Duration</th>
                      <th>Progress</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeExercises.map((exercise, index) => (
                      <tr key={index}>
                        <td>
                          <strong>{exercise.name}</strong>
                          {exercise.ai_generated && (
                            <Badge variant="success" className="ml-2">
                              <i className="fas fa-robot"></i> AI
                            </Badge>
                          )}
                        </td>
                        <td>
                          <Badge variant="info">{exercise.exercise_type}</Badge>
                        </td>
                        <td>
                          <Badge variant={getSimulationStatusVariant(exercise.simulation_status)}>
                            {exercise.simulation_status}
                          </Badge>
                        </td>
                        <td>{exercise.participant_count} people</td>
                        <td>{exercise.elapsed_time}</td>
                        <td>
                          <Progress
                            variant="success"
                            now={exercise.progress_percentage}
                            label={`${exercise.progress_percentage}%`}
                          />
                        </td>
                        <td>
                          <div className="btn-group">
                            <button
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => openSimulationDetail(exercise.id)}
                            >
                              <i className="fas fa-chart-line"></i> Details
                            </button>
                            <button
                              className="btn btn-sm btn-outline-info"
                              onClick={() => openVNCViewer(exercise.id)}
                            >
                              <i className="fas fa-desktop"></i> VNC
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* JaamSim Metrics Charts */}
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6><i className="fas fa-chart-area"></i> Resource Utilization</h6>
            </Card.Header>
            <Card.Body>
              <Line data={resourceUtilizationData} options={chartOptions} />
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h6><i className="fas fa-clock"></i> Response Times</h6>
            </Card.Header>
            <Card.Body>
              <Line data={responseTimeData} options={chartOptions} />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* NICS Integration Status */}
      <Row className="mb-4">
        <Col md={12}>
          <Card>
            <Card.Header>
              <h6><i className="fas fa-sitemap"></i> NICS Command Structure</h6>
            </Card.Header>
            <Card.Body>
              <NICSCommandStructure exercises={activeExercises} />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// NICS Command Structure Component
const NICSCommandStructure = ({ exercises }) => {
  const [commandStructure, setCommandStructure] = useState({});

  const nicsRoles = [
    { code: 'IC', name: 'Incident Commander', level: 1 },
    { code: 'OPS', name: 'Operations Chief', level: 2 },
    { code: 'PLAN', name: 'Planning Chief', level: 2 },
    { code: 'LOG', name: 'Logistics Chief', level: 2 },
    { code: 'FA', name: 'Finance/Admin Chief', level: 2 }
  ];

  return (
    <div className="nics-command-structure">
      {exercises.length === 0 ? (
        <div className="text-center text-muted">
          <p>No active exercises with NICS integration</p>
        </div>
      ) : (
        <div className="command-org-chart">
          {exercises.map((exercise, index) => (
            <div key={index} className="exercise-command">
              <h6>Exercise: {exercise.name}</h6>
              <div className="org-chart">
                {nicsRoles.map((role, roleIndex) => (
                  <div key={roleIndex}
                       className={`role-box level-${role.level}`}>
                    <div className="role-title">{role.name}</div>
                    <div className="role-code">({role.code})</div>
                    <div className="role-assignee">
                      {exercise.nics_assignments?.[role.code] || 'Unassigned'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExerciseMonitoringDashboard;
```

---

## 🧠 **Scenario Orchestrator как накопитель опыта**

Ты абсолютно прав! **Scenario Orchestrator должен быть центром experience accumulation**:

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create PHASE 4 documentation and interface specs", "status": "completed", "activeForm": "Creating PHASE 4 documentation and interface specs"}, {"content": "Enhance Scenario Orchestrator as experience accumulator", "status": "in_progress", "activeForm": "Enhancing Scenario Orchestrator as experience accumulator"}, {"content": "Design learning loop architecture", "status": "pending", "activeForm": "Designing learning loop architecture"}, {"content": "Prepare for PHASE 5 Intelligence & Analytics", "status": "pending", "activeForm": "Preparing for PHASE 5 Intelligence & Analytics"}]