<template>
  <div class="digital-twin-page">
    <div class="page-header">
      <h1 class="page-title">Digital Twin</h1>
      <p class="page-description">
        Real-time 3D visualization and monitoring of your organization's business continuity infrastructure
      </p>
    </div>

    <div class="digital-twin-container">
      <!-- 3D Scene Container -->
      <div class="scene-container" ref="sceneContainer">
        <div class="scene-placeholder">
          <div class="placeholder-content">
            <div class="placeholder-icon">
              <CubeTransparentIcon class="w-24 h-24 text-blue-400" />
            </div>
            <h3 class="placeholder-title">3D Digital Twin Visualization</h3>
            <p class="placeholder-description">
              Interactive 3D model of your business continuity infrastructure will be rendered here
            </p>
            <div class="placeholder-features">
              <div class="feature-item">
                <CheckIcon class="w-5 h-5 text-green-400" />
                <span>Real-time data visualization</span>
              </div>
              <div class="feature-item">
                <CheckIcon class="w-5 h-5 text-green-400" />
                <span>Interactive 3D models</span>
              </div>
              <div class="feature-item">
                <CheckIcon class="w-5 h-5 text-green-400" />
                <span>Performance monitoring</span>
              </div>
              <div class="feature-item">
                <CheckIcon class="w-5 h-5 text-green-400" />
                <span>Risk assessment overlay</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Control Panel -->
      <div class="control-panel">
        <div class="panel-section">
          <h3 class="section-title">Visualization Settings</h3>
          <div class="control-group">
            <label class="control-label">View Mode</label>
            <select class="control-select" v-model="viewMode">
              <option value="infrastructure">Infrastructure View</option>
              <option value="processes">Process Flow</option>
              <option value="risks">Risk Assessment</option>
              <option value="recovery">Recovery Plans</option>
            </select>
          </div>
          <div class="control-group">
            <label class="control-label">Data Layer</label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" v-model="dataLayers.realtime" />
                <span>Real-time Metrics</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="dataLayers.historical" />
                <span>Historical Data</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="dataLayers.predictions" />
                <span>AI Predictions</span>
              </label>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">System Status</h3>
          <div class="status-grid">
            <div class="status-item">
              <div class="status-indicator status-online"></div>
              <div class="status-details">
                <span class="status-label">Primary Systems</span>
                <span class="status-value">98% Operational</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-indicator status-warning"></div>
              <div class="status-details">
                <span class="status-label">Backup Systems</span>
                <span class="status-value">2 Warnings</span>
              </div>
            </div>
            <div class="status-item">
              <div class="status-indicator status-online"></div>
              <div class="status-details">
                <span class="status-label">Recovery Sites</span>
                <span class="status-value">All Available</span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3 class="section-title">Quick Actions</h3>
          <div class="action-buttons">
            <button class="action-btn primary" @click="startSimulation">
              <PlayIcon class="w-4 h-4" />
              Start Simulation
            </button>
            <button class="action-btn secondary" @click="takeSnapshot">
              <CameraIcon class="w-4 h-4" />
              Take Snapshot
            </button>
            <button class="action-btn secondary" @click="generateReport">
              <DocumentTextIcon class="w-4 h-4" />
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Metrics Dashboard -->
    <div class="metrics-dashboard">
      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Recovery Time Objective</h4>
          <ArrowTrendingUpIcon class="w-5 h-5 text-green-500" />
        </div>
        <div class="metric-value">{{ rtoMetrics.current }}h</div>
        <div class="metric-change positive">
          ↑ {{ rtoMetrics.improvement }}% from last month
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Business Impact</h4>
          <ShieldCheckIcon class="w-5 h-5 text-blue-500" />
        </div>
        <div class="metric-value">${{ businessImpact.value }}M</div>
        <div class="metric-change negative">
          ↓ {{ businessImpact.reduction }}% risk reduction
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">System Resilience</h4>
          <CpuChipIcon class="w-5 h-5 text-purple-500" />
        </div>
        <div class="metric-value">{{ resilience.score }}/100</div>
        <div class="metric-change positive">
          ↑ {{ resilience.improvement }} points this quarter
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h4 class="metric-title">Training Completion</h4>
          <AcademicCapIcon class="w-5 h-5 text-orange-500" />
        </div>
        <div class="metric-value">{{ training.completion }}%</div>
        <div class="metric-change positive">
          ↑ {{ training.increase }}% this month
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import {
  CubeTransparentIcon,
  CheckIcon,
  PlayIcon,
  CameraIcon,
  DocumentTextIcon,
  ArrowTrendingUpIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

// Reactive data
const viewMode = ref('infrastructure')
const dataLayers = reactive({
  realtime: true,
  historical: false,
  predictions: true
})

// Mock metrics data
const rtoMetrics = reactive({
  current: 4.2,
  improvement: 15
})

const businessImpact = reactive({
  value: 2.8,
  reduction: 23
})

const resilience = reactive({
  score: 87,
  improvement: 12
})

const training = reactive({
  completion: 94,
  increase: 8
})

// Template ref for 3D scene
const sceneContainer = ref<HTMLElement>()

// Initialize 3D scene when component mounts
onMounted(() => {
  console.log('Digital Twin component mounted')
  // Future: Initialize Three.js scene here
  initializeDigitalTwin()
})

// Mock initialization function
function initializeDigitalTwin() {
  console.log('Initializing Digital Twin 3D visualization...')
  // This would initialize Three.js scene, cameras, lighting, etc.
  // For now, we show a placeholder
}

// Button click handlers
function startSimulation() {
  console.log('Starting simulation...')
  // TODO: Implement simulation start logic
  alert('Simulation starting...')
}

function takeSnapshot() {
  console.log('Taking snapshot...')
  // TODO: Implement snapshot logic
  alert('Snapshot taken!')
}

function generateReport() {
  console.log('Generating report...')
  // TODO: Implement report generation logic
  alert('Generating report...')
}
</script>

<style lang="scss" scoped>
@import "@/styles/variables.scss";

.digital-twin-page {
  @apply p-6 space-y-6;
}

.page-header {
  @apply mb-8;
}

.page-title {
  @apply text-3xl font-bold text-gray-900 dark:text-white mb-2;
}

.page-description {
  @apply text-lg text-gray-600 dark:text-gray-300;
}

.digital-twin-container {
  @apply grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8;
}

.scene-container {
  @apply lg:col-span-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden;
  min-height: 500px;
}

.scene-placeholder {
  @apply h-full flex items-center justify-center p-8;
  min-height: 500px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.placeholder-content {
  @apply text-center text-white;
}

.placeholder-icon {
  @apply mx-auto mb-6;
}

.placeholder-title {
  @apply text-2xl font-bold mb-4;
}

.placeholder-description {
  @apply text-lg mb-8 opacity-90;
}

.placeholder-features {
  @apply space-y-3;
}

.feature-item {
  @apply flex items-center justify-center gap-2 text-sm;
}

.control-panel {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6;
}

.panel-section {
  @apply space-y-4;
}

.section-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white;
}

.control-group {
  @apply space-y-2;
}

.control-label {
  @apply block text-sm font-medium text-gray-700 dark:text-gray-300;
}

.control-select {
  @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md
         bg-white dark:bg-gray-700 text-gray-900 dark:text-white
         focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.checkbox-group {
  @apply space-y-2;
}

.checkbox-item {
  @apply flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer;
}

.status-grid {
  @apply space-y-3;
}

.status-item {
  @apply flex items-center gap-3;
}

.status-indicator {
  @apply w-3 h-3 rounded-full;
}

.status-online {
  @apply bg-green-500;
}

.status-warning {
  @apply bg-yellow-500;
}

.status-error {
  @apply bg-red-500;
}

.status-details {
  @apply flex flex-col;
}

.status-label {
  @apply text-sm font-medium text-gray-700 dark:text-gray-300;
}

.status-value {
  @apply text-xs text-gray-500 dark:text-gray-400;
}

.action-buttons {
  @apply space-y-2;
}

.action-btn {
  @apply w-full flex items-center justify-center gap-2 px-4 py-2 rounded-md
         font-medium transition-colors;
}

.action-btn.primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white;
}

.action-btn.secondary {
  @apply bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600
         text-gray-900 dark:text-white;
}

.metrics-dashboard {
  @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6;
}

.metric-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6;
}

.metric-header {
  @apply flex items-center justify-between mb-4;
}

.metric-title {
  @apply text-sm font-medium text-gray-600 dark:text-gray-400;
}

.metric-value {
  @apply text-3xl font-bold text-gray-900 dark:text-white mb-2;
}

.metric-change {
  @apply text-sm font-medium;
}

.metric-change.positive {
  @apply text-green-600 dark:text-green-400;
}

.metric-change.negative {
  @apply text-red-600 dark:text-red-400;
}
</style>