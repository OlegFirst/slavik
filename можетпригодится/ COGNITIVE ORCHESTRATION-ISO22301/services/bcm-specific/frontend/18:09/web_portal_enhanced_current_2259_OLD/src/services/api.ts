import axios from 'axios'
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { useAuthStore } from '@stores/auth'
import { useAppStore } from '@stores/app'
import { useToast } from 'vue-toastification'

// API Configuration - disabled for development mode
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/mock-api'
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'
const API_TIMEOUT = 5000 // 5 seconds for mock development

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/${API_VERSION}`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const appStore = useAppStore()

    // Add loading state
    appStore.setLoading(true)

    // Add authorization header
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }

    // Add request timestamp for monitoring
    config.metadata = { startTime: new Date() }

    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      data: config.data,
      params: config.params,
    })

    return config
  },
  (error) => {
    const appStore = useAppStore()
    appStore.setLoading(false)
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const appStore = useAppStore()
    appStore.setLoading(false)

    // Calculate request duration
    const duration = new Date().getTime() - response.config.metadata.startTime.getTime()

    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      duration: `${duration}ms`,
      data: response.data,
    })

    return response
  },
  async (error: AxiosError) => {
    const appStore = useAppStore()
    const authStore = useAuthStore()
    const toast = useToast()

    appStore.setLoading(false)

    console.error('❌ API Error:', error.response?.status, error.message)

    // Handle different error types
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          toast.error('Session expired. Please login again.')
          await authStore.logout()
          window.location.href = '/login'
          break

        case 403:
          // Forbidden
          toast.error('Access denied. You don\'t have permission to perform this action.')
          break

        case 404:
          // Not found
          toast.error('The requested resource was not found.')
          break

        case 422:
          // Validation errors
          if (data?.errors) {
            const errorMessages = Object.values(data.errors).flat()
            errorMessages.forEach((message: any) => toast.error(message))
          } else {
            toast.error(data?.message || 'Validation error occurred.')
          }
          break

        case 429:
          // Rate limited
          toast.error('Too many requests. Please try again later.')
          break

        case 500:
          // Internal server error
          toast.error('Server error occurred. Please try again later.')
          break

        case 502:
        case 503:
        case 504:
          // Service unavailable
          toast.error('Service temporarily unavailable. Please try again later.')
          break

        default:
          toast.error(data?.message || 'An unexpected error occurred.')
      }
    } else if (error.request) {
      // Network error
      toast.error('Network error. Please check your connection.')
    } else {
      // Other error
      toast.error('An unexpected error occurred.')
    }

    return Promise.reject(error)
  }
)

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  meta?: {
    pagination?: {
      page: number
      limit: number
      total: number
      totalPages: number
    }
  }
}

export interface ApiError {
  success: false
  message: string
  errors?: Record<string, string[]>
}

export { api }
export default api
