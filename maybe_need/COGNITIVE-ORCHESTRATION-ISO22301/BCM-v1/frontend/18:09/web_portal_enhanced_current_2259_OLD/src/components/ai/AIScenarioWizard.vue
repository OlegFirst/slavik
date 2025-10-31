<template>
  <div class="ai-scenario-wizard">
    <!-- Wizard Header -->
    <div class="wizard-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h2 class="wizard-title">
              <i class="fas fa-magic me-2"></i>
              AI Scenario Generation Wizard
            </h2>
            <p class="wizard-subtitle">
              Create customized BCM scenarios powered by artificial intelligence
            </p>
          </div>
          <div class="col-md-4 text-end">
            <div class="wizard-progress">
              <span class="step-indicator">Step {{ currentStep }} of 3</span>
              <div class="progress-bar-container">
                <div
                  class="progress-bar"
                  :style="{ width: `${(currentStep / 3) * 100}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step Navigation Breadcrumb -->
    <div class="step-navigation">
      <div class="container-fluid">
        <nav aria-label="Wizard steps">
          <ol class="breadcrumb">
            <li
              class="breadcrumb-item"
              :class="{
                active: currentStep === 1,
                completed: currentStep > 1
              }"
            >
              <i class="fas fa-cog me-1"></i>
              Parameters
            </li>
            <li
              class="breadcrumb-item"
              :class="{
                active: currentStep === 2,
                completed: currentStep > 2
              }"
            >
              <i class="fas fa-building me-1"></i>
              Context
            </li>
            <li
              class="breadcrumb-item"
              :class="{ active: currentStep === 3 }"
            >
              <i class="fas fa-magic me-1"></i>
              Generation
            </li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Wizard Content -->
    <div class="wizard-content">
      <div class="container-fluid">
        <!-- Step 1: Basic Parameters -->
        <div v-if="currentStep === 1" class="wizard-step" id="step-1">
          <div class="row">
            <div class="col-md-8">
              <div class="step-card">
                <div class="step-header">
                  <h3>
                    <i class="fas fa-sliders-h me-2 text-primary"></i>
                    Basic Scenario Parameters
                  </h3>
                  <p>Define the fundamental characteristics of your scenario</p>
                </div>

                <div class="step-body">
                  <div class="row">
                    <!-- Scenario Category -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label required">Scenario Category</label>
                      <select
                        v-model="scenarioParams.category"
                        class="form-select"
                        :class="{ 'is-invalid': errors.category }"
                      >
                        <option value="">Select a category...</option>
                        <option
                          v-for="category in categories"
                          :key="category.id"
                          :value="category.id"
                        >
                          {{ category.icon }} {{ category.name }}
                        </option>
                      </select>
                      <div v-if="errors.category" class="invalid-feedback">
                        {{ errors.category }}
                      </div>
                    </div>

                    <!-- Scenario Type -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label required">Scenario Type</label>
                      <select
                        v-model="scenarioParams.scenario_type"
                        class="form-select"
                        :class="{ 'is-invalid': errors.scenario_type }"
                      >
                        <option value="tabletop">📋 Tabletop Exercise</option>
                        <option value="functional">⚡ Functional Exercise</option>
                        <option value="full_scale">🎯 Full-Scale Exercise</option>
                        <option value="simulation">🎮 Digital Simulation</option>
                      </select>
                      <div v-if="errors.scenario_type" class="invalid-feedback">
                        {{ errors.scenario_type }}
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <!-- Complexity Level -->
                    <div class="col-md-12 mb-4">
                      <label class="form-label required">Complexity Level</label>
                      <div class="complexity-slider">
                        <input
                          type="range"
                          v-model="scenarioParams.complexity"
                          min="1"
                          max="5"
                          class="form-range"
                          :class="{ 'is-invalid': errors.complexity }"
                        >
                        <div class="complexity-labels">
                          <span :class="{ active: scenarioParams.complexity == 1 }">
                            1 - Basic
                          </span>
                          <span :class="{ active: scenarioParams.complexity == 2 }">
                            2 - Simple
                          </span>
                          <span :class="{ active: scenarioParams.complexity == 3 }">
                            3 - Intermediate
                          </span>
                          <span :class="{ active: scenarioParams.complexity == 4 }">
                            4 - Advanced
                          </span>
                          <span :class="{ active: scenarioParams.complexity == 5 }">
                            5 - Expert
                          </span>
                        </div>
                      </div>
                      <div v-if="errors.complexity" class="invalid-feedback d-block">
                        {{ errors.complexity }}
                      </div>
                    </div>
                  </div>

                  <div class="row">
                    <!-- Duration -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label required">Duration (hours)</label>
                      <input
                        type="number"
                        v-model.number="scenarioParams.duration_hours"
                        min="0.5"
                        max="72"
                        step="0.5"
                        class="form-control"
                        :class="{ 'is-invalid': errors.duration_hours }"
                        placeholder="e.g., 4"
                      >
                      <div class="form-text">
                        Recommended: 2-8 hours for tabletop, 8-24 hours for functional
                      </div>
                      <div v-if="errors.duration_hours" class="invalid-feedback">
                        {{ errors.duration_hours }}
                      </div>
                    </div>

                    <!-- Participants -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label required">Number of Participants</label>
                      <input
                        type="number"
                        v-model.number="scenarioParams.participants"
                        min="3"
                        max="200"
                        class="form-control"
                        :class="{ 'is-invalid': errors.participants }"
                        placeholder="e.g., 12"
                      >
                      <div class="form-text">
                        Optimal range: 6-20 participants for most scenarios
                      </div>
                      <div v-if="errors.participants" class="invalid-feedback">
                        {{ errors.participants }}
                      </div>
                    </div>
                  </div>

                  <!-- Language Selection -->
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Scenario Language</label>
                      <select v-model="scenarioParams.language" class="form-select">
                        <option value="en">🇺🇸 English</option>
                        <option value="ru">🇷🇺 Russian</option>
                        <option value="es">🇪🇸 Spanish</option>
                        <option value="fr">🇫🇷 French</option>
                        <option value="de">🇩🇪 German</option>
                        <option value="zh">🇨🇳 Chinese</option>
                      </select>
                    </div>

                    <!-- Template Selection -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Base Template (Optional)</label>
                      <select v-model="scenarioParams.template_id" class="form-select">
                        <option value="">Generate from scratch</option>
                        <option
                          v-for="template in templates"
                          :key="template.id"
                          :value="template.id"
                        >
                          {{ template.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Sidebar - Preview and Tips -->
            <div class="col-md-4">
              <div class="sidebar-card">
                <h5>
                  <i class="fas fa-lightbulb me-2 text-warning"></i>
                  Tips & Recommendations
                </h5>
                <div class="tips-content">
                  <div class="tip-item">
                    <i class="fas fa-info-circle text-info"></i>
                    <span>Choose complexity based on your team's BCM experience</span>
                  </div>
                  <div class="tip-item">
                    <i class="fas fa-clock text-warning"></i>
                    <span>Tabletop exercises typically run 2-4 hours</span>
                  </div>
                  <div class="tip-item">
                    <i class="fas fa-users text-success"></i>
                    <span>Include representatives from all key business areas</span>
                  </div>
                </div>
              </div>

              <!-- Quick Preview -->
              <div class="sidebar-card mt-3">
                <h5>
                  <i class="fas fa-eye me-2 text-primary"></i>
                  Quick Preview
                </h5>
                <div class="preview-content">
                  <div class="preview-item">
                    <strong>Category:</strong>
                    <span v-if="scenarioParams.category">
                      {{ getCategoryName(scenarioParams.category) }}
                    </span>
                    <span v-else class="text-muted">Not selected</span>
                  </div>
                  <div class="preview-item">
                    <strong>Complexity:</strong>
                    <span class="complexity-badge" :class="`level-${scenarioParams.complexity}`">
                      Level {{ scenarioParams.complexity }}
                    </span>
                  </div>
                  <div class="preview-item">
                    <strong>Duration:</strong>
                    <span>{{ scenarioParams.duration_hours || 0 }} hours</span>
                  </div>
                  <div class="preview-item">
                    <strong>Participants:</strong>
                    <span>{{ scenarioParams.participants || 0 }} people</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Organization Context -->
        <div v-if="currentStep === 2" class="wizard-step" id="step-2">
          <div class="row">
            <div class="col-md-8">
              <div class="step-card">
                <div class="step-header">
                  <h3>
                    <i class="fas fa-building me-2 text-success"></i>
                    Organization Context
                  </h3>
                  <p>Customize the scenario for your specific organizational environment</p>
                </div>

                <div class="step-body">
                  <!-- Organization Type -->
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label required">Industry Type</label>
                      <select
                        v-model="scenarioParams.organization_context"
                        class="form-select"
                        :class="{ 'is-invalid': errors.organization_context }"
                        @change="loadSystemsForIndustry"
                      >
                        <option value="">Select industry...</option>
                        <option
                          v-for="industry in industries"
                          :key="industry.id"
                          :value="industry.id"
                        >
                          {{ industry.icon }} {{ industry.name }}
                        </option>
                      </select>
                      <div v-if="errors.organization_context" class="invalid-feedback">
                        {{ errors.organization_context }}
                      </div>
                    </div>

                    <!-- Organization Size -->
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Organization Size</label>
                      <select v-model="scenarioParams.organization_size" class="form-select">
                        <option value="small">🏢 Small (< 100 employees)</option>
                        <option value="medium">🏬 Medium (100-1000 employees)</option>
                        <option value="large">🏭 Large (1000-10000 employees)</option>
                        <option value="enterprise">🏗️ Enterprise (> 10000 employees)</option>
                      </select>
                    </div>
                  </div>

                  <!-- Affected Systems -->
                  <div class="mb-4">
                    <label class="form-label">Critical Systems Affected</label>
                    <p class="form-text mb-3">
                      Select the systems that will be impacted in your scenario
                    </p>

                    <div class="systems-grid" v-if="availableSystems.length > 0">
                      <div
                        v-for="system in availableSystems"
                        :key="system"
                        class="system-card"
                        :class="{ selected: scenarioParams.affected_systems.includes(system) }"
                        @click="toggleSystem(system)"
                      >
                        <div class="system-icon">
                          <i class="fas fa-server"></i>
                        </div>
                        <div class="system-name">{{ system }}</div>
                        <div class="system-check">
                          <i class="fas fa-check" v-if="scenarioParams.affected_systems.includes(system)"></i>
                        </div>
                      </div>
                    </div>

                    <div v-else class="text-center py-4">
                      <div class="spinner-border text-primary mb-2" role="status"></div>
                      <p class="text-muted">Loading systems for selected industry...</p>
                    </div>
                  </div>

                  <!-- Custom Objectives -->
                  <div class="mb-4">
                    <label class="form-label">Custom Learning Objectives</label>
                    <p class="form-text mb-3">
                      Define specific goals and outcomes for your scenario
                    </p>

                    <div class="objectives-manager">
                      <div
                        v-for="(objective, index) in scenarioParams.custom_objectives"
                        :key="index"
                        class="objective-item"
                      >
                        <div class="objective-input">
                          <input
                            type="text"
                            v-model="scenarioParams.custom_objectives[index]"
                            class="form-control"
                            :placeholder="`Learning objective ${index + 1}...`"
                          >
                        </div>
                        <div class="objective-actions">
                          <button
                            @click="removeObjective(index)"
                            class="btn btn-sm btn-outline-danger"
                            type="button"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>

                      <button
                        @click="addObjective"
                        class="btn btn-sm btn-outline-primary"
                        type="button"
                      >
                        <i class="fas fa-plus me-1"></i>
                        Add Learning Objective
                      </button>
                    </div>
                  </div>

                  <!-- Compliance Requirements -->
                  <div class="mb-3">
                    <label class="form-label">Compliance Standards</label>
                    <p class="form-text mb-3">
                      Select relevant compliance frameworks to incorporate
                    </p>

                    <div class="compliance-grid">
                      <div
                        v-for="standard in complianceStandards"
                        :key="standard.id"
                        class="compliance-card"
                        :class="{ selected: scenarioParams.compliance_requirements.includes(standard.id) }"
                        @click="toggleCompliance(standard.id)"
                      >
                        <div class="compliance-name">{{ standard.name }}</div>
                        <div class="compliance-description">{{ standard.description }}</div>
                        <div class="compliance-check">
                          <i class="fas fa-check" v-if="scenarioParams.compliance_requirements.includes(standard.id)"></i>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Right Sidebar - Context Preview -->
            <div class="col-md-4">
              <div class="sidebar-card">
                <h5>
                  <i class="fas fa-chart-pie me-2 text-info"></i>
                  Context Summary
                </h5>
                <div class="context-summary">
                  <div class="summary-item">
                    <strong>Industry:</strong>
                    <span v-if="scenarioParams.organization_context">
                      {{ getIndustryName(scenarioParams.organization_context) }}
                    </span>
                    <span v-else class="text-muted">Not selected</span>
                  </div>
                  <div class="summary-item">
                    <strong>Systems:</strong>
                    <span v-if="scenarioParams.affected_systems.length > 0">
                      {{ scenarioParams.affected_systems.length }} selected
                    </span>
                    <span v-else class="text-muted">None selected</span>
                  </div>
                  <div class="summary-item">
                    <strong>Objectives:</strong>
                    <span v-if="validObjectives.length > 0">
                      {{ validObjectives.length }} defined
                    </span>
                    <span v-else class="text-muted">None defined</span>
                  </div>
                  <div class="summary-item">
                    <strong>Compliance:</strong>
                    <span v-if="scenarioParams.compliance_requirements.length > 0">
                      {{ scenarioParams.compliance_requirements.length }} standards
                    </span>
                    <span v-else class="text-muted">None selected</span>
                  </div>
                </div>
              </div>

              <!-- Advanced Options -->
              <div class="sidebar-card mt-3">
                <h5>
                  <i class="fas fa-cogs me-2 text-secondary"></i>
                  Advanced Options
                </h5>
                <div class="advanced-options">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="include_jaamsim"
                      v-model="scenarioParams.include_jaamsim"
                    >
                    <label class="form-check-label" for="include_jaamsim">
                      Include JaamSim Configuration
                    </label>
                  </div>
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="include_bpmn"
                      v-model="scenarioParams.include_bpmn"
                    >
                    <label class="form-check-label" for="include_bpmn">
                      Generate BPMN Workflow
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: AI Generation & Preview -->
        <div v-if="currentStep === 3" class="wizard-step" id="step-3">
          <div class="row">
            <div class="col-md-12">
              <!-- Generation in Progress -->
              <div v-if="isGenerating" class="generation-progress">
                <div class="progress-container">
                  <div class="ai-animation">
                    <div class="brain-container">
                      <div class="brain-icon">🧠</div>
                      <div class="thinking-particles">
                        <span class="particle"></span>
                        <span class="particle"></span>
                        <span class="particle"></span>
                        <span class="particle"></span>
                        <span class="particle"></span>
                      </div>
                    </div>
                  </div>

                  <div class="progress-content">
                    <h3 class="generation-title">AI is crafting your scenario...</h3>
                    <p class="generation-status">{{ generationStatus }}</p>

                    <div class="progress-bar-container">
                      <div
                        class="progress-bar animated"
                        :style="{ width: `${generationProgress}%` }"
                      ></div>
                    </div>

                    <div class="progress-details">
                      <span class="progress-percent">{{ generationProgress }}%</span>
                      <span class="progress-eta" v-if="estimatedTime">
                        ETA: {{ estimatedTime }}
                      </span>
                    </div>
                  </div>

                  <!-- Real-time Generation Steps -->
                  <div class="generation-steps">
                    <div
                      v-for="step in generationSteps"
                      :key="step.id"
                      class="generation-step"
                      :class="{
                        active: step.status === 'active',
                        completed: step.status === 'completed',
                        pending: step.status === 'pending'
                      }"
                    >
                      <div class="step-icon">
                        <i v-if="step.status === 'completed'" class="fas fa-check"></i>
                        <i v-else-if="step.status === 'active'" class="fas fa-spinner fa-spin"></i>
                        <i v-else class="fas fa-circle"></i>
                      </div>
                      <div class="step-content">
                        <div class="step-name">{{ step.name }}</div>
                        <div class="step-description">{{ step.description }}</div>
                      </div>
                    </div>
                  </div>

                  <!-- Cancel Button -->
                  <div class="generation-actions">
                    <button
                      @click="cancelGeneration"
                      class="btn btn-outline-danger"
                      :disabled="cancelling"
                    >
                      <i class="fas fa-times me-1"></i>
                      {{ cancelling ? 'Cancelling...' : 'Cancel Generation' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Generation Complete -->
              <div v-else-if="generatedScenario" class="generation-complete">
                <div class="completion-header">
                  <div class="success-animation">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <h3>Scenario Generated Successfully!</h3>
                  <p>Your AI-powered BCM scenario is ready for review and implementation.</p>
                </div>

                <!-- Scenario Preview -->
                <div class="scenario-preview">
                  <div class="row">
                    <div class="col-md-8">
                      <!-- Scenario Content -->
                      <div class="preview-card">
                        <div class="preview-header">
                          <h4>
                            <i class="fas fa-file-alt me-2"></i>
                            {{ generatedScenario.title }}
                          </h4>
                          <div class="scenario-meta">
                            <span class="badge badge-primary">
                              {{ getCategoryName(generatedScenario.category) }}
                            </span>
                            <span class="badge badge-info">
                              Level {{ generatedScenario.complexity }}
                            </span>
                            <span class="badge badge-warning">
                              {{ generatedScenario.duration_hours }}h
                            </span>
                            <span class="badge badge-success">
                              {{ generatedScenario.participants }} participants
                            </span>
                          </div>
                        </div>

                        <div class="preview-content">
                          <div class="scenario-section">
                            <h5>Executive Summary</h5>
                            <div class="content-block" v-html="formatContent(generatedScenario.executive_summary)"></div>
                          </div>

                          <div class="scenario-section" v-if="generatedScenario.scenario_description">
                            <h5>Scenario Description</h5>
                            <div class="content-block" v-html="formatContent(generatedScenario.scenario_description)"></div>
                          </div>

                          <div class="scenario-section" v-if="generatedScenario.learning_objectives">
                            <h5>Learning Objectives</h5>
                            <ul class="objectives-list">
                              <li v-for="objective in generatedScenario.learning_objectives" :key="objective">
                                {{ objective }}
                              </li>
                            </ul>
                          </div>

                          <div class="scenario-section" v-if="generatedScenario.timeline">
                            <h5>Exercise Timeline</h5>
                            <div class="timeline">
                              <div
                                v-for="event in generatedScenario.timeline"
                                :key="event.time"
                                class="timeline-event"
                              >
                                <div class="event-time">{{ event.time }}</div>
                                <div class="event-content">{{ event.event }}</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Technical Components -->
                      <div v-if="generatedScenario.jaamsim_config || generatedScenario.bpmn_workflow" class="technical-components">
                        <div class="row">
                          <div class="col-md-6" v-if="generatedScenario.jaamsim_config">
                            <div class="component-card">
                              <h5>
                                <i class="fas fa-play-circle me-2 text-primary"></i>
                                JaamSim Configuration
                              </h5>
                              <pre class="code-block">{{ generatedScenario.jaamsim_config }}</pre>
                              <button class="btn btn-sm btn-outline-primary" @click="downloadJaamSim">
                                <i class="fas fa-download me-1"></i>
                                Download Config
                              </button>
                            </div>
                          </div>

                          <div class="col-md-6" v-if="generatedScenario.bpmn_workflow">
                            <div class="component-card">
                              <h5>
                                <i class="fas fa-project-diagram me-2 text-success"></i>
                                BPMN Workflow
                              </h5>
                              <div class="bpmn-preview">
                                <!-- BPMN diagram would be rendered here -->
                                <p class="text-muted">BPMN diagram preview</p>
                              </div>
                              <button class="btn btn-sm btn-outline-success" @click="downloadBPMN">
                                <i class="fas fa-download me-1"></i>
                                Download BPMN
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Sidebar - Actions and Metadata -->
                    <div class="col-md-4">
                      <div class="actions-card">
                        <h5>
                          <i class="fas fa-cog me-2"></i>
                          Actions
                        </h5>
                        <div class="d-grid gap-2">
                          <button
                            @click="showSaveModal = true"
                            class="btn btn-success"
                          >
                            <i class="fas fa-save me-1"></i>
                            Save Scenario
                          </button>
                          <button
                            @click="customizeScenario"
                            class="btn btn-outline-primary"
                          >
                            <i class="fas fa-edit me-1"></i>
                            Customize
                          </button>
                          <button
                            @click="shareScenario"
                            class="btn btn-outline-info"
                          >
                            <i class="fas fa-share me-1"></i>
                            Share
                          </button>
                          <button
                            @click="exportScenario"
                            class="btn btn-outline-secondary"
                          >
                            <i class="fas fa-file-export me-1"></i>
                            Export
                          </button>
                        </div>
                      </div>

                      <!-- Generation Metadata -->
                      <div class="metadata-card mt-3">
                        <h5>
                          <i class="fas fa-info-circle me-2"></i>
                          Generation Details
                        </h5>
                        <div class="metadata-content">
                          <div class="metadata-item">
                            <strong>Generated:</strong>
                            <span>{{ formatDateTime(generatedScenario.created_at) }}</span>
                          </div>
                          <div class="metadata-item">
                            <strong>AI Model:</strong>
                            <span>{{ generatedScenario.ai_model || 'GPT-4' }}</span>
                          </div>
                          <div class="metadata-item">
                            <strong>Generation ID:</strong>
                            <span class="font-monospace">{{ generatedScenario.generation_id?.slice(0, 8) }}...</span>
                          </div>
                          <div class="metadata-item">
                            <strong>Quality Score:</strong>
                            <div class="quality-score">
                              <div class="score-bar">
                                <div
                                  class="score-fill"
                                  :style="{ width: `${generatedScenario.quality_score || 85}%` }"
                                ></div>
                              </div>
                              <span>{{ generatedScenario.quality_score || 85 }}%</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- AI Suggestions -->
                      <div class="suggestions-card mt-3" v-if="aiSuggestions.length > 0">
                        <h5>
                          <i class="fas fa-lightbulb me-2 text-warning"></i>
                          AI Suggestions
                        </h5>
                        <div class="suggestions-content">
                          <div
                            v-for="suggestion in aiSuggestions"
                            :key="suggestion.id"
                            class="suggestion-item"
                          >
                            <div class="suggestion-text">{{ suggestion.text }}</div>
                            <button
                              v-if="suggestion.actionable"
                              @click="applySuggestion(suggestion)"
                              class="btn btn-sm btn-outline-primary"
                            >
                              Apply
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Generation Error -->
              <div v-else-if="generationError" class="generation-error">
                <div class="error-container">
                  <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                  </div>
                  <h3>Generation Failed</h3>
                  <p class="error-message">{{ generationError }}</p>
                  <div class="error-actions">
                    <button @click="retryGeneration" class="btn btn-primary">
                      <i class="fas fa-retry me-1"></i>
                      Retry Generation
                    </button>
                    <button @click="goToStep(2)" class="btn btn-outline-secondary">
                      <i class="fas fa-arrow-left me-1"></i>
                      Modify Parameters
                    </button>
                  </div>
                </div>
              </div>

              <!-- Initial State -->
              <div v-else class="generation-initial">
                <div class="initial-container">
                  <div class="initial-icon">
                    <i class="fas fa-magic"></i>
                  </div>
                  <h3>Ready to Generate</h3>
                  <p>Review your parameters and start the AI scenario generation process.</p>

                  <!-- Parameter Summary -->
                  <div class="parameters-summary">
                    <div class="row">
                      <div class="col-md-6">
                        <div class="summary-card">
                          <h6>Basic Parameters</h6>
                          <ul>
                            <li>Category: {{ getCategoryName(scenarioParams.category) }}</li>
                            <li>Type: {{ scenarioParams.scenario_type }}</li>
                            <li>Complexity: Level {{ scenarioParams.complexity }}</li>
                            <li>Duration: {{ scenarioParams.duration_hours }} hours</li>
                            <li>Participants: {{ scenarioParams.participants }}</li>
                          </ul>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="summary-card">
                          <h6>Context</h6>
                          <ul>
                            <li>Industry: {{ getIndustryName(scenarioParams.organization_context) }}</li>
                            <li>Systems: {{ scenarioParams.affected_systems.length }} selected</li>
                            <li>Objectives: {{ validObjectives.length }} defined</li>
                            <li>Compliance: {{ scenarioParams.compliance_requirements.length }} standards</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="initial-actions">
                    <button
                      @click="startGeneration"
                      class="btn btn-primary btn-lg"
                      :disabled="!canStartGeneration"
                    >
                      <i class="fas fa-magic me-2"></i>
                      Start AI Generation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Wizard Navigation -->
    <div class="wizard-navigation">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-6">
            <button
              v-if="currentStep > 1"
              @click="previousStep"
              class="btn btn-outline-secondary"
              :disabled="isGenerating"
            >
              <i class="fas fa-arrow-left me-1"></i>
              Previous
            </button>
          </div>
          <div class="col-md-6 text-end">
            <button
              v-if="currentStep < 3"
              @click="nextStep"
              class="btn btn-primary"
              :disabled="!canProceed"
            >
              Next
              <i class="fas fa-arrow-right ms-1"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Save Scenario Modal -->
    <div v-if="showSaveModal" class="modal-overlay" @click="showSaveModal = false">
      <div class="modal-dialog" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Save Scenario</h5>
            <button @click="showSaveModal = false" class="btn-close"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Scenario Title</label>
              <input
                v-model="saveForm.title"
                type="text"
                class="form-control"
                :placeholder="generatedScenario?.title"
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea
                v-model="saveForm.description"
                class="form-control"
                rows="3"
                :placeholder="generatedScenario?.executive_summary"
              ></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Tags</label>
              <input
                v-model="saveForm.tags"
                type="text"
                class="form-control"
                placeholder="Enter tags separated by commas"
              >
            </div>
            <div class="form-check">
              <input
                v-model="saveForm.is_public"
                class="form-check-input"
                type="checkbox"
                id="is_public"
              >
              <label class="form-check-label" for="is_public">
                Make this scenario public in the scenario hub
              </label>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showSaveModal = false" class="btn btn-secondary">
              Cancel
            </button>
            <button @click="saveScenario" class="btn btn-success" :disabled="saving">
              <i class="fas fa-save me-1"></i>
              {{ saving ? 'Saving...' : 'Save Scenario' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import scenarioOrchestratorService from '@/services/scenarioOrchestrator'
import { useToast } from 'vue-toastification'

export default {
  name: 'AIScenarioWizard',
  emits: ['scenario-generated', 'wizard-closed'],
  setup(props, { emit }) {
    const toast = useToast()

    // Reactive state
    const currentStep = ref(1)
    const isGenerating = ref(false)
    const cancelling = ref(false)
    const generationProgress = ref(0)
    const generationStatus = ref('')
    const estimatedTime = ref('')
    const generatedScenario = ref(null)
    const generationError = ref('')
    const showSaveModal = ref(false)
    const saving = ref(false)

    // Form data
    const scenarioParams = reactive({
      category: '',
      scenario_type: 'tabletop',
      complexity: 3,
      duration_hours: 4,
      participants: 12,
      language: 'en',
      template_id: '',
      organization_context: '',
      organization_size: 'medium',
      affected_systems: [],
      custom_objectives: [],
      compliance_requirements: [],
      include_jaamsim: false,
      include_bpmn: false
    })

    // Save form
    const saveForm = reactive({
      title: '',
      description: '',
      tags: '',
      is_public: false
    })

    // Validation errors
    const errors = reactive({})

    // Data arrays
    const categories = ref([])
    const industries = ref([])
    const templates = ref([])
    const availableSystems = ref([])
    const complianceStandards = ref([
      {
        id: 'iso22301',
        name: 'ISO 22301',
        description: 'Business Continuity Management'
      },
      {
        id: 'iso27001',
        name: 'ISO 27001',
        description: 'Information Security Management'
      },
      {
        id: 'nist',
        name: 'NIST Framework',
        description: 'Cybersecurity Framework'
      },
      {
        id: 'sox',
        name: 'SOX',
        description: 'Sarbanes-Oxley Act'
      },
      {
        id: 'gdpr',
        name: 'GDPR',
        description: 'General Data Protection Regulation'
      },
      {
        id: 'hipaa',
        name: 'HIPAA',
        description: 'Health Insurance Portability'
      }
    ])

    // Generation tracking
    const generationId = ref('')
    const scenarioId = ref('')
    const progressListener = ref(null)
    const aiSuggestions = ref([])

    // Generation steps for real-time display
    const generationSteps = ref([
      {
        id: 1,
        name: 'Analyzing Parameters',
        description: 'Processing scenario requirements',
        status: 'pending'
      },
      {
        id: 2,
        name: 'Building Context',
        description: 'Creating organizational scenario',
        status: 'pending'
      },
      {
        id: 3,
        name: 'Generating Content',
        description: 'AI crafting scenario content',
        status: 'pending'
      },
      {
        id: 4,
        name: 'Creating Timeline',
        description: 'Building exercise timeline',
        status: 'pending'
      },
      {
        id: 5,
        name: 'Final Review',
        description: 'Quality assurance check',
        status: 'pending'
      }
    ])

    // Computed properties
    const canProceed = computed(() => {
      if (currentStep.value === 1) {
        return validateStep1()
      } else if (currentStep.value === 2) {
        return validateStep2()
      }
      return true
    })

    const canStartGeneration = computed(() => {
      return validateStep1() && validateStep2()
    })

    const validObjectives = computed(() => {
      return scenarioParams.custom_objectives.filter(obj => obj && obj.trim())
    })

    // Validation methods
    const validateStep1 = () => {
      clearErrors()
      let isValid = true

      if (!scenarioParams.category) {
        errors.category = 'Please select a scenario category'
        isValid = false
      }

      if (!scenarioParams.scenario_type) {
        errors.scenario_type = 'Please select a scenario type'
        isValid = false
      }

      if (!scenarioParams.duration_hours || scenarioParams.duration_hours < 0.5) {
        errors.duration_hours = 'Please enter a valid duration (minimum 0.5 hours)'
        isValid = false
      }

      if (!scenarioParams.participants || scenarioParams.participants < 3) {
        errors.participants = 'Please enter a valid number of participants (minimum 3)'
        isValid = false
      }

      return isValid
    }

    const validateStep2 = () => {
      clearErrors()
      let isValid = true

      if (!scenarioParams.organization_context) {
        errors.organization_context = 'Please select an industry type'
        isValid = false
      }

      return isValid
    }

    const clearErrors = () => {
      Object.keys(errors).forEach(key => {
        delete errors[key]
      })
    }

    // Navigation methods
    const nextStep = () => {
      if (canProceed.value && currentStep.value < 3) {
        currentStep.value++
      }
    }

    const previousStep = () => {
      if (currentStep.value > 1 && !isGenerating.value) {
        currentStep.value--
      }
    }

    const goToStep = (step) => {
      if (step >= 1 && step <= 3 && !isGenerating.value) {
        currentStep.value = step
      }
    }

    // Data loading methods
    const loadInitialData = async () => {
      try {
        const [categoriesData, industriesData, templatesData] = await Promise.all([
          scenarioOrchestratorService.getCategories(),
          scenarioOrchestratorService.getIndustryTypes(),
          scenarioOrchestratorService.getTemplates({ limit: 20 })
        ])

        categories.value = categoriesData
        industries.value = industriesData
        templates.value = templatesData
      } catch (error) {
        console.error('Error loading initial data:', error)
        toast.error('Failed to load wizard data. Please refresh and try again.')
      }
    }

    const loadSystemsForIndustry = async () => {
      if (!scenarioParams.organization_context) return

      try {
        availableSystems.value = []
        const systems = await scenarioOrchestratorService.getAvailableSystems(
          scenarioParams.organization_context
        )
        availableSystems.value = systems
        // Clear previously selected systems when industry changes
        scenarioParams.affected_systems = []
      } catch (error) {
        console.error('Error loading systems:', error)
        toast.error('Failed to load systems for selected industry')
      }
    }

    // System and compliance selection
    const toggleSystem = (system) => {
      const index = scenarioParams.affected_systems.indexOf(system)
      if (index > -1) {
        scenarioParams.affected_systems.splice(index, 1)
      } else {
        scenarioParams.affected_systems.push(system)
      }
    }

    const toggleCompliance = (standardId) => {
      const index = scenarioParams.compliance_requirements.indexOf(standardId)
      if (index > -1) {
        scenarioParams.compliance_requirements.splice(index, 1)
      } else {
        scenarioParams.compliance_requirements.push(standardId)
      }
    }

    // Learning objectives management
    const addObjective = () => {
      scenarioParams.custom_objectives.push('')
    }

    const removeObjective = (index) => {
      scenarioParams.custom_objectives.splice(index, 1)
    }

    // AI Generation methods
    const startGeneration = async () => {
      if (!canStartGeneration.value) {
        toast.error('Please complete all required fields before generating')
        return
      }

      try {
        isGenerating.value = true
        generationError.value = ''
        generationProgress.value = 0
        generationStatus.value = 'Initializing AI generation...'

        // Reset generation steps
        generationSteps.value.forEach(step => {
          step.status = 'pending'
        })

        // Start generation
        const response = await scenarioOrchestratorService.generateScenario(scenarioParams)

        if (response.success) {
          generationId.value = response.generation_id
          scenarioId.value = response.scenario_id
          estimatedTime.value = response.estimated_time

          // Subscribe to real-time progress
          subscribeToProgress()

          // Start progress simulation (fallback if WebSocket fails)
          startProgressSimulation()
        } else {
          throw new Error(response.error || 'Generation failed')
        }
      } catch (error) {
        console.error('Error starting generation:', error)
        isGenerating.value = false
        generationError.value = error.message || 'Failed to start scenario generation'
        toast.error('Failed to start AI generation')
      }
    }

    const subscribeToProgress = () => {
      progressListener.value = (data) => {
        generationProgress.value = data.progress || 0
        generationStatus.value = data.status || 'Processing...'

        if (data.step) {
          updateGenerationStep(data.step, data.step_status)
        }

        if (data.estimated_time) {
          estimatedTime.value = data.estimated_time
        }

        if (data.completed) {
          handleGenerationComplete(data)
        }

        if (data.error) {
          handleGenerationError(data.error)
        }
      }

      scenarioOrchestratorService.websocket.subscribe(
        scenarioId.value,
        progressListener.value
      )
    }

    const startProgressSimulation = () => {
      // Fallback progress simulation if WebSocket doesn't work
      const progressInterval = setInterval(() => {
        if (!isGenerating.value) {
          clearInterval(progressInterval)
          return
        }

        if (generationProgress.value < 90) {
          generationProgress.value += Math.random() * 10

          // Update generation steps based on progress
          const stepIndex = Math.floor((generationProgress.value / 100) * generationSteps.value.length)
          for (let i = 0; i < stepIndex && i < generationSteps.value.length; i++) {
            if (generationSteps.value[i].status === 'pending') {
              generationSteps.value[i].status = i === stepIndex - 1 ? 'active' : 'completed'
            }
          }
        }
      }, 1000)

      // Check for completion every 5 seconds
      const completionInterval = setInterval(async () => {
        if (!isGenerating.value) {
          clearInterval(completionInterval)
          return
        }

        try {
          const status = await scenarioOrchestratorService.getGenerationStatus(generationId.value)
          if (status.completed) {
            clearInterval(progressInterval)
            clearInterval(completionInterval)

            const scenario = await scenarioOrchestratorService.getGeneratedScenario(scenarioId.value)
            handleGenerationComplete({ scenario })
          } else if (status.error) {
            clearInterval(progressInterval)
            clearInterval(completionInterval)
            handleGenerationError(status.error)
          }
        } catch (error) {
          console.error('Error checking generation status:', error)
        }
      }, 5000)
    }

    const updateGenerationStep = (stepId, status) => {
      const step = generationSteps.value.find(s => s.id === stepId)
      if (step) {
        step.status = status
      }
    }

    const handleGenerationComplete = (data) => {
      isGenerating.value = false
      generationProgress.value = 100
      generationStatus.value = 'Generation completed successfully!'

      // Mark all steps as completed
      generationSteps.value.forEach(step => {
        step.status = 'completed'
      })

      if (data.scenario) {
        generatedScenario.value = data.scenario

        // Pre-fill save form
        saveForm.title = data.scenario.title || ''
        saveForm.description = data.scenario.executive_summary || ''

        // Load AI suggestions if available
        if (data.scenario.ai_suggestions) {
          aiSuggestions.value = data.scenario.ai_suggestions
        }

        emit('scenario-generated', data.scenario)
        toast.success('Scenario generated successfully!')
      }

      // Cleanup WebSocket listener
      if (progressListener.value) {
        scenarioOrchestratorService.websocket.unsubscribe(
          scenarioId.value,
          progressListener.value
        )
      }
    }

    const handleGenerationError = (error) => {
      isGenerating.value = false
      generationError.value = error
      toast.error('Scenario generation failed')

      // Cleanup WebSocket listener
      if (progressListener.value) {
        scenarioOrchestratorService.websocket.unsubscribe(
          scenarioId.value,
          progressListener.value
        )
      }
    }

    const cancelGeneration = async () => {
      if (!generationId.value) return

      try {
        cancelling.value = true
        await scenarioOrchestratorService.cancelGeneration(generationId.value)

        isGenerating.value = false
        generationError.value = 'Generation cancelled by user'
        toast.info('Scenario generation cancelled')

        // Cleanup WebSocket listener
        if (progressListener.value) {
          scenarioOrchestratorService.websocket.unsubscribe(
            scenarioId.value,
            progressListener.value
          )
        }
      } catch (error) {
        console.error('Error cancelling generation:', error)
        toast.error('Failed to cancel generation')
      } finally {
        cancelling.value = false
      }
    }

    const retryGeneration = () => {
      generationError.value = ''
      generatedScenario.value = null
      startGeneration()
    }

    // Scenario actions
    const saveScenario = async () => {
      if (!generatedScenario.value) return

      try {
        saving.value = true

        const metadata = {
          title: saveForm.title || generatedScenario.value.title,
          description: saveForm.description || generatedScenario.value.executive_summary,
          tags: saveForm.tags ? saveForm.tags.split(',').map(t => t.trim()) : [],
          category: scenarioParams.category,
          is_public: saveForm.is_public
        }

        await scenarioOrchestratorService.saveScenario(scenarioId.value, metadata)

        showSaveModal.value = false
        toast.success('Scenario saved successfully!')

        emit('scenario-generated', {
          ...generatedScenario.value,
          ...metadata
        })
      } catch (error) {
        console.error('Error saving scenario:', error)
        toast.error('Failed to save scenario')
      } finally {
        saving.value = false
      }
    }

    const customizeScenario = () => {
      // Navigate back to step 2 to modify parameters
      currentStep.value = 2
      toast.info('Modify parameters and regenerate to customize your scenario')
    }

    const shareScenario = async () => {
      if (!generatedScenario.value) return

      const shareData = {
        title: generatedScenario.value.title,
        text: `Check out this AI-generated BCM scenario: ${generatedScenario.value.title}`,
        url: window.location.href
      }

      try {
        if (navigator.share) {
          await navigator.share(shareData)
        } else {
          await navigator.clipboard.writeText(shareData.url)
          toast.success('Scenario link copied to clipboard!')
        }
      } catch (error) {
        console.error('Error sharing scenario:', error)
        toast.error('Failed to share scenario')
      }
    }

    const exportScenario = () => {
      if (!generatedScenario.value) return

      const exportData = {
        scenario: generatedScenario.value,
        parameters: scenarioParams,
        generated_at: new Date().toISOString()
      }

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      })

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${generatedScenario.value.title || 'scenario'}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      toast.success('Scenario exported successfully!')
    }

    const downloadJaamSim = () => {
      if (!generatedScenario.value?.jaamsim_config) return

      const blob = new Blob([generatedScenario.value.jaamsim_config], {
        type: 'text/plain'
      })

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${generatedScenario.value.title || 'scenario'}.cfg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const downloadBPMN = () => {
      if (!generatedScenario.value?.bpmn_workflow) return

      const blob = new Blob([generatedScenario.value.bpmn_workflow], {
        type: 'application/xml'
      })

      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${generatedScenario.value.title || 'scenario'}.bpmn`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }

    const applySuggestion = (suggestion) => {
      // Apply AI suggestion logic here
      toast.info('AI suggestion applied!')
    }

    // Utility methods
    const getCategoryName = (categoryId) => {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? `${category.icon} ${category.name}` : categoryId
    }

    const getIndustryName = (industryId) => {
      const industry = industries.value.find(i => i.id === industryId)
      return industry ? `${industry.icon} ${industry.name}` : industryId
    }

    const formatContent = (content) => {
      if (!content) return ''
      // Convert markdown to HTML (basic conversion)
      return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>')
    }

    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString()
    }

    // Watchers
    watch(() => scenarioParams.organization_context, loadSystemsForIndustry)

    // Lifecycle
    onMounted(() => {
      loadInitialData()
    })

    onUnmounted(() => {
      // Cleanup WebSocket connections
      if (progressListener.value && scenarioId.value) {
        scenarioOrchestratorService.websocket.unsubscribe(
          scenarioId.value,
          progressListener.value
        )
      }
    })

    return {
      // State
      currentStep,
      isGenerating,
      cancelling,
      generationProgress,
      generationStatus,
      estimatedTime,
      generatedScenario,
      generationError,
      showSaveModal,
      saving,

      // Form data
      scenarioParams,
      saveForm,
      errors,

      // Data
      categories,
      industries,
      templates,
      availableSystems,
      complianceStandards,
      generationSteps,
      aiSuggestions,

      // Computed
      canProceed,
      canStartGeneration,
      validObjectives,

      // Methods
      nextStep,
      previousStep,
      goToStep,
      toggleSystem,
      toggleCompliance,
      addObjective,
      removeObjective,
      startGeneration,
      cancelGeneration,
      retryGeneration,
      saveScenario,
      customizeScenario,
      shareScenario,
      exportScenario,
      downloadJaamSim,
      downloadBPMN,
      applySuggestion,
      getCategoryName,
      getIndustryName,
      formatContent,
      formatDateTime
    }
  }
}
</script>

<style scoped>
/* AI Scenario Wizard Styles */
.ai-scenario-wizard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

/* Wizard Header */
.wizard-header {
  background: linear-gradient(135deg, #FF6B35 0%, #F5621C 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 1rem;
}

.wizard-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.wizard-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0;
}

.wizard-progress {
  text-align: right;
}

.step-indicator {
  font-size: 0.9rem;
  opacity: 0.8;
  display: block;
  margin-bottom: 0.5rem;
}

.progress-bar-container {
  width: 200px;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
  margin-left: auto;
}

.progress-bar {
  height: 100%;
  background: white;
  transition: width 0.3s ease;
  border-radius: 3px;
}

/* Step Navigation */
.step-navigation {
  background: white;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 2rem;
}

.breadcrumb {
  margin-bottom: 0;
  background: none;
  padding: 0;
}

.breadcrumb-item {
  font-weight: 500;
  color: #666;
}

.breadcrumb-item.active {
  color: #FF6B35;
  font-weight: 600;
}

.breadcrumb-item.completed {
  color: #4A90E2;
}

.breadcrumb-item.completed::before {
  content: "✓ ";
  color: #4A90E2;
  font-weight: bold;
}

/* Step Cards */
.step-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.step-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1A1A1A;
}

.step-header p {
  color: #666;
  margin-bottom: 2rem;
}

/* Form Styles */
.form-label.required::after {
  content: " *";
  color: #FF6B35;
}

.form-select, .form-control {
  border-radius: 8px;
  border: 2px solid #e9ecef;
  padding: 0.75rem;
  transition: all 0.2s;
}

.form-select:focus, .form-control:focus {
  border-color: #4A90E2;
  box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.1);
}

.form-select.is-invalid, .form-control.is-invalid {
  border-color: #dc3545;
}

/* Complexity Slider */
.complexity-slider {
  margin: 1rem 0;
}

.form-range {
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  outline: none;
}

.form-range::-webkit-slider-thumb {
  width: 20px;
  height: 20px;
  background: #FF6B35;
  border-radius: 50%;
  border: none;
  cursor: pointer;
}

.form-range::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: #FF6B35;
  border-radius: 50%;
  border: none;
  cursor: pointer;
}

.complexity-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.complexity-labels span.active {
  color: #FF6B35;
  font-weight: 600;
}

/* Systems Grid */
.systems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.system-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  position: relative;
}

.system-card:hover {
  border-color: #4A90E2;
  background: #f0f7ff;
}

.system-card.selected {
  border-color: #FF6B35;
  background: #fff5f0;
}

.system-icon {
  font-size: 1.5rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.system-card.selected .system-icon {
  color: #FF6B35;
}

.system-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1A1A1A;
}

.system-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  color: #FF6B35;
  font-size: 1rem;
}

/* Objectives Manager */
.objectives-manager {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  background: #f8f9fa;
}

.objective-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.objective-item:last-of-type {
  margin-bottom: 1rem;
}

.objective-input {
  flex: 1;
}

/* Compliance Grid */
.compliance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.compliance-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.compliance-card:hover {
  border-color: #4A90E2;
  background: #f0f7ff;
}

.compliance-card.selected {
  border-color: #FF6B35;
  background: #fff5f0;
}

.compliance-name {
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 0.25rem;
}

.compliance-description {
  font-size: 0.8rem;
  color: #666;
}

.compliance-check {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  color: #FF6B35;
  font-size: 1rem;
}

/* Sidebar Cards */
.sidebar-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.sidebar-card h5 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1A1A1A;
}

.tips-content {
  space-y: 1rem;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.tip-item:last-child {
  margin-bottom: 0;
}

.tip-item i {
  margin-top: 0.1rem;
  font-size: 0.8rem;
}

/* Preview Content */
.preview-content {
  space-y: 1rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item strong {
  color: #1A1A1A;
}

.complexity-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.complexity-badge.level-1, .complexity-badge.level-2 {
  background: #d4edda;
  color: #155724;
}

.complexity-badge.level-3 {
  background: #fff3cd;
  color: #856404;
}

.complexity-badge.level-4, .complexity-badge.level-5 {
  background: #f8d7da;
  color: #721c24;
}

/* Generation Progress */
.generation-progress {
  text-align: center;
  padding: 3rem 2rem;
}

.progress-container {
  max-width: 600px;
  margin: 0 auto;
}

.ai-animation {
  margin-bottom: 2rem;
}

.brain-container {
  position: relative;
  display: inline-block;
}

.brain-icon {
  font-size: 4rem;
  animation: pulse 2s infinite;
}

.thinking-particles {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
}

.particle {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #FF6B35;
  border-radius: 50%;
  margin: 0 2px;
  animation: float 1.5s infinite ease-in-out;
}

.particle:nth-child(2) {
  animation-delay: 0.2s;
}

.particle:nth-child(3) {
  animation-delay: 0.4s;
}

.particle:nth-child(4) {
  animation-delay: 0.6s;
}

.particle:nth-child(5) {
  animation-delay: 0.8s;
}

.generation-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
}

.generation-status {
  color: #666;
  margin-bottom: 2rem;
}

.progress-bar-container {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-bar.animated {
  background: linear-gradient(90deg, #FF6B35, #4A90E2, #FF6B35);
  background-size: 200% 100%;
  animation: shimmer 2s infinite;
  transition: width 0.5s ease;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 2rem;
}

/* Generation Steps */
.generation-steps {
  max-width: 400px;
  margin: 2rem auto 0;
  text-align: left;
}

.generation-step {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  transition: all 0.3s;
}

.generation-step.pending {
  background: #f8f9fa;
  opacity: 0.6;
}

.generation-step.active {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
}

.generation-step.completed {
  background: #d4edda;
  border: 1px solid #c3e6cb;
}

.step-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.8rem;
}

.generation-step.pending .step-icon {
  background: #e9ecef;
  color: #6c757d;
}

.generation-step.active .step-icon {
  background: #ffc107;
  color: white;
}

.generation-step.completed .step-icon {
  background: #28a745;
  color: white;
}

.step-content {
  flex: 1;
}

.step-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #1A1A1A;
}

.step-description {
  font-size: 0.8rem;
  color: #666;
}

/* Generation Complete */
.generation-complete {
  padding: 2rem;
}

.completion-header {
  text-align: center;
  margin-bottom: 3rem;
}

.success-animation {
  font-size: 4rem;
  color: #28a745;
  margin-bottom: 1rem;
  animation: bounceIn 0.8s ease;
}

.completion-header h3 {
  font-size: 2rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 0.5rem;
}

.completion-header p {
  color: #666;
  font-size: 1.1rem;
}

/* Scenario Preview */
.preview-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  margin-bottom: 2rem;
}

.preview-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.preview-header h4 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
}

.scenario-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-primary {
  background: #4A90E2;
  color: white;
}

.badge-info {
  background: #17a2b8;
  color: white;
}

.badge-warning {
  background: #ffc107;
  color: #212529;
}

.badge-success {
  background: #28a745;
  color: white;
}

.scenario-section {
  margin-bottom: 2rem;
}

.scenario-section h5 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
  border-left: 4px solid #FF6B35;
  padding-left: 1rem;
}

.content-block {
  line-height: 1.6;
  color: #333;
}

.objectives-list {
  padding-left: 1.5rem;
}

.objectives-list li {
  margin-bottom: 0.5rem;
  color: #333;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #4A90E2;
}

.timeline-event {
  position: relative;
  margin-bottom: 1.5rem;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1rem;
}

.timeline-event::before {
  content: '';
  position: absolute;
  left: -1.75rem;
  top: 1rem;
  width: 12px;
  height: 12px;
  background: #4A90E2;
  border-radius: 50%;
  border: 3px solid white;
}

.event-time {
  font-weight: 600;
  color: #FF6B35;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.event-content {
  color: #333;
  line-height: 1.4;
}

/* Technical Components */
.technical-components {
  margin-top: 2rem;
}

.component-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.component-card h5 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.code-block {
  background: #2d3748;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.8rem;
  line-height: 1.4;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.bpmn-preview {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 1rem;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Action Cards */
.actions-card, .metadata-card, .suggestions-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.actions-card h5, .metadata-card h5, .suggestions-card h5 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #1A1A1A;
}

.metadata-content {
  space-y: 1rem;
}

.metadata-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.metadata-item:last-child {
  margin-bottom: 0;
}

.metadata-item strong {
  color: #1A1A1A;
}

.quality-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  margin-left: 1rem;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #28a745, #ffc107);
  transition: width 0.3s ease;
}

/* AI Suggestions */
.suggestions-content {
  space-y: 1rem;
}

.suggestion-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.suggestion-item:last-child {
  margin-bottom: 0;
}

.suggestion-text {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.4;
  color: #333;
}

/* Generation Error */
.generation-error {
  text-align: center;
  padding: 3rem 2rem;
}

.error-container {
  max-width: 500px;
  margin: 0 auto;
}

.error-icon {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.generation-error h3 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
}

.error-message {
  color: #666;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

/* Generation Initial */
.generation-initial {
  text-align: center;
  padding: 3rem 2rem;
}

.initial-container {
  max-width: 800px;
  margin: 0 auto;
}

.initial-icon {
  font-size: 4rem;
  color: #4A90E2;
  margin-bottom: 1rem;
}

.generation-initial h3 {
  font-size: 1.8rem;
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
}

.generation-initial p {
  color: #666;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.parameters-summary {
  margin-bottom: 3rem;
}

.summary-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: left;
}

.summary-card h6 {
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
}

.summary-card ul {
  margin: 0;
  padding-left: 1.5rem;
}

.summary-card li {
  margin-bottom: 0.5rem;
  color: #333;
}

/* Wizard Navigation */
.wizard-navigation {
  background: white;
  border-top: 1px solid #eee;
  padding: 1.5rem 0;
  margin-top: 2rem;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

/* Modal */
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
}

.modal-dialog {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

/* Animations */
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes bounceIn {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

/* Responsive Design */
@media (max-width: 768px) {
  .wizard-header {
    padding: 1.5rem 0;
  }

  .wizard-title {
    font-size: 1.8rem;
  }

  .step-card {
    padding: 1.5rem;
  }

  .systems-grid, .compliance-grid {
    grid-template-columns: 1fr;
  }

  .error-actions, .initial-actions {
    flex-direction: column;
  }

  .preview-header .scenario-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal-dialog {
    width: 95%;
  }
}

@media (max-width: 480px) {
  .wizard-progress {
    text-align: left;
    margin-top: 1rem;
  }

  .progress-bar-container {
    width: 100%;
  }

  .step-navigation {
    padding: 0.5rem 0;
  }

  .breadcrumb {
    font-size: 0.8rem;
  }

  .generation-initial, .generation-progress, .generation-error {
    padding: 2rem 1rem;
  }
}
</style>