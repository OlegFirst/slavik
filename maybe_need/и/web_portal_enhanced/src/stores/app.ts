import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface AppState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark' | 'auto'
  notifications: Notification[]
  loading: boolean
}

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  timestamp: Date
  read: boolean
}

export const useAppStore = defineStore('app', () => {
  // State
  const sidebarCollapsed = ref(false)
  const theme = ref<'light' | 'dark' | 'auto'>('light')
  const notifications = ref<Notification[]>([])
  const loading = ref(false)
  const currentModule = ref<string | null>(null)

  // Getters
  const unreadNotificationsCount = computed(() =>
    notifications.value.filter(n => !n.read).length
  )

  const isDarkMode = computed(() => {
    if (theme.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return theme.value === 'dark'
  })

  // Actions
  function toggleSidebar(): void {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('sidebar_collapsed', sidebarCollapsed.value.toString())
  }

  function setSidebarCollapsed(collapsed: boolean): void {
    sidebarCollapsed.value = collapsed
    localStorage.setItem('sidebar_collapsed', collapsed.toString())
  }

  function setTheme(newTheme: 'light' | 'dark' | 'auto'): void {
    theme.value = newTheme
    localStorage.setItem('app_theme', newTheme)
    updateThemeClass()
  }

  function updateThemeClass(): void {
    const html = document.documentElement
    if (isDarkMode.value) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }

  function addNotification(notification: Omit<Notification, 'id' | 'timestamp' | 'read'>): void {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false
    }
    notifications.value.unshift(newNotification)
  }

  function markNotificationRead(id: string): void {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  function markAllNotificationsRead(): void {
    notifications.value.forEach(notification => {
      notification.read = true
    })
  }

  function removeNotification(id: string): void {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  function clearAllNotifications(): void {
    notifications.value = []
  }

  function setLoading(isLoading: boolean): void {
    loading.value = isLoading
  }

  function setCurrentModule(module: string | null): void {
    currentModule.value = module
  }

  // Initialize from localStorage
  function initializeApp(): void {
    // Load sidebar state
    const storedSidebar = localStorage.getItem('sidebar_collapsed')
    if (storedSidebar !== null) {
      sidebarCollapsed.value = storedSidebar === 'true'
    }

    // Load theme
    const storedTheme = localStorage.getItem('app_theme') as 'light' | 'dark' | 'auto'
    if (storedTheme && ['light', 'dark', 'auto'].includes(storedTheme)) {
      theme.value = storedTheme
    }

    // Apply theme
    updateThemeClass()

    // Listen for system theme changes
    if (theme.value === 'auto') {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateThemeClass)
    }
  }

  return {
    // State
    sidebarCollapsed,
    theme,
    notifications,
    loading,
    currentModule,
    // Getters
    unreadNotificationsCount,
    isDarkMode,
    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    setTheme,
    updateThemeClass,
    addNotification,
    markNotificationRead,
    markAllNotificationsRead,
    removeNotification,
    clearAllNotifications,
    setLoading,
    setCurrentModule,
    initializeApp
  }
})