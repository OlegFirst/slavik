/**
 * Local storage and session storage utilities
 * Provides a consistent interface for browser storage with error handling
 */

/**
 * Local storage wrapper with error handling and type safety
 */
export const localStorage = {
  /**
   * Get item from localStorage
   */
  getItem<T = string>(key: string, defaultValue?: T): T | null {
    try {
      const item = window.localStorage.getItem(key)
      if (item === null) return defaultValue || null

      try {
        return JSON.parse(item)
      } catch {
        // If it's not JSON, return as string
        return item as unknown as T
      }
    } catch (error) {
      console.warn(`Error reading from localStorage key "${key}":`, error)
      return defaultValue || null
    }
  },

  /**
   * Set item in localStorage
   */
  setItem<T>(key: string, value: T): boolean {
    try {
      const serializedValue = typeof value === 'string' ? value : JSON.stringify(value)
      window.localStorage.setItem(key, serializedValue)
      return true
    } catch (error) {
      console.warn(`Error writing to localStorage key "${key}":`, error)
      return false
    }
  },

  /**
   * Remove item from localStorage
   */
  removeItem(key: string): boolean {
    try {
      window.localStorage.removeItem(key)
      return true
    } catch (error) {
      console.warn(`Error removing from localStorage key "${key}":`, error)
      return false
    }
  },

  /**
   * Clear all items from localStorage
   */
  clear(): boolean {
    try {
      window.localStorage.clear()
      return true
    } catch (error) {
      console.warn('Error clearing localStorage:', error)
      return false
    }
  },

  /**
   * Check if localStorage is available
   */
  isAvailable(): boolean {
    try {
      const test = '__localStorage_test__'
      window.localStorage.setItem(test, 'test')
      window.localStorage.removeItem(test)
      return true
    } catch {
      return false
    }
  }
}

/**
 * Session storage wrapper with error handling and type safety
 */
export const sessionStorage = {
  /**
   * Get item from sessionStorage
   */
  getItem<T = string>(key: string, defaultValue?: T): T | null {
    try {
      const item = window.sessionStorage.getItem(key)
      if (item === null) return defaultValue || null

      try {
        return JSON.parse(item)
      } catch {
        // If it's not JSON, return as string
        return item as unknown as T
      }
    } catch (error) {
      console.warn(`Error reading from sessionStorage key "${key}":`, error)
      return defaultValue || null
    }
  },

  /**
   * Set item in sessionStorage
   */
  setItem<T>(key: string, value: T): boolean {
    try {
      const serializedValue = typeof value === 'string' ? value : JSON.stringify(value)
      window.sessionStorage.setItem(key, serializedValue)
      return true
    } catch (error) {
      console.warn(`Error writing to sessionStorage key "${key}":`, error)
      return false
    }
  },

  /**
   * Remove item from sessionStorage
   */
  removeItem(key: string): boolean {
    try {
      window.sessionStorage.removeItem(key)
      return true
    } catch (error) {
      console.warn(`Error removing from sessionStorage key "${key}":`, error)
      return false
    }
  },

  /**
   * Clear all items from sessionStorage
   */
  clear(): boolean {
    try {
      window.sessionStorage.clear()
      return true
    } catch (error) {
      console.warn('Error clearing sessionStorage:', error)
      return false
    }
  },

  /**
   * Check if sessionStorage is available
   */
  isAvailable(): boolean {
    try {
      const test = '__sessionStorage_test__'
      window.sessionStorage.setItem(test, 'test')
      window.sessionStorage.removeItem(test)
      return true
    } catch {
      return false
    }
  }
}

/**
 * Storage keys used throughout the application
 */
export const STORAGE_KEYS = {
  // Authentication
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  REMEMBER_ME: 'remember_me',

  // App Settings
  THEME: 'app_theme',
  LANGUAGE: 'app_language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',

  // User Preferences
  TABLE_SETTINGS: 'table_settings',
  DASHBOARD_LAYOUT: 'dashboard_layout',
  NOTIFICATION_SETTINGS: 'notification_settings',

  // Temporary Data
  FORM_DRAFT: 'form_draft',
  SEARCH_HISTORY: 'search_history',
  RECENT_ITEMS: 'recent_items',
} as const

/**
 * Utility functions for common storage operations
 */

/**
 * Store user preferences
 */
export function saveUserPreferences(preferences: Record<string, any>): boolean {
  return localStorage.setItem('user_preferences', preferences)
}

/**
 * Load user preferences
 */
export function loadUserPreferences(): Record<string, any> {
  return localStorage.getItem('user_preferences', {})
}

/**
 * Store form draft data
 */
export function saveDraftData(formName: string, data: any): boolean {
  const key = `${STORAGE_KEYS.FORM_DRAFT}_${formName}`
  return sessionStorage.setItem(key, data)
}

/**
 * Load form draft data
 */
export function loadDraftData(formName: string): any {
  const key = `${STORAGE_KEYS.FORM_DRAFT}_${formName}`
  return sessionStorage.getItem(key)
}

/**
 * Clear form draft data
 */
export function clearDraftData(formName: string): boolean {
  const key = `${STORAGE_KEYS.FORM_DRAFT}_${formName}`
  return sessionStorage.removeItem(key)
}

/**
 * Add item to recent items list
 */
export function addToRecentItems(item: any, maxItems: number = 10): boolean {
  const recentItems = localStorage.getItem<any[]>(STORAGE_KEYS.RECENT_ITEMS, [])

  // Remove item if it already exists
  const filteredItems = recentItems.filter((existing: any) => existing.id !== item.id)

  // Add to beginning of array
  filteredItems.unshift(item)

  // Limit array size
  const limitedItems = filteredItems.slice(0, maxItems)

  return localStorage.setItem(STORAGE_KEYS.RECENT_ITEMS, limitedItems)
}

/**
 * Get recent items list
 */
export function getRecentItems(): any[] {
  return localStorage.getItem<any[]>(STORAGE_KEYS.RECENT_ITEMS, [])
}

/**
 * Clear recent items list
 */
export function clearRecentItems(): boolean {
  return localStorage.removeItem(STORAGE_KEYS.RECENT_ITEMS)
}

/**
 * Storage quota and usage utilities
 */

/**
 * Get storage quota information
 */
export async function getStorageQuota(): Promise<{
  quota: number
  usage: number
  available: number
  usagePercentage: number
} | null> {
  if ('storage' in navigator && 'estimate' in navigator.storage) {
    try {
      const estimate = await navigator.storage.estimate()
      const quota = estimate.quota || 0
      const usage = estimate.usage || 0
      const available = quota - usage
      const usagePercentage = quota > 0 ? (usage / quota) * 100 : 0

      return {
        quota,
        usage,
        available,
        usagePercentage
      }
    } catch (error) {
      console.warn('Error getting storage quota:', error)
      return null
    }
  }
  return null
}

/**
 * Check if storage is near quota limit
 */
export async function isStorageNearLimit(threshold: number = 80): Promise<boolean> {
  const quota = await getStorageQuota()
  return quota ? quota.usagePercentage >= threshold : false
}

/**
 * Cleanup old storage data
 */
export function cleanupOldStorageData(daysToKeep: number = 30): void {
  const cutoffTime = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000)

  // Check localStorage
  for (let i = 0; i < window.localStorage.length; i++) {
    const key = window.localStorage.key(i)
    if (key && key.includes('_timestamp_')) {
      try {
        const data = localStorage.getItem(key)
        if (typeof data === 'object' && data && 'timestamp' in data) {
          if (data.timestamp < cutoffTime) {
            localStorage.removeItem(key)
          }
        }
      } catch (error) {
        console.warn(`Error cleaning up storage key "${key}":`, error)
      }
    }
  }
}

/**
 * Export all storage data (for backup/debugging)
 */
export function exportStorageData(): {
  localStorage: Record<string, any>
  sessionStorage: Record<string, any>
} {
  const localData: Record<string, any> = {}
  const sessionData: Record<string, any> = {}

  // Export localStorage
  for (let i = 0; i < window.localStorage.length; i++) {
    const key = window.localStorage.key(i)
    if (key) {
      localData[key] = localStorage.getItem(key)
    }
  }

  // Export sessionStorage
  for (let i = 0; i < window.sessionStorage.length; i++) {
    const key = window.sessionStorage.key(i)
    if (key) {
      sessionData[key] = sessionStorage.getItem(key)
    }
  }

  return {
    localStorage: localData,
    sessionStorage: sessionData
  }
}