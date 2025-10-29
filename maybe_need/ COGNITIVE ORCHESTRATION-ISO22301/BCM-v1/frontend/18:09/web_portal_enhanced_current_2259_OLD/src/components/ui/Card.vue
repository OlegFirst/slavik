<template>
  <div class="card" :class="cardClasses">
    <!-- Card Header -->
    <div v-if="hasHeader" class="card-header">
      <div class="card-title-section">
        <component
          v-if="icon"
          :is="icon"
          class="card-icon"
        />
        <h3 v-if="title" class="card-title">{{ title }}</h3>
      </div>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </div>

    <!-- Card Content -->
    <div class="card-content" :class="{ 'no-padding': noPadding }">
      <slot />
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

// Props
interface Props {
  title?: string
  icon?: Component
  variant?: 'default' | 'bordered' | 'elevated' | 'flat'
  size?: 'sm' | 'md' | 'lg'
  noPadding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  noPadding: false
})

// Slots
const slots = defineSlots<{
  default(): any
  actions?(): any
  footer?(): any
}>()

// Computed
const hasHeader = computed(() => props.title || props.icon || slots.actions)

const cardClasses = computed(() => {
  const classes = []

  // Variant classes
  switch (props.variant) {
    case 'bordered':
      classes.push('card-bordered')
      break
    case 'elevated':
      classes.push('card-elevated')
      break
    case 'flat':
      classes.push('card-flat')
      break
    default:
      classes.push('card-default')
  }

  // Size classes
  switch (props.size) {
    case 'sm':
      classes.push('card-sm')
      break
    case 'lg':
      classes.push('card-lg')
      break
    default:
      classes.push('card-md')
  }

  return classes
})
</script>

<style lang="scss" scoped>
.card {
  @apply bg-white dark:bg-gray-800 rounded-lg overflow-hidden;
}

// Variants
.card-default {
  @apply border border-gray-200 dark:border-gray-700 shadow-sm;
}

.card-bordered {
  @apply border-2 border-gray-300 dark:border-gray-600;
}

.card-elevated {
  @apply shadow-lg border-0;
}

.card-flat {
  @apply border-0 shadow-none bg-gray-50 dark:bg-gray-700;
}

// Sizes
.card-sm {
  @apply text-sm;
}

.card-md {
  @apply text-base;
}

.card-lg {
  @apply text-lg;
}

// Header
.card-header {
  @apply flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700;
}

.card-title-section {
  @apply flex items-center space-x-3;
}

.card-icon {
  @apply w-5 h-5 text-gray-600 dark:text-gray-400;
}

.card-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white;
}

.card-actions {
  @apply flex items-center space-x-2;
}

// Content
.card-content {
  @apply px-6 py-4;

  &.no-padding {
    @apply p-0;
  }
}

// Footer
.card-footer {
  @apply px-6 py-4 border-t border-gray-200 dark:border-gray-700
         bg-gray-50 dark:bg-gray-700/50;
}
</style>