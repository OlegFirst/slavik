<template>
  <div class="bcm-exercise">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>
            <i class="fas fa-dumbbell"></i>
            BCM Exercise Management
          </h1>
          <p>Plan, execute, and analyze business continuity exercises</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-outline-primary" @click="getAIRecommendations">
            <i class="fas fa-robot"></i>
            AI Recommendations
          </button>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="fas fa-plus"></i>
            New Exercise
          </button>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #FF6B35, #FF8B65)">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ exerciseStats.total || 0 }}</div>
            <div class="kpi-label">Total Exercises</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #4A90E2, #6BB6FF)">
            <i class="fas fa-play"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ exerciseStats.ongoing || 0 }}</div>
            <div class="kpi-label">In Progress</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #10B981, #34D399)">
            <i class="fas fa-trophy"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ exerciseStats.completed || 0 }}</div>
            <div class="kpi-label">Completed</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon" style="background: linear-gradient(135deg, #8B5CF6, #A78BFA)">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="kpi-content">
            <div class="kpi-value">{{ averageEffectiveness }}%</div>
            <div class="kpi-label">Avg Effectiveness</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Tabs Navigation -->
      <div class="tabs-container">
        <div class="tabs-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <i :class="tab.icon"></i>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        <!-- Exercise List Tab -->
        <div v-if="activeTab === 'exercises'" class="tab-pane active">
          <div class="exercises-toolbar">
            <div class="filters">
              <select v-model="filters.status" @change="loadExercises" class="form-select">
                <option value="">All Status</option>
                <option value="planned">Planned</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
              <select v-model="filters.exercise_type" @change="loadExercises" class="form-select">
                <option value="">All Types</option>
                <option value="tabletop">Tabletop</option>
                <option value="walkthrough">Walkthrough</option>
                <option value="functional">Functional</option>
                <option value="full_scale">Full-Scale</option>
              </select>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search exercises..."
                class="form-control"
                @input="debounceSearch"
              >
            </div>
            <div class="view-toggle">
              <button
                :class="['btn', 'btn-sm', viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary']"
                @click="viewMode = 'list'"
              >
                <i class="fas fa-list"></i>
              </button>
              <button
                :class="['btn', 'btn-sm', viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary']"
                @click="viewMode = 'grid'"
              >
                <i class="fas fa-th"></i>
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading exercises...</p>
          </div>

          <!-- Exercise Grid View -->
          <div v-else-if="viewMode === 'grid'" class="exercise-grid">
            <div
              v-for="exercise in filteredExercises"
              :key="exercise.id"
              class="exercise-card"
              @click="selectExercise(exercise)"
            >
              <div class="card-header">
                <div class="exercise-type-badge" :class="exercise.exercise_type">
                  {{ formatExerciseType(exercise.exercise_type) }}
                </div>
                <div class="exercise-status" :class="exercise.status">
                  {{ formatStatus(exercise.status) }}
                </div>
              </div>
              <div class="card-body">
                <h3>{{ exercise.name }}</h3>
                <p>{{ truncateText(exercise.description, 100) }}</p>
                <div class="exercise-meta">
                  <div class="meta-item">
                    <i class="fas fa-calendar"></i>
                    {{ formatDate(exercise.scheduled_date) }}
                  </div>
                  <div class="meta-item">
                    <i class="fas fa-clock"></i>
                    {{ exercise.duration || 0 }}min
                  </div>
                  <div class="meta-item">
                    <i class="fas fa-users"></i>
                    {{ exercise.participants?.length || 0 }} participants
                  </div>
                </div>
              </div>
              <div class="card-footer">
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: getExerciseProgress(exercise) + '%' }"
                  ></div>
                </div>
                <div class="actions">
                  <button
                    v-if="exercise.status === 'planned'"
                    class="btn btn-sm btn-success"
                    @click.stop="startExercise(exercise.id)"
                  >
                    <i class="fas fa-play"></i>
                    Start
                  </button>
                  <button
                    v-if="exercise.status === 'in_progress'"
                    class="btn btn-sm btn-primary"
                    @click.stop="monitorExercise(exercise.id)"
                  >
                    <i class="fas fa-eye"></i>
                    Monitor
                  </button>
                  <button
                    class="btn btn-sm btn-outline-primary"
                    @click.stop="editExercise(exercise)"
                  >
                    <i class="fas fa-edit"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Exercise List View -->
          <div v-else class="exercise-list">
            <div class="table-container">
              <table class="exercise-table">
                <thead>
                  <tr>
                    <th>Exercise Name</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Scheduled Date</th>
                    <th>Duration</th>
                    <th>Participants</th>
                    <th>Progress</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="exercise in filteredExercises" :key="exercise.id">
                    <td>
                      <div class="exercise-name" @click="selectExercise(exercise)">
                        <strong>{{ exercise.name }}</strong>
                        <small>{{ truncateText(exercise.description, 60) }}</small>
                      </div>
                    </td>
                    <td>
                      <span class="type-badge" :class="exercise.exercise_type">
                        {{ formatExerciseType(exercise.exercise_type) }}
                      </span>
                    </td>
                    <td>
                      <span class="status-badge" :class="exercise.status">
                        {{ formatStatus(exercise.status) }}
                      </span>
                    </td>
                    <td>{{ formatDate(exercise.scheduled_date) }}</td>
                    <td>{{ exercise.duration || 0 }}min</td>
                    <td>{{ exercise.participants?.length || 0 }}</td>
                    <td>
                      <div class="progress-container">
                        <div class="progress-bar-small">
                          <div
                            class="progress-fill"
                            :style="{ width: getExerciseProgress(exercise) + '%' }"
                          ></div>
                        </div>
                        <span class="progress-text">{{ getExerciseProgress(exercise) }}%</span>
                      </div>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button
                          v-if="exercise.status === 'planned'"
                          class="btn btn-sm btn-success"
                          @click="startExercise(exercise.id)"
                          title="Start Exercise"
                        >
                          <i class="fas fa-play"></i>
                        </button>
                        <button
                          v-if="exercise.status === 'in_progress'"
                          class="btn btn-sm btn-primary"
                          @click="monitorExercise(exercise.id)"
                          title="Monitor Exercise"
                        >
                          <i class="fas fa-eye"></i>
                        </button>
                        <button
                          class="btn btn-sm btn-outline-primary"
                          @click="editExercise(exercise)"
                          title="Edit Exercise"
                        >
                          <i class="fas fa-edit"></i>
                        </button>
                        <button
                          class="btn btn-sm btn-outline-danger"
                          @click="deleteExercise(exercise.id)"
                          title="Delete Exercise"
                        >
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Exercise Monitoring Tab -->
        <div v-if="activeTab === 'monitoring'" class="tab-pane active">
          <div v-if="!currentExercise" class="empty-state">
            <i class="fas fa-eye"></i>
            <h3>No Exercise Selected</h3>
            <p>Select an active exercise to monitor real-time progress</p>
          </div>
          <div v-else class="monitoring-dashboard">
            <div class="monitoring-header">
              <h2>{{ currentExercise.name }}</h2>
              <div class="status-indicator" :class="exerciseStatus.status">
                {{ formatStatus(exerciseStatus.status) }}
              </div>
            </div>

            <div class="monitoring-grid">
              <!-- Exercise Progress -->
              <div class="monitoring-card">
                <h3><i class="fas fa-chart-line"></i> Exercise Progress</h3>
                <div class="progress-circle">
                  <div class="progress-value">{{ exerciseStatus.progress_percentage || 0 }}%</div>
                  <div class="progress-label">{{ exerciseStatus.current_phase || 'Initializing' }}</div>
                </div>
                <div class="timeline">
                  <div class="timeline-item" v-for="phase in exercisePhases" :key="phase.id">
                    <div
                      class="timeline-marker"
                      :class="{ active: phase.id === exerciseStatus.current_phase, completed: phase.completed }"
                    ></div>
                    <div class="timeline-content">
                      <strong>{{ phase.name }}</strong>
                      <small>{{ phase.description }}</small>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Participants Status -->
              <div class="monitoring-card">
                <h3><i class="fas fa-users"></i> Participants</h3>
                <div class="participant-grid">
                  <div
                    v-for="participant in currentParticipants"
                    :key="participant.id"
                    class="participant-card"
                  >
                    <div class="participant-avatar">{{ getInitials(participant.name) }}</div>
                    <div class="participant-info">
                      <strong>{{ participant.name }}</strong>
                      <small>{{ participant.role }}</small>
                    </div>
                    <div class="participant-status" :class="participant.status">
                      <i :class="getStatusIcon(participant.status)"></i>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Current Inject -->
              <div v-if="exerciseStatus.current_inject" class="monitoring-card">
                <h3><i class="fas fa-bolt"></i> Current Inject</h3>
                <div class="inject-card">
                  <div class="inject-header">
                    <strong>{{ exerciseStatus.current_inject.name }}</strong>
                    <span class="inject-type">{{ exerciseStatus.current_inject.type }}</span>
                  </div>
                  <p>{{ exerciseStatus.current_inject.content }}</p>
                  <div class="inject-actions">
                    <button class="btn btn-sm btn-primary" @click="executeNextInject">
                      Next Inject
                    </button>
                    <button class="btn btn-sm btn-outline-primary" @click="pauseExercise">
                      Pause
                    </button>
                  </div>
                </div>
              </div>

              <!-- Real-time Metrics -->
              <div class="monitoring-card">
                <h3><i class="fas fa-tachometer-alt"></i> Real-time Metrics</h3>
                <div class="metrics-grid">
                  <div class="metric-item">
                    <div class="metric-value">{{ realTimeMetrics.response_time || 0 }}min</div>
                    <div class="metric-label">Avg Response Time</div>
                  </div>
                  <div class="metric-item">
                    <div class="metric-value">{{ realTimeMetrics.decisions_made || 0 }}</div>
                    <div class="metric-label">Decisions Made</div>
                  </div>
                  <div class="metric-item">
                    <div class="metric-value">{{ realTimeMetrics.communications || 0 }}</div>
                    <div class="metric-label">Communications</div>
                  </div>
                  <div class="metric-item">
                    <div class="metric-value">{{ realTimeMetrics.issues_raised || 0 }}</div>
                    <div class="metric-label">Issues Raised</div>
                  </div>
                </div>
              </div>

              <!-- Simulation Data -->
              <div v-if="simulationData" class="monitoring-card">
                <h3><i class="fas fa-cube"></i> Simulation Engine</h3>
                <div class="simulation-status">
                  <div class="sim-indicator" :class="simulationData.status">
                    {{ simulationData.status.toUpperCase() }}
                  </div>
                  <div class="sim-metrics">
                    <div>Entities: {{ simulationData.entities || 0 }}</div>
                    <div>Events: {{ simulationData.events || 0 }}</div>
                    <div>Sim Time: {{ simulationData.simulation_time || '00:00' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Analytics Tab -->
        <div v-if="activeTab === 'analytics'" class="tab-pane active">
          <div class="analytics-dashboard">
            <div class="analytics-header">
              <h2>Exercise Analytics</h2>
              <div class="period-selector">
                <select v-model="analyticsPeriod" @change="loadAnalytics" class="form-select">
                  <option value="30">Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                  <option value="180">Last 6 Months</option>
                  <option value="365">Last Year</option>
                </select>
              </div>
            </div>

            <div class="analytics-grid">
              <!-- Exercise Trends Chart -->
              <div class="analytics-card full-width">
                <h3><i class="fas fa-chart-line"></i> Exercise Trends</h3>
                <div class="chart-container">
                  <canvas ref="trendsChart"></canvas>
                </div>
              </div>

              <!-- Effectiveness Scores -->
              <div class="analytics-card">
                <h3><i class="fas fa-trophy"></i> Effectiveness Scores</h3>
                <div class="score-list">
                  <div
                    v-for="score in effectivenessScores"
                    :key="score.exercise_id"
                    class="score-item"
                  >
                    <div class="score-info">
                      <strong>{{ score.exercise_name }}</strong>
                      <small>{{ formatDate(score.date) }}</small>
                    </div>
                    <div class="score-value" :class="getScoreClass(score.score)">
                      {{ score.score }}%
                    </div>
                  </div>
                </div>
              </div>

              <!-- Exercise Types Distribution -->
              <div class="analytics-card">
                <h3><i class="fas fa-pie-chart"></i> Exercise Types</h3>
                <div class="chart-container">
                  <canvas ref="typesChart"></canvas>
                </div>
              </div>

              <!-- Participation Analysis -->
              <div class="analytics-card">
                <h3><i class="fas fa-users"></i> Participation Analysis</h3>
                <div class="participation-stats">
                  <div class="stat-item">
                    <div class="stat-value">{{ participationStats.average_participants || 0 }}</div>
                    <div class="stat-label">Avg Participants</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ participationStats.participation_rate || 0 }}%</div>
                    <div class="stat-label">Participation Rate</div>
                  </div>
                  <div class="stat-item">
                    <div class="stat-value">{{ participationStats.completion_rate || 0 }}%</div>
                    <div class="stat-label">Completion Rate</div>
                  </div>
                </div>
              </div>

              <!-- Lessons Learned -->
              <div class="analytics-card full-width">
                <h3><i class="fas fa-lightbulb"></i> Key Lessons Learned</h3>
                <div class="lessons-list">
                  <div
                    v-for="lesson in lessonsLearned"
                    :key="lesson.id"
                    class="lesson-item"
                  >
                    <div class="lesson-header">
                      <strong>{{ lesson.title }}</strong>
                      <span class="lesson-category">{{ lesson.category }}</span>
                    </div>
                    <p>{{ lesson.description }}</p>
                    <div class="lesson-actions">
                      <span class="lesson-impact" :class="lesson.impact">{{ lesson.impact }} Impact</span>
                      <span class="lesson-status">{{ lesson.status }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Scenarios Tab -->
        <div v-if="activeTab === 'scenarios'" class="tab-pane active">
          <div class="scenarios-header">
            <h2>Exercise Scenarios</h2>
            <button class="btn btn-primary" @click="showScenarioModal = true">
              <i class="fas fa-plus"></i>
              Create Scenario
            </button>
          </div>

          <div class="scenarios-grid">
            <div
              v-for="scenario in scenarios"
              :key="scenario.id"
              class="scenario-card"
            >
              <div class="scenario-header">
                <h3>{{ scenario.name }}</h3>
                <div class="scenario-complexity" :class="scenario.complexity_level">
                  {{ scenario.complexity_level }}
                </div>
              </div>
              <div class="scenario-body">
                <p>{{ scenario.description }}</p>
                <div class="scenario-meta">
                  <div class="meta-row">
                    <i class="fas fa-tag"></i>
                    <span>{{ scenario.scenario_type }}</span>
                  </div>
                  <div class="meta-row">
                    <i class="fas fa-clock"></i>
                    <span>{{ scenario.estimated_duration }}min</span>
                  </div>
                  <div class="meta-row">
                    <i class="fas fa-users"></i>
                    <span>{{ scenario.target_audience }}</span>
                  </div>
                </div>
                <div class="scenario-objectives">
                  <strong>Learning Objectives:</strong>
                  <ul>
                    <li v-for="objective in scenario.learning_objectives?.slice(0, 3)" :key="objective">
                      {{ objective }}
                    </li>
                  </ul>
                </div>
              </div>
              <div class="scenario-footer">
                <button class="btn btn-sm btn-primary" @click="useScenario(scenario)">
                  Use Scenario
                </button>
                <button class="btn btn-sm btn-outline-primary" @click="customizeScenario(scenario)">
                  Customize
                </button>
                <button class="btn btn-sm btn-outline-secondary" @click="editScenario(scenario)">
                  Edit
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Exercise Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-dialog" @click.stop>
        <div class="modal-header">
          <h3>Create New Exercise</h3>
          <button class="btn-close" @click="showCreateModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="createExercise" class="exercise-form">
            <div class="form-grid">
              <div class="form-group">
                <label>Exercise Name *</label>
                <input
                  v-model="newExercise.name"
                  type="text"
                  class="form-control"
                  required
                >
              </div>
              <div class="form-group">
                <label>Exercise Type *</label>
                <select v-model="newExercise.exercise_type" class="form-select" required>
                  <option value="">Select Type</option>
                  <option value="tabletop">Tabletop Exercise</option>
                  <option value="walkthrough">Walkthrough Exercise</option>
                  <option value="functional">Functional Exercise</option>
                  <option value="full_scale">Full-Scale Exercise</option>
                </select>
              </div>
              <div class="form-group">
                <label>Scheduled Date *</label>
                <input
                  v-model="newExercise.scheduled_date"
                  type="datetime-local"
                  class="form-control"
                  required
                >
              </div>
              <div class="form-group">
                <label>Duration (minutes)</label>
                <input
                  v-model="newExercise.duration"
                  type="number"
                  class="form-control"
                  min="30"
                  max="1440"
                >
              </div>
              <div class="form-group full-width">
                <label>Description</label>
                <textarea
                  v-model="newExercise.description"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>
              <div class="form-group full-width">
                <label>Objectives</label>
                <div class="objectives-input">
                  <input
                    v-model="objectiveInput"
                    type="text"
                    class="form-control"
                    placeholder="Add objective and press Enter"
                    @keypress.enter.prevent="addObjective"
                  >
                  <div class="objectives-list">
                    <span
                      v-for="(objective, index) in newExercise.objectives"
                      :key="index"
                      class="objective-tag"
                    >
                      {{ objective }}
                      <button type="button" @click="removeObjective(index)">&times;</button>
                    </span>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>Scenario</label>
                <select v-model="newExercise.scenario_id" class="form-select">
                  <option value="">Select Scenario</option>
                  <option v-for="scenario in scenarios" :key="scenario.id" :value="scenario.id">
                    {{ scenario.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Complexity Level</label>
                <select v-model="newExercise.complexity_level" class="form-select">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="maximum">Maximum</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showCreateModal = false">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="creatingExercise">
                {{ creatingExercise ? 'Creating...' : 'Create Exercise' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- AI Recommendations Modal -->
    <div v-if="showRecommendationsModal" class="modal-overlay" @click="showRecommendationsModal = false">
      <div class="modal-dialog large" @click.stop>
        <div class="modal-header">
          <h3><i class="fas fa-robot"></i> AI Exercise Recommendations</h3>
          <button class="btn-close" @click="showRecommendationsModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingRecommendations" class="loading-state">
            <div class="spinner"></div>
            <p>Analyzing your environment and generating recommendations...</p>
          </div>
          <div v-else-if="aiRecommendations" class="recommendations-content">
            <div class="recommendations-grid">
              <div class="recommendation-section">
                <h4><i class="fas fa-lightbulb"></i> Recommended Scenarios</h4>
                <div class="recommendation-list">
                  <div
                    v-for="rec in aiRecommendations.scenario_recommendations"
                    :key="rec.type"
                    class="recommendation-item"
                  >
                    <strong>{{ rec.type }}</strong>
                    <p>{{ rec.reason }}</p>
                    <button class="btn btn-sm btn-primary" @click="applyScenarioRecommendation(rec)">
                      Apply
                    </button>
                  </div>
                </div>
              </div>
              <div class="recommendation-section">
                <h4><i class="fas fa-cogs"></i> Exercise Types</h4>
                <div class="recommendation-list">
                  <div
                    v-for="type in aiRecommendations.exercise_types"
                    :key="type"
                    class="recommendation-item"
                  >
                    <strong>{{ formatExerciseType(type) }}</strong>
                    <button class="btn btn-sm btn-primary" @click="applyTypeRecommendation(type)">
                      Use
                    </button>
                  </div>
                </div>
              </div>
              <div class="recommendation-section">
                <h4><i class="fas fa-calendar-alt"></i> Timing Suggestions</h4>
                <div class="timing-recommendation">
                  <p><strong>Recommended Date:</strong> {{ formatDate(aiRecommendations.timing_suggestions?.recommended_date) }}</p>
                  <p v-if="aiRecommendations.timing_suggestions?.reason">
                    <strong>Reason:</strong> {{ aiRecommendations.timing_suggestions.reason }}
                  </p>
                </div>
              </div>
              <div class="recommendation-section">
                <h4><i class="fas fa-users"></i> Participant Suggestions</h4>
                <div class="participant-recommendations">
                  <div
                    v-for="participant in aiRecommendations.participant_suggestions"
                    :key="participant.id"
                    class="participant-rec"
                  >
                    <strong>{{ participant.name }}</strong>
                    <small>{{ participant.job_title }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Assistant Panel Integration -->
    <AssistantPanel ref="assistantPanel" />
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import bcmExerciseService from '@/services/bcmExercise'
import eventBus from '@/services/eventbus'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BCMExercise',
  components: {
    AssistantPanel
  },
  setup() {
    const router = useRouter()

    // Reactive state
    const loading = ref(true)
    const exercises = ref([])
    const scenarios = ref([])
    const exerciseStats = reactive({
      total: 0,
      ongoing: 0,
      completed: 0,
      planned: 0,
      cancelled: 0
    })
    const currentExercise = ref(null)
    const exerciseStatus = reactive({
      status: 'not_started',
      progress_percentage: 0,
      current_phase: 'initialization',
      participants_status: {},
      metrics: {}
    })
    const realTimeMetrics = reactive({
      response_time: 0,
      decisions_made: 0,
      communications: 0,
      issues_raised: 0
    })
    const simulationData = ref(null)
    const currentParticipants = ref([])

    // UI State
    const activeTab = ref('exercises')
    const viewMode = ref('grid')
    const searchQuery = ref('')
    const filters = reactive({
      status: '',
      exercise_type: '',
      date_range: null
    })

    // Modals
    const showCreateModal = ref(false)
    const showRecommendationsModal = ref(false)
    const showScenarioModal = ref(false)
    const creatingExercise = ref(false)
    const loadingRecommendations = ref(false)

    // Form data
    const newExercise = reactive({
      name: '',
      description: '',
      exercise_type: '',
      scheduled_date: '',
      duration: 120,
      objectives: [],
      scenario_id: null,
      complexity_level: 'medium',
      participants: [],
      observers: [],
      success_criteria: [],
      resources_required: []
    })
    const objectiveInput = ref('')
    const aiRecommendations = ref(null)

    // Analytics
    const analyticsPeriod = ref('90')
    const effectivenessScores = ref([])
    const participationStats = reactive({
      average_participants: 0,
      participation_rate: 0,
      completion_rate: 0
    })
    const lessonsLearned = ref([])

    // Tabs configuration
    const tabs = [
      { id: 'exercises', label: 'Exercises', icon: 'fas fa-dumbbell' },
      { id: 'monitoring', label: 'Real-time Monitoring', icon: 'fas fa-eye' },
      { id: 'analytics', label: 'Analytics', icon: 'fas fa-chart-line' },
      { id: 'scenarios', label: 'Scenarios', icon: 'fas fa-file-alt' }
    ]

    // Exercise phases for monitoring
    const exercisePhases = [
      { id: 'initialization', name: 'Initialization', description: 'Setting up exercise environment', completed: false },
      { id: 'briefing', name: 'Briefing', description: 'Participant briefing and setup', completed: false },
      { id: 'execution', name: 'Execution', description: 'Exercise scenario execution', completed: false },
      { id: 'debrief', name: 'Debrief', description: 'Exercise debrief and feedback', completed: false },
      { id: 'analysis', name: 'Analysis', description: 'Results analysis and reporting', completed: false }
    ]

    // Computed properties
    const filteredExercises = computed(() => {
      let filtered = exercises.value

      if (filters.status) {
        filtered = filtered.filter(ex => ex.status === filters.status)
      }

      if (filters.exercise_type) {
        filtered = filtered.filter(ex => ex.exercise_type === filters.exercise_type)
      }

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(ex =>
          ex.name.toLowerCase().includes(query) ||
          ex.description?.toLowerCase().includes(query)
        )
      }

      return filtered
    })

    const averageEffectiveness = computed(() => {
      if (effectivenessScores.value.length === 0) return 0
      const total = effectivenessScores.value.reduce((sum, score) => sum + score.score, 0)
      return Math.round(total / effectivenessScores.value.length)
    })

    // Methods
    const loadExercises = async () => {
      try {
        loading.value = true
        const data = await bcmExerciseService.getExercises(filters)
        exercises.value = data

        // Update stats
        exerciseStats.total = data.length
        exerciseStats.ongoing = data.filter(ex => ex.status === 'in_progress').length
        exerciseStats.completed = data.filter(ex => ex.status === 'completed').length
        exerciseStats.planned = data.filter(ex => ex.status === 'planned').length
        exerciseStats.cancelled = data.filter(ex => ex.status === 'cancelled').length

      } catch (error) {
        console.error('Failed to load exercises:', error)
        showNotification('Failed to load exercises', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadScenarios = async () => {
      try {
        const data = await bcmExerciseService.getScenarios()
        scenarios.value = data
      } catch (error) {
        console.error('Failed to load scenarios:', error)
      }
    }

    const loadAnalytics = async () => {
      try {
        // Load effectiveness scores
        const scores = await bcmExerciseService.getExercises({
          status: 'completed',
          date_range: {
            start: new Date(Date.now() - analyticsPeriod.value * 24 * 60 * 60 * 1000).toISOString(),
            end: new Date().toISOString()
          }
        })

        effectivenessScores.value = scores.map(ex => ({
          exercise_id: ex.id,
          exercise_name: ex.name,
          score: ex.effectiveness_score || 0,
          date: ex.scheduled_date
        }))

        // Calculate participation stats
        if (scores.length > 0) {
          participationStats.average_participants = Math.round(
            scores.reduce((sum, ex) => sum + (ex.participants?.length || 0), 0) / scores.length
          )
          participationStats.participation_rate = 85 // This would be calculated based on actual data
          participationStats.completion_rate = Math.round((scores.length / (scores.length + exerciseStats.cancelled)) * 100) || 100
        }

        // Load lessons learned (mock data for now)
        lessonsLearned.value = [
          {
            id: 1,
            title: 'Communication Protocol Improvement',
            category: 'Communication',
            description: 'Need to establish clearer escalation paths during incidents',
            impact: 'high',
            status: 'In Progress'
          },
          {
            id: 2,
            title: 'Resource Allocation',
            category: 'Operations',
            description: 'Backup systems need faster activation procedures',
            impact: 'medium',
            status: 'Planned'
          }
        ]

        // Initialize charts after data is loaded
        await nextTick()
        initializeCharts()

      } catch (error) {
        console.error('Failed to load analytics:', error)
      }
    }

    const createExercise = async () => {
      try {
        creatingExercise.value = true
        await bcmExerciseService.createExercise(newExercise)

        showNotification('Exercise created successfully', 'success')
        showCreateModal.value = false
        resetNewExercise()
        await loadExercises()

      } catch (error) {
        console.error('Failed to create exercise:', error)
        showNotification('Failed to create exercise', 'error')
      } finally {
        creatingExercise.value = false
      }
    }

    const startExercise = async (exerciseId) => {
      try {
        const result = await bcmExerciseService.startExercise(exerciseId)
        showNotification('Exercise started successfully', 'success')

        // Switch to monitoring tab and load exercise
        activeTab.value = 'monitoring'
        currentExercise.value = exercises.value.find(ex => ex.id === exerciseId)
        await monitorExercise(exerciseId)

      } catch (error) {
        console.error('Failed to start exercise:', error)
        showNotification('Failed to start exercise', 'error')
      }
    }

    const monitorExercise = async (exerciseId) => {
      try {
        currentExercise.value = exercises.value.find(ex => ex.id === exerciseId)
        if (!currentExercise.value) return

        // Get exercise status
        const status = await bcmExerciseService.getExerciseStatus(exerciseId)
        Object.assign(exerciseStatus, status)

        // Load participants
        currentParticipants.value = currentExercise.value.participants || []

        // Setup real-time updates
        bcmExerciseService.setupRealTimeUpdates(exerciseId, handleRealTimeUpdate)

        // Switch to monitoring tab
        activeTab.value = 'monitoring'

      } catch (error) {
        console.error('Failed to monitor exercise:', error)
        showNotification('Failed to load exercise monitoring', 'error')
      }
    }

    const getAIRecommendations = async () => {
      try {
        showRecommendationsModal.value = true
        loadingRecommendations.value = true

        const recommendations = await bcmExerciseService.getAIRecommendations(1, {
          previous_exercises: exercises.value,
          current_risks: []
        })

        aiRecommendations.value = recommendations

      } catch (error) {
        console.error('Failed to get AI recommendations:', error)
        showNotification('Failed to get AI recommendations', 'error')
      } finally {
        loadingRecommendations.value = false
      }
    }

    const selectExercise = (exercise) => {
      currentExercise.value = exercise
      if (exercise.status === 'in_progress') {
        monitorExercise(exercise.id)
      }
    }

    const editExercise = (exercise) => {
      // This would open an edit modal (implementation similar to create modal)
      console.log('Edit exercise:', exercise)
    }

    const deleteExercise = async (exerciseId) => {
      if (!confirm('Are you sure you want to delete this exercise?')) return

      try {
        // Implementation would call delete API
        console.log('Delete exercise:', exerciseId)
        showNotification('Exercise deleted successfully', 'success')
        await loadExercises()
      } catch (error) {
        console.error('Failed to delete exercise:', error)
        showNotification('Failed to delete exercise', 'error')
      }
    }

    const executeNextInject = async () => {
      try {
        // Mock inject execution
        const mockInject = {
          name: 'System Failure Alert',
          type: 'technical',
          content: 'Primary database server has gone offline. Implement recovery procedures.',
          expected_responses: ['Activate backup systems', 'Notify stakeholders', 'Begin recovery process']
        }

        await bcmExerciseService.executeInject(currentExercise.value.id, mockInject)
        showNotification('Inject executed successfully', 'success')

      } catch (error) {
        console.error('Failed to execute inject:', error)
        showNotification('Failed to execute inject', 'error')
      }
    }

    const pauseExercise = () => {
      // Implementation would pause the exercise
      console.log('Pause exercise')
      showNotification('Exercise paused', 'info')
    }

    const handleRealTimeUpdate = (data) => {
      console.log('Real-time update:', data)

      // Update exercise status based on event type
      if (data.event_type?.includes('exercise')) {
        // Update exercise status, metrics, etc.
        if (data.data.progress_percentage) {
          exerciseStatus.progress_percentage = data.data.progress_percentage
        }
        if (data.data.current_phase) {
          exerciseStatus.current_phase = data.data.current_phase
        }
      }

      // Update real-time metrics
      if (data.data.metrics) {
        Object.assign(realTimeMetrics, data.data.metrics)
      }
    }

    const addObjective = () => {
      if (objectiveInput.value.trim()) {
        newExercise.objectives.push(objectiveInput.value.trim())
        objectiveInput.value = ''
      }
    }

    const removeObjective = (index) => {
      newExercise.objectives.splice(index, 1)
    }

    const resetNewExercise = () => {
      Object.assign(newExercise, {
        name: '',
        description: '',
        exercise_type: '',
        scheduled_date: '',
        duration: 120,
        objectives: [],
        scenario_id: null,
        complexity_level: 'medium',
        participants: [],
        observers: [],
        success_criteria: [],
        resources_required: []
      })
    }

    const applyScenarioRecommendation = (recommendation) => {
      // Implementation would create exercise based on recommendation
      console.log('Apply scenario recommendation:', recommendation)
      showCreateModal.value = true
      showRecommendationsModal.value = false
    }

    const applyTypeRecommendation = (exerciseType) => {
      newExercise.exercise_type = exerciseType
      showCreateModal.value = true
      showRecommendationsModal.value = false
    }

    const useScenario = (scenario) => {
      newExercise.scenario_id = scenario.id
      newExercise.duration = scenario.estimated_duration
      newExercise.objectives = [...(scenario.learning_objectives || [])]
      showCreateModal.value = true
    }

    const customizeScenario = async (scenario) => {
      try {
        // This would open a scenario customization modal
        console.log('Customize scenario:', scenario)
      } catch (error) {
        console.error('Failed to customize scenario:', error)
      }
    }

    const editScenario = (scenario) => {
      // Implementation would open scenario edit modal
      console.log('Edit scenario:', scenario)
    }

    const initializeCharts = () => {
      // Chart initialization would happen here using Chart.js or similar
      // This is a placeholder for chart initialization
      console.log('Initialize charts')
    }

    // Utility methods
    const formatDate = (dateString) => {
      if (!dateString) return 'Not scheduled'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatExerciseType = (type) => {
      const types = {
        tabletop: 'Tabletop',
        walkthrough: 'Walkthrough',
        functional: 'Functional',
        full_scale: 'Full-Scale'
      }
      return types[type] || type
    }

    const formatStatus = (status) => {
      const statuses = {
        planned: 'Planned',
        in_progress: 'In Progress',
        completed: 'Completed',
        cancelled: 'Cancelled',
        paused: 'Paused'
      }
      return statuses[status] || status
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const getExerciseProgress = (exercise) => {
      if (exercise.status === 'completed') return 100
      if (exercise.status === 'in_progress') return 50
      if (exercise.status === 'planned') return 0
      return 0
    }

    const getInitials = (name) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase()
    }

    const getStatusIcon = (status) => {
      const icons = {
        active: 'fas fa-circle text-success',
        away: 'fas fa-circle text-warning',
        offline: 'fas fa-circle text-secondary'
      }
      return icons[status] || 'fas fa-circle text-secondary'
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 70) return 'satisfactory'
      if (score >= 60) return 'needs-improvement'
      return 'poor'
    }

    const debounceSearch = (() => {
      let timeout
      return () => {
        clearTimeout(timeout)
        timeout = setTimeout(() => {
          // Search is reactive through computed property
        }, 300)
      }
    })()

    const showNotification = (message, type = 'info') => {
      // Integration with notification system
      window.dispatchEvent(new CustomEvent('showNotification', {
        detail: { message, type, timestamp: Date.now() }
      }))
    }

    // Lifecycle hooks
    onMounted(async () => {
      try {
        await Promise.all([
          loadExercises(),
          loadScenarios(),
          loadAnalytics()
        ])
      } catch (error) {
        console.error('Failed to initialize BCM Exercise module:', error)
      }
    })

    onUnmounted(() => {
      // Cleanup real-time connections
      if (currentExercise.value) {
        bcmExerciseService.disconnectRealTimeUpdates(currentExercise.value.id, handleRealTimeUpdate)
      }
    })

    // Watch for tab changes
    watch(activeTab, (newTab) => {
      if (newTab === 'analytics') {
        nextTick(() => initializeCharts())
      }
    })

    return {
      // State
      loading,
      exercises,
      scenarios,
      exerciseStats,
      currentExercise,
      exerciseStatus,
      realTimeMetrics,
      simulationData,
      currentParticipants,

      // UI State
      activeTab,
      viewMode,
      searchQuery,
      filters,
      tabs,
      exercisePhases,

      // Modals
      showCreateModal,
      showRecommendationsModal,
      showScenarioModal,
      creatingExercise,
      loadingRecommendations,

      // Forms
      newExercise,
      objectiveInput,
      aiRecommendations,

      // Analytics
      analyticsPeriod,
      effectivenessScores,
      participationStats,
      lessonsLearned,

      // Computed
      filteredExercises,
      averageEffectiveness,

      // Methods
      loadExercises,
      loadScenarios,
      loadAnalytics,
      createExercise,
      startExercise,
      monitorExercise,
      getAIRecommendations,
      selectExercise,
      editExercise,
      deleteExercise,
      executeNextInject,
      pauseExercise,
      addObjective,
      removeObjective,
      resetNewExercise,
      applyScenarioRecommendation,
      applyTypeRecommendation,
      useScenario,
      customizeScenario,
      editScenario,

      // Utilities
      formatDate,
      formatExerciseType,
      formatStatus,
      truncateText,
      getExerciseProgress,
      getInitials,
      getStatusIcon,
      getScoreClass,
      debounceSearch
    }
  }
}
</script>

<style scoped>
.bcm-exercise {
  min-height: 100vh;
  background: linear-gradient(to bottom, #f8fafc 0%, #f1f5f9 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* Header Styles */
.page-header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 24px;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1A1A1A;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h1 i {
  color: #FF6B35;
}

.header-title p {
  margin: 8px 0 0 0;
  color: #64748b;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #FF6B35, #FF8B65);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #e55a2b, #ff7b55);
  transform: translateY(-1px);
}

.btn-outline-primary {
  background: transparent;
  border: 1px solid #4A90E2;
  color: #4A90E2;
}

.btn-outline-primary:hover {
  background: #4A90E2;
  color: white;
}

.btn-success {
  background: #10B981;
  color: white;
}

.btn-secondary {
  background: #6B7280;
  color: white;
}

.btn-outline-secondary {
  background: transparent;
  border: 1px solid #6B7280;
  color: #6B7280;
}

.btn-outline-danger {
  background: transparent;
  border: 1px solid #EF4444;
  color: #EF4444;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 14px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.kpi-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 4px;
}

.kpi-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* Main Content */
.main-content {
  padding: 0 24px 24px;
}

/* Tabs */
.tabs-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.tabs-nav {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
}

.tab-btn {
  padding: 16px 24px;
  background: none;
  border: none;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #4A90E2;
  background: #f8fafc;
}

.tab-btn.active {
  color: #4A90E2;
  border-bottom-color: #4A90E2;
  background: #f8fafc;
}

/* Tab Content */
.tab-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tab-pane {
  padding: 24px;
}

/* Exercise List Styles */
.exercises-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.filters {
  display: flex;
  gap: 12px;
  flex: 1;
}

.form-select,
.form-control {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-control {
  min-width: 200px;
}

.view-toggle {
  display: flex;
  gap: 4px;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4A90E2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Exercise Grid */
.exercise-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.exercise-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
  cursor: pointer;
}

.exercise-card:hover {
  border-color: #4A90E2;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.12);
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.exercise-type-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.exercise-type-badge.tabletop {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.exercise-type-badge.walkthrough {
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
}

.exercise-type-badge.functional {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
}

.exercise-type-badge.full_scale {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}

.exercise-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.exercise-status.planned {
  background: rgba(107, 114, 128, 0.1);
  color: #6B7280;
}

.exercise-status.in_progress {
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
}

.exercise-status.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.exercise-status.cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.card-body {
  padding: 20px;
}

.card-body h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1A1A1A;
}

.card-body p {
  margin: 0 0 16px 0;
  color: #64748b;
  line-height: 1.5;
}

.exercise-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
}

.meta-item i {
  width: 16px;
  color: #9CA3AF;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}

.progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4A90E2, #6BB6FF);
  transition: width 0.3s ease;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* Exercise Table */
.table-container {
  overflow-x: auto;
}

.exercise-table {
  width: 100%;
  border-collapse: collapse;
}

.exercise-table th,
.exercise-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.exercise-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #374151;
}

.exercise-name {
  cursor: pointer;
}

.exercise-name strong {
  display: block;
  color: #1A1A1A;
  margin-bottom: 2px;
}

.exercise-name small {
  color: #64748b;
}

.type-badge,
.status-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar-small {
  width: 60px;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-text {
  font-size: 12px;
  color: #64748b;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

/* Monitoring Dashboard */
.monitoring-dashboard {
  padding: 0;
}

.monitoring-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.monitoring-header h2 {
  margin: 0;
  color: #1A1A1A;
}

.status-indicator {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 24px;
}

.monitoring-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.monitoring-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-circle {
  text-align: center;
  margin: 20px 0;
}

.progress-value {
  font-size: 36px;
  font-weight: 700;
  color: #4A90E2;
}

.progress-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #e2e8f0;
  border: 2px solid #e2e8f0;
  flex-shrink: 0;
}

.timeline-marker.active {
  background: #4A90E2;
  border-color: #4A90E2;
}

.timeline-marker.completed {
  background: #10B981;
  border-color: #10B981;
}

.timeline-content strong {
  display: block;
  color: #374151;
  font-size: 14px;
}

.timeline-content small {
  color: #64748b;
  font-size: 12px;
}

/* Participant Grid */
.participant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.participant-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.participant-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90E2, #6BB6FF);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.participant-info {
  flex: 1;
}

.participant-info strong {
  display: block;
  color: #374151;
  font-size: 14px;
}

.participant-info small {
  color: #64748b;
  font-size: 12px;
}

.participant-status {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Inject Card */
.inject-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.inject-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.inject-type {
  padding: 2px 8px;
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
  border-radius: 12px;
  font-size: 12px;
}

.inject-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #4A90E2;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* Simulation Status */
.simulation-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sim-indicator {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.sim-indicator.running {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.sim-metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
}

/* Analytics Dashboard */
.analytics-dashboard {
  padding: 0;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.analytics-header h2 {
  margin: 0;
  color: #1A1A1A;
}

.analytics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 24px;
}

.analytics-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.analytics-card.full-width {
  grid-column: 1 / -1;
}

.analytics-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.score-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.score-info strong {
  display: block;
  color: #374151;
}

.score-info small {
  color: #64748b;
}

.score-value {
  font-size: 18px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
}

.score-value.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.score-value.good {
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
}

.score-value.satisfactory {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.score-value.needs-improvement {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
}

.score-value.poor {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.participation-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #4A90E2;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* Lessons Learned */
.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.lesson-item {
  padding: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.lesson-category {
  padding: 2px 8px;
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
  border-radius: 12px;
  font-size: 12px;
}

.lesson-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.lesson-impact {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.lesson-impact.high {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.lesson-impact.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.lesson-impact.low {
  background: rgba(107, 114, 128, 0.1);
  color: #6B7280;
}

/* Scenarios */
.scenarios-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.scenarios-header h2 {
  margin: 0;
  color: #1A1A1A;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.scenario-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.scenario-card:hover {
  border-color: #4A90E2;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.12);
}

.scenario-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scenario-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-size: 18px;
}

.scenario-complexity {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.scenario-complexity.low {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.scenario-complexity.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.scenario-complexity.high {
  background: rgba(255, 107, 53, 0.1);
  color: #FF6B35;
}

.scenario-complexity.maximum {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.scenario-body {
  padding: 20px;
}

.scenario-meta {
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
}

.meta-row i {
  width: 16px;
  color: #9CA3AF;
}

.scenario-objectives {
  margin-top: 16px;
}

.scenario-objectives ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.scenario-objectives li {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
}

.scenario-footer {
  padding: 16px 20px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
  display: flex;
  gap: 8px;
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-dialog {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-dialog.large {
  max-width: 900px;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #1A1A1A;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #9CA3AF;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Forms */
.exercise-form {
  display: flex;
  flex-direction: column;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-control,
.form-select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-control:focus,
.form-select:focus {
  outline: none;
  border-color: #4A90E2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

/* Objectives Input */
.objectives-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.objectives-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.objective-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(74, 144, 226, 0.1);
  color: #4A90E2;
  border-radius: 20px;
  font-size: 12px;
}

.objective-tag button {
  background: none;
  border: none;
  color: #4A90E2;
  cursor: pointer;
  font-size: 14px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.objective-tag button:hover {
  background: rgba(74, 144, 226, 0.2);
}

/* Recommendations */
.recommendations-content {
  padding: 0;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.recommendation-section {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.recommendation-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.recommendation-item strong {
  display: block;
  margin-bottom: 4px;
}

.recommendation-item p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.timing-recommendation {
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
}

.participant-recommendations {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.participant-rec {
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.participant-rec strong {
  display: block;
  font-size: 14px;
}

.participant-rec small {
  color: #64748b;
  font-size: 12px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  color: #64748b;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #9CA3AF;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #374151;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-end;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .tabs-nav {
    overflow-x: auto;
    flex-wrap: nowrap;
  }

  .tab-btn {
    white-space: nowrap;
  }

  .exercises-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters {
    flex-direction: column;
  }

  .exercise-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .monitoring-grid,
  .analytics-grid {
    grid-template-columns: 1fr;
  }

  .scenarios-grid {
    grid-template-columns: 1fr;
  }

  .participant-recommendations {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .page-header,
  .main-content {
    padding: 16px;
  }

  .modal-dialog {
    margin: 0;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>