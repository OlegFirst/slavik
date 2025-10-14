/**
 * API Client - Legacy compatibility wrapper for existing .js services
 * This provides backward compatibility for services that still use .js imports
 */

import { api } from './api'

// Export the api instance as default export for legacy .js files
export default api

// Also export as named export for modern usage
export { api }