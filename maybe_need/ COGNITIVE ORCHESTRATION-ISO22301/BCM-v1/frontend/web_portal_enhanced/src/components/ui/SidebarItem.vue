<template>
  <router-link
    :to="to"
    class="sidebar-item"
    :class="{ 'collapsed': collapsed }"
    v-slot="{ isActive }"
  >
    <div class="sidebar-item-content" :class="{ 'active': isActive }">
      <component :is="icon" class="sidebar-item-icon" />
      <Transition name="label">
        <span v-if="!collapsed" class="sidebar-item-label">{{ label }}</span>
      </Transition>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

// Props
defineProps<{
  to: string
  icon: Component
  label: string
  collapsed: boolean
}>()
</script>

<style lang="scss" scoped>
.sidebar-item {
  @apply block w-full text-decoration-none;
}

.sidebar-item-content {
  @apply flex items-center space-x-3 px-3 py-2 rounded-lg
         text-gray-700 hover:text-gray-900 hover:bg-gray-100
         dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700
         transition-all duration-200 cursor-pointer;

  &.active {
    @apply bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300;

    .sidebar-item-icon {
      @apply text-blue-700 dark:text-blue-300;
    }
  }
}

.collapsed .sidebar-item-content {
  @apply justify-center space-x-0 px-2;
}

.sidebar-item-icon {
  @apply w-6 h-6 flex-shrink-0;
}

.sidebar-item-label {
  @apply text-sm font-medium truncate;
}

// Transitions
.label-enter-active,
.label-leave-active {
  transition: all 0.3s ease;
}

.label-enter-from,
.label-leave-to {
  opacity: 0;
  width: 0;
}
</style>