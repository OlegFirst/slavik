/**
 * BCM Base API Service
 * Handles communication with Odoo bcm_base module
 */

import apiClient from './apiClient'

class BCMBaseService {
  constructor() {
    this.baseURL = '/web/dataset/call_kw/bcm.base'
    this.organizationURL = '/web/dataset/call_kw/bcm.organization'
    this.locationURL = '/web/dataset/call_kw/bcm.location'
    this.assetURL = '/web/dataset/call_kw/bcm.asset'
    this.contactURL = '/web/dataset/call_kw/bcm.contact'
  }

  /**
   * Get all base data
   */
  async getBaseData() {
    try {
      const [organizations, locations, assets, contacts, metrics] = await Promise.all([
        this.getOrganizations(),
        this.getLocations(),
        this.getAssets(),
        this.getContacts(),
        this.getBaseMetrics()
      ])

      return {
        organizations,
        locations,
        assets,
        contacts,
        metrics
      }
    } catch (error) {
      console.error('Failed to get base data:', error)
      throw error
    }
  }

  /**
   * Get base metrics
   */
  async getBaseMetrics() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.base',
          method: 'get_base_metrics',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get base metrics:', error)
      return {
        total_records: 0,
        active_records: 0,
        recent_updates: 0,
        last_sync: null
      }
    }
  }

  /**
   * Get organizations
   */
  async getOrganizations() {
    try {
      const response = await apiClient.post(this.organizationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.organization',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'description', 'type', 'status', 'contact_email', 'write_date'],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get organizations:', error)
      return []
    }
  }

  /**
   * Get locations
   */
  async getLocations() {
    try {
      const response = await apiClient.post(this.locationURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.location',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'code', 'address', 'type', 'capacity', 'status'],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get locations:', error)
      return []
    }
  }

  /**
   * Get assets
   */
  async getAssets() {
    try {
      const response = await apiClient.post(this.assetURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.asset',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'asset_id', 'category', 'criticality', 'owner_id', 'owner_name', 'status'],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get assets:', error)
      return []
    }
  }

  /**
   * Get contacts
   */
  async getContacts() {
    try {
      const response = await apiClient.post(this.contactURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.contact',
          method: 'search_read',
          args: [[]],
          kwargs: {
            fields: ['name', 'title', 'role', 'organization', 'phone', 'email'],
            order: 'name asc'
          }
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to get contacts:', error)
      return []
    }
  }

  /**
   * Create entry
   */
  async createEntry(type, entryData) {
    const urlMap = {
      organization: this.organizationURL,
      location: this.locationURL,
      asset: this.assetURL,
      contact: this.contactURL
    }

    const modelMap = {
      organization: 'bcm.organization',
      location: 'bcm.location',
      asset: 'bcm.asset',
      contact: 'bcm.contact'
    }

    try {
      const response = await apiClient.post(urlMap[type], {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: modelMap[type],
          method: 'create',
          args: [entryData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error(`Failed to create ${type}:`, error)
      throw error
    }
  }

  /**
   * Update entry
   */
  async updateEntry(type, entryId, entryData) {
    const urlMap = {
      organization: this.organizationURL,
      location: this.locationURL,
      asset: this.assetURL,
      contact: this.contactURL
    }

    const modelMap = {
      organization: 'bcm.organization',
      location: 'bcm.location',
      asset: 'bcm.asset',
      contact: 'bcm.contact'
    }

    try {
      const response = await apiClient.post(urlMap[type], {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: modelMap[type],
          method: 'write',
          args: [entryId, entryData],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error(`Failed to update ${type}:`, error)
      throw error
    }
  }

  /**
   * Delete entry
   */
  async deleteEntry(type, entryId) {
    const urlMap = {
      organization: this.organizationURL,
      location: this.locationURL,
      asset: this.assetURL,
      contact: this.contactURL
    }

    const modelMap = {
      organization: 'bcm.organization',
      location: 'bcm.location',
      asset: 'bcm.asset',
      contact: 'bcm.contact'
    }

    try {
      const response = await apiClient.post(urlMap[type], {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: modelMap[type],
          method: 'unlink',
          args: [entryId],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error(`Failed to delete ${type}:`, error)
      throw error
    }
  }

  /**
   * Initialize base system
   */
  async initializeBase() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.base',
          method: 'initialize_system',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to initialize base system:', error)
      throw error
    }
  }

  /**
   * Sync master data
   */
  async syncMasterData() {
    try {
      const response = await apiClient.post(this.baseURL, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model: 'bcm.base',
          method: 'sync_master_data',
          args: [],
          kwargs: {}
        }
      })
      return response.data.result
    } catch (error) {
      console.error('Failed to sync master data:', error)
      throw error
    }
  }
}

export default new BCMBaseService()