<template>
  <div class="layout-container">
    <!-- Sidebar -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      @toggle="toggleSidebar"
      class="layout-sidebar"
    />

    <!-- Main Content Area -->
    <div class="layout-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Header -->
      <Header
        @toggle-sidebar="toggleSidebar"
        class="layout-header"
      />

      <!-- Page Content -->
      <main class="layout-content">
        <div class="page-container">
          <router-view v-slot="{ Component, route }">
            <Transition name="page" mode="out-in">
              <component
                :is="Component"
                :key="route.path"
                class="page-view"
              />
            </Transition>
          </router-view>
        </div>
      </main>

      <!-- Footer -->
      <Footer class="layout-footer" />
    </div>

    <!-- Mobile Overlay -->
    <div
      v-if="!sidebarCollapsed"
      class="mobile-overlay lg:hidden"
      @click="toggleSidebar"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@stores/app'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import Footer from './Footer.vue'

// Store
const appStore = useAppStore()

// Computed
const sidebarCollapsed = computed(() => appStore.sidebarCollapsed)

// Methods
function toggleSidebar(): void {
  appStore.toggleSidebar()
}
</script>

<style lang="scss" scoped>
.layout-container {
  @apply flex min-h-screen bg-gray-50 dark:bg-gray-900;
}

.layout-sidebar {
  @apply fixed inset-y-0 left-0 z-50 lg:relative lg:z-auto;
}

.layout-main {
  @apply flex flex-1 flex-col min-w-0;
  margin-left: 0;
  transition: margin-left 0.3s ease;

  &:not(.sidebar-collapsed) {
    @apply lg:ml-64;
  }

  &.sidebar-collapsed {
    @apply lg:ml-16;
  }
}

.layout-header {
  @apply sticky top-0 z-40 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700;
}

.layout-content {
  @apply flex-1 overflow-auto;
}

.page-container {
  @apply container mx-auto px-4 sm:px-6 lg:px-8 py-8;
  max-width: 1400px;
}

.page-view {
  @apply w-full;
}

.layout-footer {
  @apply mt-auto bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700;
}

.mobile-overlay {
  @apply fixed inset-0 z-40 bg-black bg-opacity-50;
}

// Page transitions
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>