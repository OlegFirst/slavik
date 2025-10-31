<template>
  <div class="bcm-scenario-hub">
    <!-- Header Section -->
    <div class="hub-header">
      <div class="container-fluid">
        <div class="row align-items-center mb-4">
          <div class="col-md-8">
            <h1 class="hub-title">
              <i class="fas fa-store me-2"></i>
              BCM Scenario Hub
            </h1>
            <p class="hub-subtitle">
              Community marketplace for Business Continuity scenarios, exercises, and best practices
            </p>
          </div>
          <div class="col-md-4 text-end">
            <div class="hub-actions">
              <button
                class="btn btn-ai-primary me-2"
                @click="showAIWizard = true"
              >
                <i class="fas fa-magic me-1"></i>
                AI Generate
              </button>
              <button
                class="btn btn-outline-primary me-2"
                @click="showPublishModal = true"
              >
                <i class="fas fa-plus me-1"></i>
                Publish Scenario
              </button>
              <button
                class="btn btn-primary"
                @click="showMyContributions = true"
              >
                <i class="fas fa-user me-1"></i>
                My Hub
              </button>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-number">{{ marketplaceStats.totalScenarios || 0 }}</div>
              <div class="stat-label">Total Scenarios</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-number">{{ marketplaceStats.activeContributors || 0 }}</div>
              <div class="stat-label">Active Contributors</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-number">{{ marketplaceStats.totalDownloads || 0 }}</div>
              <div class="stat-label">Downloads</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="stat-card">
              <div class="stat-number">{{ marketplaceStats.avgRating || 0 }}</div>
              <div class="stat-label">Avg Rating</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="hub-content">
      <div class="container-fluid">
        <div class="row">
          <!-- Left Sidebar - Filters and Navigation -->
          <div class="col-md-3">
            <div class="sidebar-section">
              <!-- Search -->
              <div class="search-section mb-4">
                <div class="input-group">
                  <input
                    v-model="searchQuery"
                    type="text"
                    class="form-control"
                    placeholder="Search scenarios..."
                    @input="debouncedSearch"
                  />
                  <button class="btn btn-outline-secondary" @click="performSearch">
                    <i class="fas fa-search"></i>
                  </button>
                </div>
                <div class="advanced-search-toggle mt-2">
                  <button
                    class="btn btn-sm btn-link p-0"
                    @click="showAdvancedSearch = !showAdvancedSearch"
                  >
                    <i class="fas fa-filter me-1"></i>
                    Advanced Filters
                  </button>
                </div>
              </div>

              <!-- Advanced Filters -->
              <div v-if="showAdvancedSearch" class="filters-section mb-4">
                <div class="filter-group mb-3">
                  <h6 class="filter-title">Categories</h6>
                  <div class="filter-options">
                    <div
                      v-for="category in categories"
                      :key="category.id"
                      class="form-check"
                    >
                      <input
                        :id="`cat-${category.id}`"
                        v-model="selectedCategories"
                        :value="category.id"
                        type="checkbox"
                        class="form-check-input"
                        @change="applyFilters"
                      />
                      <label :for="`cat-${category.id}`" class="form-check-label">
                        {{ category.name }} ({{ category.count }})
                      </label>
                    </div>
                  </div>
                </div>

                <div class="filter-group mb-3">
                  <h6 class="filter-title">Rating</h6>
                  <div class="rating-filter">
                    <div
                      v-for="rating in [5, 4, 3, 2, 1]"
                      :key="rating"
                      class="form-check"
                    >
                      <input
                        :id="`rating-${rating}`"
                        v-model="selectedRating"
                        :value="rating"
                        type="radio"
                        name="rating"
                        class="form-check-input"
                        @change="applyFilters"
                      />
                      <label :for="`rating-${rating}`" class="form-check-label">
                        <div class="star-rating">
                          <i
                            v-for="n in 5"
                            :key="n"
                            :class="n <= rating ? 'fas fa-star' : 'far fa-star'"
                          ></i>
                        </div>
                        & up
                      </label>
                    </div>
                  </div>
                </div>

                <div class="filter-group mb-3">
                  <h6 class="filter-title">Difficulty</h6>
                  <select v-model="selectedDifficulty" class="form-select" @change="applyFilters">
                    <option value="">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>

                <div class="filter-group mb-3">
                  <h6 class="filter-title">Duration</h6>
                  <select v-model="selectedDuration" class="form-select" @change="applyFilters">
                    <option value="">Any Duration</option>
                    <option value="short">&lt; 2 hours</option>
                    <option value="medium">2-8 hours</option>
                    <option value="long">1-3 days</option>
                    <option value="extended">&gt; 3 days</option>
                  </select>
                </div>

                <button class="btn btn-sm btn-outline-secondary w-100" @click="clearFilters">
                  Clear Filters
                </button>
              </div>

              <!-- Popular Tags -->
              <div class="tags-section mb-4">
                <h6 class="section-title">Popular Tags</h6>
                <div class="tag-cloud">
                  <span
                    v-for="tag in popularTags"
                    :key="tag.id"
                    class="tag-pill"
                    :class="{ active: selectedTags.includes(tag.name) }"
                    @click="toggleTag(tag.name)"
                  >
                    {{ tag.name }} ({{ tag.count }})
                  </span>
                </div>
              </div>

              <!-- Quick Navigation -->
              <div class="navigation-section">
                <h6 class="section-title">Quick Access</h6>
                <ul class="nav flex-column">
                  <li class="nav-item">
                    <a
                      class="nav-link"
                      :class="{ active: currentView === 'all' }"
                      @click="setView('all')"
                    >
                      <i class="fas fa-th me-2"></i>All Scenarios
                    </a>
                  </li>
                  <li class="nav-item">
                    <a
                      class="nav-link"
                      :class="{ active: currentView === 'featured' }"
                      @click="setView('featured')"
                    >
                      <i class="fas fa-star me-2"></i>Featured
                    </a>
                  </li>
                  <li class="nav-item">
                    <a
                      class="nav-link"
                      :class="{ active: currentView === 'popular' }"
                      @click="setView('popular')"
                    >
                      <i class="fas fa-fire me-2"></i>Popular
                    </a>
                  </li>
                  <li class="nav-item">
                    <a
                      class="nav-link"
                      :class="{ active: currentView === 'recent' }"
                      @click="setView('recent')"
                    >
                      <i class="fas fa-clock me-2"></i>Recently Added
                    </a>
                  </li>
                  <li class="nav-item">
                    <a
                      class="nav-link"
                      :class="{ active: currentView === 'favorites' }"
                      @click="setView('favorites')"
                    >
                      <i class="fas fa-heart me-2"></i>My Favorites
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Main Content Area -->
          <div class="col-md-6">
            <!-- Sort and View Options -->
            <div class="content-header mb-3">
              <div class="row align-items-center">
                <div class="col-md-6">
                  <div class="results-info">
                    Showing {{ scenarios.length }} of {{ totalScenarios }} scenarios
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="view-controls d-flex align-items-center justify-content-end">
                    <select v-model="sortBy" class="form-select form-select-sm me-2" @change="applySorting">
                      <option value="created_desc">Newest First</option>
                      <option value="created_asc">Oldest First</option>
                      <option value="rating_desc">Highest Rated</option>
                      <option value="downloads_desc">Most Downloaded</option>
                      <option value="name_asc">Name A-Z</option>
                    </select>
                    <div class="btn-group" role="group">
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-secondary"
                        :class="{ active: viewMode === 'grid' }"
                        @click="viewMode = 'grid'"
                      >
                        <i class="fas fa-th"></i>
                      </button>
                      <button
                        type="button"
                        class="btn btn-sm btn-outline-secondary"
                        :class="{ active: viewMode === 'list' }"
                        @click="viewMode = 'list'"
                      >
                        <i class="fas fa-list"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-state text-center py-5">
              <div class="spinner-border text-primary mb-3" role="status"></div>
              <p>Loading scenarios...</p>
            </div>

            <!-- Scenarios Grid/List -->
            <div v-else class="scenarios-container">
              <div
                v-if="viewMode === 'grid'"
                class="row"
              >
                <div
                  v-for="scenario in scenarios"
                  :key="scenario.id"
                  class="col-md-6 mb-4"
                >
                  <ScenarioCard
                    :scenario="scenario"
                    @select="openScenarioDetail"
                    @favorite="toggleScenarioFavorite"
                    @apply="applyScenario"
                    @share="shareScenario"
                  />
                </div>
              </div>

              <div
                v-else
                class="scenarios-list"
              >
                <ScenarioListItem
                  v-for="scenario in scenarios"
                  :key="scenario.id"
                  :scenario="scenario"
                  @select="openScenarioDetail"
                  @favorite="toggleScenarioFavorite"
                  @apply="applyScenario"
                  @share="shareScenario"
                />
              </div>

              <!-- Empty State -->
              <div v-if="scenarios.length === 0" class="empty-state text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No scenarios found</h5>
                <p class="text-muted">Try adjusting your search criteria or browse all scenarios.</p>
                <button class="btn btn-primary" @click="clearFilters">
                  Clear All Filters
                </button>
              </div>

              <!-- Pagination -->
              <nav v-if="totalPages > 1" class="mt-4">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <a class="page-link" @click="changePage(currentPage - 1)">Previous</a>
                  </li>
                  <li
                    v-for="page in visiblePages"
                    :key="page"
                    class="page-item"
                    :class="{ active: page === currentPage }"
                  >
                    <a class="page-link" @click="changePage(page)">{{ page }}</a>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <a class="page-link" @click="changePage(currentPage + 1)">Next</a>
                  </li>
                </ul>
              </nav>
            </div>
          </div>

          <!-- Right Sidebar - AI Assistant and Community -->
          <div class="col-md-3">
            <!-- AI Assistant Panel -->
            <div class="assistant-section mb-4">
              <AssistantPanel
                context="scenario-hub"
                :context-data="{
                  currentScenarios: scenarios.length,
                  selectedFilters: getActiveFilters(),
                  userPreferences: userPreferences
                }"
                @recommendation="handleAIRecommendation"
              />
            </div>

            <!-- AI Recommendations -->
            <div v-if="recommendations.length > 0" class="recommendations-section mb-4">
              <h6 class="section-title">
                <i class="fas fa-robot me-2"></i>AI Recommendations
              </h6>
              <div class="recommendation-list">
                <div
                  v-for="rec in recommendations"
                  :key="rec.scenarioId"
                  class="recommendation-item"
                  @click="openScenarioDetail(rec.scenarioId)"
                >
                  <div class="rec-content">
                    <h6 class="rec-title">{{ rec.title }}</h6>
                    <p class="rec-reason">{{ rec.reason }}</p>
                    <div class="rec-meta">
                      <span class="confidence">{{ rec.confidence }}% match</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Community Activity -->
            <div class="community-section mb-4">
              <h6 class="section-title">
                <i class="fas fa-users me-2"></i>Community Activity
              </h6>
              <div class="activity-feed">
                <div
                  v-for="activity in communityActivity"
                  :key="activity.id"
                  class="activity-item"
                >
                  <div class="activity-avatar">
                    <img :src="activity.user.avatar" :alt="activity.user.name" />
                  </div>
                  <div class="activity-content">
                    <p class="activity-text">
                      <strong>{{ activity.user.name }}</strong>
                      {{ activity.action }}
                      <a @click="openScenarioDetail(activity.scenarioId)">
                        {{ activity.scenarioTitle }}
                      </a>
                    </p>
                    <small class="activity-time">{{ formatTime(activity.timestamp) }}</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Popular Contributors -->
            <div class="contributors-section mb-4">
              <h6 class="section-title">
                <i class="fas fa-award me-2"></i>Top Contributors
              </h6>
              <div class="contributors-list">
                <div
                  v-for="contributor in topContributors"
                  :key="contributor.id"
                  class="contributor-item"
                >
                  <div class="contributor-avatar">
                    <img :src="contributor.avatar" :alt="contributor.name" />
                  </div>
                  <div class="contributor-info">
                    <h6 class="contributor-name">{{ contributor.name }}</h6>
                    <p class="contributor-stats">
                      {{ contributor.scenarioCount }} scenarios •
                      ⭐ {{ contributor.avgRating }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="quick-actions-section">
              <h6 class="section-title">Quick Actions</h6>
              <div class="d-grid gap-2">
                <button class="btn btn-outline-primary btn-sm" @click="showImportModal = true">
                  <i class="fas fa-upload me-1"></i>Import Scenario
                </button>
                <button class="btn btn-outline-info btn-sm" @click="openCommunityForum">
                  <i class="fas fa-comments me-1"></i>Community Forum
                </button>
                <button class="btn btn-outline-warning btn-sm" @click="showHelpModal = true">
                  <i class="fas fa-question-circle me-1"></i>Help & Guide
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <!-- Scenario Detail Modal -->
    <ScenarioDetailModal
      v-if="selectedScenario"
      :scenario="selectedScenario"
      :show="showDetailModal"
      @hide="closeScenarioDetail"
      @apply="applyScenario"
      @customize="customizeScenario"
      @rate="rateScenario"
      @review="addReview"
      @comment="addComment"
      @share="shareScenario"
    />

    <!-- Publish Scenario Modal -->
    <PublishScenarioModal
      :show="showPublishModal"
      @hide="showPublishModal = false"
      @published="onScenarioPublished"
    />

    <!-- Import Scenario Modal -->
    <ImportScenarioModal
      :show="showImportModal"
      @hide="showImportModal = false"
      @imported="onScenarioImported"
    />

    <!-- Scenario Application Wizard -->
    <ScenarioApplicationWizard
      v-if="applicationScenario"
      :scenario="applicationScenario"
      :show="showApplicationWizard"
      @hide="closeApplicationWizard"
      @applied="onScenarioApplied"
    />

    <!-- Customization Modal -->
    <ScenarioCustomizationModal
      v-if="customizationScenario"
      :scenario="customizationScenario"
      :show="showCustomizationModal"
      @hide="closeCustomizationModal"
      @customized="onScenarioCustomized"
    />

    <!-- My Contributions Modal -->
    <MyContributionsModal
      :show="showMyContributions"
      @hide="showMyContributions = false"
    />

    <!-- AI Scenario Wizard Modal -->
    <div v-if="showAIWizard" class="modal-overlay" @click="closeAIWizard">
      <div class="modal-dialog modal-fullscreen" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-magic me-2 text-warning"></i>
              AI Scenario Generation Wizard
            </h5>
            <button @click="closeAIWizard" class="btn-close" aria-label="Close">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body p-0">
            <AIScenarioWizard
              @scenario-generated="onAIScenarioGenerated"
              @wizard-closed="closeAIWizard"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { debounce } from 'lodash'
import bcmScenarioHubService from '@/services/bcmScenarioHub'
import AssistantPanel from '@/components/assistant/AssistantPanel.vue'

// Import child components (these would need to be created)
import ScenarioCard from '@/components/scenario-hub/ScenarioCard.vue'
import ScenarioListItem from '@/components/scenario-hub/ScenarioListItem.vue'
import ScenarioDetailModal from '@/components/scenario-hub/ScenarioDetailModal.vue'
import PublishScenarioModal from '@/components/scenario-hub/PublishScenarioModal.vue'
import ImportScenarioModal from '@/components/scenario-hub/ImportScenarioModal.vue'
import ScenarioApplicationWizard from '@/components/scenario-hub/ScenarioApplicationWizard.vue'
import ScenarioCustomizationModal from '@/components/scenario-hub/ScenarioCustomizationModal.vue'
import MyContributionsModal from '@/components/scenario-hub/MyContributionsModal.vue'
import AIScenarioWizard from '@/components/ai/AIScenarioWizard.vue'

export default {
  name: 'BCMScenarioHub',
  components: {
    AssistantPanel,
    ScenarioCard,
    ScenarioListItem,
    ScenarioDetailModal,
    PublishScenarioModal,
    ImportScenarioModal,
    ScenarioApplicationWizard,
    ScenarioCustomizationModal,
    MyContributionsModal,
    AIScenarioWizard
  },
  setup() {
    // Reactive state
    const loading = ref(false)
    const scenarios = ref([])
    const selectedScenario = ref(null)
    const totalScenarios = ref(0)
    const currentPage = ref(1)
    const totalPages = ref(0)

    // UI state
    const viewMode = ref('grid')
    const currentView = ref('all')
    const showAdvancedSearch = ref(false)
    const showDetailModal = ref(false)
    const showPublishModal = ref(false)
    const showImportModal = ref(false)
    const showApplicationWizard = ref(false)
    const showCustomizationModal = ref(false)
    const showMyContributions = ref(false)
    const showHelpModal = ref(false)
    const showAIWizard = ref(false)

    // Search and filters
    const searchQuery = ref('')
    const selectedCategories = ref([])
    const selectedTags = ref([])
    const selectedRating = ref('')
    const selectedDifficulty = ref('')
    const selectedDuration = ref('')
    const sortBy = ref('created_desc')

    // Data
    const categories = ref([])
    const popularTags = ref([])
    const marketplaceStats = ref({})
    const recommendations = ref([])
    const communityActivity = ref([])
    const topContributors = ref([])

    // Modal data
    const applicationScenario = ref(null)
    const customizationScenario = ref(null)

    // User preferences
    const userPreferences = ref({})

    // Computed properties
    const visiblePages = computed(() => {
      const pages = []
      const current = currentPage.value
      const total = totalPages.value
      const maxVisible = 5

      let start = Math.max(1, current - Math.floor(maxVisible / 2))
      let end = Math.min(total, start + maxVisible - 1)

      if (end - start + 1 < maxVisible) {
        start = Math.max(1, end - maxVisible + 1)
      }

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    })

    // Methods
    const loadScenarios = async (params = {}) => {
      try {
        loading.value = true
        const response = await bcmScenarioHubService.getScenarios({
          page: currentPage.value,
          limit: 20,
          search: searchQuery.value,
          categories: selectedCategories.value,
          tags: selectedTags.value,
          rating: selectedRating.value,
          difficulty: selectedDifficulty.value,
          duration: selectedDuration.value,
          sort: sortBy.value,
          ...params
        })

        scenarios.value = response.scenarios || []
        totalScenarios.value = response.total || 0
        totalPages.value = Math.ceil(totalScenarios.value / 20)
      } catch (error) {
        console.error('Error loading scenarios:', error)
      } finally {
        loading.value = false
      }
    }

    const loadInitialData = async () => {
      try {
        const [categoriesRes, tagsRes, statsRes, recRes] = await Promise.all([
          bcmScenarioHubService.getCategories(),
          bcmScenarioHubService.getPopularTags(),
          bcmScenarioHubService.getMarketplaceStats(),
          bcmScenarioHubService.getRecommendations('current-user')
        ])

        categories.value = categoriesRes.categories || []
        popularTags.value = tagsRes.tags || []
        marketplaceStats.value = statsRes || {}
        recommendations.value = recRes.recommendations || []
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    const performSearch = () => {
      currentPage.value = 1
      loadScenarios()
    }

    const debouncedSearch = debounce(() => {
      performSearch()
    }, 300)

    const applyFilters = () => {
      currentPage.value = 1
      loadScenarios()
    }

    const applySorting = () => {
      loadScenarios()
    }

    const clearFilters = () => {
      searchQuery.value = ''
      selectedCategories.value = []
      selectedTags.value = []
      selectedRating.value = ''
      selectedDifficulty.value = ''
      selectedDuration.value = ''
      currentPage.value = 1
      loadScenarios()
    }

    const toggleTag = (tagName) => {
      const index = selectedTags.value.indexOf(tagName)
      if (index > -1) {
        selectedTags.value.splice(index, 1)
      } else {
        selectedTags.value.push(tagName)
      }
      applyFilters()
    }

    const setView = (view) => {
      currentView.value = view
      currentPage.value = 1

      switch (view) {
        case 'featured':
          loadScenarios({ featured: true })
          break
        case 'popular':
          loadScenarios({ sort: 'downloads_desc' })
          break
        case 'recent':
          loadScenarios({ sort: 'created_desc' })
          break
        case 'favorites':
          loadFavorites()
          break
        default:
          loadScenarios()
      }
    }

    const loadFavorites = async () => {
      try {
        loading.value = true
        const response = await bcmScenarioHubService.getFavorites()
        scenarios.value = response.scenarios || []
        totalScenarios.value = response.total || 0
        totalPages.value = Math.ceil(totalScenarios.value / 20)
      } catch (error) {
        console.error('Error loading favorites:', error)
      } finally {
        loading.value = false
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        loadScenarios()
      }
    }

    const openScenarioDetail = async (scenarioId) => {
      try {
        const scenario = await bcmScenarioHubService.getScenario(scenarioId)
        selectedScenario.value = scenario
        showDetailModal.value = true
      } catch (error) {
        console.error('Error loading scenario details:', error)
      }
    }

    const closeScenarioDetail = () => {
      selectedScenario.value = null
      showDetailModal.value = false
    }

    const toggleScenarioFavorite = async (scenarioId) => {
      try {
        await bcmScenarioHubService.toggleFavorite(scenarioId)
        // Update scenario in list
        const scenario = scenarios.value.find(s => s.id === scenarioId)
        if (scenario) {
          scenario.isFavorited = !scenario.isFavorited
        }
      } catch (error) {
        console.error('Error toggling favorite:', error)
      }
    }

    const applyScenario = (scenario) => {
      applicationScenario.value = scenario
      showApplicationWizard.value = true
      showDetailModal.value = false
    }

    const customizeScenario = (scenario) => {
      customizationScenario.value = scenario
      showCustomizationModal.value = true
      showDetailModal.value = false
    }

    const closeApplicationWizard = () => {
      applicationScenario.value = null
      showApplicationWizard.value = false
    }

    const closeCustomizationModal = () => {
      customizationScenario.value = null
      showCustomizationModal.value = false
    }

    const shareScenario = async (scenario) => {
      if (navigator.share) {
        try {
          await navigator.share({
            title: scenario.title,
            text: scenario.description,
            url: `${window.location.origin}/scenario-hub/${scenario.id}`
          })
        } catch (error) {
          console.log('Error sharing:', error)
        }
      } else {
        // Fallback: copy to clipboard
        const url = `${window.location.origin}/scenario-hub/${scenario.id}`
        await navigator.clipboard.writeText(url)
        // Show toast notification
      }
    }

    const rateScenario = async (scenarioId, rating, review) => {
      try {
        await bcmScenarioHubService.rateScenario(scenarioId, rating, review)
        // Refresh scenario details
        if (selectedScenario.value?.id === scenarioId) {
          selectedScenario.value = await bcmScenarioHubService.getScenario(scenarioId)
        }
      } catch (error) {
        console.error('Error rating scenario:', error)
      }
    }

    const addReview = async (scenarioId, reviewData) => {
      try {
        await bcmScenarioHubService.addReview(scenarioId, reviewData)
        // Refresh scenario details
        if (selectedScenario.value?.id === scenarioId) {
          selectedScenario.value = await bcmScenarioHubService.getScenario(scenarioId)
        }
      } catch (error) {
        console.error('Error adding review:', error)
      }
    }

    const addComment = async (scenarioId, commentData) => {
      try {
        await bcmScenarioHubService.addComment(scenarioId, commentData)
        // Refresh scenario details
        if (selectedScenario.value?.id === scenarioId) {
          selectedScenario.value = await bcmScenarioHubService.getScenario(scenarioId)
        }
      } catch (error) {
        console.error('Error adding comment:', error)
      }
    }

    const handleAIRecommendation = (recommendation) => {
      // Handle AI assistant recommendations
      if (recommendation.action === 'view_scenario') {
        openScenarioDetail(recommendation.scenarioId)
      } else if (recommendation.action === 'search') {
        searchQuery.value = recommendation.query
        performSearch()
      }
    }

    const onScenarioPublished = (scenario) => {
      // Refresh the scenario list
      loadScenarios()
    }

    const onScenarioImported = (scenario) => {
      // Refresh the scenario list
      loadScenarios()
    }

    const onScenarioApplied = (result) => {
      // Handle successful scenario application
      closeApplicationWizard()
      // Maybe navigate to exercise or show success message
    }

    const onScenarioCustomized = (customizedScenario) => {
      // Handle scenario customization completion
      closeCustomizationModal()
    }

    const closeAIWizard = () => {
      showAIWizard.value = false
    }

    const onAIScenarioGenerated = (generatedScenario) => {
      // Handle successful AI scenario generation
      closeAIWizard()

      // Add the generated scenario to the scenarios list
      scenarios.value.unshift({
        ...generatedScenario,
        isAIGenerated: true,
        generatedAt: new Date().toISOString()
      })

      // Update stats
      if (marketplaceStats.value.totalScenarios) {
        marketplaceStats.value.totalScenarios += 1
      }

      // Show success message
      toast?.success?.('AI scenario generated successfully! Check it out in the hub.')
    }

    const openCommunityForum = () => {
      // Navigate to community forum
      // This could be a separate route or external link
    }

    const getActiveFilters = () => {
      return {
        categories: selectedCategories.value,
        tags: selectedTags.value,
        rating: selectedRating.value,
        difficulty: selectedDifficulty.value,
        duration: selectedDuration.value
      }
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleDateString()
    }

    // Watchers
    watch(currentView, (newView) => {
      setView(newView)
    })

    // Lifecycle
    onMounted(async () => {
      await loadInitialData()
      await loadScenarios()
    })

    return {
      // State
      loading,
      scenarios,
      selectedScenario,
      totalScenarios,
      currentPage,
      totalPages,
      viewMode,
      currentView,
      showAdvancedSearch,
      showDetailModal,
      showPublishModal,
      showImportModal,
      showApplicationWizard,
      showCustomizationModal,
      showMyContributions,
      showHelpModal,
      showAIWizard,

      // Filters
      searchQuery,
      selectedCategories,
      selectedTags,
      selectedRating,
      selectedDifficulty,
      selectedDuration,
      sortBy,

      // Data
      categories,
      popularTags,
      marketplaceStats,
      recommendations,
      communityActivity,
      topContributors,
      applicationScenario,
      customizationScenario,
      userPreferences,

      // Computed
      visiblePages,

      // Methods
      loadScenarios,
      performSearch,
      debouncedSearch,
      applyFilters,
      applySorting,
      clearFilters,
      toggleTag,
      setView,
      changePage,
      openScenarioDetail,
      closeScenarioDetail,
      toggleScenarioFavorite,
      applyScenario,
      customizeScenario,
      closeApplicationWizard,
      closeCustomizationModal,
      shareScenario,
      rateScenario,
      addReview,
      addComment,
      handleAIRecommendation,
      onScenarioPublished,
      onScenarioImported,
      onScenarioApplied,
      onScenarioCustomized,
      closeAIWizard,
      onAIScenarioGenerated,
      openCommunityForum,
      getActiveFilters,
      formatTime
    }
  }
}
</script>

<style scoped>
.bcm-scenario-hub {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

/* Header Styles */
.hub-header {
  background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.hub-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #FF6B35;
}

.hub-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0;
}

.hub-actions .btn {
  border-radius: 8px;
  padding: 0.5rem 1rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #FF6B35;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

/* Content Styles */
.hub-content {
  padding: 0 0 2rem;
}

.sidebar-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.section-title {
  font-weight: 600;
  color: #1A1A1A;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.filter-title {
  font-weight: 600;
  color: #666;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.filter-options {
  max-height: 200px;
  overflow-y: auto;
}

.star-rating {
  color: #FF6B35;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-pill {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-pill:hover {
  background: #e9ecef;
  border-color: #4A90E2;
}

.tag-pill.active {
  background: #4A90E2;
  color: white;
  border-color: #4A90E2;
}

.nav-link {
  color: #666;
  padding: 0.5rem 0;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #4A90E2;
  background: none;
}

.nav-link.active {
  color: #FF6B35;
  font-weight: 600;
}

/* Content Header */
.content-header {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.results-info {
  color: #666;
  font-size: 0.9rem;
}

.view-controls .form-select {
  width: auto;
  min-width: 150px;
}

/* Scenarios Container */
.scenarios-container {
  min-height: 400px;
}

.loading-state {
  color: #666;
}

.empty-state {
  color: #666;
}

/* Assistant Section */
.assistant-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  overflow: hidden;
}

/* Recommendations */
.recommendations-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.recommendation-item {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.recommendation-item:hover {
  border-color: #4A90E2;
  box-shadow: 0 2px 4px rgba(74, 144, 226, 0.1);
}

.rec-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #1A1A1A;
}

.rec-reason {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.confidence {
  font-size: 0.75rem;
  color: #4A90E2;
  font-weight: 500;
}

/* Community Section */
.community-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.activity-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.activity-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 0.75rem;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.activity-time {
  color: #999;
  font-size: 0.75rem;
}

/* Contributors Section */
.contributors-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.contributor-item {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.contributor-item:last-child {
  margin-bottom: 0;
}

.contributor-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 0.75rem;
}

.contributor-name {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #1A1A1A;
}

.contributor-stats {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0;
}

/* Quick Actions */
.quick-actions-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hub-title {
    font-size: 2rem;
  }

  .stat-card {
    margin-bottom: 1rem;
  }

  .content-header .row {
    flex-direction: column;
  }

  .view-controls {
    justify-content: flex-start !important;
    margin-top: 1rem;
  }

  .viewMode = 'list' {
    display: block;
  }
}

/* Animation Classes */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Custom Scrollbar */
.filter-options::-webkit-scrollbar {
  width: 4px;
}

.filter-options::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.filter-options::-webkit-scrollbar-thumb {
  background: #4A90E2;
  border-radius: 2px;
}

.filter-options::-webkit-scrollbar-thumb:hover {
  background: #FF6B35;
}

/* AI Button Styles */
.btn-ai-primary {
  background: linear-gradient(135deg, #FF6B35 0%, #F5621C 100%);
  border: none;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
}

.btn-ai-primary:hover {
  background: linear-gradient(135deg, #F5621C 0%, #E5571A 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
  color: white;
}

.btn-ai-primary:focus {
  background: linear-gradient(135deg, #F5621C 0%, #E5571A 100%);
  box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.25);
  color: white;
}

.btn-ai-primary i {
  margin-right: 0.5rem;
  animation: sparkle 2s infinite;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.1) rotate(180deg); }
}

/* AI Wizard Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  backdrop-filter: blur(4px);
}

.modal-fullscreen {
  width: 95vw;
  height: 95vh;
  max-width: none;
  max-height: none;
}

.modal-fullscreen .modal-content {
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3);
}

.modal-fullscreen .modal-header {
  background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
  color: white;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #444;
}

.modal-fullscreen .modal-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.modal-fullscreen .btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.modal-fullscreen .btn-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #FF6B35;
}

.modal-fullscreen .modal-body {
  height: calc(100% - 80px);
  overflow-y: auto;
  background: #f8f9fa;
}
</style>