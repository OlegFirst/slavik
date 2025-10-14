/**
 * Scenario Orchestrator Service
 * Handles AI scenario generation, templates, and real-time progress tracking
 * Port: 8085
 */

import axios from 'axios'

const SCENARIO_ORCHESTRATOR_URL = 'http://localhost:8085'

// WebSocket connection for real-time updates
let wsConnection = null
let wsListeners = new Map()

/**
 * Create axios instance with default config
 */
const api = axios.create({
  baseURL: SCENARIO_ORCHESTRATOR_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request interceptor for authentication
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response interceptor for error handling
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * WebSocket connection management
 */
const connectWebSocket = () => {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
    return wsConnection
  }

  wsConnection = new WebSocket(`ws://localhost:8085/scenarios/generation-progress`)

  wsConnection.onopen = () => {
    console.log('WebSocket connected to Scenario Orchestrator')
  }

  wsConnection.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)

      // Notify all listeners for this scenario
      const listeners = wsListeners.get(data.scenario_id) || []
      listeners.forEach(callback => callback(data))
    } catch (error) {
      console.error('Error parsing WebSocket message:', error)
    }
  }

  wsConnection.onclose = () => {
    console.log('WebSocket disconnected from Scenario Orchestrator')
    // Attempt to reconnect after 3 seconds
    setTimeout(() => {
      if (wsListeners.size > 0) {
        connectWebSocket()
      }
    }, 3000)
  }

  wsConnection.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  return wsConnection
}

/**
 * Subscribe to scenario generation progress
 */
const subscribeToProgress = (scenarioId, callback) => {
  if (!wsListeners.has(scenarioId)) {
    wsListeners.set(scenarioId, [])
  }
  wsListeners.get(scenarioId).push(callback)

  // Ensure WebSocket connection is active
  connectWebSocket()
}

/**
 * Unsubscribe from scenario generation progress
 */
const unsubscribeFromProgress = (scenarioId, callback) => {
  const listeners = wsListeners.get(scenarioId) || []
  const index = listeners.indexOf(callback)
  if (index > -1) {
    listeners.splice(index, 1)
  }

  if (listeners.length === 0) {
    wsListeners.delete(scenarioId)
  }

  // Close WebSocket if no more listeners
  if (wsListeners.size === 0 && wsConnection) {
    wsConnection.close()
    wsConnection = null
  }
}

/**
 * Scenario Orchestrator API Service
 */
const scenarioOrchestratorService = {
  /**
   * Generate AI scenario
   * @param {Object} params - Scenario generation parameters
   * @returns {Promise<Object>} Generation response with scenario ID
   */
  async generateScenario(params) {
    try {
      const response = await api.post('/scenarios/generate', {
        category: params.category,
        complexity: params.complexity,
        duration_hours: params.duration_hours,
        participants: params.participants,
        organization_context: params.organization_context,
        affected_systems: params.affected_systems || [],
        custom_objectives: params.custom_objectives || [],
        industry_type: params.industry_type,
        compliance_requirements: params.compliance_requirements || [],
        scenario_type: params.scenario_type || 'tabletop',
        include_jaamsim: params.include_jaamsim || false,
        include_bpmn: params.include_bpmn || false,
        language: params.language || 'en',
        template_id: params.template_id
      })

      return {
        success: true,
        scenario_id: response.data.scenario_id,
        generation_id: response.data.generation_id,
        estimated_time: response.data.estimated_time,
        status: response.data.status
      }
    } catch (error) {
      console.error('Error generating scenario:', error)
      throw {
        success: false,
        error: error.response?.data?.message || error.message,
        code: error.response?.status || 500
      }
    }
  },

  /**
   * Get scenario generation status
   * @param {string} generationId - Generation ID
   * @returns {Promise<Object>} Generation status
   */
  async getGenerationStatus(generationId) {
    try {
      const response = await api.get(`/scenarios/generation/${generationId}/status`)
      return response.data
    } catch (error) {
      console.error('Error getting generation status:', error)
      throw error
    }
  },

  /**
   * Get generated scenario
   * @param {string} scenarioId - Scenario ID
   * @returns {Promise<Object>} Generated scenario data
   */
  async getGeneratedScenario(scenarioId) {
    try {
      const response = await api.get(`/scenarios/${scenarioId}`)
      return response.data
    } catch (error) {
      console.error('Error getting generated scenario:', error)
      throw error
    }
  },

  /**
   * Save generated scenario
   * @param {string} scenarioId - Scenario ID
   * @param {Object} metadata - Additional metadata
   * @returns {Promise<Object>} Save response
   */
  async saveScenario(scenarioId, metadata = {}) {
    try {
      const response = await api.post(`/scenarios/${scenarioId}/save`, {
        title: metadata.title,
        description: metadata.description,
        tags: metadata.tags || [],
        category: metadata.category,
        is_public: metadata.is_public || false,
        organization_id: metadata.organization_id
      })
      return response.data
    } catch (error) {
      console.error('Error saving scenario:', error)
      throw error
    }
  },

  /**
   * Get scenario templates
   * @param {Object} filters - Template filters
   * @returns {Promise<Array>} List of templates
   */
  async getTemplates(filters = {}) {
    try {
      const response = await api.get('/scenarios/templates', {
        params: {
          category: filters.category,
          complexity: filters.complexity,
          industry: filters.industry,
          type: filters.type,
          limit: filters.limit || 50,
          offset: filters.offset || 0
        }
      })
      return response.data.templates || []
    } catch (error) {
      console.error('Error getting templates:', error)
      throw error
    }
  },

  /**
   * Get template details
   * @param {string} templateId - Template ID
   * @returns {Promise<Object>} Template details
   */
  async getTemplate(templateId) {
    try {
      const response = await api.get(`/scenarios/templates/${templateId}`)
      return response.data
    } catch (error) {
      console.error('Error getting template:', error)
      throw error
    }
  },

  /**
   * Get scenario categories
   * @returns {Promise<Array>} List of categories
   */
  async getCategories() {
    try {
      const response = await api.get('/scenarios/categories')
      return response.data.categories || []
    } catch (error) {
      console.error('Error getting categories:', error)
      return [
        { id: 'cyber', name: 'Cyber Security Incident', icon: '🔒' },
        { id: 'epidemic', name: 'Epidemic/Pandemic', icon: '🦠' },
        { id: 'blackout', name: 'Power Blackout', icon: '⚡' },
        { id: 'supply', name: 'Supply Chain Disruption', icon: '📦' },
        { id: 'natural', name: 'Natural Disaster', icon: '🌪️' },
        { id: 'terrorism', name: 'Terrorism/Security', icon: '🎯' },
        { id: 'financial', name: 'Financial Crisis', icon: '💰' },
        { id: 'infrastructure', name: 'Infrastructure Failure', icon: '🏗️' },
        { id: 'data', name: 'Data Loss/Breach', icon: '💾' },
        { id: 'personnel', name: 'Key Personnel Loss', icon: '👥' }
      ]
    }
  },

  /**
   * Get industry types
   * @returns {Promise<Array>} List of industries
   */
  async getIndustryTypes() {
    try {
      const response = await api.get('/scenarios/industries')
      return response.data.industries || []
    } catch (error) {
      console.error('Error getting industries:', error)
      return [
        { id: 'healthcare', name: 'Healthcare', icon: '🏥' },
        { id: 'financial', name: 'Financial Services', icon: '🏦' },
        { id: 'manufacturing', name: 'Manufacturing', icon: '🏭' },
        { id: 'government', name: 'Government', icon: '🏛️' },
        { id: 'education', name: 'Education', icon: '🎓' },
        { id: 'retail', name: 'Retail', icon: '🛒' },
        { id: 'technology', name: 'Technology', icon: '💻' },
        { id: 'energy', name: 'Energy & Utilities', icon: '⚡' },
        { id: 'transportation', name: 'Transportation', icon: '🚚' },
        { id: 'telecommunications', name: 'Telecommunications', icon: '📡' }
      ]
    }
  },

  /**
   * Get available systems for selection
   * @param {string} organizationType - Organization type
   * @returns {Promise<Array>} List of systems
   */
  async getAvailableSystems(organizationType) {
    try {
      const response = await api.get('/scenarios/systems', {
        params: { organization_type: organizationType }
      })
      return response.data.systems || []
    } catch (error) {
      console.error('Error getting systems:', error)
      // Return default systems based on organization type
      const defaultSystems = {
        healthcare: ['EHR System', 'PACS', 'Laboratory System', 'Pharmacy System', 'Patient Monitoring', 'Communication System'],
        financial: ['Core Banking', 'Trading Platform', 'ATM Network', 'Payment Processing', 'Risk Management', 'Customer Portal'],
        manufacturing: ['ERP System', 'Production Line', 'Quality Control', 'Supply Chain', 'Inventory Management', 'Safety Systems'],
        government: ['Citizen Services', 'Document Management', 'Emergency Systems', 'Communication Network', 'Security Systems', 'Data Centers'],
        education: ['Student Information', 'Learning Management', 'Library System', 'Research Systems', 'Communication Platform', 'Campus Security'],
        retail: ['POS System', 'Inventory Management', 'E-commerce Platform', 'Customer Database', 'Supply Chain', 'Security Systems'],
        technology: ['Development Environment', 'Production Systems', 'Customer Platform', 'Data Analytics', 'Security Infrastructure', 'Communication Tools']
      }
      return defaultSystems[organizationType] || defaultSystems.technology
    }
  },

  /**
   * Cancel scenario generation
   * @param {string} generationId - Generation ID
   * @returns {Promise<Object>} Cancellation response
   */
  async cancelGeneration(generationId) {
    try {
      const response = await api.post(`/scenarios/generation/${generationId}/cancel`)
      return response.data
    } catch (error) {
      console.error('Error canceling generation:', error)
      throw error
    }
  },

  /**
   * Get generation history
   * @param {Object} filters - History filters
   * @returns {Promise<Array>} Generation history
   */
  async getGenerationHistory(filters = {}) {
    try {
      const response = await api.get('/scenarios/generation/history', {
        params: {
          limit: filters.limit || 20,
          offset: filters.offset || 0,
          status: filters.status,
          category: filters.category,
          start_date: filters.start_date,
          end_date: filters.end_date
        }
      })
      return response.data.history || []
    } catch (error) {
      console.error('Error getting generation history:', error)
      throw error
    }
  },

  /**
   * Get service health
   * @returns {Promise<Object>} Service health status
   */
  async getHealth() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      console.error('Error getting service health:', error)
      return { status: 'error', message: 'Service unavailable' }
    }
  },

  /**
   * WebSocket utilities
   */
  websocket: {
    subscribe: subscribeToProgress,
    unsubscribe: unsubscribeFromProgress,
    connect: connectWebSocket,
    disconnect: () => {
      if (wsConnection) {
        wsConnection.close()
        wsConnection = null
        wsListeners.clear()
      }
    }
  }
}

export default scenarioOrchestratorService