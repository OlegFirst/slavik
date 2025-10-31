/**
 * BCM Portal API Service
 * Handles client self-service portal API calls
 * Integrates with Odoo bcm_portal module and Keycloak SSO
 */

import apiClient from './apiClient'

class BCMPortalService {
  constructor() {
    this.apiClient = apiClient
    this.tenantId = this.getCurrentTenantId()
  }

  /**
   * Get current tenant ID from token or localStorage
   */
  getCurrentTenantId() {
    try {
      const token = localStorage.getItem('bcm_auth_token')
      if (token) {
        // Decode JWT token to get tenant info (simplified)
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.tenant_id
      }
      return localStorage.getItem('client_tenant_id') || null
    } catch (error) {
      console.warn('Failed to extract tenant ID:', error)
      return null
    }
  }

  /**
   * Get client dashboard overview
   */
  async getDashboardOverview() {
    try {
      const response = await this.apiClient.call(
        'bcm.portal.dashboard',
        'get_client_overview',
        [this.tenantId],
        { context: { tenant_id: this.tenantId } }
      )
      return response
    } catch (error) {
      console.error('Failed to fetch dashboard overview:', error)
      throw error
    }
  }

  /**
   * Get client service requests
   */
  async getServiceRequests(filters = {}) {
    try {
      const domain = [['client_id.tenant_id', '=', this.tenantId]]

      if (filters.status) {
        domain.push(['state', '=', filters.status])
      }
      if (filters.type) {
        domain.push(['request_type', '=', filters.type])
      }
      if (filters.dateFrom) {
        domain.push(['create_date', '>=', filters.dateFrom])
      }
      if (filters.dateTo) {
        domain.push(['create_date', '<=', filters.dateTo])
      }

      return await this.apiClient.searchRead(
        'bcm.portal.service.request',
        domain,
        ['name', 'request_type', 'description', 'state', 'priority', 'create_date', 'expected_completion', 'assigned_to'],
        { order: 'create_date desc' }
      )
    } catch (error) {
      console.error('Failed to fetch service requests:', error)
      throw error
    }
  }

  /**
   * Create new service request
   */
  async createServiceRequest(requestData) {
    try {
      const values = {
        ...requestData,
        client_id: await this.getClientId(),
        tenant_id: this.tenantId,
        state: 'draft'
      }

      const requestId = await this.apiClient.create('bcm.portal.service.request', values)

      // Send notification to client
      await this.sendNotification({
        type: 'service_request_created',
        title: 'Service Request Created',
        message: `Your service request "${requestData.name}" has been submitted successfully.`,
        request_id: requestId
      })

      return requestId
    } catch (error) {
      console.error('Failed to create service request:', error)
      throw error
    }
  }

  /**
   * Get document library for client
   */
  async getDocumentLibrary(filters = {}) {
    try {
      const domain = [
        ['client_access', '=', true],
        '|',
        ['client_ids', 'in', [await this.getClientId()]],
        ['is_public', '=', true]
      ]

      if (filters.category) {
        domain.push(['category_id', '=', filters.category])
      }
      if (filters.search) {
        domain.push([
          '|',
          ['name', 'ilike', filters.search],
          ['description', 'ilike', filters.search]
        ])
      }

      return await this.apiClient.searchRead(
        'bcm.document',
        domain,
        ['name', 'description', 'category_id', 'file_size', 'create_date', 'document_type', 'version'],
        { order: 'create_date desc' }
      )
    } catch (error) {
      console.error('Failed to fetch document library:', error)
      throw error
    }
  }

  /**
   * Download document
   */
  async downloadDocument(documentId) {
    try {
      const response = await this.apiClient.call(
        'bcm.document',
        'download_document',
        [documentId],
        { context: { client_id: await this.getClientId() } }
      )
      return response
    } catch (error) {
      console.error('Failed to download document:', error)
      throw error
    }
  }

  /**
   * Get available training programs
   */
  async getTrainingPrograms(filters = {}) {
    try {
      const domain = [
        ['client_access', '=', true],
        ['state', '=', 'published']
      ]

      if (filters.type) {
        domain.push(['training_type', '=', filters.type])
      }
      if (filters.level) {
        domain.push(['difficulty_level', '=', filters.level])
      }

      return await this.apiClient.searchRead(
        'bcm.training.program',
        domain,
        ['name', 'description', 'training_type', 'duration', 'difficulty_level', 'enrollment_count', 'rating'],
        { order: 'name asc' }
      )
    } catch (error) {
      console.error('Failed to fetch training programs:', error)
      throw error
    }
  }

  /**
   * Enroll in training program
   */
  async enrollInTraining(programId, userId = null) {
    try {
      const values = {
        program_id: programId,
        client_id: await this.getClientId(),
        user_id: userId || await this.getCurrentUserId(),
        enrollment_date: new Date().toISOString().split('T')[0],
        status: 'enrolled'
      }

      const enrollmentId = await this.apiClient.create('bcm.training.enrollment', values)

      // Send confirmation notification
      await this.sendNotification({
        type: 'training_enrolled',
        title: 'Training Enrollment Confirmed',
        message: `You have been successfully enrolled in the training program.`,
        program_id: programId
      })

      return enrollmentId
    } catch (error) {
      console.error('Failed to enroll in training:', error)
      throw error
    }
  }

  /**
   * Get client training enrollments
   */
  async getTrainingEnrollments() {
    try {
      const domain = [['client_id', '=', await this.getClientId()]]

      return await this.apiClient.searchRead(
        'bcm.training.enrollment',
        domain,
        ['program_id', 'status', 'enrollment_date', 'completion_date', 'progress', 'certificate_id'],
        { order: 'enrollment_date desc' }
      )
    } catch (error) {
      console.error('Failed to fetch training enrollments:', error)
      throw error
    }
  }

  /**
   * Get available exercises for client participation
   */
  async getAvailableExercises() {
    try {
      const domain = [
        ['client_participation', '=', true],
        ['state', 'in', ['scheduled', 'in_progress']]
      ]

      return await this.apiClient.searchRead(
        'bcm.exercise',
        domain,
        ['name', 'description', 'exercise_type', 'scheduled_date', 'duration', 'state', 'participant_count'],
        { order: 'scheduled_date asc' }
      )
    } catch (error) {
      console.error('Failed to fetch available exercises:', error)
      throw error
    }
  }

  /**
   * Register for exercise participation
   */
  async registerForExercise(exerciseId, participantData) {
    try {
      const values = {
        exercise_id: exerciseId,
        client_id: await this.getClientId(),
        participant_name: participantData.name,
        participant_email: participantData.email,
        participant_role: participantData.role,
        registration_date: new Date().toISOString(),
        status: 'registered'
      }

      const participationId = await this.apiClient.create('bcm.exercise.participation', values)

      // Send confirmation
      await this.sendNotification({
        type: 'exercise_registered',
        title: 'Exercise Registration Confirmed',
        message: `You have been registered for the exercise. Details will be sent closer to the date.`,
        exercise_id: exerciseId
      })

      return participationId
    } catch (error) {
      console.error('Failed to register for exercise:', error)
      throw error
    }
  }

  /**
   * Get client compliance status
   */
  async getComplianceStatus() {
    try {
      const response = await this.apiClient.call(
        'bcm.portal.compliance',
        'get_client_status',
        [await this.getClientId()],
        { context: { tenant_id: this.tenantId } }
      )
      return response
    } catch (error) {
      console.error('Failed to fetch compliance status:', error)
      throw error
    }
  }

  /**
   * Get SSO integration status
   */
  async getSSOStatus() {
    try {
      const response = await this.apiClient.call(
        'bcm.portal.sso',
        'get_client_sso_status',
        [await this.getClientId()]
      )
      return response
    } catch (error) {
      console.error('Failed to fetch SSO status:', error)
      // Return default status if API fails
      return {
        enabled: false,
        provider: 'keycloak',
        status: 'not_configured',
        last_sync: null
      }
    }
  }

  /**
   * Configure SSO for client
   */
  async configureSSOSettings(ssoConfig) {
    try {
      const response = await this.apiClient.call(
        'bcm.portal.sso',
        'configure_client_sso',
        [await this.getClientId(), ssoConfig]
      )
      return response
    } catch (error) {
      console.error('Failed to configure SSO:', error)
      throw error
    }
  }

  /**
   * Get client notifications
   */
  async getNotifications(filters = {}) {
    try {
      const domain = [['client_id', '=', await this.getClientId()]]

      if (filters.unreadOnly) {
        domain.push(['is_read', '=', false])
      }
      if (filters.type) {
        domain.push(['notification_type', '=', filters.type])
      }

      return await this.apiClient.searchRead(
        'bcm.portal.notification',
        domain,
        ['title', 'message', 'notification_type', 'is_read', 'create_date', 'priority'],
        { order: 'create_date desc', limit: filters.limit || 50 }
      )
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      throw error
    }
  }

  /**
   * Mark notification as read
   */
  async markNotificationRead(notificationId) {
    try {
      await this.apiClient.write('bcm.portal.notification', [notificationId], { is_read: true })
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      throw error
    }
  }

  /**
   * Send notification to client
   */
  async sendNotification(notificationData) {
    try {
      const values = {
        client_id: await this.getClientId(),
        title: notificationData.title,
        message: notificationData.message,
        notification_type: notificationData.type,
        priority: notificationData.priority || 'normal',
        is_read: false,
        create_date: new Date().toISOString()
      }

      return await this.apiClient.create('bcm.portal.notification', values)
    } catch (error) {
      console.error('Failed to send notification:', error)
      throw error
    }
  }

  /**
   * Get client ID for current tenant
   */
  async getClientId() {
    if (this._clientId) {
      return this._clientId
    }

    try {
      const clients = await this.apiClient.searchRead(
        'res.partner',
        [['tenant_id', '=', this.tenantId], ['is_company', '=', true]],
        ['id'],
        { limit: 1 }
      )

      this._clientId = clients.length > 0 ? clients[0].id : null
      return this._clientId
    } catch (error) {
      console.error('Failed to fetch client ID:', error)
      return null
    }
  }

  /**
   * Get current user ID
   */
  async getCurrentUserId() {
    try {
      const response = await this.apiClient.call('res.users', 'get_current_user_id', [])
      return response
    } catch (error) {
      console.error('Failed to get current user ID:', error)
      return null
    }
  }

  /**
   * Refresh authentication token
   */
  async refreshToken() {
    try {
      // This would integrate with Keycloak token refresh
      const refreshToken = localStorage.getItem('bcm_refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      // Call Keycloak refresh endpoint through our backend
      const response = await this.apiClient.post('/auth/refresh', {
        refresh_token: refreshToken,
        tenant_id: this.tenantId
      })

      if (response.data.access_token) {
        localStorage.setItem('bcm_auth_token', response.data.access_token)
        if (response.data.refresh_token) {
          localStorage.setItem('bcm_refresh_token', response.data.refresh_token)
        }
        return response.data
      } else {
        throw new Error('Token refresh failed')
      }
    } catch (error) {
      console.error('Failed to refresh token:', error)
      // Clear tokens and redirect to login
      localStorage.removeItem('bcm_auth_token')
      localStorage.removeItem('bcm_refresh_token')
      window.location.href = '/login'
      throw error
    }
  }

  /**
   * Logout and cleanup
   */
  async logout() {
    try {
      // Call logout endpoint to invalidate session
      await this.apiClient.post('/auth/logout', {
        tenant_id: this.tenantId
      })
    } catch (error) {
      console.warn('Logout API call failed:', error)
    } finally {
      // Clear local storage
      localStorage.removeItem('bcm_auth_token')
      localStorage.removeItem('bcm_refresh_token')
      localStorage.removeItem('client_tenant_id')

      // Redirect to login
      window.location.href = '/login'
    }
  }
}

export default new BCMPortalService()