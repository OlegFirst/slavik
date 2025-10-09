<template>
  <div class="bcm-portal">
    <!-- Header Section -->
    <div class="portal-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="portal-title">BCM Client Portal</h1>
            <p class="portal-subtitle">Self-Service Business Continuity Management</p>
          </div>
          <div class="col-md-4 text-end">
            <div class="client-info">
              <div class="client-badge">
                <i class="fas fa-building"></i>
                <span class="client-name">{{ clientInfo.name }}</span>
              </div>
              <div class="sso-status" :class="ssoStatus.status">
                <i class="fas" :class="ssoStatus.enabled ? 'fa-shield-alt' : 'fa-exclamation-triangle'"></i>
                <span>{{ ssoStatus.enabled ? 'SSO Active' : 'SSO Inactive' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Overview -->
    <div class="dashboard-overview">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="overview-card primary">
              <div class="card-icon">
                <i class="fas fa-clipboard-check"></i>
              </div>
              <div class="card-content">
                <h3 class="card-value">{{ dashboardData.activeRequests || 0 }}</h3>
                <p class="card-label">Active Service Requests</p>
                <small class="card-trend" :class="dashboardData.requestsTrend?.direction">
                  <i class="fas" :class="dashboardData.requestsTrend?.direction === 'up' ? 'fa-arrow-up' : 'fa-arrow-down'"></i>
                  {{ dashboardData.requestsTrend?.percentage }}% from last month
                </small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="overview-card success">
              <div class="card-icon">
                <i class="fas fa-graduation-cap"></i>
              </div>
              <div class="card-content">
                <h3 class="card-value">{{ dashboardData.completedTraining || 0 }}</h3>
                <p class="card-label">Training Completed</p>
                <small class="card-trend up">
                  <i class="fas fa-arrow-up"></i>
                  {{ dashboardData.trainingProgress }}% completion rate
                </small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="overview-card warning">
              <div class="card-icon">
                <i class="fas fa-dumbbell"></i>
              </div>
              <div class="card-content">
                <h3 class="card-value">{{ dashboardData.upcomingExercises || 0 }}</h3>
                <p class="card-label">Upcoming Exercises</p>
                <small class="card-trend">
                  <i class="fas fa-calendar"></i>
                  Next: {{ formatDate(dashboardData.nextExerciseDate) }}
                </small>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="overview-card info">
              <div class="card-icon">
                <i class="fas fa-shield-alt"></i>
              </div>
              <div class="card-content">
                <h3 class="card-value">{{ dashboardData.complianceScore || 0 }}%</h3>
                <p class="card-label">Compliance Status</p>
                <small class="card-trend" :class="dashboardData.complianceScore >= 80 ? 'up' : 'down'">
                  <i class="fas" :class="dashboardData.complianceScore >= 80 ? 'fa-check-circle' : 'fa-exclamation-triangle'"></i>
                  {{ dashboardData.complianceScore >= 80 ? 'Compliant' : 'Needs Attention' }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="portal-content">
      <div class="container-fluid">
        <!-- Navigation Tabs -->
        <ul class="nav nav-pills portal-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'dashboard' }"
              @click="setActiveTab('dashboard')"
              type="button"
            >
              <i class="fas fa-tachometer-alt"></i>
              Dashboard
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'requests' }"
              @click="setActiveTab('requests')"
              type="button"
            >
              <i class="fas fa-hand-paper"></i>
              Service Requests
              <span v-if="serviceRequests.filter(r => r.state === 'new').length" class="badge bg-primary ms-1">
                {{ serviceRequests.filter(r => r.state === 'new').length }}
              </span>
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'documents' }"
              @click="setActiveTab('documents')"
              type="button"
            >
              <i class="fas fa-folder-open"></i>
              Document Library
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'training' }"
              @click="setActiveTab('training')"
              type="button"
            >
              <i class="fas fa-graduation-cap"></i>
              Training
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'exercises' }"
              @click="setActiveTab('exercises')"
              type="button"
            >
              <i class="fas fa-dumbbell"></i>
              Exercises
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'compliance' }"
              @click="setActiveTab('compliance')"
              type="button"
            >
              <i class="fas fa-clipboard-check"></i>
              Compliance
            </button>
          </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content portal-tab-content">
          <!-- Dashboard Tab -->
          <div v-show="activeTab === 'dashboard'" class="tab-pane fade show active">
            <div class="row">
              <div class="col-md-8">
                <!-- Recent Activity -->
                <div class="content-card">
                  <div class="card-header">
                    <h5>Recent Activity</h5>
                    <div class="card-actions">
                      <button class="btn btn-outline-primary btn-sm" @click="refreshActivity">
                        <i class="fas fa-sync"></i>
                      </button>
                    </div>
                  </div>
                  <div class="card-body">
                    <div v-if="loading" class="text-center py-4">
                      <div class="spinner-border text-primary" role="status"></div>
                    </div>
                    <div v-else-if="recentActivity.length === 0" class="text-center py-4 text-muted">
                      <i class="fas fa-info-circle mb-2" style="font-size: 2rem;"></i>
                      <p>No recent activity to display</p>
                    </div>
                    <div v-else class="activity-timeline">
                      <div
                        v-for="activity in recentActivity"
                        :key="activity.id"
                        class="timeline-item"
                      >
                        <div class="timeline-marker" :class="activity.type">
                          <i class="fas" :class="getActivityIcon(activity.type)"></i>
                        </div>
                        <div class="timeline-content">
                          <h6 class="timeline-title">{{ activity.title }}</h6>
                          <p class="timeline-description">{{ activity.description }}</p>
                          <small class="timeline-time">{{ formatDateTime(activity.timestamp) }}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <!-- Quick Actions -->
                <div class="content-card">
                  <div class="card-header">
                    <h5>Quick Actions</h5>
                  </div>
                  <div class="card-body">
                    <div class="quick-actions-grid">
                      <button class="quick-action-btn" @click="showNewRequestModal">
                        <i class="fas fa-plus-circle"></i>
                        <span>New Service Request</span>
                      </button>
                      <button class="quick-action-btn" @click="setActiveTab('documents')">
                        <i class="fas fa-download"></i>
                        <span>Download Documents</span>
                      </button>
                      <button class="quick-action-btn" @click="setActiveTab('training')">
                        <i class="fas fa-book-open"></i>
                        <span>Browse Training</span>
                      </button>
                      <button class="quick-action-btn" @click="configureSSOModal">
                        <i class="fas fa-cog"></i>
                        <span>Configure SSO</span>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Notifications -->
                <div class="content-card">
                  <div class="card-header">
                    <h5>Notifications</h5>
                    <span v-if="unreadNotifications > 0" class="badge bg-danger">{{ unreadNotifications }}</span>
                  </div>
                  <div class="card-body">
                    <div v-if="notifications.length === 0" class="text-center py-3 text-muted">
                      <i class="fas fa-bell-slash"></i>
                      <p class="mb-0">No notifications</p>
                    </div>
                    <div v-else class="notifications-list">
                      <div
                        v-for="notification in notifications.slice(0, 5)"
                        :key="notification.id"
                        class="notification-item"
                        :class="{ unread: !notification.is_read }"
                        @click="markAsRead(notification.id)"
                      >
                        <div class="notification-icon">
                          <i class="fas" :class="getNotificationIcon(notification.notification_type)"></i>
                        </div>
                        <div class="notification-content">
                          <h6 class="notification-title">{{ notification.title }}</h6>
                          <p class="notification-message">{{ notification.message }}</p>
                          <small class="notification-time">{{ formatDateTime(notification.create_date) }}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Service Requests Tab -->
          <div v-show="activeTab === 'requests'" class="tab-pane">
            <div class="content-card">
              <div class="card-header">
                <h5>Service Requests</h5>
                <div class="card-actions">
                  <button class="btn btn-primary" @click="showNewRequestModal">
                    <i class="fas fa-plus"></i> New Request
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- Filters -->
                <div class="filters-row mb-4">
                  <div class="row">
                    <div class="col-md-3">
                      <select v-model="requestFilters.status" class="form-select" @change="loadServiceRequests">
                        <option value="">All Status</option>
                        <option value="draft">Draft</option>
                        <option value="submitted">Submitted</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>
                    <div class="col-md-3">
                      <select v-model="requestFilters.type" class="form-select" @change="loadServiceRequests">
                        <option value="">All Types</option>
                        <option value="bcp_review">BCP Review</option>
                        <option value="training">Training Request</option>
                        <option value="exercise">Exercise Planning</option>
                        <option value="compliance">Compliance Support</option>
                        <option value="consulting">Consulting</option>
                      </select>
                    </div>
                    <div class="col-md-6">
                      <div class="input-group">
                        <input
                          type="text"
                          class="form-control"
                          placeholder="Search requests..."
                          v-model="requestFilters.search"
                          @input="debounceSearch"
                        >
                        <button class="btn btn-outline-secondary" type="button" @click="clearFilters">
                          <i class="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Requests Table -->
                <div class="table-responsive">
                  <table class="table table-hover">
                    <thead>
                      <tr>
                        <th>Request ID</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Created</th>
                        <th>Expected Completion</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="loading">
                        <td colspan="8" class="text-center py-4">
                          <div class="spinner-border text-primary" role="status"></div>
                        </td>
                      </tr>
                      <tr v-else-if="filteredServiceRequests.length === 0">
                        <td colspan="8" class="text-center py-4 text-muted">
                          <i class="fas fa-inbox" style="font-size: 2rem;"></i>
                          <p class="mb-0 mt-2">No service requests found</p>
                        </td>
                      </tr>
                      <tr v-else v-for="request in filteredServiceRequests" :key="request.id">
                        <td>
                          <span class="request-id">#{{ request.name }}</span>
                        </td>
                        <td>
                          <span class="badge" :class="getRequestTypeBadge(request.request_type)">
                            {{ formatRequestType(request.request_type) }}
                          </span>
                        </td>
                        <td>
                          <div class="request-description">
                            {{ truncateText(request.description, 50) }}
                          </div>
                        </td>
                        <td>
                          <span class="status-badge" :class="request.state">
                            {{ formatStatus(request.state) }}
                          </span>
                        </td>
                        <td>
                          <span class="priority-badge" :class="request.priority">
                            {{ request.priority }}
                          </span>
                        </td>
                        <td>{{ formatDate(request.create_date) }}</td>
                        <td>{{ formatDate(request.expected_completion) }}</td>
                        <td>
                          <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" @click="viewRequest(request)">
                              <i class="fas fa-eye"></i>
                            </button>
                            <button
                              v-if="request.state === 'draft'"
                              class="btn btn-outline-success"
                              @click="editRequest(request)"
                            >
                              <i class="fas fa-edit"></i>
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

          <!-- Documents Tab -->
          <div v-show="activeTab === 'documents'" class="tab-pane">
            <div class="content-card">
              <div class="card-header">
                <h5>Document Library</h5>
                <div class="card-actions">
                  <button class="btn btn-outline-primary" @click="loadDocuments">
                    <i class="fas fa-sync"></i> Refresh
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- Document Filters -->
                <div class="filters-row mb-4">
                  <div class="row">
                    <div class="col-md-4">
                      <select v-model="documentFilters.category" class="form-select" @change="loadDocuments">
                        <option value="">All Categories</option>
                        <option value="policies">Policies</option>
                        <option value="procedures">Procedures</option>
                        <option value="templates">Templates</option>
                        <option value="training">Training Materials</option>
                        <option value="reports">Reports</option>
                      </select>
                    </div>
                    <div class="col-md-8">
                      <div class="input-group">
                        <input
                          type="text"
                          class="form-control"
                          placeholder="Search documents..."
                          v-model="documentFilters.search"
                          @input="debounceDocumentSearch"
                        >
                        <button class="btn btn-outline-secondary" type="button" @click="documentFilters.search = ''">
                          <i class="fas fa-times"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Documents Grid -->
                <div class="documents-grid">
                  <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-2 text-muted">Loading documents...</p>
                  </div>
                  <div v-else-if="documents.length === 0" class="text-center py-5 text-muted">
                    <i class="fas fa-folder-open" style="font-size: 3rem;"></i>
                    <p class="mt-3">No documents available</p>
                  </div>
                  <div v-else class="row">
                    <div v-for="document in documents" :key="document.id" class="col-md-4 col-lg-3 mb-4">
                      <div class="document-card">
                        <div class="document-icon">
                          <i class="fas" :class="getDocumentIcon(document.document_type)"></i>
                        </div>
                        <div class="document-info">
                          <h6 class="document-title">{{ document.name }}</h6>
                          <p class="document-description">{{ truncateText(document.description, 80) }}</p>
                          <div class="document-meta">
                            <small class="text-muted">
                              <i class="fas fa-calendar"></i>
                              {{ formatDate(document.create_date) }}
                            </small>
                            <small class="text-muted">
                              <i class="fas fa-file"></i>
                              {{ formatFileSize(document.file_size) }}
                            </small>
                          </div>
                        </div>
                        <div class="document-actions">
                          <button class="btn btn-primary btn-sm" @click="downloadDocument(document.id)">
                            <i class="fas fa-download"></i> Download
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Training Tab -->
          <div v-show="activeTab === 'training'" class="tab-pane">
            <div class="row">
              <div class="col-md-8">
                <div class="content-card">
                  <div class="card-header">
                    <h5>Available Training Programs</h5>
                  </div>
                  <div class="card-body">
                    <div class="training-grid">
                      <div v-if="loading" class="text-center py-5">
                        <div class="spinner-border text-primary" role="status"></div>
                      </div>
                      <div v-else class="row">
                        <div v-for="program in trainingPrograms" :key="program.id" class="col-md-6 mb-4">
                          <div class="training-card">
                            <div class="training-header">
                              <div class="training-type">
                                <span class="badge" :class="getTrainingTypeBadge(program.training_type)">
                                  {{ formatTrainingType(program.training_type) }}
                                </span>
                              </div>
                              <div class="training-level">
                                <span class="level-badge" :class="program.difficulty_level">
                                  {{ program.difficulty_level }}
                                </span>
                              </div>
                            </div>
                            <div class="training-content">
                              <h6 class="training-title">{{ program.name }}</h6>
                              <p class="training-description">{{ truncateText(program.description, 100) }}</p>
                              <div class="training-meta">
                                <small><i class="fas fa-clock"></i> {{ program.duration }} hours</small>
                                <small><i class="fas fa-users"></i> {{ program.enrollment_count }} enrolled</small>
                                <small><i class="fas fa-star"></i> {{ program.rating }}/5</small>
                              </div>
                            </div>
                            <div class="training-actions">
                              <button
                                class="btn btn-primary btn-sm"
                                @click="enrollInTraining(program.id)"
                                :disabled="isEnrolled(program.id)"
                              >
                                <i class="fas" :class="isEnrolled(program.id) ? 'fa-check' : 'fa-graduation-cap'"></i>
                                {{ isEnrolled(program.id) ? 'Enrolled' : 'Enroll' }}
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="content-card">
                  <div class="card-header">
                    <h5>My Training</h5>
                  </div>
                  <div class="card-body">
                    <div v-if="trainingEnrollments.length === 0" class="text-center py-4 text-muted">
                      <i class="fas fa-graduation-cap" style="font-size: 2rem;"></i>
                      <p class="mt-2">No training enrolled yet</p>
                    </div>
                    <div v-else class="enrollment-list">
                      <div v-for="enrollment in trainingEnrollments" :key="enrollment.id" class="enrollment-item">
                        <h6 class="enrollment-title">{{ enrollment.program_id[1] }}</h6>
                        <div class="progress mb-2">
                          <div
                            class="progress-bar"
                            :style="{ width: enrollment.progress + '%' }"
                            :class="enrollment.progress === 100 ? 'bg-success' : 'bg-primary'"
                          ></div>
                        </div>
                        <div class="enrollment-meta">
                          <small>Progress: {{ enrollment.progress }}%</small>
                          <small class="ms-2">Status: {{ enrollment.status }}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Exercises Tab -->
          <div v-show="activeTab === 'exercises'" class="tab-pane">
            <div class="content-card">
              <div class="card-header">
                <h5>Available Exercises</h5>
              </div>
              <div class="card-body">
                <div v-if="availableExercises.length === 0" class="text-center py-5 text-muted">
                  <i class="fas fa-dumbbell" style="font-size: 3rem;"></i>
                  <p class="mt-3">No exercises available for participation</p>
                </div>
                <div v-else class="exercises-list">
                  <div v-for="exercise in availableExercises" :key="exercise.id" class="exercise-card">
                    <div class="exercise-header">
                      <div class="exercise-type">
                        <span class="badge" :class="getExerciseTypeBadge(exercise.exercise_type)">
                          {{ formatExerciseType(exercise.exercise_type) }}
                        </span>
                      </div>
                      <div class="exercise-status">
                        <span class="status-badge" :class="exercise.state">{{ exercise.state }}</span>
                      </div>
                    </div>
                    <div class="exercise-content">
                      <h5 class="exercise-title">{{ exercise.name }}</h5>
                      <p class="exercise-description">{{ exercise.description }}</p>
                      <div class="exercise-details">
                        <div class="detail-item">
                          <i class="fas fa-calendar"></i>
                          <span>{{ formatDateTime(exercise.scheduled_date) }}</span>
                        </div>
                        <div class="detail-item">
                          <i class="fas fa-clock"></i>
                          <span>{{ exercise.duration }} hours</span>
                        </div>
                        <div class="detail-item">
                          <i class="fas fa-users"></i>
                          <span>{{ exercise.participant_count }} participants</span>
                        </div>
                      </div>
                    </div>
                    <div class="exercise-actions">
                      <button
                        class="btn btn-primary"
                        @click="showExerciseRegistration(exercise)"
                        :disabled="exercise.state !== 'scheduled'"
                      >
                        <i class="fas fa-hand-paper"></i>
                        Register
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Compliance Tab -->
          <div v-show="activeTab === 'compliance'" class="tab-pane">
            <div class="content-card">
              <div class="card-header">
                <h5>Compliance Status</h5>
                <div class="card-actions">
                  <button class="btn btn-outline-primary" @click="loadComplianceStatus">
                    <i class="fas fa-sync"></i> Refresh
                  </button>
                </div>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status"></div>
                </div>
                <div v-else>
                  <!-- Compliance Score -->
                  <div class="compliance-overview">
                    <div class="row">
                      <div class="col-md-6">
                        <div class="compliance-score">
                          <div class="score-circle" :class="getComplianceScoreClass(complianceStatus.overall_score)">
                            <span class="score-value">{{ complianceStatus.overall_score || 0 }}%</span>
                            <span class="score-label">Overall Compliance</span>
                          </div>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="compliance-breakdown">
                          <div
                            v-for="area in complianceStatus.areas || []"
                            :key="area.name"
                            class="compliance-area"
                          >
                            <div class="area-header">
                              <span class="area-name">{{ area.name }}</span>
                              <span class="area-score">{{ area.score }}%</span>
                            </div>
                            <div class="progress">
                              <div
                                class="progress-bar"
                                :class="getComplianceProgressClass(area.score)"
                                :style="{ width: area.score + '%' }"
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Action Items -->
                  <div class="compliance-actions mt-4">
                    <h6>Action Items</h6>
                    <div v-if="complianceStatus.action_items?.length === 0" class="text-muted">
                      <i class="fas fa-check-circle"></i> All compliance requirements are met
                    </div>
                    <div v-else class="action-items-list">
                      <div
                        v-for="item in complianceStatus.action_items || []"
                        :key="item.id"
                        class="action-item"
                        :class="item.priority"
                      >
                        <div class="item-icon">
                          <i class="fas" :class="getActionItemIcon(item.priority)"></i>
                        </div>
                        <div class="item-content">
                          <h6 class="item-title">{{ item.title }}</h6>
                          <p class="item-description">{{ item.description }}</p>
                          <small class="item-due">Due: {{ formatDate(item.due_date) }}</small>
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

    <!-- AI Assistant Panel -->
    <AssistantPanel ref="assistantPanel" />

    <!-- Service Request Modal -->
    <div class="modal fade" id="newRequestModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">New Service Request</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitServiceRequest">
              <div class="mb-3">
                <label class="form-label">Request Type *</label>
                <select v-model="newRequest.request_type" class="form-select" required>
                  <option value="">Select type...</option>
                  <option value="bcp_review">BCP Review</option>
                  <option value="training">Training Request</option>
                  <option value="exercise">Exercise Planning</option>
                  <option value="compliance">Compliance Support</option>
                  <option value="consulting">Consulting</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Title *</label>
                <input v-model="newRequest.name" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description *</label>
                <textarea v-model="newRequest.description" class="form-control" rows="4" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Priority</label>
                <select v-model="newRequest.priority" class="form-select">
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Expected Completion Date</label>
                <input v-model="newRequest.expected_completion" type="date" class="form-control">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submitServiceRequest" :disabled="submitting">
              <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
              {{ submitting ? 'Submitting...' : 'Submit Request' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Exercise Registration Modal -->
    <div class="modal fade" id="exerciseRegistrationModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Exercise Registration</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedExercise">
              <h6>{{ selectedExercise.name }}</h6>
              <p class="text-muted">{{ selectedExercise.description }}</p>

              <form @submit.prevent="submitExerciseRegistration">
                <div class="mb-3">
                  <label class="form-label">Participant Name *</label>
                  <input v-model="exerciseRegistration.name" type="text" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Email *</label>
                  <input v-model="exerciseRegistration.email" type="email" class="form-control" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Role *</label>
                  <input v-model="exerciseRegistration.role" type="text" class="form-control" required>
                </div>
              </form>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submitExerciseRegistration" :disabled="submitting">
              <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
              {{ submitting ? 'Registering...' : 'Register' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'
import bcmPortalService from '@/services/bcmPortal'

export default {
  name: 'BCMPortal',
  components: {
    AssistantPanel
  },
  setup() {
    const router = useRouter()

    // Reactive state
    const loading = ref(false)
    const submitting = ref(false)
    const activeTab = ref('dashboard')

    // Data
    const clientInfo = reactive({
      name: 'Demo Client Corporation',
      tenantId: null
    })

    const dashboardData = reactive({
      activeRequests: 0,
      completedTraining: 0,
      upcomingExercises: 0,
      complianceScore: 0,
      requestsTrend: { direction: 'up', percentage: 15 },
      trainingProgress: 85,
      nextExerciseDate: null
    })

    const ssoStatus = reactive({
      enabled: false,
      status: 'inactive',
      provider: 'keycloak',
      last_sync: null
    })

    const serviceRequests = ref([])
    const documents = ref([])
    const trainingPrograms = ref([])
    const trainingEnrollments = ref([])
    const availableExercises = ref([])
    const complianceStatus = reactive({
      overall_score: 0,
      areas: [],
      action_items: []
    })

    const notifications = ref([])
    const recentActivity = ref([])

    // Filters
    const requestFilters = reactive({
      status: '',
      type: '',
      search: ''
    })

    const documentFilters = reactive({
      category: '',
      search: ''
    })

    // Forms
    const newRequest = reactive({
      request_type: '',
      name: '',
      description: '',
      priority: 'normal',
      expected_completion: ''
    })

    const selectedExercise = ref(null)
    const exerciseRegistration = reactive({
      name: '',
      email: '',
      role: ''
    })

    // Computed
    const unreadNotifications = computed(() => {
      return notifications.value.filter(n => !n.is_read).length
    })

    const filteredServiceRequests = computed(() => {
      let filtered = serviceRequests.value

      if (requestFilters.status) {
        filtered = filtered.filter(r => r.state === requestFilters.status)
      }
      if (requestFilters.type) {
        filtered = filtered.filter(r => r.request_type === requestFilters.type)
      }
      if (requestFilters.search) {
        const search = requestFilters.search.toLowerCase()
        filtered = filtered.filter(r =>
          r.name.toLowerCase().includes(search) ||
          r.description.toLowerCase().includes(search)
        )
      }

      return filtered
    })

    // Methods
    const setActiveTab = (tab) => {
      activeTab.value = tab

      // Load data for specific tabs when activated
      switch (tab) {
        case 'requests':
          loadServiceRequests()
          break
        case 'documents':
          loadDocuments()
          break
        case 'training':
          loadTrainingPrograms()
          loadTrainingEnrollments()
          break
        case 'exercises':
          loadAvailableExercises()
          break
        case 'compliance':
          loadComplianceStatus()
          break
      }
    }

    const loadDashboardOverview = async () => {
      try {
        loading.value = true
        const overview = await bcmPortalService.getDashboardOverview()

        Object.assign(dashboardData, overview.dashboard_data || {})
        Object.assign(clientInfo, overview.client_info || {})

        // Load recent activity
        recentActivity.value = overview.recent_activity || []

      } catch (error) {
        console.error('Failed to load dashboard overview:', error)
        showToast('Failed to load dashboard data', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadServiceRequests = async () => {
      try {
        loading.value = true
        const requests = await bcmPortalService.getServiceRequests(requestFilters)
        serviceRequests.value = requests || []
      } catch (error) {
        console.error('Failed to load service requests:', error)
        showToast('Failed to load service requests', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadDocuments = async () => {
      try {
        loading.value = true
        const docs = await bcmPortalService.getDocumentLibrary(documentFilters)
        documents.value = docs || []
      } catch (error) {
        console.error('Failed to load documents:', error)
        showToast('Failed to load documents', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadTrainingPrograms = async () => {
      try {
        const programs = await bcmPortalService.getTrainingPrograms()
        trainingPrograms.value = programs || []
      } catch (error) {
        console.error('Failed to load training programs:', error)
        showToast('Failed to load training programs', 'error')
      }
    }

    const loadTrainingEnrollments = async () => {
      try {
        const enrollments = await bcmPortalService.getTrainingEnrollments()
        trainingEnrollments.value = enrollments || []
      } catch (error) {
        console.error('Failed to load training enrollments:', error)
      }
    }

    const loadAvailableExercises = async () => {
      try {
        loading.value = true
        const exercises = await bcmPortalService.getAvailableExercises()
        availableExercises.value = exercises || []
      } catch (error) {
        console.error('Failed to load exercises:', error)
        showToast('Failed to load exercises', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadComplianceStatus = async () => {
      try {
        loading.value = true
        const compliance = await bcmPortalService.getComplianceStatus()
        Object.assign(complianceStatus, compliance || {})
      } catch (error) {
        console.error('Failed to load compliance status:', error)
        showToast('Failed to load compliance status', 'error')
      } finally {
        loading.value = false
      }
    }

    const loadSSO = async () => {
      try {
        const status = await bcmPortalService.getSSOStatus()
        Object.assign(ssoStatus, status)
      } catch (error) {
        console.error('Failed to load SSO status:', error)
      }
    }

    const loadNotifications = async () => {
      try {
        const notifs = await bcmPortalService.getNotifications({ limit: 10 })
        notifications.value = notifs || []
      } catch (error) {
        console.error('Failed to load notifications:', error)
      }
    }

    const showNewRequestModal = () => {
      // Reset form
      Object.assign(newRequest, {
        request_type: '',
        name: '',
        description: '',
        priority: 'normal',
        expected_completion: ''
      })

      // Show modal (Bootstrap 5)
      const modal = new Modal(document.getElementById('newRequestModal'))
      modal.show()
    }

    const submitServiceRequest = async () => {
      try {
        submitting.value = true
        await bcmPortalService.createServiceRequest(newRequest)

        // Hide modal
        const modal = Modal.getInstance(document.getElementById('newRequestModal'))
        modal.hide()

        showToast('Service request submitted successfully', 'success')
        loadServiceRequests()

      } catch (error) {
        console.error('Failed to submit service request:', error)
        showToast('Failed to submit service request', 'error')
      } finally {
        submitting.value = false
      }
    }

    const showExerciseRegistration = (exercise) => {
      selectedExercise.value = exercise

      // Reset form
      Object.assign(exerciseRegistration, {
        name: '',
        email: '',
        role: ''
      })

      const modal = new Modal(document.getElementById('exerciseRegistrationModal'))
      modal.show()
    }

    const submitExerciseRegistration = async () => {
      try {
        submitting.value = true
        await bcmPortalService.registerForExercise(selectedExercise.value.id, exerciseRegistration)

        const modal = Modal.getInstance(document.getElementById('exerciseRegistrationModal'))
        modal.hide()

        showToast('Exercise registration successful', 'success')

      } catch (error) {
        console.error('Failed to register for exercise:', error)
        showToast('Failed to register for exercise', 'error')
      } finally {
        submitting.value = false
      }
    }

    const enrollInTraining = async (programId) => {
      try {
        await bcmPortalService.enrollInTraining(programId)
        showToast('Training enrollment successful', 'success')
        loadTrainingEnrollments()
      } catch (error) {
        console.error('Failed to enroll in training:', error)
        showToast('Failed to enroll in training', 'error')
      }
    }

    const downloadDocument = async (documentId) => {
      try {
        const response = await bcmPortalService.downloadDocument(documentId)

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = response.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)

      } catch (error) {
        console.error('Failed to download document:', error)
        showToast('Failed to download document', 'error')
      }
    }

    const markAsRead = async (notificationId) => {
      try {
        await bcmPortalService.markNotificationRead(notificationId)

        // Update local state
        const notification = notifications.value.find(n => n.id === notificationId)
        if (notification) {
          notification.is_read = true
        }
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    }

    const refreshActivity = () => {
      loadDashboardOverview()
    }

    const configureSSOModal = () => {
      showToast('SSO configuration feature coming soon', 'info')
    }

    // Utility methods
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString()
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return 'N/A'
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
    }

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const formatStatus = (status) => {
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const formatRequestType = (type) => {
      const types = {
        bcp_review: 'BCP Review',
        training: 'Training',
        exercise: 'Exercise',
        compliance: 'Compliance',
        consulting: 'Consulting'
      }
      return types[type] || type
    }

    const formatTrainingType = (type) => {
      const types = {
        online: 'Online',
        classroom: 'Classroom',
        workshop: 'Workshop',
        certification: 'Certification'
      }
      return types[type] || type
    }

    const formatExerciseType = (type) => {
      const types = {
        tabletop: 'Tabletop',
        simulation: 'Simulation',
        drill: 'Drill',
        full_scale: 'Full Scale'
      }
      return types[type] || type
    }

    const getActivityIcon = (type) => {
      const icons = {
        request: 'fa-hand-paper',
        training: 'fa-graduation-cap',
        exercise: 'fa-dumbbell',
        document: 'fa-file-alt',
        compliance: 'fa-shield-alt'
      }
      return icons[type] || 'fa-info-circle'
    }

    const getNotificationIcon = (type) => {
      const icons = {
        service_request_created: 'fa-hand-paper',
        training_enrolled: 'fa-graduation-cap',
        exercise_registered: 'fa-dumbbell',
        document_updated: 'fa-file-alt',
        compliance_alert: 'fa-exclamation-triangle'
      }
      return icons[type] || 'fa-bell'
    }

    const getDocumentIcon = (type) => {
      const icons = {
        pdf: 'fa-file-pdf',
        doc: 'fa-file-word',
        xls: 'fa-file-excel',
        ppt: 'fa-file-powerpoint',
        image: 'fa-file-image',
        video: 'fa-file-video'
      }
      return icons[type] || 'fa-file'
    }

    const getRequestTypeBadge = (type) => {
      const badges = {
        bcp_review: 'bg-primary',
        training: 'bg-success',
        exercise: 'bg-warning',
        compliance: 'bg-info',
        consulting: 'bg-secondary'
      }
      return badges[type] || 'bg-secondary'
    }

    const getTrainingTypeBadge = (type) => {
      const badges = {
        online: 'bg-primary',
        classroom: 'bg-success',
        workshop: 'bg-warning',
        certification: 'bg-info'
      }
      return badges[type] || 'bg-secondary'
    }

    const getExerciseTypeBadge = (type) => {
      const badges = {
        tabletop: 'bg-info',
        simulation: 'bg-warning',
        drill: 'bg-success',
        full_scale: 'bg-danger'
      }
      return badges[type] || 'bg-secondary'
    }

    const getComplianceScoreClass = (score) => {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 70) return 'fair'
      return 'poor'
    }

    const getComplianceProgressClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 80) return 'bg-info'
      if (score >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const getActionItemIcon = (priority) => {
      const icons = {
        urgent: 'fa-exclamation-circle',
        high: 'fa-exclamation-triangle',
        normal: 'fa-info-circle',
        low: 'fa-check-circle'
      }
      return icons[priority] || 'fa-info-circle'
    }

    const isEnrolled = (programId) => {
      return trainingEnrollments.value.some(e => e.program_id[0] === programId)
    }

    const showToast = (message, type = 'info') => {
      window.dispatchEvent(new CustomEvent('showNotification', {
        detail: {
          title: 'BCM Portal',
          message,
          type,
          timestamp: Date.now()
        }
      }))
    }

    const clearFilters = () => {
      Object.assign(requestFilters, {
        status: '',
        type: '',
        search: ''
      })
      loadServiceRequests()
    }

    const debounceSearch = (() => {
      let timeoutId
      return () => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(loadServiceRequests, 300)
      }
    })()

    const debounceDocumentSearch = (() => {
      let timeoutId
      return () => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(loadDocuments, 300)
      }
    })()

    // Lifecycle
    onMounted(async () => {
      await loadDashboardOverview()
      await loadSSO()
      await loadNotifications()

      // Load initial tab data
      if (activeTab.value === 'requests') {
        loadServiceRequests()
      }
    })

    return {
      // State
      loading,
      submitting,
      activeTab,

      // Data
      clientInfo,
      dashboardData,
      ssoStatus,
      serviceRequests,
      documents,
      trainingPrograms,
      trainingEnrollments,
      availableExercises,
      complianceStatus,
      notifications,
      recentActivity,

      // Filters
      requestFilters,
      documentFilters,

      // Forms
      newRequest,
      selectedExercise,
      exerciseRegistration,

      // Computed
      unreadNotifications,
      filteredServiceRequests,

      // Methods
      setActiveTab,
      loadServiceRequests,
      loadDocuments,
      loadTrainingPrograms,
      loadAvailableExercises,
      loadComplianceStatus,
      showNewRequestModal,
      submitServiceRequest,
      showExerciseRegistration,
      submitExerciseRegistration,
      enrollInTraining,
      downloadDocument,
      markAsRead,
      refreshActivity,
      configureSSOModal,

      // Utilities
      formatDate,
      formatDateTime,
      formatFileSize,
      truncateText,
      formatStatus,
      formatRequestType,
      formatTrainingType,
      formatExerciseType,
      getActivityIcon,
      getNotificationIcon,
      getDocumentIcon,
      getRequestTypeBadge,
      getTrainingTypeBadge,
      getExerciseTypeBadge,
      getComplianceScoreClass,
      getComplianceProgressClass,
      getActionItemIcon,
      isEnrolled,
      clearFilters,
      debounceSearch,
      debounceDocumentSearch
    }
  }
}
</script>

<style scoped>
/* Anthropic Color Palette */
:root {
  --anthro-orange: #FF6B35;
  --anthro-blue: #4A90E2;
  --anthro-dark: #1A1A1A;
  --anthro-light-gray: #F5F7FA;
  --anthro-medium-gray: #E1E8ED;
  --anthro-dark-gray: #657786;
}

.bcm-portal {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, var(--anthro-light-gray) 0%, #ffffff 100%);
  min-height: 100vh;
}

/* Header */
.portal-header {
  background: linear-gradient(135deg, var(--anthro-blue) 0%, var(--anthro-orange) 100%);
  color: white;
  padding: 2rem 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.portal-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
}

.portal-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin: 0.5rem 0 0 0;
}

.client-info {
  text-align: right;
}

.client-badge {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.sso-status {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
  font-size: 0.875rem;
  opacity: 0.9;
}

.sso-status.active {
  color: #10b981;
}

.sso-status.inactive {
  color: #f59e0b;
}

/* Dashboard Overview */
.dashboard-overview {
  padding: 2rem 0;
  background: white;
}

.overview-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--anthro-medium-gray);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.overview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--anthro-blue);
}

.overview-card.primary::before { background: var(--anthro-blue); }
.overview-card.success::before { background: #10b981; }
.overview-card.warning::before { background: var(--anthro-orange); }
.overview-card.info::before { background: #6366f1; }

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  color: white;
}

.overview-card.primary .card-icon { background: var(--anthro-blue); }
.overview-card.success .card-icon { background: #10b981; }
.overview-card.warning .card-icon { background: var(--anthro-orange); }
.overview-card.info .card-icon { background: #6366f1; }

.card-content {
  flex: 1;
}

.card-value {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--anthro-dark);
}

.card-label {
  font-size: 0.875rem;
  color: var(--anthro-dark-gray);
  margin: 0.25rem 0 0.5rem 0;
  font-weight: 500;
}

.card-trend {
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-trend.up { color: #10b981; }
.card-trend.down { color: #ef4444; }

/* Portal Content */
.portal-content {
  padding: 2rem 0;
}

.portal-tabs {
  background: white;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  border: none;
}

.portal-tabs .nav-link {
  border: none;
  border-radius: 8px;
  color: var(--anthro-dark-gray);
  font-weight: 500;
  padding: 0.75rem 1.25rem;
  margin: 0 0.25rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.portal-tabs .nav-link:hover {
  background: var(--anthro-light-gray);
  color: var(--anthro-blue);
}

.portal-tabs .nav-link.active {
  background: linear-gradient(135deg, var(--anthro-blue), var(--anthro-orange));
  color: white;
}

.portal-tabs .badge {
  font-size: 0.75rem;
}

/* Content Cards */
.content-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--anthro-medium-gray);
  overflow: hidden;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--anthro-medium-gray);
  background: var(--anthro-light-gray);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h5 {
  margin: 0;
  color: var(--anthro-dark);
  font-weight: 600;
}

.card-body {
  padding: 1.5rem;
}

/* Activity Timeline */
.activity-timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 15px;
  top: 40px;
  bottom: -20px;
  width: 2px;
  background: var(--anthro-medium-gray);
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.timeline-marker.request { background: var(--anthro-blue); }
.timeline-marker.training { background: #10b981; }
.timeline-marker.exercise { background: var(--anthro-orange); }
.timeline-marker.document { background: #6366f1; }
.timeline-marker.compliance { background: #ef4444; }

.timeline-content {
  flex: 1;
}

.timeline-title {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  color: var(--anthro-dark);
}

.timeline-description {
  margin: 0 0 0.5rem 0;
  color: var(--anthro-dark-gray);
  font-size: 0.875rem;
}

.timeline-time {
  color: var(--anthro-dark-gray);
  font-size: 0.75rem;
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: var(--anthro-light-gray);
  border: 1px solid var(--anthro-medium-gray);
  border-radius: 8px;
  color: var(--anthro-dark);
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.quick-action-btn:hover {
  background: var(--anthro-blue);
  color: white;
  border-color: var(--anthro-blue);
  transform: translateY(-2px);
}

.quick-action-btn i {
  font-size: 1.5rem;
}

.quick-action-btn span {
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}

/* Notifications */
.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--anthro-medium-gray);
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background: var(--anthro-light-gray);
  margin: 0 -1.5rem;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

.notification-item.unread {
  background: rgba(74, 144, 226, 0.1);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--anthro-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-title {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--anthro-dark);
}

.notification-message {
  margin: 0 0 0.25rem 0;
  font-size: 0.8125rem;
  color: var(--anthro-dark-gray);
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--anthro-dark-gray);
}

/* Tables */
.table {
  margin-bottom: 0;
}

.table th {
  border-bottom: 2px solid var(--anthro-medium-gray);
  font-weight: 600;
  color: var(--anthro-dark);
  font-size: 0.875rem;
  padding: 1rem 0.75rem;
}

.table td {
  border-bottom: 1px solid var(--anthro-medium-gray);
  padding: 1rem 0.75rem;
  vertical-align: middle;
}

.request-id {
  font-weight: 600;
  color: var(--anthro-blue);
}

.request-description {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-badge.draft { background: #f3f4f6; color: #374151; }
.status-badge.submitted { background: #dbeafe; color: #1d4ed8; }
.status-badge.in_progress { background: #fed7aa; color: #c2410c; }
.status-badge.completed { background: #dcfce7; color: #166534; }
.status-badge.cancelled { background: #fee2e2; color: #dc2626; }

.priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.priority-badge.low { background: #f0f9ff; color: #0369a1; }
.priority-badge.normal { background: #f3f4f6; color: #374151; }
.priority-badge.high { background: #fef3c7; color: #d97706; }
.priority-badge.urgent { background: #fee2e2; color: #dc2626; }

/* Documents Grid */
.documents-grid .row {
  margin: 0;
}

.document-card {
  background: white;
  border: 1px solid var(--anthro-medium-gray);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.document-card:hover {
  border-color: var(--anthro-blue);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.document-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: var(--anthro-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.document-info {
  flex: 1;
}

.document-title {
  font-weight: 600;
  color: var(--anthro-dark);
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.document-description {
  color: var(--anthro-dark-gray);
  font-size: 0.8125rem;
  line-height: 1.4;
  margin: 0 0 1rem 0;
}

.document-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.document-meta small {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.document-actions {
  margin-top: auto;
}

/* Training Cards */
.training-grid .row {
  margin: 0;
}

.training-card {
  background: white;
  border: 1px solid var(--anthro-medium-gray);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.training-card:hover {
  border-color: var(--anthro-orange);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.training-type .badge {
  font-size: 0.75rem;
}

.level-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: capitalize;
}

.level-badge.beginner { background: #dcfce7; color: #166534; }
.level-badge.intermediate { background: #fef3c7; color: #d97706; }
.level-badge.advanced { background: #fee2e2; color: #dc2626; }

.training-content {
  flex: 1;
}

.training-title {
  font-weight: 600;
  color: var(--anthro-dark);
  margin: 0 0 0.5rem 0;
}

.training-description {
  color: var(--anthro-dark-gray);
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 1rem 0;
}

.training-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.training-meta small {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--anthro-dark-gray);
}

.training-actions {
  margin-top: auto;
}

/* Enrollment List */
.enrollment-list {
  max-height: 400px;
  overflow-y: auto;
}

.enrollment-item {
  padding: 1rem 0;
  border-bottom: 1px solid var(--anthro-medium-gray);
}

.enrollment-item:last-child {
  border-bottom: none;
}

.enrollment-title {
  font-weight: 600;
  color: var(--anthro-dark);
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
}

.enrollment-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--anthro-dark-gray);
}

/* Exercise Cards */
.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.exercise-card {
  background: white;
  border: 1px solid var(--anthro-medium-gray);
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.exercise-card:hover {
  border-color: var(--anthro-orange);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.exercise-content {
  margin-bottom: 1.5rem;
}

.exercise-title {
  font-weight: 600;
  color: var(--anthro-dark);
  margin: 0 0 0.5rem 0;
}

.exercise-description {
  color: var(--anthro-dark-gray);
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.exercise-details {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--anthro-dark-gray);
}

.detail-item i {
  color: var(--anthro-blue);
}

/* Compliance */
.compliance-overview {
  margin-bottom: 2rem;
}

.compliance-score {
  display: flex;
  justify-content: center;
  align-items: center;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 8px solid;
  position: relative;
}

.score-circle.excellent { border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
.score-circle.good { border-color: var(--anthro-blue); background: rgba(74, 144, 226, 0.1); }
.score-circle.fair { border-color: var(--anthro-orange); background: rgba(255, 107, 53, 0.1); }
.score-circle.poor { border-color: #ef4444; background: rgba(239, 68, 68, 0.1); }

.score-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthro-dark);
}

.score-label {
  font-size: 0.875rem;
  color: var(--anthro-dark-gray);
  text-align: center;
  margin-top: 0.25rem;
}

.compliance-breakdown {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.compliance-area {
  background: var(--anthro-light-gray);
  padding: 1rem;
  border-radius: 8px;
}

.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.area-name {
  font-weight: 500;
  color: var(--anthro-dark);
}

.area-score {
  font-weight: 600;
  color: var(--anthro-blue);
}

.progress {
  height: 8px;
  border-radius: 4px;
  background: var(--anthro-medium-gray);
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Action Items */
.action-items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid var(--anthro-medium-gray);
}

.action-item.urgent {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.action-item.high {
  border-color: var(--anthro-orange);
  background: rgba(255, 107, 53, 0.05);
}

.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  color: white;
  flex-shrink: 0;
}

.action-item.urgent .item-icon { background: #ef4444; }
.action-item.high .item-icon { background: var(--anthro-orange); }
.action-item.normal .item-icon { background: var(--anthro-blue); }
.action-item.low .item-icon { background: #10b981; }

.item-content {
  flex: 1;
}

.item-title {
  font-weight: 600;
  color: var(--anthro-dark);
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
}

.item-description {
  color: var(--anthro-dark-gray);
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  line-height: 1.4;
}

.item-due {
  font-size: 0.75rem;
  color: var(--anthro-dark-gray);
}

/* Filters */
.filters-row {
  background: var(--anthro-light-gray);
  padding: 1rem;
  border-radius: 8px;
}

/* Badge Colors */
.badge.bg-primary { background-color: var(--anthro-blue) !important; }
.badge.bg-warning { background-color: var(--anthro-orange) !important; color: white !important; }

/* Responsive */
@media (max-width: 768px) {
  .portal-title {
    font-size: 2rem;
  }

  .overview-card {
    margin-bottom: 1rem;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .exercise-details,
  .training-meta {
    flex-direction: column;
    gap: 0.5rem;
  }

  .compliance-overview .row {
    flex-direction: column;
  }

  .score-circle {
    width: 120px;
    height: 120px;
    margin-bottom: 2rem;
  }
}

/* Loading and Empty States */
.spinner-border {
  color: var(--anthro-blue) !important;
}

/* Scrollbar Styling */
.notifications-list::-webkit-scrollbar,
.enrollment-list::-webkit-scrollbar {
  width: 4px;
}

.notifications-list::-webkit-scrollbar-track,
.enrollment-list::-webkit-scrollbar-track {
  background: transparent;
}

.notifications-list::-webkit-scrollbar-thumb,
.enrollment-list::-webkit-scrollbar-thumb {
  background: var(--anthro-medium-gray);
  border-radius: 2px;
}

.notifications-list::-webkit-scrollbar-thumb:hover,
.enrollment-list::-webkit-scrollbar-thumb:hover {
  background: var(--anthro-dark-gray);
}
</style>