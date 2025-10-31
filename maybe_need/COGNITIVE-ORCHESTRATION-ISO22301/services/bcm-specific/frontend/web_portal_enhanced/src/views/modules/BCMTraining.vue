<template>
  <div class="bcm-training">
    <!-- Header -->
    <div class="header">
      <div class="header-content">
        <h1 class="page-title">BCM Training Management</h1>
        <p class="page-subtitle">Comprehensive training program management and competency development</p>
      </div>
      <div class="header-actions">
        <button
          class="btn-primary"
          @click="showCreateProgram = true"
          :disabled="loading"
        >
          <i class="icon-plus"></i>
          New Program
        </button>
        <button
          class="btn-secondary"
          @click="refreshData"
          :disabled="loading"
        >
          <i class="icon-refresh" :class="{ 'spinning': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tab-navigation">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="count-badge">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Main Content Area -->
    <div class="content-area">
      <!-- Training Programs Tab -->
      <div v-if="activeTab === 'programs'" class="tab-content">
        <div class="content-header">
          <div class="filters">
            <select v-model="filters.category" @change="fetchTrainingPrograms">
              <option value="">All Categories</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
            <select v-model="filters.status" @change="fetchTrainingPrograms">
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="scheduled">Scheduled</option>
              <option value="ongoing">Ongoing</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <label class="checkbox-label">
              <input type="checkbox" v-model="filters.mandatory" @change="fetchTrainingPrograms">
              Mandatory Only
            </label>
            <input
              type="text"
              v-model="filters.search"
              placeholder="Search programs..."
              @input="debounceSearch"
              class="search-input"
            >
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading training programs...</p>
        </div>

        <div v-else-if="trainingPrograms.length === 0" class="empty-state">
          <i class="icon-book"></i>
          <h3>No Training Programs Found</h3>
          <p>Create your first training program to get started</p>
          <button class="btn-primary" @click="showCreateProgram = true">
            Create Program
          </button>
        </div>

        <div v-else class="programs-grid">
          <div
            v-for="program in trainingPrograms"
            :key="program.id"
            class="program-card"
            @click="selectProgram(program)"
          >
            <div class="card-header">
              <h3>{{ program.name }}</h3>
              <div class="status-badge" :class="program.status">{{ program.status }}</div>
            </div>
            <div class="card-content">
              <p class="description">{{ program.description }}</p>
              <div class="program-meta">
                <div class="meta-item">
                  <i class="icon-calendar"></i>
                  <span>{{ formatDate(program.start_date) }} - {{ formatDate(program.end_date) }}</span>
                </div>
                <div class="meta-item">
                  <i class="icon-clock"></i>
                  <span>{{ program.duration }} hours</span>
                </div>
                <div class="meta-item">
                  <i class="icon-users"></i>
                  <span>{{ program.enrolled_count }}/{{ program.max_participants }}</span>
                </div>
              </div>
              <div class="program-tags">
                <span v-if="program.is_mandatory" class="tag mandatory">Mandatory</span>
                <span v-if="program.certification_type" class="tag certified">{{ program.certification_type }}</span>
              </div>
            </div>
            <div class="card-actions">
              <button class="btn-icon" @click.stop="editProgram(program)">
                <i class="icon-edit"></i>
              </button>
              <button class="btn-icon" @click.stop="viewAnalytics(program)">
                <i class="icon-chart"></i>
              </button>
              <button class="btn-icon danger" @click.stop="deleteProgram(program)">
                <i class="icon-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Competency & Skills Tab -->
      <div v-if="activeTab === 'competency'" class="tab-content">
        <div class="competency-dashboard">
          <div class="dashboard-cards">
            <div class="dashboard-card">
              <h3>Competency Overview</h3>
              <div class="competency-stats">
                <div class="stat">
                  <span class="stat-value">{{ competencyStats.total }}</span>
                  <span class="stat-label">Total Competencies</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ competencyStats.assessed }}</span>
                  <span class="stat-label">Assessed</span>
                </div>
                <div class="stat">
                  <span class="stat-value">{{ competencyStats.gaps }}</span>
                  <span class="stat-label">Skill Gaps</span>
                </div>
              </div>
            </div>
            <div class="dashboard-card">
              <h3>Skill Matrix Heatmap</h3>
              <div class="skill-heatmap">
                <div
                  v-for="skill in skillMatrix"
                  :key="skill.id"
                  class="skill-cell"
                  :class="getSkillLevelClass(skill.current_level)"
                  :title="`${skill.competency_name}: Level ${skill.current_level}/${skill.target_level}`"
                >
                  {{ skill.competency_name.substring(0, 3) }}
                </div>
              </div>
            </div>
          </div>

          <div class="competency-table-container">
            <table class="competency-table">
              <thead>
                <tr>
                  <th>Competency</th>
                  <th>Category</th>
                  <th>Current Level</th>
                  <th>Target Level</th>
                  <th>Gap</th>
                  <th>Last Assessment</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="skill in skillMatrix" :key="skill.id">
                  <td>
                    <div class="competency-info">
                      <strong>{{ skill.competency_name }}</strong>
                      <p class="competency-desc">{{ skill.competency_description }}</p>
                    </div>
                  </td>
                  <td>{{ skill.category }}</td>
                  <td>
                    <div class="level-indicator">
                      <div class="level-bar">
                        <div
                          class="level-fill"
                          :style="{ width: (skill.current_level / 5) * 100 + '%' }"
                        ></div>
                      </div>
                      <span class="level-text">{{ skill.current_level }}/5</span>
                    </div>
                  </td>
                  <td>
                    <div class="level-indicator">
                      <div class="level-bar target">
                        <div
                          class="level-fill"
                          :style="{ width: (skill.target_level / 5) * 100 + '%' }"
                        ></div>
                      </div>
                      <span class="level-text">{{ skill.target_level }}/5</span>
                    </div>
                  </td>
                  <td>
                    <span
                      class="gap-indicator"
                      :class="{ 'has-gap': skill.target_level > skill.current_level }"
                    >
                      {{ skill.target_level - skill.current_level }}
                    </span>
                  </td>
                  <td>{{ formatDate(skill.assessment_date) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button class="btn-sm" @click="assessSkill(skill)">Assess</button>
                      <button class="btn-sm secondary" @click="createDevelopmentPlan(skill)">Plan</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Enrollments Tab -->
      <div v-if="activeTab === 'enrollments'" class="tab-content">
        <div class="enrollments-header">
          <h2>Course Enrollments & Progress</h2>
          <button class="btn-primary" @click="showEnrollModal = true">
            <i class="icon-plus"></i>
            Enroll in Course
          </button>
        </div>

        <div class="enrollments-list">
          <div
            v-for="enrollment in enrollments"
            :key="enrollment.id"
            class="enrollment-card"
          >
            <div class="enrollment-header">
              <div class="course-info">
                <h3>{{ enrollment.program_name }}</h3>
                <p>{{ enrollment.program_description }}</p>
              </div>
              <div class="enrollment-status" :class="enrollment.status">
                {{ enrollment.status }}
              </div>
            </div>

            <div class="progress-section">
              <div class="progress-info">
                <span>Progress: {{ enrollment.progress_percentage }}%</span>
                <span>Score: {{ enrollment.assessment_score || 'N/A' }}</span>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: enrollment.progress_percentage + '%' }"
                ></div>
              </div>
            </div>

            <div class="enrollment-meta">
              <div class="meta-row">
                <span><i class="icon-calendar"></i> Enrolled: {{ formatDate(enrollment.enrollment_date) }}</span>
                <span v-if="enrollment.completion_date">
                  <i class="icon-check"></i> Completed: {{ formatDate(enrollment.completion_date) }}
                </span>
              </div>
            </div>

            <div class="enrollment-actions">
              <button
                v-if="enrollment.status === 'enrolled'"
                class="btn-primary"
                @click="continueTraining(enrollment)"
              >
                Continue
              </button>
              <button
                v-if="enrollment.certificate_id"
                class="btn-secondary"
                @click="viewCertificate(enrollment.certificate_id)"
              >
                View Certificate
              </button>
              <button class="btn-secondary" @click="provideFeedback(enrollment)">
                Feedback
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Calendar Tab -->
      <div v-if="activeTab === 'calendar'" class="tab-content">
        <div class="calendar-header">
          <h2>Training Calendar</h2>
          <div class="calendar-controls">
            <button class="btn-icon" @click="previousMonth">
              <i class="icon-chevron-left"></i>
            </button>
            <span class="current-month">{{ currentMonthYear }}</span>
            <button class="btn-icon" @click="nextMonth">
              <i class="icon-chevron-right"></i>
            </button>
            <button class="btn-primary" @click="showScheduleModal = true">
              Schedule Training
            </button>
          </div>
        </div>

        <div class="calendar-container">
          <div class="calendar-grid">
            <div class="calendar-header-row">
              <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="calendar-header-cell">
                {{ day }}
              </div>
            </div>
            <div
              v-for="week in calendarWeeks"
              :key="week.weekNumber"
              class="calendar-week"
            >
              <div
                v-for="day in week.days"
                :key="day.date"
                class="calendar-day"
                :class="{
                  'other-month': !day.currentMonth,
                  'today': day.isToday,
                  'has-events': day.events.length > 0
                }"
              >
                <div class="day-number">{{ day.dayNumber }}</div>
                <div class="day-events">
                  <div
                    v-for="event in day.events.slice(0, 3)"
                    :key="event.id"
                    class="calendar-event"
                    :class="event.status"
                    @click="viewTrainingDetails(event)"
                  >
                    <span class="event-title">{{ event.program_name }}</span>
                    <span class="event-time">{{ formatTime(event.start_datetime) }}</span>
                  </div>
                  <div v-if="day.events.length > 3" class="more-events">
                    +{{ day.events.length - 3 }} more
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Certificates Tab -->
      <div v-if="activeTab === 'certificates'" class="tab-content">
        <div class="certificates-header">
          <h2>Training Certificates</h2>
          <div class="certificate-stats">
            <div class="stat-card">
              <span class="stat-number">{{ certificates.length }}</span>
              <span class="stat-label">Total Certificates</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ activeCertificates.length }}</span>
              <span class="stat-label">Active</span>
            </div>
            <div class="stat-card">
              <span class="stat-number">{{ expiringCertificates.length }}</span>
              <span class="stat-label">Expiring Soon</span>
            </div>
          </div>
        </div>

        <div class="certificates-grid">
          <div
            v-for="certificate in certificates"
            :key="certificate.id"
            class="certificate-card"
          >
            <div class="certificate-header">
              <div class="certificate-icon">
                <i class="icon-award"></i>
              </div>
              <div class="certificate-info">
                <h3>{{ certificate.program_name }}</h3>
                <p>Certificate #{{ certificate.certificate_number }}</p>
              </div>
              <div class="certificate-status" :class="certificate.status">
                {{ certificate.status }}
              </div>
            </div>

            <div class="certificate-details">
              <div class="detail-row">
                <span class="label">Issued:</span>
                <span class="value">{{ formatDate(certificate.issue_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Expires:</span>
                <span class="value" :class="{ 'expiring': isExpiringSoon(certificate.expiry_date) }">
                  {{ certificate.expiry_date ? formatDate(certificate.expiry_date) : 'Never' }}
                </span>
              </div>
              <div class="detail-row">
                <span class="label">Authority:</span>
                <span class="value">{{ certificate.issuing_authority }}</span>
              </div>
            </div>

            <div class="certificate-actions">
              <button class="btn-primary" @click="downloadCertificate(certificate)">
                <i class="icon-download"></i>
                Download
              </button>
              <button class="btn-secondary" @click="verifyCertificate(certificate)">
                <i class="icon-shield"></i>
                Verify
              </button>
              <button class="btn-secondary" @click="shareCertificate(certificate)">
                <i class="icon-share"></i>
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Compliance Tab -->
      <div v-if="activeTab === 'compliance'" class="tab-content">
        <div class="compliance-dashboard">
          <div class="compliance-overview">
            <div class="compliance-card">
              <h3>Compliance Status</h3>
              <div class="compliance-meter">
                <div class="meter-container">
                  <div
                    class="meter-fill"
                    :style="{ width: complianceStats.overall + '%' }"
                    :class="getComplianceClass(complianceStats.overall)"
                  ></div>
                </div>
                <div class="meter-label">{{ complianceStats.overall }}% Compliant</div>
              </div>
            </div>

            <div class="compliance-stats">
              <div class="stat-item">
                <span class="stat-value compliant">{{ complianceStats.compliant }}</span>
                <span class="stat-label">Compliant</span>
              </div>
              <div class="stat-item">
                <span class="stat-value overdue">{{ complianceStats.overdue }}</span>
                <span class="stat-label">Overdue</span>
              </div>
              <div class="stat-item">
                <span class="stat-value due-soon">{{ complianceStats.dueSoon }}</span>
                <span class="stat-label">Due Soon</span>
              </div>
            </div>
          </div>

          <div class="mandatory-training-list">
            <h3>Mandatory Training Requirements</h3>
            <div class="training-requirements">
              <div
                v-for="requirement in mandatoryTrainings"
                :key="requirement.id"
                class="requirement-card"
                :class="requirement.compliance_status"
              >
                <div class="requirement-header">
                  <h4>{{ requirement.name }}</h4>
                  <div class="status-badge" :class="requirement.compliance_status">
                    {{ requirement.compliance_status }}
                  </div>
                </div>

                <div class="requirement-details">
                  <p>{{ requirement.description }}</p>
                  <div class="requirement-meta">
                    <div class="meta-item">
                      <i class="icon-calendar"></i>
                      <span>Due: {{ formatDate(requirement.due_date) }}</span>
                    </div>
                    <div class="meta-item">
                      <i class="icon-repeat"></i>
                      <span>Frequency: {{ requirement.frequency }}</span>
                    </div>
                    <div v-if="requirement.last_completion_date" class="meta-item">
                      <i class="icon-check"></i>
                      <span>Last Completed: {{ formatDate(requirement.last_completion_date) }}</span>
                    </div>
                  </div>
                </div>

                <div class="requirement-actions">
                  <button
                    v-if="requirement.compliance_status !== 'compliant'"
                    class="btn-primary"
                    @click="enrollInMandatoryTraining(requirement)"
                  >
                    Enroll Now
                  </button>
                  <button class="btn-secondary" @click="viewRequirementDetails(requirement)">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Analytics Tab -->
      <div v-if="activeTab === 'analytics'" class="tab-content">
        <div class="analytics-dashboard">
          <div class="analytics-header">
            <h2>Training Analytics</h2>
            <div class="date-range-picker">
              <input type="date" v-model="analyticsDateRange.start" @change="fetchAnalytics">
              <span>to</span>
              <input type="date" v-model="analyticsDateRange.end" @change="fetchAnalytics">
            </div>
          </div>

          <div class="analytics-cards">
            <div class="analytics-card">
              <h3>Training Completion Rate</h3>
              <div class="metric-value">{{ analytics.completionRate }}%</div>
              <div class="metric-trend" :class="analytics.completionTrend">
                <i :class="getTrendIcon(analytics.completionTrend)"></i>
                {{ analytics.completionTrendValue }}%
              </div>
            </div>

            <div class="analytics-card">
              <h3>Average Training Score</h3>
              <div class="metric-value">{{ analytics.averageScore }}</div>
              <div class="metric-trend" :class="analytics.scoreTrend">
                <i :class="getTrendIcon(analytics.scoreTrend)"></i>
                {{ analytics.scoreTrendValue }}
              </div>
            </div>

            <div class="analytics-card">
              <h3>Training Hours</h3>
              <div class="metric-value">{{ analytics.totalHours }}h</div>
              <div class="metric-trend" :class="analytics.hoursTrend">
                <i :class="getTrendIcon(analytics.hoursTrend)"></i>
                {{ analytics.hoursTrendValue }}h
              </div>
            </div>

            <div class="analytics-card">
              <h3>Cost per Employee</h3>
              <div class="metric-value">${{ analytics.costPerEmployee }}</div>
              <div class="metric-trend" :class="analytics.costTrend">
                <i :class="getTrendIcon(analytics.costTrend)"></i>
                ${{ analytics.costTrendValue }}
              </div>
            </div>
          </div>

          <div class="analytics-charts">
            <div class="chart-container">
              <h3>Training Progress Over Time</h3>
              <canvas id="progressChart" ref="progressChart"></canvas>
            </div>

            <div class="chart-container">
              <h3>Training Categories Distribution</h3>
              <canvas id="categoryChart" ref="categoryChart"></canvas>
            </div>
          </div>

          <div class="effectiveness-metrics">
            <h3>Training Effectiveness</h3>
            <div class="effectiveness-grid">
              <div class="effectiveness-card">
                <h4>Knowledge Retention</h4>
                <div class="effectiveness-score">{{ analytics.knowledgeRetention }}%</div>
                <div class="effectiveness-description">
                  Based on follow-up assessments and skill evaluations
                </div>
              </div>

              <div class="effectiveness-card">
                <h4>Performance Improvement</h4>
                <div class="effectiveness-score">{{ analytics.performanceImprovement }}%</div>
                <div class="effectiveness-description">
                  Measured through KPI improvements post-training
                </div>
              </div>

              <div class="effectiveness-card">
                <h4>Employee Satisfaction</h4>
                <div class="effectiveness-score">{{ analytics.satisfaction }}/5</div>
                <div class="effectiveness-description">
                  Average training satisfaction score from feedback
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Recommendations Tab -->
      <div v-if="activeTab === 'ai-recommendations'" class="tab-content">
        <div class="ai-recommendations">
          <div class="ai-header">
            <h2>AI-Powered Learning Recommendations</h2>
            <p>Personalized training suggestions based on your profile and learning goals</p>
          </div>

          <div class="recommendation-sections">
            <div class="recommendation-section">
              <h3>
                <i class="icon-target"></i>
                Recommended Learning Paths
              </h3>
              <div class="learning-paths">
                <div
                  v-for="path in learningPaths"
                  :key="path.id"
                  class="learning-path-card"
                >
                  <div class="path-header">
                    <h4>{{ path.name }}</h4>
                    <div class="confidence-score">
                      <span>{{ Math.round(path.confidence * 100) }}% match</span>
                    </div>
                  </div>
                  <p class="path-description">{{ path.description }}</p>
                  <div class="path-details">
                    <div class="detail">
                      <i class="icon-clock"></i>
                      <span>{{ path.estimated_duration }} hours</span>
                    </div>
                    <div class="detail">
                      <i class="icon-star"></i>
                      <span>{{ path.difficulty }} level</span>
                    </div>
                    <div class="detail">
                      <i class="icon-users"></i>
                      <span>{{ path.enrolled_count }} enrolled</span>
                    </div>
                  </div>
                  <div class="path-courses">
                    <span class="courses-label">Includes:</span>
                    <div class="course-tags">
                      <span
                        v-for="course in path.courses.slice(0, 3)"
                        :key="course"
                        class="course-tag"
                      >
                        {{ course }}
                      </span>
                      <span v-if="path.courses.length > 3" class="more-courses">
                        +{{ path.courses.length - 3 }} more
                      </span>
                    </div>
                  </div>
                  <button class="btn-primary" @click="enrollInLearningPath(path)">
                    Start Learning Path
                  </button>
                </div>
              </div>
            </div>

            <div class="recommendation-section">
              <h3>
                <i class="icon-lightbulb"></i>
                Skill Gap Recommendations
              </h3>
              <div class="skill-recommendations">
                <div
                  v-for="recommendation in skillRecommendations"
                  :key="recommendation.id"
                  class="skill-recommendation-card"
                >
                  <div class="skill-gap-info">
                    <h4>{{ recommendation.competency }}</h4>
                    <div class="gap-indicator">
                      <span class="current-level">Current: {{ recommendation.current_level }}/5</span>
                      <i class="icon-arrow-right"></i>
                      <span class="target-level">Target: {{ recommendation.target_level }}/5</span>
                    </div>
                  </div>
                  <div class="recommended-courses">
                    <h5>Recommended Courses:</h5>
                    <div class="course-list">
                      <div
                        v-for="course in recommendation.courses"
                        :key="course.id"
                        class="recommended-course"
                      >
                        <span class="course-name">{{ course.name }}</span>
                        <span class="course-impact">+{{ course.skill_impact }} levels</span>
                        <button class="btn-sm" @click="enrollInCourse(course)">
                          Enroll
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="recommendation-section">
              <h3>
                <i class="icon-trending-up"></i>
                Trending Courses
              </h3>
              <div class="trending-courses">
                <div
                  v-for="course in trendingCourses"
                  :key="course.id"
                  class="trending-course-card"
                >
                  <div class="course-header">
                    <h4>{{ course.name }}</h4>
                    <div class="trending-indicator">
                      <i class="icon-fire"></i>
                      <span>{{ course.enrollment_growth }}% growth</span>
                    </div>
                  </div>
                  <p class="course-description">{{ course.description }}</p>
                  <div class="course-stats">
                    <div class="stat">
                      <i class="icon-users"></i>
                      <span>{{ course.enrolled_count }} enrolled</span>
                    </div>
                    <div class="stat">
                      <i class="icon-star"></i>
                      <span>{{ course.rating }}/5 rating</span>
                    </div>
                    <div class="stat">
                      <i class="icon-clock"></i>
                      <span>{{ course.duration }} hours</span>
                    </div>
                  </div>
                  <button class="btn-secondary" @click="viewCourseDetails(course)">
                    Learn More
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Assistant Panel -->
    <AssistantPanel
      v-if="showAssistant"
      :context="assistantContext"
      @close="showAssistant = false"
      @action="handleAssistantAction"
    />

    <!-- Floating AI Assistant Button -->
    <button
      class="ai-assistant-fab"
      @click="showAssistant = !showAssistant"
      :class="{ active: showAssistant }"
    >
      <i class="icon-robot"></i>
    </button>

    <!-- Modals -->
    <!-- Create/Edit Program Modal -->
    <div v-if="showCreateProgram || editingProgram" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingProgram ? 'Edit' : 'Create' }} Training Program</h2>
          <button class="btn-icon" @click="closeModal">
            <i class="icon-x"></i>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveProgram">
            <div class="form-group">
              <label>Program Name *</label>
              <input type="text" v-model="programForm.name" required>
            </div>
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="programForm.description" rows="3"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Category</label>
                <select v-model="programForm.category_id">
                  <option value="">Select Category</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Duration (hours)</label>
                <input type="number" v-model="programForm.duration" min="1">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Start Date</label>
                <input type="date" v-model="programForm.start_date">
              </div>
              <div class="form-group">
                <label>End Date</label>
                <input type="date" v-model="programForm.end_date">
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>Max Participants</label>
                <input type="number" v-model="programForm.max_participants" min="1">
              </div>
              <div class="form-group">
                <label>Certification Type</label>
                <select v-model="programForm.certification_type">
                  <option value="">No Certification</option>
                  <option value="completion">Completion Certificate</option>
                  <option value="competency">Competency Certificate</option>
                  <option value="professional">Professional Certificate</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="programForm.is_mandatory">
                Mandatory Training
              </label>
            </div>
            <div class="form-actions">
              <button type="button" class="btn-secondary" @click="closeModal">
                Cancel
              </button>
              <button type="submit" class="btn-primary" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Program' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Enrollment Modal -->
    <div v-if="showEnrollModal" class="modal-overlay" @click.self="showEnrollModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>Enroll in Training Program</h2>
          <button class="btn-icon" @click="showEnrollModal = false">
            <i class="icon-x"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="available-programs">
            <div
              v-for="program in availablePrograms"
              :key="program.id"
              class="program-option"
              @click="selectProgramForEnrollment(program)"
              :class="{ selected: selectedProgramForEnrollment?.id === program.id }"
            >
              <h4>{{ program.name }}</h4>
              <p>{{ program.description }}</p>
              <div class="program-details">
                <span><i class="icon-calendar"></i> {{ formatDate(program.start_date) }}</span>
                <span><i class="icon-clock"></i> {{ program.duration }} hours</span>
                <span><i class="icon-users"></i> {{ program.enrolled_count }}/{{ program.max_participants }}</span>
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="showEnrollModal = false">
              Cancel
            </button>
            <button
              class="btn-primary"
              @click="confirmEnrollment"
              :disabled="!selectedProgramForEnrollment || enrolling"
            >
              {{ enrolling ? 'Enrolling...' : 'Enroll' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner-large"></div>
    </div>

    <!-- Toast Notifications -->
    <div class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <i :class="getToastIcon(toast.type)"></i>
        <span>{{ toast.message }}</span>
        <button class="toast-close" @click="removeToast(toast.id)">
          <i class="icon-x"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue'
import bcmTrainingService from '@/services/bcmTraining.js'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BCMTraining',
  components: {
    AssistantPanel
  },
  setup() {
    // Reactive state
    const activeTab = ref('programs')
    const loading = ref(false)
    const saving = ref(false)
    const enrolling = ref(false)
    const showAssistant = ref(false)
    const showCreateProgram = ref(false)
    const showEnrollModal = ref(false)
    const showScheduleModal = ref(false)
    const editingProgram = ref(null)
    const selectedProgramForEnrollment = ref(null)

    // Data arrays
    const trainingPrograms = ref([])
    const categories = ref([])
    const competencies = ref([])
    const skillMatrix = ref([])
    const enrollments = ref([])
    const certificates = ref([])
    const mandatoryTrainings = ref([])
    const trainingCalendar = ref([])
    const learningPaths = ref([])
    const skillRecommendations = ref([])
    const trendingCourses = ref([])
    const toasts = ref([])

    // Filters and search
    const filters = reactive({
      category: '',
      status: '',
      mandatory: null,
      search: ''
    })

    // Forms
    const programForm = reactive({
      name: '',
      description: '',
      category_id: '',
      duration: null,
      start_date: '',
      end_date: '',
      max_participants: null,
      certification_type: '',
      is_mandatory: false
    })

    // Statistics
    const competencyStats = reactive({
      total: 0,
      assessed: 0,
      gaps: 0
    })

    const complianceStats = reactive({
      overall: 0,
      compliant: 0,
      overdue: 0,
      dueSoon: 0
    })

    const analytics = reactive({
      completionRate: 0,
      completionTrend: 'up',
      completionTrendValue: 0,
      averageScore: 0,
      scoreTrend: 'up',
      scoreTrendValue: 0,
      totalHours: 0,
      hoursTrend: 'up',
      hoursTrendValue: 0,
      costPerEmployee: 0,
      costTrend: 'down',
      costTrendValue: 0,
      knowledgeRetention: 0,
      performanceImprovement: 0,
      satisfaction: 0
    })

    // Calendar
    const currentDate = ref(new Date())
    const analyticsDateRange = reactive({
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    })

    // Computed properties
    const tabs = computed(() => [
      { id: 'programs', label: 'Training Programs', icon: 'icon-book', count: trainingPrograms.value.length },
      { id: 'competency', label: 'Competency & Skills', icon: 'icon-target', count: skillMatrix.value.length },
      { id: 'enrollments', label: 'My Enrollments', icon: 'icon-user-check', count: enrollments.value.length },
      { id: 'calendar', label: 'Calendar', icon: 'icon-calendar', count: trainingCalendar.value.length },
      { id: 'certificates', label: 'Certificates', icon: 'icon-award', count: certificates.value.length },
      { id: 'compliance', label: 'Compliance', icon: 'icon-shield', count: mandatoryTrainings.value.length },
      { id: 'analytics', label: 'Analytics', icon: 'icon-chart', count: undefined },
      { id: 'ai-recommendations', label: 'AI Recommendations', icon: 'icon-robot', count: undefined }
    ])

    const availablePrograms = computed(() => {
      return trainingPrograms.value.filter(program => {
        const isNotEnrolled = !enrollments.value.some(enrollment =>
          enrollment.program_id === program.id
        )
        const hasCapacity = program.enrolled_count < program.max_participants
        const isNotCancelled = program.status !== 'cancelled'
        return isNotEnrolled && hasCapacity && isNotCancelled
      })
    })

    const activeCertificates = computed(() => {
      return certificates.value.filter(cert => cert.status === 'active')
    })

    const expiringCertificates = computed(() => {
      const thirtyDaysFromNow = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      return certificates.value.filter(cert => {
        if (!cert.expiry_date) return false
        const expiryDate = new Date(cert.expiry_date)
        return expiryDate <= thirtyDaysFromNow && cert.status === 'active'
      })
    })

    const currentMonthYear = computed(() => {
      return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    })

    const calendarWeeks = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())

      const weeks = []
      let currentWeekStart = new Date(startDate)
      let weekNumber = 1

      while (currentWeekStart <= lastDay || currentWeekStart.getMonth() === month) {
        const week = {
          weekNumber,
          days: []
        }

        for (let i = 0; i < 7; i++) {
          const day = new Date(currentWeekStart)
          day.setDate(day.getDate() + i)

          const dayEvents = trainingCalendar.value.filter(event => {
            const eventDate = new Date(event.start_datetime)
            return eventDate.toDateString() === day.toDateString()
          })

          week.days.push({
            date: day.toISOString().split('T')[0],
            dayNumber: day.getDate(),
            currentMonth: day.getMonth() === month,
            isToday: day.toDateString() === new Date().toDateString(),
            events: dayEvents
          })
        }

        weeks.push(week)
        currentWeekStart.setDate(currentWeekStart.getDate() + 7)
        weekNumber++

        if (weeks.length > 6) break // Prevent infinite loop
      }

      return weeks
    })

    const assistantContext = computed(() => ({
      currentTab: activeTab.value,
      trainingPrograms: trainingPrograms.value.length,
      enrollments: enrollments.value.length,
      skillGaps: skillMatrix.value.filter(skill => skill.target_level > skill.current_level).length,
      complianceIssues: complianceStats.overdue + complianceStats.dueSoon
    }))

    // Methods
    const showToast = (message, type = 'info') => {
      const id = Date.now()
      toasts.value.push({ id, message, type })
      setTimeout(() => removeToast(id), 5000)
    }

    const removeToast = (id) => {
      const index = toasts.value.findIndex(toast => toast.id === id)
      if (index > -1) toasts.value.splice(index, 1)
    }

    const getToastIcon = (type) => {
      const icons = {
        success: 'icon-check-circle',
        error: 'icon-x-circle',
        warning: 'icon-alert-triangle',
        info: 'icon-info-circle'
      }
      return icons[type] || icons.info
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatTime = (dateTimeString) => {
      if (!dateTimeString) return ''
      return new Date(dateTimeString).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const isExpiringSoon = (expiryDate) => {
      if (!expiryDate) return false
      const thirtyDaysFromNow = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      return new Date(expiryDate) <= thirtyDaysFromNow
    }

    const getSkillLevelClass = (level) => {
      if (level >= 4) return 'skill-level-high'
      if (level >= 3) return 'skill-level-medium'
      if (level >= 2) return 'skill-level-low'
      return 'skill-level-none'
    }

    const getComplianceClass = (percentage) => {
      if (percentage >= 90) return 'compliance-excellent'
      if (percentage >= 80) return 'compliance-good'
      if (percentage >= 70) return 'compliance-warning'
      return 'compliance-critical'
    }

    const getTrendIcon = (trend) => {
      return trend === 'up' ? 'icon-trending-up' : 'icon-trending-down'
    }

    // API methods
    const fetchTrainingPrograms = async () => {
      try {
        loading.value = true
        trainingPrograms.value = await bcmTrainingService.getTrainingPrograms(filters)
      } catch (error) {
        showToast(error.message, 'error')
      } finally {
        loading.value = false
      }
    }

    const fetchCompetencies = async () => {
      try {
        competencies.value = await bcmTrainingService.getCompetencies()
        skillMatrix.value = await bcmTrainingService.getSkillMatrix()

        // Update stats
        competencyStats.total = competencies.value.length
        competencyStats.assessed = skillMatrix.value.filter(skill => skill.assessment_date).length
        competencyStats.gaps = skillMatrix.value.filter(skill => skill.target_level > skill.current_level).length
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchEnrollments = async () => {
      try {
        enrollments.value = await bcmTrainingService.getEnrollments()
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchCertificates = async () => {
      try {
        certificates.value = await bcmTrainingService.getCertificates()
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchMandatoryTrainings = async () => {
      try {
        mandatoryTrainings.value = await bcmTrainingService.getMandatoryTrainings()
        const complianceReport = await bcmTrainingService.getComplianceReport()

        // Update compliance stats
        complianceStats.overall = complianceReport.overall_compliance || 0
        complianceStats.compliant = complianceReport.compliant || 0
        complianceStats.overdue = complianceReport.overdue || 0
        complianceStats.dueSoon = complianceReport.due_soon || 0
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchTrainingCalendar = async () => {
      try {
        const startDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth(), 1)
        const endDate = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 0)

        trainingCalendar.value = await bcmTrainingService.getTrainingCalendar(
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        )
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchAnalytics = async () => {
      try {
        const analyticsData = await bcmTrainingService.getTrainingAnalytics({
          start_date: analyticsDateRange.start,
          end_date: analyticsDateRange.end
        })

        Object.assign(analytics, analyticsData)
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const fetchAIRecommendations = async () => {
      try {
        // Fetch learning path recommendations
        learningPaths.value = await bcmTrainingService.getLearningPathRecommendations(
          null, // Current user
          { interests: [], career_goals: [] }
        )

        // Fetch skill gap recommendations
        const skillGaps = skillMatrix.value
          .filter(skill => skill.target_level > skill.current_level)
          .map(skill => ({
            competency_id: skill.competency_id,
            gap: skill.target_level - skill.current_level
          }))

        skillRecommendations.value = await bcmTrainingService.getPersonalizedCourses(
          null, // Current user
          skillGaps
        )

        // Mock trending courses for now
        trendingCourses.value = trainingPrograms.value
          .slice(0, 6)
          .map(program => ({
            ...program,
            enrollment_growth: Math.floor(Math.random() * 50) + 10,
            rating: (Math.random() * 2 + 3).toFixed(1),
            enrolled_count: Math.floor(Math.random() * 100) + 20
          }))
      } catch (error) {
        showToast(error.message, 'error')
      }
    }

    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([
          fetchTrainingPrograms(),
          fetchCompetencies(),
          fetchEnrollments(),
          fetchCertificates(),
          fetchMandatoryTrainings(),
          fetchTrainingCalendar(),
          fetchAnalytics(),
          fetchAIRecommendations()
        ])
        showToast('Data refreshed successfully', 'success')
      } catch (error) {
        showToast('Failed to refresh data', 'error')
      } finally {
        loading.value = false
      }
    }

    // Program management
    const selectProgram = (program) => {
      // Handle program selection logic
      console.log('Selected program:', program)
    }

    const editProgram = (program) => {
      editingProgram.value = program
      Object.assign(programForm, program)
      showCreateProgram.value = true
    }

    const deleteProgram = async (program) => {
      if (confirm(`Are you sure you want to delete "${program.name}"?`)) {
        try {
          await bcmTrainingService.deleteTrainingProgram(program.id)
          showToast('Program deleted successfully', 'success')
          fetchTrainingPrograms()
        } catch (error) {
          showToast(error.message, 'error')
        }
      }
    }

    const saveProgram = async () => {
      try {
        saving.value = true

        if (editingProgram.value) {
          await bcmTrainingService.updateTrainingProgram(editingProgram.value.id, programForm)
          showToast('Program updated successfully', 'success')
        } else {
          await bcmTrainingService.createTrainingProgram(programForm)
          showToast('Program created successfully', 'success')
        }

        closeModal()
        fetchTrainingPrograms()
      } catch (error) {
        showToast(error.message, 'error')
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showCreateProgram.value = false
      editingProgram.value = null
      Object.keys(programForm).forEach(key => {
        if (typeof programForm[key] === 'boolean') {
          programForm[key] = false
        } else {
          programForm[key] = ''
        }
      })
    }

    // Enrollment methods
    const selectProgramForEnrollment = (program) => {
      selectedProgramForEnrollment.value = program
    }

    const confirmEnrollment = async () => {
      if (!selectedProgramForEnrollment.value) return

      try {
        enrolling.value = true
        await bcmTrainingService.enrollInCourse(selectedProgramForEnrollment.value.id)
        showToast('Successfully enrolled in course', 'success')
        showEnrollModal.value = false
        selectedProgramForEnrollment.value = null
        fetchEnrollments()
        fetchTrainingPrograms()
      } catch (error) {
        showToast(error.message, 'error')
      } finally {
        enrolling.value = false
      }
    }

    const continueTraining = (enrollment) => {
      // Navigate to LMS or training content
      console.log('Continue training:', enrollment)
    }

    const provideFeedback = (enrollment) => {
      // Open feedback modal
      console.log('Provide feedback:', enrollment)
    }

    // Calendar methods
    const previousMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
      fetchTrainingCalendar()
    }

    const nextMonth = () => {
      currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
      fetchTrainingCalendar()
    }

    const viewTrainingDetails = (event) => {
      console.log('View training details:', event)
    }

    // Certificate methods
    const viewCertificate = (certificateId) => {
      console.log('View certificate:', certificateId)
    }

    const downloadCertificate = (certificate) => {
      console.log('Download certificate:', certificate)
    }

    const verifyCertificate = (certificate) => {
      console.log('Verify certificate:', certificate)
    }

    const shareCertificate = (certificate) => {
      console.log('Share certificate:', certificate)
    }

    // Competency methods
    const assessSkill = (skill) => {
      console.log('Assess skill:', skill)
    }

    const createDevelopmentPlan = (skill) => {
      console.log('Create development plan:', skill)
    }

    // Compliance methods
    const enrollInMandatoryTraining = (requirement) => {
      console.log('Enroll in mandatory training:', requirement)
    }

    const viewRequirementDetails = (requirement) => {
      console.log('View requirement details:', requirement)
    }

    // Analytics methods
    const viewAnalytics = (program) => {
      console.log('View analytics:', program)
    }

    // AI Recommendations methods
    const enrollInLearningPath = (path) => {
      console.log('Enroll in learning path:', path)
    }

    const enrollInCourse = (course) => {
      console.log('Enroll in course:', course)
    }

    const viewCourseDetails = (course) => {
      console.log('View course details:', course)
    }

    // AI Assistant methods
    const handleAssistantAction = (action) => {
      console.log('Assistant action:', action)
      // Handle AI assistant actions
    }

    // Search debounce
    let searchTimeout
    const debounceSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        fetchTrainingPrograms()
      }, 500)
    }

    // Watchers
    watch(activeTab, (newTab) => {
      switch (newTab) {
        case 'programs':
          fetchTrainingPrograms()
          break
        case 'competency':
          fetchCompetencies()
          break
        case 'enrollments':
          fetchEnrollments()
          break
        case 'calendar':
          fetchTrainingCalendar()
          break
        case 'certificates':
          fetchCertificates()
          break
        case 'compliance':
          fetchMandatoryTrainings()
          break
        case 'analytics':
          fetchAnalytics()
          break
        case 'ai-recommendations':
          fetchAIRecommendations()
          break
      }
    })

    // Lifecycle
    onMounted(() => {
      refreshData()
    })

    return {
      // Reactive state
      activeTab,
      loading,
      saving,
      enrolling,
      showAssistant,
      showCreateProgram,
      showEnrollModal,
      showScheduleModal,
      editingProgram,
      selectedProgramForEnrollment,

      // Data
      trainingPrograms,
      categories,
      competencies,
      skillMatrix,
      enrollments,
      certificates,
      mandatoryTrainings,
      trainingCalendar,
      learningPaths,
      skillRecommendations,
      trendingCourses,
      toasts,

      // Filters and forms
      filters,
      programForm,

      // Stats
      competencyStats,
      complianceStats,
      analytics,

      // Calendar
      currentDate,
      analyticsDateRange,

      // Computed
      tabs,
      availablePrograms,
      activeCertificates,
      expiringCertificates,
      currentMonthYear,
      calendarWeeks,
      assistantContext,

      // Methods
      showToast,
      removeToast,
      getToastIcon,
      formatDate,
      formatTime,
      isExpiringSoon,
      getSkillLevelClass,
      getComplianceClass,
      getTrendIcon,
      refreshData,
      selectProgram,
      editProgram,
      deleteProgram,
      saveProgram,
      closeModal,
      selectProgramForEnrollment,
      confirmEnrollment,
      continueTraining,
      provideFeedback,
      previousMonth,
      nextMonth,
      viewTrainingDetails,
      viewCertificate,
      downloadCertificate,
      verifyCertificate,
      shareCertificate,
      assessSkill,
      createDevelopmentPlan,
      enrollInMandatoryTraining,
      viewRequirementDetails,
      viewAnalytics,
      enrollInLearningPath,
      enrollInCourse,
      viewCourseDetails,
      handleAssistantAction,
      debounceSearch
    }
  }
}
</script>

<style scoped>
.bcm-training {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header */
.header {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1A1A1A;
  margin: 0;
}

.header-content p {
  color: #64748b;
  margin: 0.5rem 0 0 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Buttons */
.btn-primary {
  background: #FF6B35;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary:hover {
  background: #e55a2b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.btn-primary:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-secondary {
  background: #4A90E2;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary:hover {
  background: #357abd;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
}

.btn-icon {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #f8fafc;
  color: #1A1A1A;
  border-color: #cbd5e1;
}

.btn-icon.danger:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  border-radius: 0.375rem;
  background: #FF6B35;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm:hover {
  background: #e55a2b;
}

.btn-sm.secondary {
  background: #4A90E2;
}

.btn-sm.secondary:hover {
  background: #357abd;
}

/* Tab Navigation */
.tab-navigation {
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 0 2rem;
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
}

.tab-button {
  background: transparent;
  border: none;
  padding: 1rem 1.5rem;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 3px solid transparent;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.tab-button:hover {
  color: #1A1A1A;
  background: #f8fafc;
}

.tab-button.active {
  color: #FF6B35;
  border-bottom-color: #FF6B35;
}

.count-badge {
  background: #e2e8f0;
  color: #64748b;
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.tab-button.active .count-badge {
  background: #FF6B35;
  color: white;
}

/* Content Area */
.content-area {
  padding: 2rem;
  max-width: 100%;
}

.tab-content {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  min-height: 600px;
}

/* Content Header */
.content-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filters select,
.search-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  min-width: 150px;
}

.search-input {
  min-width: 250px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #64748b;
}

/* Loading States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #FF6B35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.spinner-large {
  width: 60px;
  height: 60px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #FF6B35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state i {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 2rem 0;
}

/* Programs Grid */
.programs-grid {
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.program-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.program-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #FF6B35;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.card-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
  flex: 1;
  margin-right: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.draft { background: #f3f4f6; color: #6b7280; }
.status-badge.scheduled { background: #dbeafe; color: #1d4ed8; }
.status-badge.ongoing { background: #dcfce7; color: #166534; }
.status-badge.completed { background: #e0e7ff; color: #3730a3; }
.status-badge.cancelled { background: #fee2e2; color: #dc2626; }

.card-content .description {
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.program-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
}

.program-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tag {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.tag.mandatory { background: #fef3c7; color: #92400e; }
.tag.certified { background: #e0e7ff; color: #3730a3; }

.card-actions {
  display: flex;
  gap: 0.5rem;
  position: absolute;
  top: 1rem;
  right: 1rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.program-card:hover .card-actions {
  opacity: 1;
}

/* Competency Dashboard */
.competency-dashboard {
  padding: 2rem;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.dashboard-card {
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.dashboard-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.competency-stats {
  display: flex;
  gap: 2rem;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #FF6B35;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.skill-heatmap {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(40px, 1fr));
  gap: 0.25rem;
  max-width: 400px;
}

.skill-cell {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  cursor: help;
}

.skill-level-none { background: #e2e8f0; color: #64748b; }
.skill-level-low { background: #fef3c7; color: #92400e; }
.skill-level-medium { background: #fed7aa; color: #ea580c; }
.skill-level-high { background: #dcfce7; color: #166534; }

/* Competency Table */
.competency-table-container {
  overflow-x: auto;
}

.competency-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.competency-table th,
.competency-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.competency-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #1A1A1A;
}

.competency-info strong {
  color: #1A1A1A;
  font-weight: 600;
}

.competency-desc {
  color: #64748b;
  margin: 0.25rem 0 0 0;
  font-size: 0.8125rem;
}

.level-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.level-bar {
  width: 60px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.level-bar.target {
  opacity: 0.6;
}

.level-fill {
  height: 100%;
  background: #FF6B35;
  transition: width 0.3s ease;
}

.level-text {
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 500;
  min-width: 30px;
}

.gap-indicator {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #64748b;
  font-weight: 600;
  font-size: 0.75rem;
}

.gap-indicator.has-gap {
  background: #fee2e2;
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Enrollments */
.enrollments-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.enrollments-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.enrollments-list {
  padding: 2rem;
}

.enrollment-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.enrollment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.course-info h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.5rem 0;
}

.course-info p {
  color: #64748b;
  margin: 0;
}

.enrollment-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.enrollment-status.enrolled { background: #dbeafe; color: #1d4ed8; }
.enrollment-status.in_progress { background: #fef3c7; color: #92400e; }
.enrollment-status.completed { background: #dcfce7; color: #166534; }
.enrollment-status.dropped { background: #fee2e2; color: #dc2626; }

.progress-section {
  margin-bottom: 1rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B35, #4A90E2);
  transition: width 0.3s ease;
}

.enrollment-meta {
  margin-bottom: 1rem;
}

.meta-row {
  display: flex;
  gap: 2rem;
  color: #64748b;
  font-size: 0.875rem;
}

.meta-row span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.enrollment-actions {
  display: flex;
  gap: 1rem;
}

/* Calendar */
.calendar-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-month {
  font-weight: 600;
  color: #1A1A1A;
  min-width: 200px;
  text-align: center;
}

.calendar-container {
  padding: 2rem;
}

.calendar-grid {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  overflow: hidden;
}

.calendar-header-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8fafc;
}

.calendar-header-cell {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
  color: #64748b;
  border-right: 1px solid #e2e8f0;
}

.calendar-header-cell:last-child {
  border-right: none;
}

.calendar-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid #e2e8f0;
}

.calendar-week:last-child {
  border-bottom: none;
}

.calendar-day {
  min-height: 120px;
  padding: 0.5rem;
  border-right: 1px solid #e2e8f0;
  background: white;
  position: relative;
}

.calendar-day:last-child {
  border-right: none;
}

.calendar-day.other-month {
  background: #f8fafc;
  color: #cbd5e1;
}

.calendar-day.today {
  background: #fff7ed;
}

.calendar-day.has-events {
  background: #fef3c7;
}

.day-number {
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
}

.other-month .day-number {
  color: #cbd5e1;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.calendar-event {
  background: #FF6B35;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: opacity 0.2s;
}

.calendar-event:hover {
  opacity: 0.8;
}

.calendar-event.scheduled { background: #4A90E2; }
.calendar-event.ongoing { background: #10b981; }
.calendar-event.completed { background: #6b7280; }

.event-title {
  display: block;
  font-weight: 500;
}

.event-time {
  display: block;
  opacity: 0.8;
  font-size: 0.6875rem;
}

.more-events {
  color: #64748b;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  cursor: pointer;
}

.more-events:hover {
  color: #1A1A1A;
}

/* Certificates */
.certificates-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
}

.certificates-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.certificate-stats {
  display: flex;
  gap: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #FF6B35;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.certificates-grid {
  padding: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.certificate-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.certificate-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(30%, -30%);
}

.certificate-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.certificate-icon {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.75rem;
  border-radius: 50%;
  font-size: 1.5rem;
}

.certificate-info h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.certificate-info p {
  opacity: 0.8;
  margin: 0;
  font-size: 0.875rem;
}

.certificate-status {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  background: rgba(255, 255, 255, 0.2);
  margin-left: auto;
}

.certificate-details {
  margin-bottom: 1.5rem;
  position: relative;
  z-index: 1;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.label {
  opacity: 0.8;
}

.value {
  font-weight: 500;
}

.value.expiring {
  color: #fbbf24;
  font-weight: 600;
}

.certificate-actions {
  display: flex;
  gap: 0.75rem;
  position: relative;
  z-index: 1;
}

.certificate-actions .btn-primary,
.certificate-actions .btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.certificate-actions .btn-primary:hover,
.certificate-actions .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

/* Compliance */
.compliance-dashboard {
  padding: 2rem;
}

.compliance-overview {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  margin-bottom: 2rem;
  background: #f8fafc;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.compliance-card h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.compliance-meter {
  max-width: 300px;
}

.meter-container {
  width: 100%;
  height: 20px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.meter-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 10px;
}

.compliance-excellent { background: linear-gradient(90deg, #10b981, #059669); }
.compliance-good { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.compliance-warning { background: linear-gradient(90deg, #f59e0b, #d97706); }
.compliance-critical { background: linear-gradient(90deg, #ef4444, #dc2626); }

.meter-label {
  font-weight: 600;
  color: #1A1A1A;
  text-align: center;
}

.compliance-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-value.compliant { color: #059669; }
.stat-value.overdue { color: #dc2626; }
.stat-value.due-soon { color: #d97706; }

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: #64748b;
}

.mandatory-training-list h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.training-requirements {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.requirement-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.requirement-card.compliant {
  border-left: 4px solid #059669;
  background: #f0fdf4;
}

.requirement-card.overdue {
  border-left: 4px solid #dc2626;
  background: #fef2f2;
}

.requirement-card.due_soon {
  border-left: 4px solid #d97706;
  background: #fffbeb;
}

.requirement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.requirement-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.requirement-details p {
  color: #64748b;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.requirement-meta {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.requirement-actions {
  display: flex;
  gap: 1rem;
}

/* Analytics */
.analytics-dashboard {
  padding: 2rem;
}

.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.analytics-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.date-range-picker {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.date-range-picker input {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.analytics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.analytics-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
}

.analytics-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 1rem 0;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
}

.metric-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.metric-trend.up { color: #059669; }
.metric-trend.down { color: #dc2626; }

.analytics-charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.chart-container h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.effectiveness-metrics h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.effectiveness-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.effectiveness-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  text-align: center;
}

.effectiveness-card h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
}

.effectiveness-score {
  font-size: 1.75rem;
  font-weight: 700;
  color: #FF6B35;
  margin-bottom: 0.5rem;
}

.effectiveness-description {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.4;
}

/* AI Recommendations */
.ai-recommendations {
  padding: 2rem;
}

.ai-header {
  margin-bottom: 2rem;
}

.ai-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.5rem 0;
}

.ai-header p {
  color: #64748b;
  margin: 0;
}

.recommendation-sections {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.recommendation-section h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.learning-paths {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.learning-path-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.learning-path-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #4A90E2;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.path-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
  flex: 1;
}

.confidence-score {
  background: #e0f2fe;
  color: #0891b2;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.path-description {
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.path-details {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.detail {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #64748b;
}

.path-courses {
  margin-bottom: 1.5rem;
}

.courses-label {
  font-weight: 500;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
  display: block;
}

.course-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.course-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
}

.more-courses {
  color: #64748b;
  font-size: 0.75rem;
  font-style: italic;
}

.skill-recommendations {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.skill-recommendation-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.skill-gap-info {
  margin-bottom: 1rem;
}

.skill-gap-info h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.5rem 0;
}

.gap-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.current-level {
  color: #dc2626;
  font-weight: 500;
}

.target-level {
  color: #059669;
  font-weight: 500;
}

.recommended-courses h5 {
  font-size: 1rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.75rem 0;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recommended-course {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.course-name {
  font-weight: 500;
  color: #1A1A1A;
  flex: 1;
}

.course-impact {
  color: #059669;
  font-size: 0.875rem;
  font-weight: 500;
  margin-right: 1rem;
}

.trending-courses {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.trending-course-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.trending-course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #FF6B35;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.course-header h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
  flex: 1;
}

.trending-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.course-description {
  color: #64748b;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.course-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #64748b;
}

/* AI Assistant */
.ai-assistant-fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #FF6B35, #4A90E2);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  z-index: 1000;
}

.ai-assistant-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
}

.ai-assistant-fab.active {
  background: #1A1A1A;
}

/* Modals */
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
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 0.75rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.modal-body {
  padding: 2rem;
}

.modal-actions {
  padding: 1rem 2rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Forms */
.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #FF6B35;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

/* Program Options */
.available-programs {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.program-option {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.program-option:hover {
  border-color: #FF6B35;
  background: #fff7ed;
}

.program-option.selected {
  border-color: #FF6B35;
  background: #fff7ed;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.program-option h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 0.5rem 0;
}

.program-option p {
  color: #64748b;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.program-details {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #64748b;
  flex-wrap: wrap;
}

.program-details span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

/* Toast Notifications */
.toast-container {
  position: fixed;
  top: 2rem;
  right: 2rem;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 300px;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  border-left: 4px solid #059669;
  background: #f0fdf4;
}

.toast.error {
  border-left: 4px solid #dc2626;
  background: #fef2f2;
}

.toast.warning {
  border-left: 4px solid #d97706;
  background: #fffbeb;
}

.toast.info {
  border-left: 4px solid #4A90E2;
  background: #eff6ff;
}

.toast-close {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  margin-left: auto;
  padding: 0.25rem;
}

.toast-close:hover {
  color: #1A1A1A;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .header-actions {
    justify-content: center;
  }

  .tab-navigation {
    padding: 0 1rem;
  }

  .content-area {
    padding: 1rem;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filters select,
  .search-input {
    min-width: auto;
    width: 100%;
  }

  .programs-grid {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .analytics-cards {
    grid-template-columns: 1fr;
  }

  .analytics-charts {
    grid-template-columns: 1fr;
  }

  .learning-paths,
  .trending-courses,
  .certificates-grid {
    grid-template-columns: 1fr;
  }

  .calendar-day {
    min-height: 80px;
    font-size: 0.875rem;
  }

  .toast-container {
    left: 1rem;
    right: 1rem;
  }

  .toast {
    min-width: auto;
  }

  .ai-assistant-fab {
    bottom: 1rem;
    right: 1rem;
  }
}

/* Utility classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }

/* Icon styles */
[class*="icon-"] {
  display: inline-block;
  width: 1em;
  height: 1em;
}

/* Print styles */
@media print {
  .header-actions,
  .tab-navigation,
  .ai-assistant-fab,
  .toast-container {
    display: none !important;
  }

  .content-area {
    padding: 0;
  }

  .tab-content {
    box-shadow: none;
    border: 1px solid #e2e8f0;
  }
}
</style>