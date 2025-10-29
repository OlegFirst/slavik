<template>
  <footer class="footer">
    <div class="footer-content">
      <!-- Left Section -->
      <div class="footer-left">
        <p class="copyright">
          © {{ currentYear }} BCM Platform v2. All rights reserved.
        </p>
      </div>

      <!-- Center Section -->
      <div class="footer-center hidden md:flex">
        <nav class="footer-nav">
          <a href="/docs" class="footer-link">Documentation</a>
          <a href="/support" class="footer-link">Support</a>
          <a href="/privacy" class="footer-link">Privacy</a>
          <a href="/terms" class="footer-link">Terms</a>
        </nav>
      </div>

      <!-- Right Section -->
      <div class="footer-right">
        <div class="version-info">
          <span class="version-label">Version:</span>
          <span class="version-number">{{ version }}</span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Computed
const currentYear = computed(() => new Date().getFullYear())
const version = computed(() => import.meta.env.VITE_APP_VERSION || '2.0.0')
</script>

<style lang="scss" scoped>
.footer {
  @apply bg-white dark:bg-gray-800 px-4 sm:px-6 lg:px-8 py-4;
}

.footer-content {
  @apply flex items-center justify-between;
}

.footer-left {
  @apply flex items-center;
}

.copyright {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

.footer-center {
  @apply flex items-center;
}

.footer-nav {
  @apply flex items-center space-x-6;
}

.footer-link {
  @apply text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200
         transition-colors duration-200;
}

.footer-right {
  @apply flex items-center;
}

.version-info {
  @apply flex items-center space-x-2 text-sm;
}

.version-label {
  @apply text-gray-500 dark:text-gray-400;
}

.version-number {
  @apply font-mono text-gray-700 dark:text-gray-300;
}
</style>