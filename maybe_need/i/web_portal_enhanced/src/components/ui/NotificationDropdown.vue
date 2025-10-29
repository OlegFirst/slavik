<template>
  <div class="notification-dropdown" @click.stop>
    <!-- Header -->
    <div class="dropdown-header">
      <h3 class="dropdown-title">Notifications</h3>
      <div class="dropdown-actions">
        <button
          v-if="unreadCount > 0"
          @click="markAllRead"
          class="action-button"
        >
          Mark all read
        </button>
        <button @click="$emit('close')" class="close-button">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Notifications List -->
    <div class="notifications-list">
      <div v-if="notifications.length === 0" class="empty-state">
        <BellIcon class="empty-icon" />
        <p class="empty-text">No notifications</p>
      </div>

      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ 'unread': !notification.read }"
        @click="markAsRead(notification.id)"
      >
        <div class="notification-icon" :class="getIconClass(notification.type)">
          <component :is="getIcon(notification.type)" class="w-4 h-4" />
        </div>

        <div class="notification-content">
          <h4 class="notification-title">{{ notification.title }}</h4>
          <p class="notification-message">{{ notification.message }}</p>
          <p class="notification-time">{{ formatTime(notification.timestamp) }}</p>
        </div>

        <button
          @click.stop="removeNotification(notification.id)"
          class="remove-button"
        >
          <XMarkIcon class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Footer -->
    <div class="dropdown-footer">
      <router-link to="/notifications" class="view-all-link">
        View all notifications
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  XMarkIcon,
  BellIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'
import { useAppStore } from '@stores/app'
import { formatDistanceToNow } from 'date-fns'

// Emits
defineEmits<{
  close: []
}>()

// Store
const appStore = useAppStore()

// Computed
const notifications = computed(() => appStore.notifications.slice(0, 10))
const unreadCount = computed(() => appStore.unreadNotificationsCount)

// Methods
function markAsRead(id: string): void {
  appStore.markNotificationRead(id)
}

function markAllRead(): void {
  appStore.markAllNotificationsRead()
}

function removeNotification(id: string): void {
  appStore.removeNotification(id)
}

function formatTime(date: Date): string {
  return formatDistanceToNow(date, { addSuffix: true })
}

function getIcon(type: string) {
  switch (type) {
    case 'success':
      return CheckCircleIcon
    case 'warning':
      return ExclamationTriangleIcon
    case 'error':
      return XCircleIcon
    default:
      return InformationCircleIcon
  }
}

function getIconClass(type: string): string {
  switch (type) {
    case 'success':
      return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/50'
    case 'warning':
      return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/50'
    case 'error':
      return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/50'
    default:
      return 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/50'
  }
}
</script>

<style lang="scss" scoped>
.notification-dropdown {
  @apply absolute right-0 top-full mt-2 w-96 max-w-sm bg-white dark:bg-gray-800
         rounded-lg shadow-lg border border-gray-200 dark:border-gray-700
         z-50;
}

.dropdown-header {
  @apply flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700;
}

.dropdown-title {
  @apply text-lg font-semibold text-gray-900 dark:text-white;
}

.dropdown-actions {
  @apply flex items-center space-x-2;
}

.action-button {
  @apply text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300
         transition-colors duration-200;
}

.close-button {
  @apply p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
         transition-colors duration-200;
}

.notifications-list {
  @apply max-h-96 overflow-y-auto;
}

.empty-state {
  @apply flex flex-col items-center justify-center p-8 text-gray-500 dark:text-gray-400;
}

.empty-icon {
  @apply w-12 h-12 mb-2;
}

.empty-text {
  @apply text-sm;
}

.notification-item {
  @apply flex items-start space-x-3 p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50
         border-b border-gray-100 dark:border-gray-700 cursor-pointer
         transition-colors duration-200;

  &.unread {
    @apply bg-blue-50/50 dark:bg-blue-900/10;

    &::before {
      content: '';
      @apply absolute left-2 top-1/2 transform -translate-y-1/2 w-2 h-2
             bg-blue-600 rounded-full;
    }
  }

  &:last-child {
    @apply border-b-0;
  }
}

.notification-icon {
  @apply flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center;
}

.notification-content {
  @apply flex-1 min-w-0;
}

.notification-title {
  @apply text-sm font-medium text-gray-900 dark:text-white truncate;
}

.notification-message {
  @apply text-sm text-gray-600 dark:text-gray-400 mt-1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  @apply text-xs text-gray-400 dark:text-gray-500 mt-1;
}

.remove-button {
  @apply flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300
         transition-colors duration-200 opacity-0 group-hover:opacity-100;
}

.notification-item:hover .remove-button {
  @apply opacity-100;
}

.dropdown-footer {
  @apply p-4 border-t border-gray-200 dark:border-gray-700;
}

.view-all-link {
  @apply block w-full text-center text-sm text-blue-600 hover:text-blue-700
         dark:text-blue-400 dark:hover:text-blue-300 transition-colors duration-200;
}
</style>