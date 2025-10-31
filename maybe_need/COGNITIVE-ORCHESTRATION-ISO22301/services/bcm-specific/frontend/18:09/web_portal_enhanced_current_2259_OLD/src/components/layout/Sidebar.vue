<template>
  <aside class="sidebar" :class="{ 'collapsed': collapsed }">
    <div class="sidebar-content">
      <!-- Logo / Brand -->
      <div class="brand-section">
        <router-link to="/" class="brand-link">
          <div class="brand-logo">
            <img
              src="/logo.svg"
              alt="BCM Platform"
              class="logo-image"
            />
          </div>
          <Transition name="brand-text">
            <div v-if="!collapsed" class="brand-text">
              <h2 class="brand-title">BCM Platform</h2>
              <p class="brand-subtitle">v2.0</p>
            </div>
          </Transition>
        </router-link>
      </div>

      <!-- Navigation Menu -->
      <nav class="navigation">
        <div class="nav-section">
          <h3 v-if="!collapsed" class="nav-section-title">Main</h3>

          <!-- Dashboard -->
          <SidebarItem
            to="/dashboard"
            :icon="HomeIcon"
            label="Dashboard"
            :collapsed="collapsed"
          />
        </div>

        <!-- BCM Modules -->
        <div class="nav-section">
          <h3 v-if="!collapsed" class="nav-section-title">BCM Modules</h3>

          <SidebarItem
            to="/risk-assessment"
            :icon="ShieldExclamationIcon"
            label="Risk Assessment"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/business-impact-analysis"
            :icon="ChartBarIcon"
            label="Business Impact Analysis"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/bcp-development"
            :icon="DocumentTextIcon"
            label="BCP Development"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/crisis-management"
            :icon="ExclamationTriangleIcon"
            label="Crisis Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/incident-management"
            :icon="BellIcon"
            label="Incident Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/emergency-response"
            :icon="FireIcon"
            label="Emergency Response"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/disaster-recovery"
            :icon="ArrowPathIcon"
            label="Disaster Recovery"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/compliance-management"
            :icon="ClipboardDocumentCheckIcon"
            label="Compliance Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/vendor-management"
            :icon="BuildingOfficeIcon"
            label="Vendor Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/asset-management"
            :icon="CubeIcon"
            label="Asset Management"
            :collapsed="collapsed"
          />
        </div>

        <!-- Management & Operations -->
        <div class="nav-section">
          <h3 v-if="!collapsed" class="nav-section-title">Management</h3>

          <SidebarItem
            to="/training-management"
            :icon="AcademicCapIcon"
            label="Training Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/document-management"
            :icon="FolderIcon"
            label="Document Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/audit-management"
            :icon="MagnifyingGlassIcon"
            label="Audit Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/testing-exercises"
            :icon="PlayIcon"
            label="Testing & Exercises"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/communication-management"
            :icon="ChatBubbleLeftRightIcon"
            label="Communication Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/resource-management"
            :icon="CogIcon"
            label="Resource Management"
            :collapsed="collapsed"
          />
        </div>

        <!-- Analytics & AI -->
        <div class="nav-section">
          <h3 v-if="!collapsed" class="nav-section-title">Analytics & AI</h3>

          <SidebarItem
            to="/performance-metrics"
            :icon="ChartBarIcon"
            label="Performance Metrics"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/reporting-analytics"
            :icon="PresentationChartLineIcon"
            label="Reporting & Analytics"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/change-management"
            :icon="ArrowsRightLeftIcon"
            label="Change Management"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/ai-assistant"
            :icon="SparklesIcon"
            label="AI Assistant"
            :collapsed="collapsed"
          />

          <SidebarItem
            to="/digital-twin"
            :icon="CubeTransparentIcon"
            label="Digital Twin"
            :collapsed="collapsed"
          />
        </div>
      </nav>
    </div>

    <!-- Sidebar Footer -->
    <div class="sidebar-footer">
      <button
        @click="$emit('toggle')"
        class="collapse-button"
        :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <ChevronLeftIcon
          class="collapse-icon"
          :class="{ 'rotate-180': collapsed }"
        />
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import {
  HomeIcon,
  ShieldExclamationIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  BellIcon,
  FireIcon,
  ArrowPathIcon,
  ClipboardDocumentCheckIcon,
  BuildingOfficeIcon,
  CubeIcon,
  CubeTransparentIcon,
  AcademicCapIcon,
  FolderIcon,
  MagnifyingGlassIcon,
  PlayIcon,
  ChatBubbleLeftRightIcon,
  CogIcon,
  PresentationChartLineIcon,
  ArrowsRightLeftIcon,
  SparklesIcon,
  ChevronLeftIcon,
} from '@heroicons/vue/24/outline'
import SidebarItem from '@components/ui/SidebarItem.vue'

// Props
defineProps<{
  collapsed: boolean
}>()

// Emits
defineEmits<{
  toggle: []
}>()
</script>

<style lang="scss" scoped>
.sidebar {
  @apply w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
         flex flex-col h-full transition-all duration-300 ease-in-out;

  &.collapsed {
    @apply w-16;
  }
}

.sidebar-content {
  @apply flex-1 overflow-y-auto;
}

.brand-section {
  @apply p-4 border-b border-gray-200 dark:border-gray-700;
}

.brand-link {
  @apply flex items-center space-x-3 no-underline;
}

.brand-logo {
  @apply flex-shrink-0;
}

.logo-image {
  @apply w-10 h-10 object-contain;
}

.brand-text {
  @apply min-w-0;
}

.brand-title {
  @apply text-lg font-bold text-gray-900 dark:text-white truncate;
}

.brand-subtitle {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

.navigation {
  @apply p-4 space-y-6;
}

.nav-section {
  @apply space-y-2;
}

.nav-section-title {
  @apply text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider
         mb-3;
}

.sidebar-footer {
  @apply p-4 border-t border-gray-200 dark:border-gray-700;
}

.collapse-button {
  @apply w-full flex items-center justify-center p-2 rounded-lg
         text-gray-500 hover:text-gray-700 hover:bg-gray-100
         dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-700
         transition-colors duration-200;
}

.collapse-icon {
  @apply w-5 h-5 transition-transform duration-300;
}

// Transitions
.brand-text-enter-active,
.brand-text-leave-active {
  transition: all 0.3s ease;
}

.brand-text-enter-from,
.brand-text-leave-to {
  opacity: 0;
  width: 0;
}
</style>