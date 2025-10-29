<template>
  <component
    :is="tag"
    :to="to"
    :href="href"
    :type="type"
    :disabled="disabled || loading"
    class="button"
    :class="buttonClasses"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <div v-if="loading" class="loading-spinner">
      <div class="spinner-ring"></div>
    </div>

    <!-- Left Icon -->
    <component
      v-if="leftIcon && !loading"
      :is="leftIcon"
      class="button-icon button-icon-left"
    />

    <!-- Button Content -->
    <span v-if="$slots.default" class="button-content">
      <slot />
    </span>

    <!-- Right Icon -->
    <component
      v-if="rightIcon && !loading"
      :is="rightIcon"
      class="button-icon button-icon-right"
    />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

// Props
interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'ghost' | 'link'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  rounded?: boolean
  leftIcon?: Component
  rightIcon?: Component
  to?: string
  href?: string
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  block: false,
  rounded: false,
  type: 'button'
})

// Emits
const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

// Computed
const tag = computed(() => {
  if (props.to) return 'router-link'
  if (props.href) return 'a'
  return 'button'
})

const buttonClasses = computed(() => {
  const classes = []

  // Variant classes
  switch (props.variant) {
    case 'secondary':
      classes.push('button-secondary')
      break
    case 'success':
      classes.push('button-success')
      break
    case 'danger':
      classes.push('button-danger')
      break
    case 'warning':
      classes.push('button-warning')
      break
    case 'ghost':
      classes.push('button-ghost')
      break
    case 'link':
      classes.push('button-link')
      break
    default:
      classes.push('button-primary')
  }

  // Size classes
  switch (props.size) {
    case 'xs':
      classes.push('button-xs')
      break
    case 'sm':
      classes.push('button-sm')
      break
    case 'lg':
      classes.push('button-lg')
      break
    case 'xl':
      classes.push('button-xl')
      break
    default:
      classes.push('button-md')
  }

  // Modifier classes
  if (props.block) classes.push('button-block')
  if (props.rounded) classes.push('button-rounded')
  if (props.disabled || props.loading) classes.push('button-disabled')

  return classes
})

// Methods
function handleClick(event: MouseEvent): void {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style lang="scss" scoped>
.button {
  @apply inline-flex items-center justify-center font-medium
         transition-all duration-200 focus:outline-none focus:ring-2
         focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed
         no-underline;
}

// Variants
.button-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500
         border border-transparent;
}

.button-secondary {
  @apply bg-white text-gray-700 hover:bg-gray-50 focus:ring-gray-500
         border border-gray-300 dark:bg-gray-800 dark:text-gray-300
         dark:border-gray-600 dark:hover:bg-gray-700;
}

.button-success {
  @apply bg-green-600 text-white hover:bg-green-700 focus:ring-green-500
         border border-transparent;
}

.button-danger {
  @apply bg-red-600 text-white hover:bg-red-700 focus:ring-red-500
         border border-transparent;
}

.button-warning {
  @apply bg-yellow-500 text-white hover:bg-yellow-600 focus:ring-yellow-500
         border border-transparent;
}

.button-ghost {
  @apply bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500
         border border-gray-300 dark:text-gray-300 dark:border-gray-600
         dark:hover:bg-gray-700;
}

.button-link {
  @apply bg-transparent text-blue-600 hover:text-blue-700 hover:underline
         focus:ring-blue-500 border-0 p-0;
}

// Sizes
.button-xs {
  @apply px-2.5 py-1.5 text-xs rounded;
}

.button-sm {
  @apply px-3 py-2 text-sm rounded-md;
}

.button-md {
  @apply px-4 py-2 text-sm rounded-md;
}

.button-lg {
  @apply px-6 py-3 text-base rounded-md;
}

.button-xl {
  @apply px-8 py-4 text-lg rounded-lg;
}

// Modifiers
.button-block {
  @apply w-full;
}

.button-rounded {
  @apply rounded-full;
}

.button-disabled {
  @apply opacity-50 cursor-not-allowed;
}

// Icons
.button-icon {
  @apply flex-shrink-0;

  &.button-icon-left {
    @apply mr-2;
  }

  &.button-icon-right {
    @apply ml-2;
  }
}

.button-xs .button-icon {
  @apply w-3 h-3;
}

.button-sm .button-icon {
  @apply w-4 h-4;
}

.button-md .button-icon {
  @apply w-4 h-4;
}

.button-lg .button-icon {
  @apply w-5 h-5;
}

.button-xl .button-icon {
  @apply w-6 h-6;
}

// Loading
.loading-spinner {
  @apply flex items-center justify-center mr-2;
}

.spinner-ring {
  @apply w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin;
}

.button-content {
  @apply flex items-center;
}
</style>