/**
 * BCM Scenario Hub Service
 * Handles marketplace functionality for BCM scenarios including community features
 */

import { api } from './api'
import { eventBus } from './eventbus'

class BCMScenarioHubService {
  constructor() {
    this.baseURL = '/api/bcm-scenario-hub'
    this.odooModule = 'bcm_scenario_hub'
  }

  // Scenario Catalog Management
  async getScenarios(params = {}) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios`, {
        params: {
          page: params.page || 1,
          limit: params.limit || 20,
          category: params.category,
          tags: params.tags,
          search: params.search,
          sort: params.sort || 'created_desc',
          featured: params.featured,
          author: params.author,
          status: params.status || 'published'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching scenarios:', error)
      throw error
    }
  }

  async getScenario(scenarioId) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching scenario:', error)
      throw error
    }
  }

  async getScenarioVersions(scenarioId) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/versions`)
      return response.data
    } catch (error) {
      console.error('Error fetching scenario versions:', error)
      throw error
    }
  }

  // Community Features
  async publishScenario(scenarioData) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios`, scenarioData)
      eventBus.emit('scenario:published', response.data)
      return response.data
    } catch (error) {
      console.error('Error publishing scenario:', error)
      throw error
    }
  }

  async updateScenario(scenarioId, updates) {
    try {
      const response = await api.put(`${this.baseURL}/scenarios/${scenarioId}`, updates)
      eventBus.emit('scenario:updated', response.data)
      return response.data
    } catch (error) {
      console.error('Error updating scenario:', error)
      throw error
    }
  }

  async deleteScenario(scenarioId) {
    try {
      await api.delete(`${this.baseURL}/scenarios/${scenarioId}`)
      eventBus.emit('scenario:deleted', { scenarioId })
      return true
    } catch (error) {
      console.error('Error deleting scenario:', error)
      throw error
    }
  }

  // Rating and Review System
  async getScenarioRatings(scenarioId) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/ratings`)
      return response.data
    } catch (error) {
      console.error('Error fetching ratings:', error)
      throw error
    }
  }

  async rateScenario(scenarioId, rating, review = null) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/ratings`, {
        rating,
        review
      })
      eventBus.emit('scenario:rated', { scenarioId, rating, review })
      return response.data
    } catch (error) {
      console.error('Error rating scenario:', error)
      throw error
    }
  }

  async getScenarioReviews(scenarioId, params = {}) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/reviews`, {
        params: {
          page: params.page || 1,
          limit: params.limit || 10,
          sort: params.sort || 'created_desc'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching reviews:', error)
      throw error
    }
  }

  async addReview(scenarioId, reviewData) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/reviews`, reviewData)
      eventBus.emit('review:added', response.data)
      return response.data
    } catch (error) {
      console.error('Error adding review:', error)
      throw error
    }
  }

  // Favorites and Collections
  async toggleFavorite(scenarioId) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/favorite`)
      eventBus.emit('scenario:favorited', { scenarioId, favorited: response.data.favorited })
      return response.data
    } catch (error) {
      console.error('Error toggling favorite:', error)
      throw error
    }
  }

  async getFavorites() {
    try {
      const response = await api.get(`${this.baseURL}/favorites`)
      return response.data
    } catch (error) {
      console.error('Error fetching favorites:', error)
      throw error
    }
  }

  // Comments and Community Engagement
  async getScenarioComments(scenarioId, params = {}) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/comments`, {
        params: {
          page: params.page || 1,
          limit: params.limit || 20
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching comments:', error)
      throw error
    }
  }

  async addComment(scenarioId, commentData) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/comments`, commentData)
      eventBus.emit('comment:added', response.data)
      return response.data
    } catch (error) {
      console.error('Error adding comment:', error)
      throw error
    }
  }

  async updateComment(commentId, updates) {
    try {
      const response = await api.put(`${this.baseURL}/comments/${commentId}`, updates)
      eventBus.emit('comment:updated', response.data)
      return response.data
    } catch (error) {
      console.error('Error updating comment:', error)
      throw error
    }
  }

  async deleteComment(commentId) {
    try {
      await api.delete(`${this.baseURL}/comments/${commentId}`)
      eventBus.emit('comment:deleted', { commentId })
      return true
    } catch (error) {
      console.error('Error deleting comment:', error)
      throw error
    }
  }

  // Search and Discovery
  async searchScenarios(query, filters = {}) {
    try {
      const response = await api.post(`${this.baseURL}/search`, {
        query,
        filters: {
          categories: filters.categories || [],
          tags: filters.tags || [],
          rating: filters.rating,
          difficulty: filters.difficulty,
          duration: filters.duration,
          author: filters.author,
          dateRange: filters.dateRange
        },
        sort: filters.sort || 'relevance'
      })
      return response.data
    } catch (error) {
      console.error('Error searching scenarios:', error)
      throw error
    }
  }

  async getPopularScenarios(limit = 10) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/popular`, {
        params: { limit }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching popular scenarios:', error)
      throw error
    }
  }

  async getFeaturedScenarios() {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/featured`)
      return response.data
    } catch (error) {
      console.error('Error fetching featured scenarios:', error)
      throw error
    }
  }

  // Categories and Tags
  async getCategories() {
    try {
      const response = await api.get(`${this.baseURL}/categories`)
      return response.data
    } catch (error) {
      console.error('Error fetching categories:', error)
      throw error
    }
  }

  async getTags() {
    try {
      const response = await api.get(`${this.baseURL}/tags`)
      return response.data
    } catch (error) {
      console.error('Error fetching tags:', error)
      throw error
    }
  }

  async getPopularTags(limit = 20) {
    try {
      const response = await api.get(`${this.baseURL}/tags/popular`, {
        params: { limit }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching popular tags:', error)
      throw error
    }
  }

  // Scenario Application and Customization
  async applyScenario(scenarioId, customizations = {}) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/apply`, {
        customizations,
        clientId: customizations.clientId
      })
      eventBus.emit('scenario:applied', response.data)
      return response.data
    } catch (error) {
      console.error('Error applying scenario:', error)
      throw error
    }
  }

  async customizeScenario(scenarioId, customizations) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/customize`, customizations)
      return response.data
    } catch (error) {
      console.error('Error customizing scenario:', error)
      throw error
    }
  }

  async previewCustomization(scenarioId, customizations) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/preview`, customizations)
      return response.data
    } catch (error) {
      console.error('Error previewing customization:', error)
      throw error
    }
  }

  // Import/Export
  async exportScenario(scenarioId, format = 'json') {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/export`, {
        params: { format },
        responseType: 'blob'
      })
      return response.data
    } catch (error) {
      console.error('Error exporting scenario:', error)
      throw error
    }
  }

  async importScenario(fileData, metadata = {}) {
    try {
      const formData = new FormData()
      formData.append('file', fileData)
      formData.append('metadata', JSON.stringify(metadata))

      const response = await api.post(`${this.baseURL}/scenarios/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      eventBus.emit('scenario:imported', response.data)
      return response.data
    } catch (error) {
      console.error('Error importing scenario:', error)
      throw error
    }
  }

  // Moderation and Approval
  async submitForApproval(scenarioId) {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/submit-approval`)
      eventBus.emit('scenario:submitted', response.data)
      return response.data
    } catch (error) {
      console.error('Error submitting for approval:', error)
      throw error
    }
  }

  async getPendingApprovals() {
    try {
      const response = await api.get(`${this.baseURL}/moderation/pending`)
      return response.data
    } catch (error) {
      console.error('Error fetching pending approvals:', error)
      throw error
    }
  }

  async approveScenario(scenarioId, moderatorNotes = '') {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/approve`, {
        moderatorNotes
      })
      eventBus.emit('scenario:approved', response.data)
      return response.data
    } catch (error) {
      console.error('Error approving scenario:', error)
      throw error
    }
  }

  async rejectScenario(scenarioId, reason, moderatorNotes = '') {
    try {
      const response = await api.post(`${this.baseURL}/scenarios/${scenarioId}/reject`, {
        reason,
        moderatorNotes
      })
      eventBus.emit('scenario:rejected', response.data)
      return response.data
    } catch (error) {
      console.error('Error rejecting scenario:', error)
      throw error
    }
  }

  // AI Recommendations
  async getRecommendations(userId, params = {}) {
    try {
      const response = await api.get(`${this.baseURL}/ai/recommendations`, {
        params: {
          userId,
          limit: params.limit || 10,
          context: params.context || 'general'
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching AI recommendations:', error)
      throw error
    }
  }

  async getSimilarScenarios(scenarioId, limit = 5) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/similar`, {
        params: { limit }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching similar scenarios:', error)
      throw error
    }
  }

  // Analytics and Insights
  async getScenarioAnalytics(scenarioId) {
    try {
      const response = await api.get(`${this.baseURL}/scenarios/${scenarioId}/analytics`)
      return response.data
    } catch (error) {
      console.error('Error fetching scenario analytics:', error)
      throw error
    }
  }

  async getMarketplaceStats() {
    try {
      const response = await api.get(`${this.baseURL}/stats`)
      return response.data
    } catch (error) {
      console.error('Error fetching marketplace stats:', error)
      throw error
    }
  }

  // User Profile and Contributions
  async getUserProfile(userId) {
    try {
      const response = await api.get(`${this.baseURL}/users/${userId}/profile`)
      return response.data
    } catch (error) {
      console.error('Error fetching user profile:', error)
      throw error
    }
  }

  async getUserContributions(userId, params = {}) {
    try {
      const response = await api.get(`${this.baseURL}/users/${userId}/contributions`, {
        params: {
          page: params.page || 1,
          limit: params.limit || 10,
          type: params.type // scenarios, reviews, comments
        }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching user contributions:', error)
      throw error
    }
  }

  // Notifications
  async getNotifications() {
    try {
      const response = await api.get(`${this.baseURL}/notifications`)
      return response.data
    } catch (error) {
      console.error('Error fetching notifications:', error)
      throw error
    }
  }

  async markNotificationRead(notificationId) {
    try {
      await api.put(`${this.baseURL}/notifications/${notificationId}/read`)
      eventBus.emit('notification:read', { notificationId })
      return true
    } catch (error) {
      console.error('Error marking notification as read:', error)
      throw error
    }
  }

  // Integration with Forum Service
  async getForumDiscussions(scenarioId) {
    try {
      const response = await api.get(`/api/forum/discussions`, {
        params: { scenarioId }
      })
      return response.data
    } catch (error) {
      console.error('Error fetching forum discussions:', error)
      throw error
    }
  }

  async createForumDiscussion(scenarioId, discussionData) {
    try {
      const response = await api.post(`/api/forum/discussions`, {
        ...discussionData,
        scenarioId
      })
      return response.data
    } catch (error) {
      console.error('Error creating forum discussion:', error)
      throw error
    }
  }
}

// Create singleton instance
export const bcmScenarioHubService = new BCMScenarioHubService()
export default bcmScenarioHubService