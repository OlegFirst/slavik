<template>
  <div class="knowledge-dashboard">
    <!-- Knowledge Base Statistics -->
    <div class="stats-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="stat-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
        <div class="flex items-center">
          <div class="stat-icon w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-book text-blue-600 text-xl"></i>
          </div>
          <div class="stat-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ stats.total_articles || 0 }}</h3>
            <p class="text-gray-600 text-sm">Total Articles</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
        <div class="flex items-center">
          <div class="stat-icon w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-robot text-green-600 text-xl"></i>
          </div>
          <div class="stat-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ stats.ai_generated || 0 }}</h3>
            <p class="text-gray-600 text-sm">AI Generated</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-purple-500">
        <div class="flex items-center">
          <div class="stat-icon w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-eye text-purple-600 text-xl"></i>
          </div>
          <div class="stat-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ stats.total_views || 0 }}</h3>
            <p class="text-gray-600 text-sm">Total Views</p>
          </div>
        </div>
      </div>

      <div class="stat-card bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
        <div class="flex items-center">
          <div class="stat-icon w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mr-4">
            <i class="fas fa-star text-yellow-600 text-xl"></i>
          </div>
          <div class="stat-content">
            <h3 class="text-2xl font-bold text-gray-900">{{ stats.avg_rating || 0 }}</h3>
            <p class="text-gray-600 text-sm">Average Rating</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Content Analytics -->
    <div class="content-analytics grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Article Categories Distribution -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Content Distribution by Category</h3>
        </div>
        <div class="chart-body">
          <Doughnut
            v-if="categoryDistributionData.datasets"
            :data="categoryDistributionData"
            :options="doughnutOptions"
            class="w-full h-64"
          />
        </div>
      </div>

      <!-- Article Views Trend -->
      <div class="chart-card bg-white rounded-lg shadow-sm p-6">
        <div class="chart-header mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Article Views Trend</h3>
        </div>
        <div class="chart-body">
          <Line
            v-if="viewsTrendData.datasets"
            :data="viewsTrendData"
            :options="lineChartOptions"
            class="w-full h-64"
          />
        </div>
      </div>
    </div>

    <!-- Top Performing Articles -->
    <div class="top-articles bg-white rounded-lg shadow-sm p-6 mb-8">
      <div class="section-header flex justify-between items-center mb-6">
        <h3 class="text-lg font-semibold text-gray-900">Top Performing Articles</h3>
        <button
          @click="viewAllArticles"
          class="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
        >
          View All Articles
          <i class="fas fa-arrow-right ml-1"></i>
        </button>
      </div>

      <div class="articles-list space-y-4">
        <div
          v-for="article in topArticles"
          :key="article.id"
          class="article-item bg-gray-50 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-start">
            <div class="article-info flex-1">
              <div class="flex items-center mb-2">
                <h4 class="font-semibold text-gray-900 mr-3">{{ article.title }}</h4>
                <span
                  v-if="article.article_type === 'ai_generated'"
                  class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full"
                >
                  <i class="fas fa-robot mr-1"></i>AI
                </span>
              </div>
              <p class="text-gray-600 text-sm mb-3">{{ article.summary }}</p>
              <div class="article-meta flex items-center space-x-4 text-xs text-gray-500">
                <span class="flex items-center">
                  <i class="fas fa-folder mr-1"></i>
                  {{ article.category }}
                </span>
                <span class="flex items-center">
                  <i class="fas fa-eye mr-1"></i>
                  {{ article.view_count }} views
                </span>
                <span class="flex items-center">
                  <i class="fas fa-star mr-1"></i>
                  {{ article.usefulness_score }}/5
                </span>
                <span class="flex items-center">
                  <i class="fas fa-bookmark mr-1"></i>
                  {{ article.bookmark_count }} bookmarks
                </span>
              </div>
            </div>
            <div class="article-actions flex space-x-2">
              <button
                @click="viewArticle(article.id)"
                class="bg-blue-50 text-blue-600 text-xs px-3 py-2 rounded hover:bg-blue-100 transition-colors"
              >
                <i class="fas fa-eye mr-1"></i>View
              </button>
              <button
                @click="editArticle(article.id)"
                class="bg-gray-50 text-gray-600 text-xs px-3 py-2 rounded hover:bg-gray-100 transition-colors"
              >
                <i class="fas fa-edit mr-1"></i>Edit
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Knowledge Base Analytics -->
    <div class="analytics-section grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Search Analytics -->
      <div class="search-analytics bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Search Analytics</h3>

        <div class="search-stats space-y-4">
          <div class="stat-row flex justify-between items-center">
            <span class="text-gray-600">Total Searches</span>
            <span class="font-semibold">{{ searchStats.total_searches }}</span>
          </div>
          <div class="stat-row flex justify-between items-center">
            <span class="text-gray-600">Successful Searches</span>
            <span class="font-semibold">{{ searchStats.successful_searches }}</span>
          </div>
          <div class="stat-row flex justify-between items-center">
            <span class="text-gray-600">Search Success Rate</span>
            <span class="font-semibold">{{ searchStats.success_rate }}%</span>
          </div>
        </div>

        <div class="popular-searches mt-6">
          <h4 class="font-medium text-gray-900 mb-3">Popular Search Terms</h4>
          <div class="search-terms space-y-2">
            <div
              v-for="term in popularSearchTerms"
              :key="term.term"
              class="flex justify-between items-center text-sm"
            >
              <span class="text-gray-700">{{ term.term }}</span>
              <span class="text-gray-500">{{ term.count }} searches</span>
            </div>
          </div>
        </div>
      </div>

      <!-- User Engagement -->
      <div class="engagement-analytics bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">User Engagement</h3>

        <div class="engagement-metrics space-y-4">
          <div class="metric-item">
            <div class="metric-header flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-600">Article Completion Rate</span>
              <span class="text-lg font-bold">{{ engagementMetrics.completion_rate }}%</span>
            </div>
            <div class="progress bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: engagementMetrics.completion_rate + '%' }"
              ></div>
            </div>
          </div>

          <div class="metric-item">
            <div class="metric-header flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-600">Average Time on Article</span>
              <span class="text-lg font-bold">{{ engagementMetrics.avg_time_on_article }}m</span>
            </div>
            <div class="progress bg-gray-200 rounded-full h-2">
              <div
                class="bg-green-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: (engagementMetrics.avg_time_on_article / 10) * 100 + '%' }"
              ></div>
            </div>
          </div>

          <div class="metric-item">
            <div class="metric-header flex justify-between items-center mb-2">
              <span class="text-sm font-medium text-gray-600">User Satisfaction</span>
              <span class="text-lg font-bold">{{ engagementMetrics.satisfaction_score }}/5</span>
            </div>
            <div class="progress bg-gray-200 rounded-full h-2">
              <div
                class="bg-yellow-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: (engagementMetrics.satisfaction_score / 5) * 100 + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <div class="engagement-actions mt-6">
          <button
            @click="generateEngagementReport"
            class="w-full bg-blue-600 text-white text-sm px-4 py-2 rounded hover:bg-blue-700 transition-colors"
          >
            <i class="fas fa-download mr-2"></i>
            Download Engagement Report
          </button>
        </div>
      </div>
    </div>

    <!-- Content Quality Insights -->
    <div class="quality-insights bg-white rounded-lg shadow-sm p-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4">Content Quality Insights</h3>

      <div class="insights-grid grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="insight-card bg-blue-50 rounded-lg p-4">
          <div class="insight-header flex items-center mb-2">
            <i class="fas fa-thumbs-up text-blue-600 mr-2"></i>
            <span class="font-medium text-blue-900">High Quality Articles</span>
          </div>
          <p class="text-2xl font-bold text-blue-900">{{ qualityInsights.high_quality_count }}</p>
          <p class="text-sm text-blue-700">Rating > 4.0</p>
        </div>

        <div class="insight-card bg-yellow-50 rounded-lg p-4">
          <div class="insight-header flex items-center mb-2">
            <i class="fas fa-exclamation-triangle text-yellow-600 mr-2"></i>
            <span class="font-medium text-yellow-900">Needs Improvement</span>
          </div>
          <p class="text-2xl font-bold text-yellow-900">{{ qualityInsights.needs_improvement_count }}</p>
          <p class="text-sm text-yellow-700">Rating < 3.0</p>
        </div>

        <div class="insight-card bg-green-50 rounded-lg p-4">
          <div class="insight-header flex items-center mb-2">
            <i class="fas fa-robot text-green-600 mr-2"></i>
            <span class="font-medium text-green-900">AI Enhancement Opportunities</span>
          </div>
          <p class="text-2xl font-bold text-green-900">{{ qualityInsights.ai_enhancement_opportunities }}</p>
          <p class="text-sm text-green-700">Articles that could benefit from AI</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import analyticsService from '@/services/analyticsService'

// Reactive data
const stats = ref<any>({})
const topArticles = ref<any[]>([])
const categoryDistributionData = ref<any>({})
const viewsTrendData = ref<any>({})
const searchStats = ref<any>({})
const popularSearchTerms = ref<any[]>([])
const engagementMetrics = ref<any>({})
const qualityInsights = ref<any>({})

// Chart options
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Methods
const loadKnowledgeAnalytics = async () => {
  try {
    const data = await analyticsService.getKnowledgeArticles()

    // Process the data
    stats.value = {
      total_articles: data.total || 0,
      ai_generated: data.articles?.filter((a: any) => a.article_type === 'ai_generated').length || 0,
      total_views: data.articles?.reduce((sum: number, a: any) => sum + (a.view_count || 0), 0) || 0,
      avg_rating: calculateAverageRating(data.articles)
    }

    topArticles.value = data.articles?.slice(0, 5) || []

    updateCharts(data)
    loadMockAnalytics() // Load additional analytics that aren't available yet

  } catch (error) {
    console.error('Failed to load knowledge analytics:', error)
    loadMockData()
  }
}

const calculateAverageRating = (articles: any[]) => {
  if (!articles || articles.length === 0) return 0
  const total = articles.reduce((sum, article) => sum + (article.usefulness_score || 0), 0)
  return (total / articles.length).toFixed(1)
}

const updateCharts = (data: any) => {
  // Category Distribution
  const categories = data.categories || []
  categoryDistributionData.value = {
    labels: categories.map((c: any) => c.name),
    datasets: [{
      data: categories.map((c: any) => c.count),
      backgroundColor: [
        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#6B7280'
      ]
    }]
  }

  // Views Trend (mock data for now)
  viewsTrendData.value = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Article Views',
      data: [120, 150, 180, 220, 190, 250],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  }
}

const loadMockAnalytics = () => {
  searchStats.value = {
    total_searches: 1250,
    successful_searches: 1125,
    success_rate: 90
  }

  popularSearchTerms.value = [
    { term: 'business continuity plan', count: 85 },
    { term: 'disaster recovery', count: 72 },
    { term: 'risk assessment', count: 58 },
    { term: 'crisis communication', count: 45 },
    { term: 'ISO 22301', count: 38 }
  ]

  engagementMetrics.value = {
    completion_rate: 78,
    avg_time_on_article: 6.5,
    satisfaction_score: 4.2
  }

  qualityInsights.value = {
    high_quality_count: 18,
    needs_improvement_count: 3,
    ai_enhancement_opportunities: 8
  }
}

const loadMockData = () => {
  stats.value = {
    total_articles: 45,
    ai_generated: 12,
    total_views: 2340,
    avg_rating: 4.3
  }

  topArticles.value = [
    {
      id: '1',
      title: 'Business Continuity Planning Best Practices',
      summary: 'Comprehensive guide to developing effective BCPs',
      category: 'Planning',
      view_count: 234,
      usefulness_score: 4.8,
      bookmark_count: 45,
      article_type: 'manual'
    },
    {
      id: '2',
      title: 'AI-Generated Crisis Communication Templates',
      summary: 'Ready-to-use templates for crisis communication',
      category: 'Communication',
      view_count: 189,
      usefulness_score: 4.5,
      bookmark_count: 32,
      article_type: 'ai_generated'
    }
  ]

  categoryDistributionData.value = {
    labels: ['Planning', 'Communication', 'Recovery', 'Training', 'Assessment'],
    datasets: [{
      data: [15, 8, 12, 6, 4],
      backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    }]
  }

  viewsTrendData.value = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [{
      label: 'Article Views',
      data: [120, 150, 180, 220, 190, 250],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  }

  loadMockAnalytics()
}

// Action methods
const viewAllArticles = () => {
  console.log('Navigate to all articles')
}

const viewArticle = (id: string) => {
  console.log('View article:', id)
}

const editArticle = (id: string) => {
  console.log('Edit article:', id)
}

const generateEngagementReport = () => {
  console.log('Generate engagement report')
}

const refreshAnalytics = async () => {
  await loadKnowledgeAnalytics()
}

// Expose method for parent component
defineExpose({
  refreshAnalytics
})

// Lifecycle
onMounted(() => {
  loadKnowledgeAnalytics()
})
</script>

<style scoped>
.knowledge-dashboard {
  @apply space-y-6;
}

.stat-card {
  @apply transition-transform hover:scale-105;
}

.chart-card {
  @apply transition-shadow hover:shadow-lg;
}

.article-item {
  @apply transition-all hover:bg-gray-100;
}

.insight-card {
  @apply transition-transform hover:scale-105;
}

.progress {
  @apply relative overflow-hidden;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .stats-grid {
    @apply grid-cols-1;
  }

  .content-analytics {
    @apply grid-cols-1;
  }

  .analytics-section {
    @apply grid-cols-1;
  }

  .insights-grid {
    @apply grid-cols-1;
  }
}
</style>