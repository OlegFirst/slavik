// Input validation and sanitization utilities

export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message)
    this.name = 'ValidationError'
  }
}

// Common validation patterns
export const VALIDATION_PATTERNS = {
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  domain: /^[a-z0-9.-]+$/,
  hex_color: /^#[0-9A-F]{6}$/i,
  uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
  alphanumeric: /^[a-zA-Z0-9_-]+$/,
  safe_string: /^[a-zA-Z0-9\s\-._@()]+$/
}

// Sanitize HTML input to prevent XSS
export const sanitizeHTML = (input: string): string => {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
}

// Sanitize input for SQL-like queries (even though we're using APIs)
export const sanitizeQuery = (input: string): string => {
  return input
    .replace(/[';\\]/g, '') // Remove dangerous SQL characters
    .trim()
    .substring(0, 1000) // Limit length
}

// Validate and sanitize user ID
export const validateUserId = (userId: string): string => {
  if (!userId || typeof userId !== 'string') {
    throw new ValidationError('User ID is required', 'userId')
  }

  if (!VALIDATION_PATTERNS.uuid.test(userId) && !VALIDATION_PATTERNS.alphanumeric.test(userId)) {
    throw new ValidationError('Invalid user ID format', 'userId')
  }

  return userId.trim()
}

// Validate email
export const validateEmail = (email: string): string => {
  if (!email || typeof email !== 'string') {
    throw new ValidationError('Email is required', 'email')
  }

  const cleanEmail = email.trim().toLowerCase()

  if (!VALIDATION_PATTERNS.email.test(cleanEmail)) {
    throw new ValidationError('Invalid email format', 'email')
  }

  return cleanEmail
}

// Validate domain name
export const validateDomain = (domain: string): string => {
  if (!domain || typeof domain !== 'string') {
    throw new ValidationError('Domain is required', 'domain')
  }

  const cleanDomain = domain.trim().toLowerCase()

  if (!VALIDATION_PATTERNS.domain.test(cleanDomain)) {
    throw new ValidationError('Invalid domain format', 'domain')
  }

  if (cleanDomain.length > 253) {
    throw new ValidationError('Domain name too long', 'domain')
  }

  return cleanDomain
}

// Validate hex color
export const validateHexColor = (color: string): string => {
  if (!color || typeof color !== 'string') {
    throw new ValidationError('Color is required', 'color')
  }

  const cleanColor = color.trim().toUpperCase()

  if (!VALIDATION_PATTERNS.hex_color.test(cleanColor)) {
    throw new ValidationError('Invalid color format (must be #RRGGBB)', 'color')
  }

  return cleanColor
}

// Validate portal name
export const validatePortalName = (name: string): string => {
  if (!name || typeof name !== 'string') {
    throw new ValidationError('Portal name is required', 'name')
  }

  const cleanName = name.trim()

  if (cleanName.length < 3) {
    throw new ValidationError('Portal name must be at least 3 characters', 'name')
  }

  if (cleanName.length > 100) {
    throw new ValidationError('Portal name must be less than 100 characters', 'name')
  }

  if (!VALIDATION_PATTERNS.safe_string.test(cleanName)) {
    throw new ValidationError('Portal name contains invalid characters', 'name')
  }

  return sanitizeHTML(cleanName)
}

// Validate points amount (for gamification)
export const validatePoints = (points: number): number => {
  if (typeof points !== 'number' || isNaN(points)) {
    throw new ValidationError('Points must be a valid number', 'points')
  }

  if (points < 0) {
    throw new ValidationError('Points cannot be negative', 'points')
  }

  if (points > 1000000) {
    throw new ValidationError('Points amount too large', 'points')
  }

  return Math.floor(points) // Ensure integer
}

// Validate pagination parameters
export const validatePaginationParams = (page: number, limit: number) => {
  const cleanPage = Math.max(1, Math.floor(page) || 1)
  const cleanLimit = Math.min(100, Math.max(1, Math.floor(limit) || 10))

  return { page: cleanPage, limit: cleanLimit }
}

// Comprehensive validation for portal configuration
export const validatePortalConfiguration = (config: any): any => {
  const validated: any = {}

  // Validate required fields
  if (config.name) {
    validated.name = validatePortalName(config.name)
  }

  if (config.customDomain) {
    validated.customDomain = validateDomain(config.customDomain)
  }

  // Validate branding
  if (config.branding) {
    validated.branding = {}

    if (config.branding.primaryColor) {
      validated.branding.primaryColor = validateHexColor(config.branding.primaryColor)
    }

    if (config.branding.secondaryColor) {
      validated.branding.secondaryColor = validateHexColor(config.branding.secondaryColor)
    }

    if (config.branding.logo) {
      validated.branding.logo = sanitizeQuery(config.branding.logo)
    }
  }

  // Validate modules
  if (config.modules && Array.isArray(config.modules)) {
    validated.modules = config.modules.map((module: any) => ({
      id: sanitizeQuery(module.id || ''),
      name: sanitizeHTML(module.name || ''),
      type: sanitizeQuery(module.type || ''),
      enabled: Boolean(module.enabled),
      config: module.config || {},
      permissions: Array.isArray(module.permissions) ?
        module.permissions.map((p: string) => sanitizeQuery(p)) : []
    }))
  }

  return validated
}

// Rate limiting helper (client-side basic implementation)
export class RateLimiter {
  private attempts: Map<string, number[]> = new Map()

  isAllowed(key: string, maxAttempts: number = 5, windowMs: number = 60000): boolean {
    const now = Date.now()
    const attempts = this.attempts.get(key) || []

    // Remove old attempts outside the window
    const recentAttempts = attempts.filter(time => now - time < windowMs)

    // Check if limit exceeded
    if (recentAttempts.length >= maxAttempts) {
      return false
    }

    // Add current attempt
    recentAttempts.push(now)
    this.attempts.set(key, recentAttempts)

    return true
  }

  reset(key: string) {
    this.attempts.delete(key)
  }
}

// Global rate limiter instance
export const rateLimiter = new RateLimiter()

// CSRF token management
export const generateCSRFToken = (): string => {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}

// Secure API request helper
export const secureApiRequest = async (
  url: string,
  options: RequestInit = {},
  rateLimitKey?: string
): Promise<Response> => {
  // Rate limiting
  if (rateLimitKey && !rateLimiter.isAllowed(rateLimitKey)) {
    throw new ValidationError('Too many requests, please try again later')
  }

  // Add security headers
  const secureOptions: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
      ...(options.headers || {})
    }
  }

  // Add CSRF token if making a mutation request
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method || 'GET')) {
    const csrfToken = sessionStorage.getItem('csrf_token') || generateCSRFToken()
    sessionStorage.setItem('csrf_token', csrfToken)

    secureOptions.headers = {
      ...secureOptions.headers,
      'X-CSRF-Token': csrfToken
    }
  }

  return fetch(url, secureOptions)
}