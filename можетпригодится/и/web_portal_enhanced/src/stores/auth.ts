import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, AuthResponse } from '@/types/auth'
import { authService } from '@services/auth'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  const toast = useToast()

  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || 'user')
  const hasPermission = computed(() => (permission: string) => {
    return user.value?.permissions?.includes(permission) || false
  })

  // Actions
  async function login(credentials: LoginCredentials): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      const response: AuthResponse = await authService.login(credentials)

      token.value = response.token
      user.value = response.user

      localStorage.setItem('auth_token', response.token)
      localStorage.setItem('user_data', JSON.stringify(response.user))

      toast.success(`Welcome back, ${response.user.firstName}!`)
      return true
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      toast.error(error.value)
      return false
    } finally {
      isLoading.value = false
    }
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (err) {
      console.warn('Logout API call failed:', err)
    } finally {
      // Clear local state regardless of API call success
      user.value = null
      token.value = null
      error.value = null

      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')

      toast.info('You have been logged out')
    }
  }

  async function refreshUser(): Promise<void> {
    if (!token.value) return

    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      localStorage.setItem('user_data', JSON.stringify(userData))
    } catch (err: any) {
      console.error('Failed to refresh user data:', err)
      // If refresh fails, logout user
      await logout()
    }
  }

  async function updateProfile(userData: Partial<User>): Promise<boolean> {
    if (!user.value) return false

    try {
      isLoading.value = true
      const updatedUser = await authService.updateProfile(userData)
      user.value = { ...user.value, ...updatedUser }
      localStorage.setItem('user_data', JSON.stringify(user.value))
      toast.success('Profile updated successfully')
      return true
    } catch (err: any) {
      error.value = err.message || 'Profile update failed'
      toast.error(error.value)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearError(): void {
    error.value = null
  }

  // Initialize store from localStorage
  function initializeAuth(): void {
    const storedUser = localStorage.getItem('user_data')
    if (storedUser && token.value) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Failed to parse stored user data:', err)
        localStorage.removeItem('user_data')
        localStorage.removeItem('auth_token')
        token.value = null
      }
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    // Getters
    isAuthenticated,
    userRole,
    hasPermission,
    // Actions
    login,
    logout,
    refreshUser,
    updateProfile,
    clearError,
    initializeAuth
  }
})