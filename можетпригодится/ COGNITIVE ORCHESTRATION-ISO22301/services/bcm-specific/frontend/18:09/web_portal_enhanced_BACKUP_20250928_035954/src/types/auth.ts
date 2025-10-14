export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  permissions: string[]
  avatar?: string
  department?: string
  phoneNumber?: string
  lastLogin?: Date
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

export interface LoginCredentials {
  email: string
  password: string
  rememberMe?: boolean
}

export interface AuthResponse {
  token: string
  user: User
  expiresIn: number
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordReset {
  token: string
  password: string
  confirmPassword: string
}

export interface ProfileUpdateData {
  firstName?: string
  lastName?: string
  phoneNumber?: string
  department?: string
  avatar?: string
}

export interface PermissionGroup {
  id: string
  name: string
  permissions: string[]
}