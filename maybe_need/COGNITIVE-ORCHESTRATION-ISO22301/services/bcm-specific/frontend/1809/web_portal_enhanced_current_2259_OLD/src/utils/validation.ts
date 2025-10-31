/**
 * Validation utilities for form inputs and data validation
 */

/**
 * Check if a value is empty
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim().length === 0
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * Validate email address
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate phone number (US format)
 */
export function isValidPhoneNumber(phone: string): boolean {
  const phoneRegex = /^[\+]?[1-9]?[\d\s\-\(\)]{8,15}$/
  return phoneRegex.test(phone)
}

/**
 * Validate URL
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): {
  isValid: boolean
  errors: string[]
  strength: 'weak' | 'medium' | 'strong'
} {
  const errors: string[] = []
  let score = 0

  // Length check
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long')
  } else {
    score += 1
  }

  // Uppercase letter check
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter')
  } else {
    score += 1
  }

  // Lowercase letter check
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter')
  } else {
    score += 1
  }

  // Number check
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number')
  } else {
    score += 1
  }

  // Special character check
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain at least one special character')
  } else {
    score += 1
  }

  // Determine strength
  let strength: 'weak' | 'medium' | 'strong'
  if (score <= 2) {
    strength = 'weak'
  } else if (score <= 4) {
    strength = 'medium'
  } else {
    strength = 'strong'
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength,
  }
}

/**
 * Validate credit card number using Luhn algorithm
 */
export function isValidCreditCard(cardNumber: string): boolean {
  const cleanNumber = cardNumber.replace(/\D/g, '')

  if (cleanNumber.length < 13 || cleanNumber.length > 19) {
    return false
  }

  let sum = 0
  let isEven = false

  for (let i = cleanNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cleanNumber[i])

    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit = digit % 10 + 1
      }
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

/**
 * Validate IP address
 */
export function isValidIP(ip: string): boolean {
  const ipv4Regex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
  const ipv6Regex = /^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/
  return ipv4Regex.test(ip) || ipv6Regex.test(ip)
}

/**
 * Validate date string
 */
export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString)
  return !isNaN(date.getTime())
}

/**
 * Validate age range
 */
export function isValidAge(birthDate: string | Date, minAge: number = 0, maxAge: number = 150): boolean {
  const birth = typeof birthDate === 'string' ? new Date(birthDate) : birthDate
  const today = new Date()
  const age = today.getFullYear() - birth.getFullYear()

  return age >= minAge && age <= maxAge
}

/**
 * Validate file type
 */
export function isValidFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type)
}

/**
 * Validate file size
 */
export function isValidFileSize(file: File, maxSizeBytes: number): boolean {
  return file.size <= maxSizeBytes
}

/**
 * Validate required fields in an object
 */
export function validateRequiredFields(
  data: Record<string, any>,
  requiredFields: string[]
): { isValid: boolean; missingFields: string[] } {
  const missingFields: string[] = []

  requiredFields.forEach((field) => {
    if (isEmpty(data[field])) {
      missingFields.push(field)
    }
  })

  return {
    isValid: missingFields.length === 0,
    missingFields,
  }
}

/**
 * Validate numeric range
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * Validate string length
 */
export function isValidLength(
  str: string,
  minLength: number = 0,
  maxLength: number = Infinity
): boolean {
  return str.length >= minLength && str.length <= maxLength
}

/**
 * Validate alphanumeric characters only
 */
export function isAlphanumeric(str: string): boolean {
  const alphanumericRegex = /^[a-zA-Z0-9]+$/
  return alphanumericRegex.test(str)
}

/**
 * Validate that string contains only letters
 */
export function isAlpha(str: string): boolean {
  const alphaRegex = /^[a-zA-Z]+$/
  return alphaRegex.test(str)
}

/**
 * Validate that string contains only numbers
 */
export function isNumeric(str: string): boolean {
  const numericRegex = /^[0-9]+$/
  return numericRegex.test(str)
}

/**
 * Validate postal code (US ZIP code)
 */
export function isValidPostalCode(postalCode: string, country: string = 'US'): boolean {
  const patterns: Record<string, RegExp> = {
    US: /^\d{5}(-\d{4})?$/,
    CA: /^[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d$/,
    UK: /^[A-Za-z]{1,2}\d[A-Za-z\d]?\s\d[A-Za-z]{2}$/,
  }

  const pattern = patterns[country.toUpperCase()]
  return pattern ? pattern.test(postalCode) : true
}

/**
 * Validate social security number (US format)
 */
export function isValidSSN(ssn: string): boolean {
  const ssnRegex = /^\d{3}-\d{2}-\d{4}$/
  return ssnRegex.test(ssn)
}

/**
 * Custom validation rule interface
 */
export interface ValidationRule {
  test: (value: any) => boolean
  message: string
}

/**
 * Run multiple validation rules
 */
export function runValidationRules(
  value: any,
  rules: ValidationRule[]
): { isValid: boolean; errors: string[] } {
  const errors: string[] = []

  rules.forEach((rule) => {
    if (!rule.test(value)) {
      errors.push(rule.message)
    }
  })

  return {
    isValid: errors.length === 0,
    errors,
  }
}