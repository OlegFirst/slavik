import { api } from './api'
import type { User, LoginCredentials, AuthResponse, PasswordResetRequest, PasswordReset, ProfileUpdateData } from '@/types/auth'

export const authService = {
  /**
   * Login user with credentials
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    return api.post<AuthResponse>('/auth/login', credentials)
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    return api.post<void>('/auth/logout')
  },

  /**
   * Get current user data
   */
  async getCurrentUser(): Promise<User> {
    return api.get<User>('/auth/me')
  },

  /**
   * Update user profile
   */
  async updateProfile(userData: ProfileUpdateData): Promise<User> {
    return api.put<User>('/auth/profile', userData)
  },

  /**
   * Change user password
   */
  async changePassword(data: { currentPassword: string; newPassword: string }): Promise<void> {
    return api.post<void>('/auth/change-password', data)
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetRequest): Promise<void> {
    return api.post<void>('/auth/forgot-password', data)
  },

  /**
   * Reset password with token
   */
  async resetPassword(data: PasswordReset): Promise<void> {
    return api.post<void>('/auth/reset-password', data)
  },

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<AuthResponse> {
    return api.post<AuthResponse>('/auth/refresh')
  },

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<void> {
    return api.post<void>('/auth/verify-email', { token })
  },

  /**
   * Resend email verification
   */
  async resendVerification(): Promise<void> {
    return api.post<void>('/auth/resend-verification')
  }
}