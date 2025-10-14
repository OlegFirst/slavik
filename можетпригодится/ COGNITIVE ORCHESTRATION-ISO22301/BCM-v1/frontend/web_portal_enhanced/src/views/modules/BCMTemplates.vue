<template>
  <div class="bcm-templates">
    <!-- Header Section -->
    <div class="header-section">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">BCM Templates & Documents</h1>
          <p class="page-subtitle">Manage business continuity templates, create documents, and ensure compliance</p>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="showAIAssistant = !showAIAssistant">
            <i class="icon-ai"></i>
            AI Assistant
          </button>
          <button class="btn btn-primary" @click="openCreateModal">
            <i class="icon-plus"></i>
            New Template
          </button>
          <button class="btn btn-outline" @click="openUploadModal">
            <i class="icon-upload"></i>
            Upload
          </button>
        </div>
      </div>
    </div>

    <!-- Dashboard Cards -->
    <div class="dashboard-cards">
      <div class="card stat-card">
        <div class="stat-icon bg-orange">
          <i class="icon-templates"></i>
        </div>
        <div class="stat-content">
          <h3>{{ totalTemplates }}</h3>
          <p>Total Templates</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon bg-blue">
          <i class="icon-documents"></i>
        </div>
        <div class="stat-content">
          <h3>{{ documentsGenerated }}</h3>
          <p>Documents Generated</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon bg-green">
          <i class="icon-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ approvedTemplates }}</h3>
          <p>Approved Templates</p>
        </div>
      </div>
      <div class="card stat-card">
        <div class="stat-icon bg-yellow">
          <i class="icon-pending"></i>
        </div>
        <div class="stat-content">
          <h3>{{ pendingApproval }}</h3>
          <p>Pending Approval</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-section">
          <h3>Categories</h3>
          <div class="category-list">
            <div
              v-for="category in categories"
              :key="category.id"
              class="category-item"
              :class="{ active: selectedCategory === category.id }"
              @click="selectCategory(category.id)"
            >
              <span class="category-icon">{{ category.icon }}</span>
              <span class="category-name">{{ category.name }}</span>
              <span class="category-count">({{ getCategoryCount(category.id) }})</span>
            </div>
          </div>
        </div>

        <div class="sidebar-section">
          <h3>Quick Actions</h3>
          <div class="quick-actions">
            <button class="quick-action-btn" @click="openFormBuilder">
              <i class="icon-form"></i>
              Form Builder
            </button>
            <button class="quick-action-btn" @click="openComplianceChecker">
              <i class="icon-shield"></i>
              Compliance Check
            </button>
            <button class="quick-action-btn" @click="openVersionManager">
              <i class="icon-versions"></i>
              Version Manager
            </button>
            <button class="quick-action-btn" @click="openPermissions">
              <i class="icon-users"></i>
              Permissions
            </button>
          </div>
        </div>

        <div class="sidebar-section">
          <h3>Recent Activity</h3>
          <div class="recent-activity">
            <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
              <div class="activity-icon" :class="`bg-${activity.type}`">
                <i :class="`icon-${activity.icon}`"></i>
              </div>
              <div class="activity-content">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Content Area -->
      <main class="content-area">
        <!-- Search and Filters -->
        <div class="search-filters">
          <div class="search-bar">
            <div class="search-input-wrapper">
              <i class="icon-search"></i>
              <input
                type="text"
                v-model="searchQuery"
                placeholder="Search templates, documents, or content..."
                @input="performSearch"
                class="search-input"
              />
              <button v-if="searchQuery" @click="clearSearch" class="clear-search">
                <i class="icon-close"></i>
              </button>
            </div>
          </div>

          <div class="filters">
            <select v-model="statusFilter" @change="applyFilters" class="filter-select">
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="review">Under Review</option>
              <option value="approved">Approved</option>
              <option value="archived">Archived</option>
            </select>

            <select v-model="sortBy" @change="applySorting" class="filter-select">
              <option value="name">Sort by Name</option>
              <option value="created_date">Created Date</option>
              <option value="last_modified">Last Modified</option>
              <option value="usage_count">Most Used</option>
            </select>

            <button class="btn btn-outline-small" @click="toggleViewMode">
              <i :class="viewMode === 'grid' ? 'icon-list' : 'icon-grid'"></i>
              {{ viewMode === 'grid' ? 'List' : 'Grid' }} View
            </button>
          </div>
        </div>

        <!-- AI Suggestions Banner -->
        <div v-if="aiSuggestions.length > 0" class="ai-suggestions-banner">
          <div class="suggestions-header">
            <i class="icon-ai"></i>
            <h4>AI Recommended Templates</h4>
            <button @click="dismissAISuggestions" class="dismiss-btn">
              <i class="icon-close"></i>
            </button>
          </div>
          <div class="suggestions-list">
            <div
              v-for="suggestion in aiSuggestions.slice(0, 3)"
              :key="suggestion.id"
              class="suggestion-item"
              @click="applySuggestion(suggestion)"
            >
              <div class="suggestion-content">
                <h5>{{ suggestion.title }}</h5>
                <p>{{ suggestion.description }}</p>
                <div class="suggestion-tags">
                  <span v-for="tag in suggestion.tags" :key="tag" class="tag">{{ tag }}</span>
                </div>
              </div>
              <button class="apply-suggestion-btn">Apply</button>
            </div>
          </div>
        </div>

        <!-- Templates Grid/List -->
        <div class="templates-container" :class="`view-${viewMode}`">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading templates...</p>
          </div>

          <div v-else-if="filteredTemplates.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="icon-templates"></i>
            </div>
            <h3>No templates found</h3>
            <p>{{ searchQuery ? 'Try adjusting your search criteria' : 'Create your first BCM template to get started' }}</p>
            <button class="btn btn-primary" @click="openCreateModal">
              <i class="icon-plus"></i>
              Create Template
            </button>
          </div>

          <div v-else class="templates-grid">
            <div
              v-for="template in paginatedTemplates"
              :key="template.id"
              class="template-card"
              @click="openTemplate(template)"
            >
              <div class="template-header">
                <div class="template-category">
                  <span class="category-badge" :class="`category-${template.category}`">
                    {{ getCategoryName(template.category) }}
                  </span>
                  <div class="template-status">
                    <span class="status-badge" :class="`status-${template.status}`">
                      {{ template.status }}
                    </span>
                  </div>
                </div>
                <div class="template-actions">
                  <button @click.stop="toggleTemplateFavorite(template)" class="action-btn">
                    <i :class="template.is_favorite ? 'icon-star-filled' : 'icon-star'"></i>
                  </button>
                  <div class="dropdown" @click.stop>
                    <button class="action-btn dropdown-toggle" @click="toggleDropdown(template.id)">
                      <i class="icon-more"></i>
                    </button>
                    <div v-if="openDropdown === template.id" class="dropdown-menu">
                      <button @click="editTemplate(template)" class="dropdown-item">
                        <i class="icon-edit"></i>
                        Edit
                      </button>
                      <button @click="duplicateTemplate(template)" class="dropdown-item">
                        <i class="icon-copy"></i>
                        Duplicate
                      </button>
                      <button @click="generateDocument(template)" class="dropdown-item">
                        <i class="icon-document"></i>
                        Generate Document
                      </button>
                      <button @click="shareTemplate(template)" class="dropdown-item">
                        <i class="icon-share"></i>
                        Share
                      </button>
                      <button @click="viewVersions(template)" class="dropdown-item">
                        <i class="icon-versions"></i>
                        Versions
                      </button>
                      <div class="dropdown-divider"></div>
                      <button @click="archiveTemplate(template)" class="dropdown-item text-warning">
                        <i class="icon-archive"></i>
                        Archive
                      </button>
                      <button @click="deleteTemplate(template)" class="dropdown-item text-danger">
                        <i class="icon-delete"></i>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="template-content">
                <h3 class="template-title">{{ template.name }}</h3>
                <p class="template-description">{{ template.description }}</p>

                <div class="template-meta">
                  <div class="meta-item">
                    <i class="icon-version"></i>
                    <span>v{{ template.version }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="icon-size"></i>
                    <span>{{ template.size }}</span>
                  </div>
                  <div class="meta-item">
                    <i class="icon-usage"></i>
                    <span>{{ template.usage_count }} uses</span>
                  </div>
                </div>

                <div v-if="template.tags && template.tags.length > 0" class="template-tags">
                  <span v-for="tag in template.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
                  <span v-if="template.tags.length > 3" class="tag-more">+{{ template.tags.length - 3 }}</span>
                </div>

                <div class="template-footer">
                  <div class="author-info">
                    <img :src="getAuthorAvatar(template.created_by)" :alt="template.created_by" class="author-avatar" />
                    <span class="author-name">{{ template.created_by }}</span>
                  </div>
                  <div class="template-date">
                    <span>{{ formatDate(template.last_modified) }}</span>
                  </div>
                </div>
              </div>

              <div class="template-overlay">
                <div class="overlay-actions">
                  <button @click.stop="previewTemplate(template)" class="btn btn-secondary">
                    <i class="icon-eye"></i>
                    Preview
                  </button>
                  <button @click.stop="generateDocument(template)" class="btn btn-primary">
                    <i class="icon-document"></i>
                    Generate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="page-btn"
          >
            <i class="icon-chevron-left"></i>
          </button>

          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }} ({{ filteredTemplates.length }} templates)
          </span>

          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            <i class="icon-chevron-right"></i>
          </button>
        </div>
      </main>
    </div>

    <!-- AI Assistant Panel -->
    <AssistantPanel
      v-if="showAIAssistant"
      :context="{
        module: 'bcm_templates',
        selectedTemplate: selectedTemplate,
        category: selectedCategory
      }"
      @close="showAIAssistant = false"
      @suggestion="handleAISuggestion"
    />

    <!-- Modals -->
    <!-- Create/Edit Template Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ editingTemplate ? 'Edit Template' : 'Create New Template' }}</h2>
          <button @click="closeModals" class="modal-close">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="saveTemplate" class="template-form">
            <div class="form-row">
              <div class="form-group">
                <label for="template-name">Template Name *</label>
                <input
                  id="template-name"
                  type="text"
                  v-model="templateForm.name"
                  required
                  class="form-input"
                  placeholder="Enter template name"
                />
              </div>

              <div class="form-group">
                <label for="template-category">Category *</label>
                <select id="template-category" v-model="templateForm.category" required class="form-select">
                  <option value="">Select category</option>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="template-description">Description</label>
              <textarea
                id="template-description"
                v-model="templateForm.description"
                class="form-textarea"
                rows="3"
                placeholder="Describe the purpose and usage of this template"
              ></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="compliance-framework">Compliance Framework</label>
                <select id="compliance-framework" v-model="templateForm.compliance_framework" class="form-select">
                  <option value="">Select framework</option>
                  <option value="iso-22301">ISO 22301</option>
                  <option value="nist">NIST Framework</option>
                  <option value="cobit">COBIT</option>
                  <option value="itil">ITIL</option>
                </select>
              </div>

              <div class="form-group">
                <label for="template-type">Template Type</label>
                <select id="template-type" v-model="templateForm.template_type" class="form-select">
                  <option value="document">Document Template</option>
                  <option value="form">Interactive Form</option>
                  <option value="checklist">Checklist</option>
                  <option value="workflow">Workflow Template</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="template-tags">Tags (comma separated)</label>
              <input
                id="template-tags"
                type="text"
                v-model="templateForm.tags_input"
                class="form-input"
                placeholder="e.g., bcm, emergency, response, critical"
              />
            </div>

            <div class="form-group">
              <label>Template Content</label>
              <div class="content-options">
                <button type="button" @click="uploadFile" class="btn btn-outline">
                  <i class="icon-upload"></i>
                  Upload File
                </button>
                <button type="button" @click="openContentEditor" class="btn btn-outline">
                  <i class="icon-edit"></i>
                  Create Content
                </button>
                <button type="button" @click="useAIGeneration" class="btn btn-primary">
                  <i class="icon-ai"></i>
                  Generate with AI
                </button>
              </div>
            </div>

            <div v-if="templateForm.content" class="content-preview">
              <h4>Content Preview</h4>
              <div class="preview-content" v-html="templateForm.content"></div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModals" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="saveDraft" class="btn btn-outline">Save as Draft</button>
          <button type="button" @click="saveTemplate" class="btn btn-primary">
            {{ editingTemplate ? 'Update Template' : 'Create Template' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Form Builder Modal -->
    <div v-if="showFormBuilder" class="modal-overlay" @click="closeModals">
      <div class="modal modal-large" @click.stop>
        <div class="modal-header">
          <h2>Form Builder</h2>
          <button @click="closeModals" class="modal-close">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-builder">
            <div class="form-builder-sidebar">
              <h3>Form Elements</h3>
              <div class="form-elements">
                <div
                  v-for="element in formElements"
                  :key="element.type"
                  class="form-element-item"
                  draggable="true"
                  @dragstart="dragStart(element)"
                >
                  <i :class="`icon-${element.icon}`"></i>
                  <span>{{ element.name }}</span>
                </div>
              </div>
            </div>

            <div class="form-builder-canvas">
              <div class="canvas-header">
                <h3>Form Preview</h3>
                <div class="canvas-actions">
                  <button @click="previewForm" class="btn btn-outline">Preview</button>
                  <button @click="saveForm" class="btn btn-primary">Save Form</button>
                </div>
              </div>

              <div
                class="form-canvas"
                @drop="dropElement"
                @dragover.prevent
              >
                <div v-if="formSchema.elements.length === 0" class="empty-canvas">
                  <p>Drag form elements here to build your form</p>
                </div>

                <div
                  v-for="(element, index) in formSchema.elements"
                  :key="index"
                  class="form-element"
                  @click="selectElement(index)"
                  :class="{ active: selectedElement === index }"
                >
                  <component
                    :is="getFormElementComponent(element.type)"
                    :element="element"
                    @update="updateElement(index, $event)"
                  />
                  <div class="element-controls">
                    <button @click="moveElementUp(index)" :disabled="index === 0">↑</button>
                    <button @click="moveElementDown(index)" :disabled="index === formSchema.elements.length - 1">↓</button>
                    <button @click="removeElement(index)" class="delete">×</button>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-builder-properties">
              <h3>Properties</h3>
              <div v-if="selectedElement !== null" class="element-properties">
                <div class="form-group">
                  <label>Label</label>
                  <input
                    type="text"
                    v-model="formSchema.elements[selectedElement].label"
                    class="form-input"
                  />
                </div>

                <div class="form-group">
                  <label>Field Name</label>
                  <input
                    type="text"
                    v-model="formSchema.elements[selectedElement].name"
                    class="form-input"
                  />
                </div>

                <div class="form-group">
                  <label>
                    <input
                      type="checkbox"
                      v-model="formSchema.elements[selectedElement].required"
                    />
                    Required
                  </label>
                </div>

                <div v-if="formSchema.elements[selectedElement].type === 'select'" class="form-group">
                  <label>Options (one per line)</label>
                  <textarea
                    v-model="formSchema.elements[selectedElement].options_text"
                    @input="updateSelectOptions"
                    class="form-textarea"
                    rows="4"
                  ></textarea>
                </div>
              </div>

              <div v-else class="no-selection">
                <p>Select an element to edit its properties</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Generation Modal -->
    <div v-if="showDocumentModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Generate Document</h2>
          <button @click="closeModals" class="modal-close">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="document-generation">
            <div class="template-info">
              <h3>{{ selectedTemplate?.name }}</h3>
              <p>{{ selectedTemplate?.description }}</p>
            </div>

            <div v-if="selectedTemplate?.merge_fields" class="merge-fields">
              <h4>Fill Required Information</h4>
              <div class="form-grid">
                <div
                  v-for="field in selectedTemplate.merge_fields"
                  :key="field.name"
                  class="form-group"
                >
                  <label :for="field.name">
                    {{ field.label }}
                    <span v-if="field.required" class="required">*</span>
                  </label>

                  <input
                    v-if="field.type === 'text'"
                    :id="field.name"
                    type="text"
                    v-model="documentData[field.name]"
                    :required="field.required"
                    class="form-input"
                    :placeholder="field.placeholder"
                  />

                  <textarea
                    v-else-if="field.type === 'textarea'"
                    :id="field.name"
                    v-model="documentData[field.name]"
                    :required="field.required"
                    class="form-textarea"
                    :placeholder="field.placeholder"
                    rows="3"
                  ></textarea>

                  <select
                    v-else-if="field.type === 'select'"
                    :id="field.name"
                    v-model="documentData[field.name]"
                    :required="field.required"
                    class="form-select"
                  >
                    <option value="">Select {{ field.label }}</option>
                    <option
                      v-for="option in field.options"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>

                  <input
                    v-else-if="field.type === 'date'"
                    :id="field.name"
                    type="date"
                    v-model="documentData[field.name]"
                    :required="field.required"
                    class="form-input"
                  />
                </div>
              </div>
            </div>

            <div class="generation-options">
              <h4>Output Options</h4>
              <div class="form-row">
                <div class="form-group">
                  <label for="output-format">Format</label>
                  <select id="output-format" v-model="documentOptions.format" class="form-select">
                    <option value="docx">Word Document (.docx)</option>
                    <option value="pdf">PDF Document (.pdf)</option>
                    <option value="html">HTML Document (.html)</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="document-name">Document Name</label>
                  <input
                    id="document-name"
                    type="text"
                    v-model="documentOptions.name"
                    class="form-input"
                    :placeholder="`${selectedTemplate?.name} - ${new Date().toLocaleDateString()}`"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModals" class="btn btn-secondary">Cancel</button>
          <button type="button" @click="previewDocument" class="btn btn-outline">Preview</button>
          <button type="button" @click="generateDocumentFile" class="btn btn-primary" :disabled="generatingDocument">
            <i v-if="generatingDocument" class="icon-spinner spinning"></i>
            <i v-else class="icon-document"></i>
            {{ generatingDocument ? 'Generating...' : 'Generate Document' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click="closeModals">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Upload Template</h2>
          <button @click="closeModals" class="modal-close">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="modal-body">
          <div class="upload-area">
            <div
              class="drop-zone"
              :class="{ 'drag-over': isDragOver }"
              @drop="handleDrop"
              @dragover.prevent="isDragOver = true"
              @dragleave="isDragOver = false"
            >
              <div class="drop-zone-content">
                <i class="icon-upload"></i>
                <h3>Drop files here or click to browse</h3>
                <p>Supported formats: .docx, .pdf, .html, .txt</p>
                <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileSelect"
                  accept=".docx,.pdf,.html,.txt"
                  multiple
                  hidden
                />
                <button @click="$refs.fileInput.click()" class="btn btn-primary">
                  Select Files
                </button>
              </div>
            </div>

            <div v-if="uploadFiles.length > 0" class="upload-files">
              <h4>Files to Upload</h4>
              <div v-for="(file, index) in uploadFiles" :key="index" class="upload-file">
                <div class="file-info">
                  <i class="icon-file"></i>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                </div>

                <div class="file-category">
                  <select v-model="file.category" class="form-select-small">
                    <option value="">Select category</option>
                    <option v-for="category in categories" :key="category.id" :value="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                </div>

                <button @click="removeUploadFile(index)" class="btn btn-outline-small">
                  <i class="icon-close"></i>
                </button>
              </div>
            </div>

            <div v-if="uploadProgress > 0" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span class="progress-text">{{ uploadProgress }}% uploaded</span>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" @click="closeModals" class="btn btn-secondary">Cancel</button>
          <button
            type="button"
            @click="startUpload"
            class="btn btn-primary"
            :disabled="uploadFiles.length === 0 || uploading"
          >
            <i v-if="uploading" class="icon-spinner spinning"></i>
            <i v-else class="icon-upload"></i>
            {{ uploading ? 'Uploading...' : `Upload ${uploadFiles.length} file(s)` }}
          </button>
        </div>
      </div>
    </div>

    <!-- Notifications -->
    <div class="notifications">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification"
        :class="`notification-${notification.type}`"
      >
        <i :class="`icon-${notification.icon}`"></i>
        <div class="notification-content">
          <h4>{{ notification.title }}</h4>
          <p>{{ notification.message }}</p>
        </div>
        <button @click="dismissNotification(notification.id)" class="notification-close">
          <i class="icon-close"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import BCMTemplatesService from '@/services/bcmTemplates.js';
import AssistantPanel from '@/components/assistant/AssistantPanel.vue';

export default {
  name: 'BCMTemplates',
  components: {
    AssistantPanel
  },
  data() {
    return {
      // UI State
      loading: true,
      showAIAssistant: false,
      showCreateModal: false,
      showFormBuilder: false,
      showDocumentModal: false,
      showUploadModal: false,
      viewMode: 'grid', // 'grid' or 'list'

      // Data
      templates: [],
      categories: [],
      recentActivity: [],
      aiSuggestions: [],

      // Search and Filtering
      searchQuery: '',
      selectedCategory: '',
      statusFilter: '',
      sortBy: 'last_modified',

      // Pagination
      currentPage: 1,
      itemsPerPage: 12,

      // Statistics
      totalTemplates: 0,
      documentsGenerated: 0,
      approvedTemplates: 0,
      pendingApproval: 0,

      // Template Management
      selectedTemplate: null,
      editingTemplate: false,
      templateForm: {
        name: '',
        description: '',
        category: '',
        compliance_framework: '',
        template_type: 'document',
        tags_input: '',
        content: ''
      },

      // Document Generation
      documentData: {},
      documentOptions: {
        format: 'docx',
        name: ''
      },
      generatingDocument: false,

      // Form Builder
      formSchema: {
        elements: []
      },
      selectedElement: null,
      formElements: [
        { type: 'text', name: 'Text Input', icon: 'text' },
        { type: 'textarea', name: 'Text Area', icon: 'textarea' },
        { type: 'select', name: 'Dropdown', icon: 'select' },
        { type: 'checkbox', name: 'Checkbox', icon: 'checkbox' },
        { type: 'radio', name: 'Radio Button', icon: 'radio' },
        { type: 'date', name: 'Date Picker', icon: 'calendar' },
        { type: 'file', name: 'File Upload', icon: 'upload' },
        { type: 'section', name: 'Section Header', icon: 'heading' }
      ],

      // Upload
      uploadFiles: [],
      uploadProgress: 0,
      uploading: false,
      isDragOver: false,

      // UI State
      openDropdown: null,
      notifications: []
    };
  },
  computed: {
    filteredTemplates() {
      let filtered = [...this.templates];

      // Category filter
      if (this.selectedCategory) {
        filtered = filtered.filter(t => t.category === this.selectedCategory);
      }

      // Status filter
      if (this.statusFilter) {
        filtered = filtered.filter(t => t.status === this.statusFilter);
      }

      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(t =>
          t.name.toLowerCase().includes(query) ||
          t.description.toLowerCase().includes(query) ||
          (t.tags && t.tags.some(tag => tag.toLowerCase().includes(query)))
        );
      }

      // Sort
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return a.name.localeCompare(b.name);
          case 'created_date':
            return new Date(b.created_date) - new Date(a.created_date);
          case 'usage_count':
            return b.usage_count - a.usage_count;
          default: // last_modified
            return new Date(b.last_modified) - new Date(a.last_modified);
        }
      });

      return filtered;
    },

    paginatedTemplates() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.filteredTemplates.slice(start, end);
    },

    totalPages() {
      return Math.ceil(this.filteredTemplates.length / this.itemsPerPage);
    }
  },
  async mounted() {
    await this.initializeComponent();
    this.setupEventListeners();
  },
  beforeUnmount() {
    this.cleanupEventListeners();
  },
  methods: {
    async initializeComponent() {
      try {
        this.loading = true;

        // Load initial data
        await Promise.all([
          this.loadTemplates(),
          this.loadCategories(),
          this.loadStatistics(),
          this.loadRecentActivity(),
          this.loadAISuggestions()
        ]);
      } catch (error) {
        this.showNotification('error', 'Initialization Error', error.message);
      } finally {
        this.loading = false;
      }
    },

    async loadTemplates() {
      try {
        this.templates = await BCMTemplatesService.getTemplates();
        this.totalTemplates = this.templates.length;
      } catch (error) {
        throw new Error('Failed to load templates');
      }
    },

    async loadCategories() {
      this.categories = BCMTemplatesService.getCategories();
    },

    async loadStatistics() {
      try {
        // Calculate statistics from templates
        this.approvedTemplates = this.templates.filter(t => t.status === 'approved').length;
        this.pendingApproval = this.templates.filter(t => t.status === 'review').length;
        this.documentsGenerated = this.templates.reduce((sum, t) => sum + t.usage_count, 0);
      } catch (error) {
        console.error('Error loading statistics:', error);
      }
    },

    async loadRecentActivity() {
      // Mock recent activity - in real implementation, this would come from API
      this.recentActivity = [
        {
          id: 1,
          type: 'orange',
          icon: 'edit',
          text: 'BCP Template v2.1 updated',
          timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30 mins ago
        },
        {
          id: 2,
          type: 'blue',
          icon: 'document',
          text: 'Risk Assessment document generated',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
        },
        {
          id: 3,
          type: 'green',
          icon: 'check',
          text: 'Crisis Management template approved',
          timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1 day ago
        }
      ];
    },

    async loadAISuggestions() {
      try {
        if (this.selectedCategory) {
          this.aiSuggestions = await BCMTemplatesService.getAITemplateSuggestions(this.selectedCategory);
        }
      } catch (error) {
        console.error('Error loading AI suggestions:', error);
        this.aiSuggestions = [];
      }
    },

    // Template Operations
    async openTemplate(template) {
      this.selectedTemplate = template;
      // Navigate to template detail view or open in modal
    },

    async editTemplate(template) {
      this.selectedTemplate = template;
      this.editingTemplate = true;

      // Populate form
      this.templateForm = {
        name: template.name,
        description: template.description,
        category: template.category,
        compliance_framework: template.compliance_framework,
        template_type: template.template_type,
        tags_input: template.tags ? template.tags.join(', ') : '',
        content: template.content || ''
      };

      this.showCreateModal = true;
    },

    async duplicateTemplate(template) {
      try {
        const duplicatedTemplate = {
          ...template,
          name: `${template.name} (Copy)`,
          id: undefined,
          version: '1.0',
          status: 'draft'
        };

        await BCMTemplatesService.createTemplate(duplicatedTemplate);
        await this.loadTemplates();

        this.showNotification('success', 'Template Duplicated', 'Template has been successfully duplicated');
      } catch (error) {
        this.showNotification('error', 'Duplication Failed', error.message);
      }
    },

    async archiveTemplate(template) {
      try {
        await BCMTemplatesService.updateTemplate(template.id, { status: 'archived' });
        await this.loadTemplates();

        this.showNotification('success', 'Template Archived', 'Template has been archived');
      } catch (error) {
        this.showNotification('error', 'Archive Failed', error.message);
      }
    },

    async deleteTemplate(template) {
      if (confirm(`Are you sure you want to delete "${template.name}"? This action cannot be undone.`)) {
        try {
          await BCMTemplatesService.deleteTemplate(template.id);
          await this.loadTemplates();

          this.showNotification('success', 'Template Deleted', 'Template has been permanently deleted');
        } catch (error) {
          this.showNotification('error', 'Delete Failed', error.message);
        }
      }
    },

    // Document Generation
    async generateDocument(template) {
      this.selectedTemplate = template;
      this.documentData = {};
      this.documentOptions.name = `${template.name} - ${new Date().toLocaleDateString()}`;
      this.showDocumentModal = true;
    },

    async generateDocumentFile() {
      try {
        this.generatingDocument = true;

        const result = await BCMTemplatesService.generateDocument(
          this.selectedTemplate.id,
          {
            ...this.documentData,
            options: this.documentOptions
          }
        );

        // Download the generated document
        const blob = new Blob([result.content], {
          type: this.getContentType(this.documentOptions.format)
        });

        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${this.documentOptions.name}.${this.documentOptions.format}`;
        link.click();
        window.URL.revokeObjectURL(url);

        this.closeModals();
        this.showNotification('success', 'Document Generated', 'Document has been generated and downloaded');
      } catch (error) {
        this.showNotification('error', 'Generation Failed', error.message);
      } finally {
        this.generatingDocument = false;
      }
    },

    async previewDocument() {
      // Open preview window or modal
      this.showNotification('info', 'Preview', 'Document preview feature coming soon');
    },

    // Form Builder
    openFormBuilder() {
      this.formSchema = { elements: [] };
      this.selectedElement = null;
      this.showFormBuilder = true;
    },

    dragStart(element) {
      this.draggedElement = element;
    },

    dropElement(event) {
      event.preventDefault();
      if (this.draggedElement) {
        const newElement = {
          type: this.draggedElement.type,
          label: this.draggedElement.name,
          name: `field_${Date.now()}`,
          required: false,
          options: this.draggedElement.type === 'select' ? [] : undefined
        };

        this.formSchema.elements.push(newElement);
        this.draggedElement = null;
      }
    },

    selectElement(index) {
      this.selectedElement = index;
    },

    updateElement(index, updates) {
      this.formSchema.elements[index] = { ...this.formSchema.elements[index], ...updates };
    },

    removeElement(index) {
      this.formSchema.elements.splice(index, 1);
      if (this.selectedElement === index) {
        this.selectedElement = null;
      }
    },

    moveElementUp(index) {
      if (index > 0) {
        const element = this.formSchema.elements.splice(index, 1)[0];
        this.formSchema.elements.splice(index - 1, 0, element);
        this.selectedElement = index - 1;
      }
    },

    moveElementDown(index) {
      if (index < this.formSchema.elements.length - 1) {
        const element = this.formSchema.elements.splice(index, 1)[0];
        this.formSchema.elements.splice(index + 1, 0, element);
        this.selectedElement = index + 1;
      }
    },

    updateSelectOptions() {
      if (this.selectedElement !== null && this.formSchema.elements[this.selectedElement].type === 'select') {
        const element = this.formSchema.elements[this.selectedElement];
        if (element.options_text) {
          element.options = element.options_text.split('\n')
            .filter(line => line.trim())
            .map(line => ({ label: line.trim(), value: line.trim().toLowerCase() }));
        }
      }
    },

    getFormElementComponent(type) {
      // Return appropriate component based on element type
      return 'div'; // Simplified for this example
    },

    async saveForm() {
      try {
        if (this.selectedTemplate) {
          await BCMTemplatesService.updateFormSchema(this.selectedTemplate.id, this.formSchema);
          this.showNotification('success', 'Form Saved', 'Form schema has been saved');
        }
      } catch (error) {
        this.showNotification('error', 'Save Failed', error.message);
      }
    },

    previewForm() {
      // Open form preview modal
      this.showNotification('info', 'Preview', 'Form preview feature coming soon');
    },

    // File Upload
    openUploadModal() {
      this.uploadFiles = [];
      this.uploadProgress = 0;
      this.showUploadModal = true;
    },

    handleFileSelect(event) {
      this.addFiles(Array.from(event.target.files));
    },

    handleDrop(event) {
      event.preventDefault();
      this.isDragOver = false;
      this.addFiles(Array.from(event.dataTransfer.files));
    },

    addFiles(files) {
      const validFiles = files.filter(file =>
        ['.docx', '.pdf', '.html', '.txt'].some(ext => file.name.toLowerCase().endsWith(ext))
      );

      validFiles.forEach(file => {
        if (!this.uploadFiles.find(f => f.name === file.name)) {
          this.uploadFiles.push({
            ...file,
            category: ''
          });
        }
      });
    },

    removeUploadFile(index) {
      this.uploadFiles.splice(index, 1);
    },

    async startUpload() {
      try {
        this.uploading = true;
        this.uploadProgress = 0;

        for (let i = 0; i < this.uploadFiles.length; i++) {
          const file = this.uploadFiles[i];
          await BCMTemplatesService.uploadFile(file, null);
          this.uploadProgress = Math.round(((i + 1) / this.uploadFiles.length) * 100);
        }

        await this.loadTemplates();
        this.closeModals();
        this.showNotification('success', 'Upload Complete', `${this.uploadFiles.length} file(s) uploaded successfully`);
      } catch (error) {
        this.showNotification('error', 'Upload Failed', error.message);
      } finally {
        this.uploading = false;
        this.uploadProgress = 0;
      }
    },

    // Template Form Operations
    async saveTemplate() {
      try {
        const templateData = {
          ...this.templateForm,
          tags: this.templateForm.tags_input.split(',').map(tag => tag.trim()).filter(Boolean)
        };

        if (this.editingTemplate) {
          await BCMTemplatesService.updateTemplate(this.selectedTemplate.id, templateData);
          this.showNotification('success', 'Template Updated', 'Template has been successfully updated');
        } else {
          await BCMTemplatesService.createTemplate(templateData);
          this.showNotification('success', 'Template Created', 'Template has been successfully created');
        }

        await this.loadTemplates();
        this.closeModals();
      } catch (error) {
        this.showNotification('error', 'Save Failed', error.message);
      }
    },

    async saveDraft() {
      try {
        const templateData = {
          ...this.templateForm,
          status: 'draft',
          tags: this.templateForm.tags_input.split(',').map(tag => tag.trim()).filter(Boolean)
        };

        if (this.editingTemplate) {
          await BCMTemplatesService.updateTemplate(this.selectedTemplate.id, templateData);
        } else {
          await BCMTemplatesService.createTemplate(templateData);
        }

        await this.loadTemplates();
        this.closeModals();
        this.showNotification('success', 'Draft Saved', 'Template draft has been saved');
      } catch (error) {
        this.showNotification('error', 'Save Failed', error.message);
      }
    },

    uploadFile() {
      // Trigger file upload for template content
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.docx,.pdf,.html,.txt';
      input.onchange = async (event) => {
        const file = event.target.files[0];
        if (file) {
          try {
            const result = await BCMTemplatesService.processTemplate(file, this.templateForm.category);
            this.templateForm.content = result.content;
            this.showNotification('success', 'File Uploaded', 'Template content has been extracted');
          } catch (error) {
            this.showNotification('error', 'Upload Failed', error.message);
          }
        }
      };
      input.click();
    },

    openContentEditor() {
      // Open rich text editor modal
      this.showNotification('info', 'Content Editor', 'Rich text editor feature coming soon');
    },

    async useAIGeneration() {
      try {
        const suggestions = await BCMTemplatesService.getAITemplateSuggestions(
          this.templateForm.category,
          this.templateForm.description
        );

        if (suggestions.length > 0) {
          this.templateForm.content = suggestions[0].content;
          this.showNotification('success', 'AI Content Generated', 'Template content has been generated using AI');
        }
      } catch (error) {
        this.showNotification('error', 'AI Generation Failed', error.message);
      }
    },

    // Search and Filtering
    async performSearch() {
      // Debounce search
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1; // Reset to first page when searching
      }, 300);
    },

    clearSearch() {
      this.searchQuery = '';
      this.currentPage = 1;
    },

    selectCategory(categoryId) {
      if (this.selectedCategory === categoryId) {
        this.selectedCategory = '';
      } else {
        this.selectedCategory = categoryId;
      }
      this.currentPage = 1;
      this.loadAISuggestions(); // Refresh AI suggestions for new category
    },

    applyFilters() {
      this.currentPage = 1;
    },

    applySorting() {
      this.currentPage = 1;
    },

    toggleViewMode() {
      this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
    },

    // AI Integration
    async handleAISuggestion(suggestion) {
      this.showNotification('info', 'AI Suggestion Applied', suggestion.message);
    },

    dismissAISuggestions() {
      this.aiSuggestions = [];
    },

    async applySuggestion(suggestion) {
      try {
        // Apply AI suggestion - this could create a new template or modify existing one
        if (suggestion.action === 'create_template') {
          this.templateForm = {
            name: suggestion.title,
            description: suggestion.description,
            category: suggestion.category,
            content: suggestion.content,
            compliance_framework: suggestion.framework || '',
            template_type: 'document',
            tags_input: suggestion.tags ? suggestion.tags.join(', ') : ''
          };
          this.showCreateModal = true;
        }

        this.showNotification('success', 'Suggestion Applied', 'AI suggestion has been applied');
      } catch (error) {
        this.showNotification('error', 'Failed to Apply Suggestion', error.message);
      }
    },

    // Additional Features
    async shareTemplate(template) {
      // Open share modal or handle sharing logic
      this.showNotification('info', 'Share Template', 'Template sharing feature coming soon');
    },

    async viewVersions(template) {
      // Open version history modal
      this.showNotification('info', 'Version History', 'Version history feature coming soon');
    },

    async toggleTemplateFavorite(template) {
      // Toggle favorite status
      template.is_favorite = !template.is_favorite;
    },

    async previewTemplate(template) {
      // Open template preview
      this.showNotification('info', 'Template Preview', 'Template preview feature coming soon');
    },

    openComplianceChecker() {
      this.showNotification('info', 'Compliance Checker', 'Compliance checker feature coming soon');
    },

    openVersionManager() {
      this.showNotification('info', 'Version Manager', 'Version manager feature coming soon');
    },

    openPermissions() {
      this.showNotification('info', 'Permissions Manager', 'Permissions manager feature coming soon');
    },

    // UI Helpers
    toggleDropdown(templateId) {
      this.openDropdown = this.openDropdown === templateId ? null : templateId;
    },

    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },

    getCategoryName(categoryId) {
      const category = this.categories.find(cat => cat.id === categoryId);
      return category ? category.name : categoryId;
    },

    getCategoryCount(categoryId) {
      return this.templates.filter(t => t.category === categoryId).length;
    },

    getAuthorAvatar(author) {
      // Return avatar URL or placeholder
      return `https://ui-avatars.com/api/?name=${encodeURIComponent(author)}&background=FF6B35&color=fff`;
    },

    formatDate(date) {
      return new Date(date).toLocaleDateString();
    },

    formatTime(date) {
      const now = new Date();
      const time = new Date(date);
      const diff = now - time;

      const minutes = Math.floor(diff / 1000 / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);

      if (minutes < 60) return `${minutes}m ago`;
      if (hours < 24) return `${hours}h ago`;
      return `${days}d ago`;
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    getContentType(format) {
      const types = {
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'pdf': 'application/pdf',
        'html': 'text/html'
      };
      return types[format] || 'application/octet-stream';
    },

    // Modal Management
    openCreateModal() {
      this.editingTemplate = false;
      this.templateForm = {
        name: '',
        description: '',
        category: '',
        compliance_framework: '',
        template_type: 'document',
        tags_input: '',
        content: ''
      };
      this.showCreateModal = true;
    },

    closeModals() {
      this.showCreateModal = false;
      this.showFormBuilder = false;
      this.showDocumentModal = false;
      this.showUploadModal = false;
      this.selectedTemplate = null;
      this.editingTemplate = false;
      this.openDropdown = null;
    },

    // Notifications
    showNotification(type, title, message) {
      const id = Date.now();
      const notification = {
        id,
        type,
        title,
        message,
        icon: this.getNotificationIcon(type)
      };

      this.notifications.push(notification);

      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        this.dismissNotification(id);
      }, 5000);
    },

    dismissNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },

    getNotificationIcon(type) {
      const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info-circle'
      };
      return icons[type] || 'info-circle';
    },

    // Event Listeners
    setupEventListeners() {
      // Close dropdowns when clicking outside
      document.addEventListener('click', this.handleOutsideClick);

      // Listen for upload progress events
      window.addEventListener('upload-progress', this.handleUploadProgress);
    },

    cleanupEventListeners() {
      document.removeEventListener('click', this.handleOutsideClick);
      window.removeEventListener('upload-progress', this.handleUploadProgress);
    },

    handleOutsideClick(event) {
      if (!event.target.closest('.dropdown')) {
        this.openDropdown = null;
      }
    },

    handleUploadProgress(event) {
      this.uploadProgress = event.detail.percent;
    }
  }
};
</script>

<style scoped>
/* Anthropic Color Palette */
:root {
  --orange: #FF6B35;
  --blue: #4A90E2;
  --dark: #1A1A1A;
  --light-gray: #F8F9FA;
  --medium-gray: #E9ECEF;
  --text-dark: #2C3E50;
  --text-medium: #6C757D;
  --white: #FFFFFF;
  --success: #28A745;
  --warning: #FFC107;
  --danger: #DC3545;
  --border-radius: 8px;
  --box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  --transition: all 0.3s ease;
}

/* Main Container */
.bcm-templates {
  min-height: 100vh;
  background-color: var(--light-gray);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Header Section */
.header-section {
  background: linear-gradient(135deg, var(--orange), var(--blue));
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.page-subtitle {
  font-size: 1.2rem;
  margin: 0;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* Dashboard Cards */
.dashboard-cards {
  max-width: 1200px;
  margin: 0 auto 2rem auto;
  padding: 0 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--box-shadow);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: var(--transition);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon.bg-orange { background-color: var(--orange); }
.stat-icon.bg-blue { background-color: var(--blue); }
.stat-icon.bg-green { background-color: var(--success); }
.stat-icon.bg-yellow { background-color: var(--warning); }

.stat-content h3 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-dark);
}

.stat-content p {
  font-size: 0.9rem;
  color: var(--text-medium);
  margin: 0.25rem 0 0 0;
}

/* Main Content Layout */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sidebar-section {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--box-shadow);
}

.sidebar-section h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-dark);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.category-item:hover {
  background-color: var(--light-gray);
}

.category-item.active {
  background-color: var(--orange);
  color: white;
}

.category-icon {
  font-size: 1.2rem;
}

.category-name {
  flex: 1;
  font-weight: 500;
}

.category-count {
  font-size: 0.85rem;
  opacity: 0.7;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: none;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  font-size: 0.9rem;
}

.quick-action-btn:hover {
  background-color: var(--light-gray);
}

.recent-activity {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  color: white;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.85rem;
  margin: 0;
  color: var(--text-dark);
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-medium);
}

/* Content Area */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Search and Filters */
.search-filters {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--box-shadow);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-bar {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrapper i {
  position: absolute;
  left: 1rem;
  color: var(--text-medium);
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid var(--medium-gray);
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: var(--transition);
}

.search-input:focus {
  outline: none;
  border-color: var(--blue);
}

.clear-search {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-medium);
}

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
}

/* AI Suggestions Banner */
.ai-suggestions-banner {
  background: linear-gradient(135deg, var(--blue), var(--orange));
  color: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.suggestions-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.suggestions-header h4 {
  flex: 1;
  margin: 0;
  font-size: 1.2rem;
}

.dismiss-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  transition: var(--transition);
}

.dismiss-btn:hover {
  background: rgba(255,255,255,0.3);
}

.suggestions-list {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.suggestion-item {
  background: rgba(255,255,255,0.1);
  border-radius: var(--border-radius);
  padding: 1rem;
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
}

.suggestion-item:hover {
  background: rgba(255,255,255,0.2);
}

.suggestion-content h5 {
  margin: 0;
  font-size: 1rem;
}

.suggestion-content p {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.suggestion-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.apply-suggestion-btn {
  background: white;
  color: var(--blue);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
}

.apply-suggestion-btn:hover {
  background: var(--light-gray);
}

/* Templates Container */
.templates-container {
  background: white;
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--box-shadow);
  min-height: 400px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  color: var(--text-medium);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--medium-gray);
  border-top: 4px solid var(--orange);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-dark);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
}

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  border: 2px solid var(--medium-gray);
  border-radius: var(--border-radius);
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
}

.template-card:hover {
  border-color: var(--blue);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.template-card:hover .template-overlay {
  opacity: 1;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1rem 0 1rem;
}

.template-category {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.category-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  background-color: var(--medium-gray);
  color: var(--text-dark);
}

.category-badge.category-bcp { background-color: var(--orange); color: white; }
.category-badge.category-drp { background-color: var(--blue); color: white; }
.category-badge.category-risk { background-color: var(--warning); color: var(--dark); }

.status-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  text-transform: capitalize;
}

.status-badge.status-draft { background-color: var(--medium-gray); color: var(--text-dark); }
.status-badge.status-review { background-color: var(--warning); color: var(--dark); }
.status-badge.status-approved { background-color: var(--success); color: white; }
.status-badge.status-archived { background-color: var(--text-medium); color: white; }

.template-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  color: var(--text-medium);
  transition: var(--transition);
}

.action-btn:hover {
  background-color: var(--light-gray);
  color: var(--text-dark);
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  z-index: 10;
  min-width: 180px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: var(--transition);
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background-color: var(--light-gray);
}

.dropdown-item.text-warning {
  color: var(--warning);
}

.dropdown-item.text-danger {
  color: var(--danger);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--medium-gray);
  margin: 0.5rem 0;
}

.template-content {
  padding: 1rem;
}

.template-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-dark);
  line-height: 1.3;
}

.template-description {
  font-size: 0.9rem;
  color: var(--text-medium);
  margin: 0 0 1rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--text-medium);
}

.template-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--light-gray);
  color: var(--text-dark);
  border-radius: 12px;
}

.tag-more {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--text-medium);
  color: white;
  border-radius: 12px;
}

.template-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.author-name {
  font-size: 0.8rem;
  color: var(--text-medium);
}

.template-date {
  font-size: 0.8rem;
  color: var(--text-medium);
}

.template-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: var(--transition);
}

.overlay-actions {
  display: flex;
  gap: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.page-btn {
  background: white;
  border: 1px solid var(--medium-gray);
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.page-btn:hover:not(:disabled) {
  background-color: var(--light-gray);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.9rem;
  color: var(--text-medium);
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn-primary {
  background-color: var(--orange);
  color: white;
}

.btn-primary:hover {
  background-color: #e55a2e;
}

.btn-secondary {
  background-color: var(--blue);
  color: white;
}

.btn-secondary:hover {
  background-color: #3a7bc8;
}

.btn-outline {
  background-color: transparent;
  color: var(--text-dark);
  border: 1px solid var(--medium-gray);
}

.btn-outline:hover {
  background-color: var(--light-gray);
}

.btn-outline-small {
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  background-color: transparent;
  color: var(--text-dark);
  border: 1px solid var(--medium-gray);
}

.btn-outline-small:hover {
  background-color: var(--light-gray);
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-large {
  max-width: 1000px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--medium-gray);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-dark);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-medium);
  padding: 0.25rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.modal-close:hover {
  background-color: var(--light-gray);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--medium-gray);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Forms */
.template-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--text-dark);
  font-size: 0.9rem;
}

.form-input, .form-select, .form-textarea {
  padding: 0.75rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  font-size: 0.9rem;
  transition: var(--transition);
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--blue);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-select-small {
  padding: 0.5rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  font-size: 0.8rem;
  background: white;
}

.content-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.content-preview {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  background-color: var(--light-gray);
}

.preview-content {
  max-height: 200px;
  overflow-y: auto;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* Form Builder */
.form-builder {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  gap: 1rem;
  height: 500px;
}

.form-builder-sidebar, .form-builder-properties {
  background-color: var(--light-gray);
  padding: 1rem;
  border-radius: var(--border-radius);
  overflow-y: auto;
}

.form-elements {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-element-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: white;
  border-radius: var(--border-radius);
  cursor: grab;
  transition: var(--transition);
  font-size: 0.85rem;
}

.form-element-item:hover {
  background-color: var(--medium-gray);
}

.form-element-item:active {
  cursor: grabbing;
}

.form-builder-canvas {
  background: white;
  border-radius: var(--border-radius);
  display: flex;
  flex-direction: column;
}

.canvas-header {
  padding: 1rem;
  border-bottom: 1px solid var(--medium-gray);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.canvas-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.canvas-actions {
  display: flex;
  gap: 0.5rem;
}

.form-canvas {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  min-height: 200px;
}

.empty-canvas {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-medium);
  font-style: italic;
}

.form-element {
  position: relative;
  margin-bottom: 1rem;
  padding: 0.75rem;
  border: 2px dashed transparent;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.form-element.active {
  border-color: var(--blue);
  background-color: rgba(74, 144, 226, 0.1);
}

.element-controls {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: var(--transition);
}

.form-element:hover .element-controls {
  opacity: 1;
}

.element-controls button {
  width: 24px;
  height: 24px;
  border: none;
  background: var(--text-medium);
  color: white;
  border-radius: 2px;
  cursor: pointer;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.element-controls button:hover {
  background: var(--text-dark);
}

.element-controls button.delete {
  background: var(--danger);
}

.element-properties {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.no-selection {
  color: var(--text-medium);
  font-style: italic;
  text-align: center;
  margin-top: 2rem;
}

/* Document Generation */
.document-generation {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.template-info {
  padding: 1rem;
  background-color: var(--light-gray);
  border-radius: var(--border-radius);
}

.template-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-dark);
}

.template-info p {
  margin: 0;
  color: var(--text-medium);
}

.merge-fields h4, .generation-options h4 {
  margin: 0 0 1rem 0;
  color: var(--text-dark);
  font-size: 1.1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.required {
  color: var(--danger);
  margin-left: 0.25rem;
}

/* Upload */
.upload-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.drop-zone {
  border: 2px dashed var(--medium-gray);
  border-radius: var(--border-radius);
  padding: 2rem;
  text-align: center;
  transition: var(--transition);
  cursor: pointer;
}

.drop-zone:hover, .drop-zone.drag-over {
  border-color: var(--blue);
  background-color: rgba(74, 144, 226, 0.05);
}

.drop-zone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.drop-zone-content i {
  font-size: 3rem;
  color: var(--text-medium);
}

.drop-zone-content h3 {
  margin: 0;
  color: var(--text-dark);
}

.drop-zone-content p {
  margin: 0;
  color: var(--text-medium);
  font-size: 0.9rem;
}

.upload-files {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.upload-files h4 {
  margin: 0;
  color: var(--text-dark);
}

.upload-file {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background-color: var(--light-gray);
  border-radius: var(--border-radius);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: var(--text-dark);
}

.file-size {
  color: var(--text-medium);
  font-size: 0.85rem;
}

.file-category {
  flex-shrink: 0;
}

.upload-progress {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--medium-gray);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--orange);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: var(--text-medium);
  text-align: center;
}

/* Notifications */
.notifications {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
}

.notification {
  background: white;
  border-radius: var(--border-radius);
  padding: 1rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  animation: slideIn 0.3s ease;
  border-left: 4px solid var(--medium-gray);
}

.notification-success { border-left-color: var(--success); }
.notification-error { border-left-color: var(--danger); }
.notification-warning { border-left-color: var(--warning); }
.notification-info { border-left-color: var(--blue); }

.notification i {
  font-size: 1.2rem;
  margin-top: 0.1rem;
}

.notification-success i { color: var(--success); }
.notification-error i { color: var(--danger); }
.notification-warning i { color: var(--warning); }
.notification-info i { color: var(--blue); }

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.95rem;
  color: var(--text-dark);
}

.notification-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-medium);
  line-height: 1.3;
}

.notification-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-medium);
  padding: 0.25rem;
  border-radius: var(--border-radius);
  transition: var(--transition);
}

.notification-close:hover {
  background-color: var(--light-gray);
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

/* Icons (using CSS classes as placeholders for icon font) */
.icon-ai::before { content: '🤖'; }
.icon-plus::before { content: '+'; }
.icon-upload::before { content: '↗'; }
.icon-templates::before { content: '📄'; }
.icon-documents::before { content: '📊'; }
.icon-check::before { content: '✓'; }
.icon-pending::before { content: '⏳'; }
.icon-search::before { content: '🔍'; }
.icon-close::before { content: '×'; }
.icon-list::before { content: '☰'; }
.icon-grid::before { content: '⊞'; }
.icon-more::before { content: '⋯'; }
.icon-edit::before { content: '✏'; }
.icon-copy::before { content: '📋'; }
.icon-document::before { content: '📄'; }
.icon-share::before { content: '↗'; }
.icon-versions::before { content: '🔄'; }
.icon-archive::before { content: '📦'; }
.icon-delete::before { content: '🗑'; }
.icon-eye::before { content: '👁'; }
.icon-star::before { content: '☆'; }
.icon-star-filled::before { content: '★'; }
.icon-version::before { content: 'v'; }
.icon-size::before { content: '📏'; }
.icon-usage::before { content: '📈'; }
.icon-chevron-left::before { content: '‹'; }
.icon-chevron-right::before { content: '›'; }
.icon-form::before { content: '📝'; }
.icon-shield::before { content: '🛡'; }
.icon-users::before { content: '👥'; }
.icon-file::before { content: '📄'; }
.icon-text::before { content: 'T'; }
.icon-textarea::before { content: '¶'; }
.icon-select::before { content: '▼'; }
.icon-checkbox::before { content: '☑'; }
.icon-radio::before { content: '◉'; }
.icon-calendar::before { content: '📅'; }
.icon-heading::before { content: 'H'; }
.icon-spinner::before { content: '⟳'; }
.icon-check-circle::before { content: '✅'; }
.icon-alert-circle::before { content: '⚠'; }
.icon-alert-triangle::before { content: '⚠'; }
.icon-info-circle::before { content: 'ℹ'; }

.spinning {
  animation: spin 1s linear infinite;
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .sidebar {
    order: 2;
  }

  .content-area {
    order: 1;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .dashboard-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .modal {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .form-builder {
    grid-template-columns: 1fr;
    height: auto;
  }

  .form-builder-sidebar,
  .form-builder-properties {
    max-height: 200px;
  }
}</style>