<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <router-view />
    <Teleport to="body">
      <LoadingOverlay v-if="isLoading" />
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@stores/auth'
import { useAppStore } from '@stores/app'
import LoadingOverlay from '@components/ui/LoadingOverlay.vue'

// Stores
const authStore = useAuthStore()
const appStore = useAppStore()

// Computed
const isDarkMode = computed(() => appStore.isDarkMode)
const isLoading = computed(() => appStore.loading)

// Initialize application
onMounted(async () => {
  // Initialize app settings
  appStore.initializeApp()

  // Initialize authentication
  authStore.initializeAuth()

  // If user is authenticated, refresh user data
  if (authStore.isAuthenticated) {
    try {
      await authStore.refreshUser()
    } catch (error) {
      console.error('Failed to refresh user data on app start:', error)
    }
  }
})
</script>

<style lang="scss">
// Import global styles
@import '@styles/main.scss';

#app {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text);
  background-color: var(--color-background);
  transition: background-color 0.3s ease;
}

// Dark mode specific styles
.dark {
  color-scheme: dark;
}

// Smooth transitions
* {
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}

// Focus styles for accessibility
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 4px;
}
</style>