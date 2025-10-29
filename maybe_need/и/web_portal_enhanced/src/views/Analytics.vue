<template>
  <DefaultLayout>
    <div class="analytics-main-dashboard">
      <!-- Page Header -->
      <div class="page-header bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="py-6">
            <div class="md:flex md:items-center md:justify-between">
              <div class="flex-1 min-w-0">
                <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                  <i class="fas fa-chart-line text-blue-600 mr-4"></i>
                  Analytics Dashboard
                </h1>
                <p class="mt-2 text-gray-600">
                  Intelligence & Analytics - AI-powered insights for your BCM platform
                </p>
              </div>
              <div class="mt-4 flex md:mt-0 md:ml-4">
                <button
                  @click="refreshAllDashboards"
                  class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
                  :disabled="isRefreshing"
                >
                  <i class="fas fa-sync mr-2" :class="{ 'fa-spin': isRefreshing }"></i>
                  {{ isRefreshing ? 'Refreshing...' : 'Refresh All' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="bg-white border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav class="flex space-x-8" aria-label="Tabs">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <i :class="tab.icon" class="mr-2"></i>
              {{ tab.name }}
            </button>
          </nav>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <!-- Learning Analytics Tab -->
        <div v-if="activeTab === 'learning'" class="space-y-6">
          <LearningDashboard ref="learningDashboard" />
        </div>

        <!-- Executive Dashboard Tab -->
        <div v-if="activeTab === 'executive'" class="space-y-6">
          <ExecutiveDashboard ref="executiveDashboard" />
        </div>

        <!-- Knowledge Analytics Tab -->
        <div v-if="activeTab === 'knowledge'" class="space-y-6">
          <KnowledgeDashboard ref="knowledgeDashboard" />
        </div>

        <!-- System Performance Tab -->
        <div v-if="activeTab === 'performance'" class="space-y-6">
          <SystemPerformanceDashboard ref="performanceDashboard" />
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import LearningDashboard from '@/components/analytics/LearningDashboard.vue'
import ExecutiveDashboard from '@/components/analytics/ExecutiveDashboard.vue'
import KnowledgeDashboard from '@/components/analytics/KnowledgeDashboard.vue'
import SystemPerformanceDashboard from '@/components/analytics/SystemPerformanceDashboard.vue'

const toast = useToast()

// Tab management
const activeTab = ref('learning')
const isRefreshing = ref(false)

const tabs = [
  {
    id: 'learning',
    name: 'AI Learning Analytics',
    icon: 'fas fa-brain'
  },
  {
    id: 'executive',
    name: 'Executive Overview',
    icon: 'fas fa-chart-bar'
  },
  {
    id: 'knowledge',
    name: 'Knowledge Base',
    icon: 'fas fa-book'
  },
  {
    id: 'performance',
    name: 'System Performance',
    icon: 'fas fa-server'
  }
]

// Refs for dashboard components
const learningDashboard = ref<InstanceType<typeof LearningDashboard> | null>(null)
const executiveDashboard = ref<InstanceType<typeof ExecutiveDashboard> | null>(null)
const knowledgeDashboard = ref<InstanceType<typeof KnowledgeDashboard> | null>(null)
const performanceDashboard = ref<InstanceType<typeof SystemPerformanceDashboard> | null>(null)

// Methods
const refreshAllDashboards = async () => {
  isRefreshing.value = true

  try {
    const promises = []

    // Refresh active dashboard
    switch (activeTab.value) {
      case 'learning':
        if (learningDashboard.value?.refreshAnalytics) {
          promises.push(learningDashboard.value.refreshAnalytics())
        }
        break
      case 'executive':
        if (executiveDashboard.value?.refreshAnalytics) {
          promises.push(executiveDashboard.value.refreshAnalytics())
        }
        break
      case 'knowledge':
        if (knowledgeDashboard.value?.refreshAnalytics) {
          promises.push(knowledgeDashboard.value.refreshAnalytics())
        }
        break
      case 'performance':
        if (performanceDashboard.value?.refreshAnalytics) {
          promises.push(performanceDashboard.value.refreshAnalytics())
        }
        break
    }

    await Promise.all(promises)
    toast.success('All dashboards refreshed successfully')

  } catch (error: any) {
    console.error('Error refreshing dashboards:', error)
    toast.error('Failed to refresh some dashboards: ' + error.message)
  } finally {
    isRefreshing.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Initialize with learning dashboard
  console.log('Analytics dashboard mounted')
})
</script>

<style scoped>
.analytics-main-dashboard {
  @apply min-h-screen bg-gray-50;
}

.page-header {
  @apply sticky top-0 z-10;
}

/* Custom tab styles */
nav button {
  @apply relative;
}

nav button:focus {
  @apply outline-none ring-2 ring-blue-500 ring-opacity-50;
}

/* Loading states */
.loading-overlay {
  @apply absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-20;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-header h1 {
    @apply text-2xl;
  }

  nav {
    @apply overflow-x-auto;
  }

  nav button {
    @apply flex-shrink-0;
  }
}
</style>