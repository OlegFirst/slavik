/**
 * Format utilities for common data formatting needs
 */

/**
 * Format a number as currency
 */
export function formatCurrency(
  amount: number,
  currency: string = 'USD',
  locale: string = 'en-US'
): string {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency,
    }).format(amount)
  } catch (error) {
    console.error('Error formatting currency:', error)
    return amount.toString()
  }
}

/**
 * Format a number with thousand separators
 */
export function formatNumber(
  value: number,
  locale: string = 'en-US',
  options?: Intl.NumberFormatOptions
): string {
  try {
    return new Intl.NumberFormat(locale, options).format(value)
  } catch (error) {
    console.error('Error formatting number:', error)
    return value.toString()
  }
}

/**
 * Format a number as a percentage
 */
export function formatPercentage(
  value: number,
  decimals: number = 1,
  locale: string = 'en-US'
): string {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(value / 100)
  } catch (error) {
    console.error('Error formatting percentage:', error)
    return `${value}%`
  }
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Truncate text with ellipsis
 */
export function truncateText(text: string, maxLength: number, suffix: string = '...'): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - suffix.length) + suffix
}

/**
 * Format phone number
 */
export function formatPhoneNumber(phoneNumber: string, format: 'US' | 'INTERNATIONAL' = 'US'): string {
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '')

  if (format === 'US' && cleaned.length === 10) {
    // Format as (XXX) XXX-XXXX
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`
    }
  }

  if (format === 'US' && cleaned.length === 11 && cleaned[0] === '1') {
    // Format as +1 (XXX) XXX-XXXX
    const match = cleaned.match(/^1(\d{3})(\d{3})(\d{4})$/)
    if (match) {
      return `+1 (${match[1]}) ${match[2]}-${match[3]}`
    }
  }

  // Return original if no formatting applied
  return phoneNumber
}

/**
 * Format credit card number
 */
export function formatCreditCard(cardNumber: string): string {
  // Remove all non-digit characters
  const cleaned = cardNumber.replace(/\D/g, '')

  // Add spaces every 4 digits
  return cleaned.replace(/(\d{4})/g, '$1 ').trim()
}

/**
 * Capitalize first letter of each word
 */
export function titleCase(text: string): string {
  return text.replace(/\w\S*/g, (txt) =>
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  )
}

/**
 * Convert camelCase to sentence case
 */
export function camelToSentence(text: string): string {
  return text
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim()
}

/**
 * Convert snake_case to sentence case
 */
export function snakeToSentence(text: string): string {
  return text
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

/**
 * Generate initials from a full name
 */
export function getInitials(name: string, maxInitials: number = 2): string {
  if (!name) return ''

  const words = name.trim().split(/\s+/)
  const initials = words
    .slice(0, maxInitials)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')

  return initials
}

/**
 * Generate a random color based on a string
 */
export function stringToColor(str: string): string {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }

  const hue = Math.abs(hash) % 360
  return `hsl(${hue}, 65%, 50%)`
}

/**
 * Format a URL to display only the domain
 */
export function formatUrl(url: string): string {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch (error) {
    return url
  }
}

/**
 * Sanitize HTML by removing script tags and other dangerous elements
 */
export function sanitizeHtml(html: string): string {
  const temp = document.createElement('div')
  temp.innerHTML = html

  // Remove script tags
  const scripts = temp.querySelectorAll('script')
  scripts.forEach((script) => script.remove())

  // Remove onclick and other event handlers
  const allElements = temp.querySelectorAll('*')
  allElements.forEach((element) => {
    const attributes = element.getAttributeNames()
    attributes.forEach((attr) => {
      if (attr.startsWith('on')) {
        element.removeAttribute(attr)
      }
    })
  })

  return temp.innerHTML
}

/**
 * Generate a slug from text
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens
}

/**
 * Mask sensitive data (e.g., credit card, SSN)
 */
export function maskData(data: string, visibleChars: number = 4, maskChar: string = '*'): string {
  if (data.length <= visibleChars) return data

  const visible = data.slice(-visibleChars)
  const masked = maskChar.repeat(data.length - visibleChars)
  return masked + visible
}

/**
 * Format address for display
 */
export function formatAddress(address: {
  street?: string
  city?: string
  state?: string
  zip?: string
  country?: string
}): string {
  const parts = [
    address.street,
    address.city,
    [address.state, address.zip].filter(Boolean).join(' '),
    address.country,
  ].filter(Boolean)

  return parts.join(', ')
}