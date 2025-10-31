<template>
  <div class="bcm-governance">
    <!-- Header Section -->
    <div class="governance-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">
              <i class="fas fa-balance-scale me-3"></i>
              BCM Governance
            </h1>
            <p class="page-subtitle">Risk & Compliance Management</p>
          </div>
          <div class="col-md-4 text-end">
            <div class="governance-status">
              <div class="status-item">
                <span class="status-label">Overall Risk:</span>
                <span class="risk-badge" :class="overallRiskClass">{{ overallRiskLevel }}</span>
              </div>
              <div class="status-item">
                <span class="status-label">Compliance:</span>
                <span class="compliance-badge" :class="complianceStatusClass">{{ overallComplianceLevel }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Dashboard -->
    <div class="metrics-dashboard">
      <div class="container-fluid">
        <div class="row">
          <div class="col-lg-3 col-md-6 mb-4">
            <div class="metric-card risk-metric">
              <div class="metric-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.totalRisks }}</h3>
                <p class="metric-label">Active Risks</p>
                <div class="metric-breakdown">
                  <span class="critical">{{ metrics.criticalRisks }} Critical</span>
                  <span class="high">{{ metrics.highRisks }} High</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-3 col-md-6 mb-4">
            <div class="metric-card compliance-metric">
              <div class="metric-icon">
                <i class="fas fa-clipboard-check"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.complianceScore }}%</h3>
                <p class="metric-label">Average Compliance</p>
                <div class="metric-breakdown">
                  <span>{{ metrics.compliantRequirements }}/{{ metrics.totalRequirements }} Requirements</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-3 col-md-6 mb-4">
            <div class="metric-card policy-metric">
              <div class="metric-icon">
                <i class="fas fa-file-contract"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.activePolicies }}</h3>
                <p class="metric-label">Active Policies</p>
                <div class="metric-breakdown">
                  <span class="warning">{{ metrics.policiesForReview }} Due for Review</span>
                </div>
              </div>
            </div>
          </div>

          <div class="col-lg-3 col-md-6 mb-4">
            <div class="metric-card audit-metric">
              <div class="metric-icon">
                <i class="fas fa-search"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ metrics.openAudits }}</h3>
                <p class="metric-label">Open Audits</p>
                <div class="metric-breakdown">
                  <span>{{ metrics.auditTrailEntries }} Trail Entries</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="governance-content">
      <div class="container-fluid">
        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <nav class="nav nav-pills" role="tablist">
            <button
              class="nav-link"
              :class="{ active: activeTab === 'overview' }"
              @click="activeTab = 'overview'"
            >
              <i class="fas fa-tachometer-alt me-2"></i>
              Overview
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'risks' }"
              @click="activeTab = 'risks'"
            >
              <i class="fas fa-exclamation-triangle me-2"></i>
              Risk Management
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'compliance' }"
              @click="activeTab = 'compliance'"
            >
              <i class="fas fa-shield-alt me-2"></i>
              Compliance
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'policies' }"
              @click="activeTab = 'policies'"
            >
              <i class="fas fa-file-contract me-2"></i>
              Policies
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'governance' }"
              @click="activeTab = 'governance'"
            >
              <i class="fas fa-sitemap me-2"></i>
              Structure
            </button>
            <button
              class="nav-link"
              :class="{ active: activeTab === 'reporting' }"
              @click="activeTab = 'reporting'"
            >
              <i class="fas fa-chart-bar me-2"></i>
              Reports
            </button>
          </nav>
        </div>

        <!-- Tab Content -->
        <div class="tab-content mt-4">

          <!-- Overview Tab -->
          <div v-show="activeTab === 'overview'" class="tab-pane">
            <div class="row">
              <!-- Risk Heat Map -->
              <div class="col-lg-8 mb-4">
                <div class="governance-card">
                  <div class="card-header">
                    <h4 class="card-title">Risk Heat Map</h4>
                    <div class="card-actions">
                      <button class="btn btn-sm btn-outline-primary" @click="refreshRiskHeatMap">
                        <i class="fas fa-refresh me-1"></i>
                        Refresh
                      </button>
                    </div>
                  </div>
                  <div class="card-body">
                    <div class="risk-heatmap" ref="heatmapContainer">
                      <div class="heatmap-grid">
                        <div class="heatmap-axis heatmap-y-axis">
                          <div class="axis-label">Impact</div>
                          <div class="axis-values">
                            <div class="axis-value" v-for="i in 5" :key="'impact-'+i">{{ 6-i }}</div>
                          </div>
                        </div>
                        <div class="heatmap-matrix">
                          <div class="matrix-row" v-for="impact in 5" :key="'row-'+impact">
                            <div
                              class="matrix-cell"
                              v-for="likelihood in 5" :key="'cell-'+impact+'-'+likelihood"
                              :class="getHeatmapCellClass(likelihood, 6-impact)"
                              @click="showRisksInCell(likelihood, 6-impact)"
                            >
                              <span class="cell-count">{{ getRiskCount(likelihood, 6-impact) }}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="heatmap-axis heatmap-x-axis">
                        <div class="axis-values">
                          <div class="axis-value" v-for="i in 5" :key="'likelihood-'+i">{{ i }}</div>
                        </div>
                        <div class="axis-label">Likelihood</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Compliance Overview -->
              <div class="col-lg-4 mb-4">
                <div class="governance-card">
                  <div class="card-header">
                    <h4 class="card-title">Compliance Overview</h4>
                  </div>
                  <div class="card-body">
                    <div class="compliance-frameworks">
                      <div
                        class="framework-item"
                        v-for="framework in complianceFrameworks"
                        :key="framework.id"
                      >
                        <div class="framework-header">
                          <span class="framework-name">{{ framework.name }}</span>
                          <span class="framework-percentage">{{ framework.compliance_level }}%</span>
                        </div>
                        <div class="framework-progress">
                          <div class="progress">
                            <div
                              class="progress-bar"
                              :class="getComplianceProgressClass(framework.compliance_level)"
                              :style="{width: framework.compliance_level + '%'}"
                            ></div>
                          </div>
                        </div>
                        <div class="framework-details">
                          <small>{{ framework.compliant_requirements || 0 }}/{{ framework.requirements }} requirements</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent Activities -->
              <div class="col-lg-6 mb-4">
                <div class="governance-card">
                  <div class="card-header">
                    <h4 class="card-title">Recent Activities</h4>
                  </div>
                  <div class="card-body">
                    <div class="activity-timeline">
                      <div
                        class="timeline-item"
                        v-for="activity in recentActivities"
                        :key="activity.id"
                      >
                        <div class="timeline-marker" :class="activity.type"></div>
                        <div class="timeline-content">
                          <div class="activity-title">{{ activity.title }}</div>
                          <div class="activity-description">{{ activity.description }}</div>
                          <div class="activity-meta">
                            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
                            <span class="activity-user">{{ activity.user }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- AI Insights -->
              <div class="col-lg-6 mb-4">
                <div class="governance-card">
                  <div class="card-header">
                    <h4 class="card-title">
                      <i class="fas fa-robot me-2"></i>
                      AI Insights
                    </h4>
                  </div>
                  <div class="card-body">
                    <div class="ai-insights">
                      <div
                        class="insight-item"
                        v-for="insight in aiInsights"
                        :key="insight.id"
                      >
                        <div class="insight-icon">
                          <i :class="insight.icon"></i>
                        </div>
                        <div class="insight-content">
                          <div class="insight-title">{{ insight.title }}</div>
                          <div class="insight-description">{{ insight.description }}</div>
                          <div class="insight-confidence">
                            Confidence: {{ insight.confidence }}%
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Risk Management Tab -->
          <div v-show="activeTab === 'risks'" class="tab-pane">
            <div class="risks-management">
              <!-- Risk Controls -->
              <div class="risk-controls mb-4">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <div class="risk-filters">
                      <select v-model="riskFilters.severity" class="form-select me-2" @change="filterRisks">
                        <option value="">All Severities</option>
                        <option value="Critical">Critical</option>
                        <option value="High">High</option>
                        <option value="Medium">Medium</option>
                        <option value="Low">Low</option>
                      </select>
                      <select v-model="riskFilters.category" class="form-select me-2" @change="filterRisks">
                        <option value="">All Categories</option>
                        <option value="Operational">Operational</option>
                        <option value="Financial">Financial</option>
                        <option value="Strategic">Strategic</option>
                        <option value="Compliance">Compliance</option>
                        <option value="Technology">Technology</option>
                      </select>
                      <select v-model="riskFilters.status" class="form-select" @change="filterRisks">
                        <option value="">All Statuses</option>
                        <option value="identified">Identified</option>
                        <option value="assessed">Assessed</option>
                        <option value="mitigated">Mitigated</option>
                        <option value="accepted">Accepted</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6 text-end">
                    <button class="btn btn-primary" @click="showCreateRiskModal">
                      <i class="fas fa-plus me-2"></i>
                      New Risk Assessment
                    </button>
                  </div>
                </div>
              </div>

              <!-- Risk List -->
              <div class="governance-card">
                <div class="card-body p-0">
                  <div class="table-responsive">
                    <table class="table table-hover mb-0">
                      <thead class="table-dark">
                        <tr>
                          <th>Risk</th>
                          <th>Category</th>
                          <th>Likelihood</th>
                          <th>Impact</th>
                          <th>Risk Score</th>
                          <th>Severity</th>
                          <th>Owner</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="risk in filteredRisks" :key="risk.id">
                          <td>
                            <div class="risk-info">
                              <div class="risk-name">{{ risk.name }}</div>
                              <div class="risk-description">{{ risk.description }}</div>
                            </div>
                          </td>
                          <td>
                            <span class="badge bg-secondary">{{ risk.category }}</span>
                          </td>
                          <td>
                            <span class="likelihood-value">{{ risk.likelihood }}/5</span>
                          </td>
                          <td>
                            <span class="impact-value">{{ risk.impact }}/5</span>
                          </td>
                          <td>
                            <span class="risk-score">{{ risk.risk_score }}</span>
                          </td>
                          <td>
                            <span class="severity-badge" :class="getRiskSeverityClass(risk.severity)">
                              {{ risk.severity }}
                            </span>
                          </td>
                          <td>{{ risk.risk_owner }}</td>
                          <td>
                            <span class="status-badge" :class="getRiskStatusClass(risk.status)">
                              {{ risk.status }}
                            </span>
                          </td>
                          <td>
                            <div class="risk-actions">
                              <button class="btn btn-sm btn-outline-primary" @click="editRisk(risk)">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-info" @click="analyzeRiskWithAI(risk)">
                                <i class="fas fa-robot"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteRisk(risk)">
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
            </div>
          </div>

          <!-- Compliance Tab -->
          <div v-show="activeTab === 'compliance'" class="tab-pane">
            <div class="compliance-management">
              <!-- Framework Selection -->
              <div class="framework-selector mb-4">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <select v-model="selectedFramework" class="form-select" @change="loadComplianceData">
                      <option value="">Select Framework</option>
                      <option
                        v-for="framework in complianceFrameworks"
                        :key="framework.id"
                        :value="framework.id"
                      >
                        {{ framework.name }}
                      </option>
                    </select>
                  </div>
                  <div class="col-md-6 text-end">
                    <button class="btn btn-primary me-2" @click="performGapAnalysis" :disabled="!selectedFramework">
                      <i class="fas fa-search me-2"></i>
                      Gap Analysis
                    </button>
                    <button class="btn btn-success" @click="generateComplianceReport" :disabled="!selectedFramework">
                      <i class="fas fa-file-pdf me-2"></i>
                      Generate Report
                    </button>
                  </div>
                </div>
              </div>

              <!-- Compliance Requirements -->
              <div class="governance-card" v-if="selectedFramework && complianceRequirements.length">
                <div class="card-header">
                  <h4 class="card-title">{{ getFrameworkName(selectedFramework) }} Requirements</h4>
                  <div class="compliance-summary">
                    <span class="compliant-count">{{ getCompliantCount() }} Compliant</span>
                    <span class="non-compliant-count">{{ getNonCompliantCount() }} Non-Compliant</span>
                    <span class="pending-count">{{ getPendingCount() }} Pending</span>
                  </div>
                </div>
                <div class="card-body p-0">
                  <div class="requirements-list">
                    <div
                      class="requirement-item"
                      v-for="requirement in complianceRequirements"
                      :key="requirement.id"
                    >
                      <div class="requirement-header">
                        <div class="requirement-info">
                          <h6 class="requirement-title">{{ requirement.title }}</h6>
                          <p class="requirement-description">{{ requirement.description }}</p>
                        </div>
                        <div class="requirement-status">
                          <select
                            v-model="requirement.status"
                            class="form-select form-select-sm"
                            @change="updateRequirementStatus(requirement)"
                          >
                            <option value="not_implemented">Not Implemented</option>
                            <option value="partially_implemented">Partially Implemented</option>
                            <option value="fully_implemented">Fully Implemented</option>
                            <option value="not_applicable">Not Applicable</option>
                          </select>
                        </div>
                      </div>
                      <div class="requirement-evidence" v-if="requirement.evidence">
                        <div class="evidence-section">
                          <strong>Evidence:</strong>
                          <p>{{ requirement.evidence }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Gap Analysis Results -->
              <div class="governance-card mt-4" v-if="gapAnalysisResults">
                <div class="card-header">
                  <h4 class="card-title">Gap Analysis Results</h4>
                </div>
                <div class="card-body">
                  <div class="gap-analysis">
                    <div class="row">
                      <div class="col-md-4">
                        <div class="gap-metric">
                          <h5>{{ gapAnalysisResults.compliance_score }}%</h5>
                          <p>Overall Compliance</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="gap-metric">
                          <h5>{{ gapAnalysisResults.gaps.length }}</h5>
                          <p>Identified Gaps</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="gap-metric">
                          <h5>{{ gapAnalysisResults.recommendations.length }}</h5>
                          <p>Recommendations</p>
                        </div>
                      </div>
                    </div>

                    <div class="gaps-section mt-4">
                      <h6>Priority Gaps</h6>
                      <div class="gap-item" v-for="gap in gapAnalysisResults.gaps" :key="gap.id">
                        <div class="gap-header">
                          <span class="gap-title">{{ gap.requirement }}</span>
                          <span class="gap-priority" :class="gap.priority.toLowerCase()">{{ gap.priority }}</span>
                        </div>
                        <div class="gap-description">{{ gap.description }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Policies Tab -->
          <div v-show="activeTab === 'policies'" class="tab-pane">
            <div class="policy-management">
              <!-- Policy Controls -->
              <div class="policy-controls mb-4">
                <div class="row align-items-center">
                  <div class="col-md-6">
                    <div class="policy-search">
                      <div class="input-group">
                        <input
                          type="text"
                          class="form-control"
                          placeholder="Search policies..."
                          v-model="policySearchTerm"
                          @input="filterPolicies"
                        >
                        <button class="btn btn-outline-secondary" type="button">
                          <i class="fas fa-search"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6 text-end">
                    <button class="btn btn-primary" @click="showCreatePolicyModal">
                      <i class="fas fa-plus me-2"></i>
                      New Policy
                    </button>
                  </div>
                </div>
              </div>

              <!-- Policy List -->
              <div class="governance-card">
                <div class="card-body p-0">
                  <div class="table-responsive">
                    <table class="table table-hover mb-0">
                      <thead class="table-dark">
                        <tr>
                          <th>Policy</th>
                          <th>Version</th>
                          <th>Status</th>
                          <th>Owner</th>
                          <th>Effective Date</th>
                          <th>Review Date</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="policy in filteredPolicies" :key="policy.id">
                          <td>
                            <div class="policy-info">
                              <div class="policy-name">{{ policy.name }}</div>
                              <div class="policy-category">{{ policy.category }}</div>
                            </div>
                          </td>
                          <td>
                            <span class="version-badge">v{{ policy.version }}</span>
                          </td>
                          <td>
                            <span class="status-badge" :class="getPolicyStatusClass(policy.status)">
                              {{ policy.status }}
                            </span>
                          </td>
                          <td>{{ policy.owner }}</td>
                          <td>{{ formatDate(policy.effective_date) }}</td>
                          <td>
                            <span :class="{'text-warning': isPolicyDueForReview(policy)}">
                              {{ formatDate(policy.review_date) }}
                            </span>
                          </td>
                          <td>
                            <div class="policy-actions">
                              <button class="btn btn-sm btn-outline-primary" @click="viewPolicy(policy)">
                                <i class="fas fa-eye"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-success" @click="editPolicy(policy)">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-info" @click="viewPolicyVersions(policy)">
                                <i class="fas fa-history"></i>
                              </button>
                              <button
                                class="btn btn-sm btn-outline-warning"
                                @click="approvePolicy(policy)"
                                v-if="policy.status === 'draft'"
                              >
                                <i class="fas fa-check"></i>
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
          </div>

          <!-- Governance Structure Tab -->
          <div v-show="activeTab === 'governance'" class="tab-pane">
            <div class="governance-structure">
              <!-- Structure Visualization -->
              <div class="governance-card">
                <div class="card-header">
                  <h4 class="card-title">Governance Structure</h4>
                  <div class="card-actions">
                    <button class="btn btn-sm btn-outline-primary" @click="editGovernanceStructure">
                      <i class="fas fa-edit me-1"></i>
                      Edit Structure
                    </button>
                  </div>
                </div>
                <div class="card-body">
                  <div class="org-chart" ref="orgChartContainer">
                    <!-- This would contain an organizational chart visualization -->
                    <div class="structure-placeholder">
                      <p class="text-muted">Governance structure visualization will be rendered here</p>
                      <p>Board → Committees → Roles → Teams</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Roles and Responsibilities -->
              <div class="row mt-4">
                <div class="col-md-6">
                  <div class="governance-card">
                    <div class="card-header">
                      <h5 class="card-title">Key Roles</h5>
                    </div>
                    <div class="card-body">
                      <div class="role-list">
                        <div class="role-item" v-for="role in governanceRoles" :key="role.id">
                          <div class="role-header">
                            <span class="role-title">{{ role.title }}</span>
                            <span class="role-level">{{ role.level }}</span>
                          </div>
                          <div class="role-description">{{ role.description }}</div>
                          <div class="role-assignee">
                            <strong>Assigned to:</strong> {{ role.assignee || 'Unassigned' }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="col-md-6">
                  <div class="governance-card">
                    <div class="card-header">
                      <h5 class="card-title">Committees</h5>
                    </div>
                    <div class="card-body">
                      <div class="committee-list">
                        <div class="committee-item" v-for="committee in governanceCommittees" :key="committee.id">
                          <div class="committee-header">
                            <span class="committee-name">{{ committee.name }}</span>
                            <span class="committee-frequency">{{ committee.meeting_frequency }}</span>
                          </div>
                          <div class="committee-purpose">{{ committee.purpose }}</div>
                          <div class="committee-members">
                            <strong>Members:</strong> {{ committee.members.join(', ') }}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Reporting Tab -->
          <div v-show="activeTab === 'reporting'" class="tab-pane">
            <div class="governance-reporting">
              <!-- Report Generation -->
              <div class="report-controls mb-4">
                <div class="row">
                  <div class="col-md-3">
                    <select v-model="reportType" class="form-select">
                      <option value="">Select Report Type</option>
                      <option value="risk_summary">Risk Summary</option>
                      <option value="compliance_status">Compliance Status</option>
                      <option value="policy_review">Policy Review</option>
                      <option value="executive_dashboard">Executive Dashboard</option>
                      <option value="audit_trail">Audit Trail</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <select v-model="reportPeriod" class="form-select">
                      <option value="current">Current Period</option>
                      <option value="last_month">Last Month</option>
                      <option value="last_quarter">Last Quarter</option>
                      <option value="last_year">Last Year</option>
                      <option value="custom">Custom Range</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <select v-model="reportFormat" class="form-select">
                      <option value="pdf">PDF</option>
                      <option value="excel">Excel</option>
                      <option value="html">HTML</option>
                    </select>
                  </div>
                  <div class="col-md-3">
                    <button
                      class="btn btn-primary w-100"
                      @click="generateReport"
                      :disabled="!reportType || generatingReport"
                    >
                      <i class="fas fa-file-download me-2"></i>
                      <span v-if="generatingReport">Generating...</span>
                      <span v-else>Generate Report</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Executive Dashboard Preview -->
              <div class="governance-card">
                <div class="card-header">
                  <h4 class="card-title">Executive Dashboard Preview</h4>
                </div>
                <div class="card-body">
                  <div class="executive-preview">
                    <div class="row">
                      <div class="col-md-4">
                        <div class="preview-metric">
                          <h3>{{ executiveDashboard.risk_score || 0 }}%</h3>
                          <p>Overall Risk Score</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="preview-metric">
                          <h3>{{ executiveDashboard.compliance_level || 0 }}%</h3>
                          <p>Compliance Level</p>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="preview-metric">
                          <h3>{{ executiveDashboard.policy_coverage || 0 }}%</h3>
                          <p>Policy Coverage</p>
                        </div>
                      </div>
                    </div>

                    <div class="mt-4">
                      <h6>Key Alerts</h6>
                      <div class="alert-list">
                        <div
                          class="alert-item"
                          v-for="alert in executiveDashboard.alerts"
                          :key="alert.id"
                          :class="'alert-' + alert.severity"
                        >
                          <i class="fas fa-exclamation-triangle me-2"></i>
                          {{ alert.message }}
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
    <AssistantPanel
      :context="{ module: 'governance', data: getCurrentTabData() }"
      :suggestions="getAISuggestions()"
      @action="handleAIAction"
    />

    <!-- Modals would go here -->
    <!-- Risk Creation Modal, Policy Creation Modal, etc. -->

  </div>
</template>

<script>
import bcmGovernanceService from '@/services/bcmGovernance.js'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

export default {
  name: 'BCMGovernance',
  components: {
    AssistantPanel
  },
  data() {
    return {
      loading: false,
      activeTab: 'overview',

      // Metrics
      metrics: {
        totalRisks: 0,
        criticalRisks: 0,
        highRisks: 0,
        complianceScore: 0,
        compliantRequirements: 0,
        totalRequirements: 0,
        activePolicies: 0,
        policiesForReview: 0,
        openAudits: 0,
        auditTrailEntries: 0
      },

      // Risk Management
      risks: [],
      filteredRisks: [],
      riskFilters: {
        severity: '',
        category: '',
        status: ''
      },
      riskHeatmapData: {
        matrix: [],
        risks: []
      },

      // Compliance
      complianceFrameworks: [],
      selectedFramework: '',
      complianceRequirements: [],
      gapAnalysisResults: null,

      // Policy Management
      policies: [],
      filteredPolicies: [],
      policySearchTerm: '',

      // Governance Structure
      governanceStructure: {
        board: [],
        committees: [],
        roles: []
      },
      governanceRoles: [],
      governanceCommittees: [],

      // Reporting
      reportType: '',
      reportPeriod: 'current',
      reportFormat: 'pdf',
      generatingReport: false,
      executiveDashboard: {},

      // Activities and Insights
      recentActivities: [],
      aiInsights: []
    }
  },

  computed: {
    overallRiskLevel() {
      if (this.metrics.criticalRisks > 0) return 'Critical'
      if (this.metrics.highRisks > 0) return 'High'
      return 'Medium'
    },

    overallRiskClass() {
      return `risk-${this.overallRiskLevel.toLowerCase()}`
    },

    overallComplianceLevel() {
      return this.metrics.complianceScore
    },

    complianceStatusClass() {
      if (this.metrics.complianceScore >= 90) return 'compliance-excellent'
      if (this.metrics.complianceScore >= 75) return 'compliance-good'
      if (this.metrics.complianceScore >= 50) return 'compliance-fair'
      return 'compliance-poor'
    }
  },

  async mounted() {
    await this.initializeData()
  },

  methods: {
    async initializeData() {
      this.loading = true
      try {
        // Load initial data
        await Promise.all([
          this.loadMetrics(),
          this.loadComplianceFrameworks(),
          this.loadRecentActivities(),
          this.loadAIInsights()
        ])

        // Load tab-specific data based on active tab
        await this.loadTabData()
      } catch (error) {
        console.error('Error initializing governance data:', error)
      } finally {
        this.loading = false
      }
    },

    async loadMetrics() {
      try {
        // This would be replaced with actual API calls
        this.metrics = {
          totalRisks: 47,
          criticalRisks: 3,
          highRisks: 12,
          complianceScore: 78,
          compliantRequirements: 34,
          totalRequirements: 45,
          activePolicies: 23,
          policiesForReview: 5,
          openAudits: 2,
          auditTrailEntries: 1247
        }
      } catch (error) {
        console.error('Error loading metrics:', error)
      }
    },

    async loadComplianceFrameworks() {
      try {
        this.complianceFrameworks = await bcmGovernanceService.getComplianceFrameworks()
      } catch (error) {
        console.error('Error loading compliance frameworks:', error)
      }
    },

    async loadTabData() {
      switch (this.activeTab) {
        case 'overview':
          await this.loadOverviewData()
          break
        case 'risks':
          await this.loadRiskData()
          break
        case 'compliance':
          await this.loadComplianceData()
          break
        case 'policies':
          await this.loadPolicyData()
          break
        case 'governance':
          await this.loadGovernanceStructureData()
          break
        case 'reporting':
          await this.loadReportingData()
          break
      }
    },

    async loadOverviewData() {
      try {
        const [heatmapData] = await Promise.all([
          bcmGovernanceService.getRiskHeatMap()
        ])
        this.riskHeatmapData = heatmapData
      } catch (error) {
        console.error('Error loading overview data:', error)
      }
    },

    async loadRiskData() {
      try {
        const riskData = await bcmGovernanceService.getRisks()
        this.risks = riskData.risks || []
        this.filteredRisks = [...this.risks]
      } catch (error) {
        console.error('Error loading risk data:', error)
      }
    },

    async loadComplianceData() {
      if (!this.selectedFramework) return

      try {
        const complianceStatus = await bcmGovernanceService.getComplianceStatus(this.selectedFramework)
        this.complianceRequirements = complianceStatus.requirements || []
      } catch (error) {
        console.error('Error loading compliance data:', error)
      }
    },

    async loadPolicyData() {
      try {
        const policyData = await bcmGovernanceService.getPolicies()
        this.policies = policyData.policies || []
        this.filteredPolicies = [...this.policies]
      } catch (error) {
        console.error('Error loading policy data:', error)
      }
    },

    async loadGovernanceStructureData() {
      try {
        const structure = await bcmGovernanceService.getGovernanceStructure()
        this.governanceStructure = structure
        this.governanceRoles = structure.roles || []
        this.governanceCommittees = structure.committees || []
      } catch (error) {
        console.error('Error loading governance structure:', error)
      }
    },

    async loadReportingData() {
      try {
        this.executiveDashboard = await bcmGovernanceService.getExecutiveDashboard()
      } catch (error) {
        console.error('Error loading reporting data:', error)
      }
    },

    async loadRecentActivities() {
      // Mock data - would be replaced with actual API call
      this.recentActivities = [
        {
          id: 1,
          type: 'risk',
          title: 'High Risk Identified',
          description: 'New cyber security risk identified in payment processing',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          user: 'John Doe'
        },
        {
          id: 2,
          type: 'compliance',
          title: 'Compliance Assessment Completed',
          description: 'ISO 22301 assessment completed with 78% compliance',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
          user: 'Jane Smith'
        }
      ]
    },

    async loadAIInsights() {
      // Mock data - would be replaced with actual AI service
      this.aiInsights = [
        {
          id: 1,
          icon: 'fas fa-exclamation-triangle text-warning',
          title: 'Risk Trend Alert',
          description: 'Operational risks have increased by 15% this quarter',
          confidence: 85
        },
        {
          id: 2,
          icon: 'fas fa-chart-line text-info',
          title: 'Compliance Opportunity',
          description: 'Implementing automated controls could improve compliance by 12%',
          confidence: 78
        }
      ]
    },

    // Risk Management Methods
    filterRisks() {
      this.filteredRisks = this.risks.filter(risk => {
        const severityMatch = !this.riskFilters.severity || risk.severity === this.riskFilters.severity
        const categoryMatch = !this.riskFilters.category || risk.category === this.riskFilters.category
        const statusMatch = !this.riskFilters.status || risk.status === this.riskFilters.status
        return severityMatch && categoryMatch && statusMatch
      })
    },

    getRiskCount(likelihood, impact) {
      return this.riskHeatmapData.risks.filter(risk =>
        risk.likelihood === likelihood && risk.impact === impact
      ).length
    },

    getHeatmapCellClass(likelihood, impact) {
      const score = likelihood * impact
      if (score >= 15) return 'heatmap-critical'
      if (score >= 10) return 'heatmap-high'
      if (score >= 6) return 'heatmap-medium'
      if (score >= 3) return 'heatmap-low'
      return 'heatmap-very-low'
    },

    showRisksInCell(likelihood, impact) {
      // Show modal with risks in this cell
      console.log(`Show risks with likelihood ${likelihood} and impact ${impact}`)
    },

    showCreateRiskModal() {
      // Show risk creation modal
      console.log('Show create risk modal')
    },

    editRisk(risk) {
      console.log('Edit risk:', risk)
    },

    async analyzeRiskWithAI(risk) {
      try {
        const analysis = await bcmGovernanceService.getAIRiskAnalysis(risk)
        console.log('AI Analysis:', analysis)
        // Show analysis results in modal
      } catch (error) {
        console.error('Error analyzing risk with AI:', error)
      }
    },

    async deleteRisk(risk) {
      if (confirm(`Are you sure you want to delete the risk "${risk.name}"?`)) {
        try {
          await bcmGovernanceService.deleteRisk(risk.id)
          this.loadRiskData()
        } catch (error) {
          console.error('Error deleting risk:', error)
        }
      }
    },

    refreshRiskHeatMap() {
      this.loadOverviewData()
    },

    // Compliance Methods
    async performGapAnalysis() {
      if (!this.selectedFramework) return

      try {
        this.gapAnalysisResults = await bcmGovernanceService.performGapAnalysis(this.selectedFramework)
      } catch (error) {
        console.error('Error performing gap analysis:', error)
      }
    },

    async updateRequirementStatus(requirement) {
      try {
        await bcmGovernanceService.updateComplianceRequirement(
          this.selectedFramework,
          requirement.id,
          requirement.status,
          requirement.evidence
        )
        // Refresh compliance data
        this.loadComplianceData()
      } catch (error) {
        console.error('Error updating requirement status:', error)
      }
    },

    getComplianceProgressClass(percentage) {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 75) return 'bg-info'
      if (percentage >= 50) return 'bg-warning'
      return 'bg-danger'
    },

    getCompliantCount() {
      return this.complianceRequirements.filter(r => r.status === 'fully_implemented').length
    },

    getNonCompliantCount() {
      return this.complianceRequirements.filter(r => r.status === 'not_implemented').length
    },

    getPendingCount() {
      return this.complianceRequirements.filter(r => r.status === 'partially_implemented').length
    },

    getFrameworkName(frameworkId) {
      const framework = this.complianceFrameworks.find(f => f.id === frameworkId)
      return framework ? framework.name : frameworkId
    },

    // Policy Methods
    filterPolicies() {
      const term = this.policySearchTerm.toLowerCase()
      this.filteredPolicies = this.policies.filter(policy =>
        policy.name.toLowerCase().includes(term) ||
        policy.category.toLowerCase().includes(term)
      )
    },

    showCreatePolicyModal() {
      console.log('Show create policy modal')
    },

    viewPolicy(policy) {
      console.log('View policy:', policy)
    },

    editPolicy(policy) {
      console.log('Edit policy:', policy)
    },

    viewPolicyVersions(policy) {
      console.log('View policy versions:', policy)
    },

    approvePolicy(policy) {
      console.log('Approve policy:', policy)
    },

    isPolicyDueForReview(policy) {
      const reviewDate = new Date(policy.review_date)
      const now = new Date()
      const daysDiff = (reviewDate - now) / (1000 * 60 * 60 * 24)
      return daysDiff <= 30
    },

    getPolicyStatusClass(status) {
      switch (status) {
        case 'active': return 'bg-success'
        case 'draft': return 'bg-warning'
        case 'archived': return 'bg-secondary'
        case 'under_review': return 'bg-info'
        default: return 'bg-light'
      }
    },

    // Governance Structure Methods
    editGovernanceStructure() {
      console.log('Edit governance structure')
    },

    // Reporting Methods
    async generateReport() {
      if (!this.reportType) return

      this.generatingReport = true
      try {
        const report = await bcmGovernanceService.generateGovernanceReport(this.reportType, {
          period: this.reportPeriod,
          format: this.reportFormat
        })

        // Handle report download/display
        console.log('Generated report:', report)

        // For demonstration, we'll just show an alert
        alert(`${this.reportType} report generated successfully!`)
      } catch (error) {
        console.error('Error generating report:', error)
        alert('Error generating report. Please try again.')
      } finally {
        this.generatingReport = false
      }
    },

    async generateComplianceReport() {
      await this.generateReport()
    },

    // Utility Methods
    getRiskSeverityClass(severity) {
      switch (severity.toLowerCase()) {
        case 'critical': return 'bg-danger'
        case 'high': return 'bg-warning'
        case 'medium': return 'bg-info'
        case 'low': return 'bg-success'
        default: return 'bg-secondary'
      }
    },

    getRiskStatusClass(status) {
      switch (status) {
        case 'identified': return 'bg-danger'
        case 'assessed': return 'bg-warning'
        case 'mitigated': return 'bg-info'
        case 'accepted': return 'bg-success'
        default: return 'bg-secondary'
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString()
    },

    // AI Assistant Methods
    getCurrentTabData() {
      switch (this.activeTab) {
        case 'risks': return { risks: this.filteredRisks }
        case 'compliance': return { framework: this.selectedFramework, requirements: this.complianceRequirements }
        case 'policies': return { policies: this.filteredPolicies }
        default: return {}
      }
    },

    getAISuggestions() {
      switch (this.activeTab) {
        case 'risks':
          return [
            'Analyze risk trends',
            'Suggest risk mitigation strategies',
            'Identify emerging risks'
          ]
        case 'compliance':
          return [
            'Recommend compliance improvements',
            'Analyze regulatory changes',
            'Suggest automation opportunities'
          ]
        default:
          return [
            'Generate governance insights',
            'Analyze risk patterns',
            'Recommend improvements'
          ]
      }
    },

    handleAIAction(action) {
      console.log('AI Action:', action)
      // Handle AI assistant actions
    }
  },

  watch: {
    activeTab() {
      this.loadTabData()
    },

    selectedFramework() {
      this.loadComplianceData()
    }
  }
}
</script>

<style scoped>
/* Anthropic Colors */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #f8f9fa;
}

.bcm-governance {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #ffffff 100%);
}

/* Header */
.governance-header {
  background: linear-gradient(135deg, var(--anthropic-dark) 0%, #2c3e50 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.8;
  margin: 0;
}

.governance-status {
  text-align: right;
}

.status-item {
  display: block;
  margin-bottom: 0.5rem;
}

.status-label {
  opacity: 0.8;
  margin-right: 0.5rem;
}

.risk-badge, .compliance-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.risk-critical { background: #dc3545; color: white; }
.risk-high { background: var(--anthropic-orange); color: white; }
.risk-medium { background: #ffc107; color: var(--anthropic-dark); }
.risk-low { background: #28a745; color: white; }

.compliance-excellent { background: #28a745; color: white; }
.compliance-good { background: var(--anthropic-blue); color: white; }
.compliance-fair { background: #ffc107; color: var(--anthropic-dark); }
.compliance-poor { background: #dc3545; color: white; }

/* Metrics Dashboard */
.metrics-dashboard {
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border-left: 4px solid;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.risk-metric { border-left-color: var(--anthropic-orange); }
.compliance-metric { border-left-color: var(--anthropic-blue); }
.policy-metric { border-left-color: #17a2b8; }
.audit-metric { border-left-color: #6f42c1; }

.metric-card .metric-icon {
  float: left;
  width: 60px;
  height: 60px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.metric-card .metric-icon i {
  font-size: 1.5rem;
  color: var(--anthropic-dark);
}

.metric-content {
  overflow: hidden;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.metric-label {
  font-size: 1rem;
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.metric-breakdown {
  font-size: 0.85rem;
}

.metric-breakdown .critical { color: #dc3545; font-weight: 600; margin-right: 1rem; }
.metric-breakdown .high { color: var(--anthropic-orange); font-weight: 600; }
.metric-breakdown .warning { color: #ffc107; font-weight: 600; }

/* Tab Navigation */
.tab-navigation {
  background: white;
  border-radius: 12px;
  padding: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.07);
  margin-bottom: 2rem;
}

.nav-pills .nav-link {
  border-radius: 8px;
  color: var(--anthropic-dark);
  font-weight: 500;
  padding: 0.75rem 1.5rem;
  margin: 0 0.25rem;
  transition: all 0.3s ease;
}

.nav-pills .nav-link:hover {
  background: rgba(74, 144, 226, 0.1);
  color: var(--anthropic-blue);
}

.nav-pills .nav-link.active {
  background: linear-gradient(135deg, var(--anthropic-blue) 0%, var(--anthropic-orange) 100%);
  color: white;
}

/* Cards */
.governance-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
  border: 1px solid rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.governance-card:hover {
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px 12px 0 0;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--anthropic-dark);
  margin: 0;
}

.card-body {
  padding: 1.5rem;
}

/* Risk Heat Map */
.risk-heatmap {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.heatmap-grid {
  display: flex;
  align-items: flex-start;
}

.heatmap-y-axis {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 1rem;
}

.heatmap-matrix {
  display: flex;
  flex-direction: column;
}

.matrix-row {
  display: flex;
}

.matrix-cell {
  width: 50px;
  height: 50px;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.matrix-cell:hover {
  transform: scale(1.1);
  z-index: 10;
}

.heatmap-critical { background: #dc3545; color: white; }
.heatmap-high { background: var(--anthropic-orange); color: white; }
.heatmap-medium { background: #ffc107; color: var(--anthropic-dark); }
.heatmap-low { background: #28a745; color: white; }
.heatmap-very-low { background: #f8f9fa; color: var(--anthropic-dark); }

.cell-count {
  font-weight: 600;
  font-size: 0.9rem;
}

.axis-label {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin: 0.5rem 0;
}

.axis-values {
  display: flex;
  flex-direction: column;
}

.heatmap-x-axis .axis-values {
  flex-direction: row;
}

.axis-value {
  width: 50px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--anthropic-dark);
}

/* Compliance Frameworks */
.compliance-frameworks {
  space-y: 1rem;
}

.framework-item {
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.framework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.framework-name {
  font-weight: 600;
  color: var(--anthropic-dark);
}

.framework-percentage {
  font-weight: 600;
  color: var(--anthropic-blue);
}

.framework-progress .progress {
  height: 8px;
  border-radius: 4px;
}

.framework-details {
  margin-top: 0.5rem;
  color: #6c757d;
}

/* Activity Timeline */
.activity-timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  margin-bottom: 1.5rem;
  position: relative;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 1rem;
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.timeline-marker.risk { background: var(--anthropic-orange); }
.timeline-marker.compliance { background: var(--anthropic-blue); }
.timeline-marker.policy { background: #17a2b8; }
.timeline-marker.audit { background: #6f42c1; }

.timeline-content {
  flex: 1;
}

.activity-title {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.activity-description {
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.activity-meta {
  font-size: 0.85rem;
  color: #adb5bd;
}

.activity-time {
  margin-right: 1rem;
}

/* AI Insights */
.ai-insights {
  space-y: 1rem;
}

.insight-item {
  display: flex;
  padding: 1rem;
  border: 1px solid rgba(74, 144, 226, 0.2);
  border-radius: 8px;
  background: rgba(74, 144, 226, 0.05);
  margin-bottom: 1rem;
}

.insight-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.insight-description {
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.insight-confidence {
  font-size: 0.85rem;
  color: var(--anthropic-blue);
  font-weight: 500;
}

/* Tables */
.table {
  margin: 0;
}

.table thead th {
  border-top: none;
  font-weight: 600;
  color: white;
  padding: 1rem;
}

.table td {
  padding: 1rem;
  vertical-align: middle;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.table-hover tbody tr:hover {
  background-color: rgba(74, 144, 226, 0.05);
}

/* Risk Management Specific */
.risk-info .risk-name {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.risk-info .risk-description {
  font-size: 0.9rem;
  color: #6c757d;
}

.severity-badge, .status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.risk-actions .btn {
  margin-right: 0.25rem;
}

/* Compliance Management */
.compliance-summary {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.compliant-count { color: #28a745; font-weight: 600; }
.non-compliant-count { color: #dc3545; font-weight: 600; }
.pending-count { color: #ffc107; font-weight: 600; }

.requirements-list {
  max-height: 600px;
  overflow-y: auto;
}

.requirement-item {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}

.requirement-item:last-child {
  border-bottom: none;
}

.requirement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.requirement-info {
  flex: 1;
  margin-right: 1rem;
}

.requirement-title {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin-bottom: 0.5rem;
}

.requirement-description {
  color: #6c757d;
  margin: 0;
}

.requirement-status {
  min-width: 200px;
}

.evidence-section {
  background: rgba(74, 144, 226, 0.05);
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid var(--anthropic-blue);
}

/* Gap Analysis */
.gap-analysis {
  padding: 1rem;
}

.gap-metric {
  text-align: center;
  padding: 1rem;
  background: rgba(74, 144, 226, 0.05);
  border-radius: 8px;
}

.gap-metric h5 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthropic-blue);
  margin-bottom: 0.5rem;
}

.gaps-section {
  margin-top: 2rem;
}

.gap-item {
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.gap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.gap-title {
  font-weight: 600;
  color: var(--anthropic-dark);
}

.gap-priority {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.gap-priority.high { background: #dc3545; color: white; }
.gap-priority.medium { background: #ffc107; color: var(--anthropic-dark); }
.gap-priority.low { background: #28a745; color: white; }

.gap-description {
  color: #6c757d;
}

/* Policy Management */
.policy-info .policy-name {
  font-weight: 600;
  color: var(--anthropic-dark);
  margin-bottom: 0.25rem;
}

.policy-info .policy-category {
  font-size: 0.9rem;
  color: #6c757d;
}

.version-badge {
  background: var(--anthropic-blue);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 500;
}

.policy-actions .btn {
  margin-right: 0.25rem;
}

/* Governance Structure */
.structure-placeholder {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.role-list, .committee-list {
  space-y: 1rem;
}

.role-item, .committee-item {
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.role-header, .committee-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.role-title, .committee-name {
  font-weight: 600;
  color: var(--anthropic-dark);
}

.role-level, .committee-frequency {
  font-size: 0.85rem;
  color: var(--anthropic-blue);
  background: rgba(74, 144, 226, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.role-description, .committee-purpose {
  color: #6c757d;
  margin-bottom: 0.5rem;
}

.role-assignee, .committee-members {
  font-size: 0.9rem;
  color: var(--anthropic-dark);
}

/* Reporting */
.report-controls {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.07);
}

.executive-preview {
  padding: 1rem;
}

.preview-metric {
  text-align: center;
  padding: 1rem;
  background: rgba(74, 144, 226, 0.05);
  border-radius: 8px;
}

.preview-metric h3 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--anthropic-blue);
  margin-bottom: 0.5rem;
}

.alert-list {
  space-y: 0.5rem;
}

.alert-item {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  border-left: 4px solid;
}

.alert-critical {
  background: rgba(220, 53, 69, 0.1);
  border-left-color: #dc3545;
  color: #721c24;
}

.alert-high {
  background: rgba(255, 107, 53, 0.1);
  border-left-color: var(--anthropic-orange);
  color: #8b2635;
}

.alert-medium {
  background: rgba(255, 193, 7, 0.1);
  border-left-color: #ffc107;
  color: #664d03;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .metrics-dashboard .col-lg-3 {
    margin-bottom: 1rem;
  }

  .tab-navigation .nav-link {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .governance-card {
    margin-bottom: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .table-responsive {
    font-size: 0.9rem;
  }

  .requirement-header, .gap-header, .role-header, .committee-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 576px) {
  .governance-header {
    text-align: center;
  }

  .governance-status {
    text-align: center;
    margin-top: 1rem;
  }

  .tab-navigation .nav {
    flex-direction: column;
  }

  .tab-navigation .nav-link {
    margin: 0.25rem 0;
  }
}
</style>