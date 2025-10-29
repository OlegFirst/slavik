import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { useAuthStore } from '@stores/auth'
import { useAppStore } from '@stores/app'
import { useToast } from 'vue-toastification'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1'
const API_TIMEOUT = 30000 // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/${API_VERSION}`,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
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
apiClient.interceptors.response.use(
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

// Generic API methods
export const api = {
  // GET request
  get: async <T>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get<ApiResponse<T>>(url, { params })
    return response.data.data
  },

  // POST request
  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, data)
    return response.data.data
  },

  // PUT request
  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put<ApiResponse<T>>(url, data)
    return response.data.data
  },

  // PATCH request
  patch: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch<ApiResponse<T>>(url, data)
    return response.data.data
  },

  // DELETE request
  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete<ApiResponse<T>>(url)
    return response.data.data
  },

  // Upload file
  upload: async <T>(url: string, formData: FormData): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data.data
  },

  // Download file
  download: async (url: string, filename?: string): Promise<void> => {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    })

    // Create download link
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(downloadUrl)
  },
}

// Health check endpoint
export const healthCheck = async (): Promise<{ status: string; timestamp: string }> => {
  return api.get('/health')
}

export default apiClient