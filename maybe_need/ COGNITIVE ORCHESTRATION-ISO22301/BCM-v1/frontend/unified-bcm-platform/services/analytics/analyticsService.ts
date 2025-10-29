/**
 * Analytics Service
 * Handles API communication for analytics dashboards and real-time data
 * Extracted from web_portal_enhanced and adapted for unified-bcm-platform
 */

import axios, { AxiosResponse } from 'axios'

// API Configuration
const ANALYTICS_BASE_URL = process.env.NEXT_PUBLIC_ANALYTICS_URL || 'http://localhost:8069/api/analytics'
const LEARNING_BASE_URL = process.env.NEXT_PUBLIC_LEARNING_URL || 'http://localhost:8085/learning'
const KNOWLEDGE_BASE_URL = process.env.NEXT_PUBLIC_KNOWLEDGE_URL || 'http://localhost:8069/bcm/community'

// Types
export interface DashboardMetrics {
  total_scenarios_with_data: number
  avg_platform_effectiveness: number
  total_exercises_completed: number
  total_scenarios: number
  total_exercises: number
  ai_generated_scenarios: number
  platform_effectiveness: number
}

export interface TopScenario {
  id: string
  title: string
  avg_rating: number
  exercise_count: number
  ai_generated: boolean
  category: string
  effectiveness: number
}

export interface AIRecommendation {
  id: string
  type: string
  priority: 'High' | 'Medium' | 'Low'
  title: string
  description: string
  confidence: number
  expected_impact: number
}

export interface ChartData {
  labels: string[]
  datasets: Array<{
    label?: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string
    tension?: number
  }>
}

export interface AnalyticsDashboard {
  dashboard: DashboardMetrics
  top_performing_scenarios: TopScenario[]
  recommendations: AIRecommendation[]
  charts: {
    effectiveness_trend: ChartData
    scenario_performance: ChartData
    exercise_type: ChartData
    ai_vs_manual: ChartData
  }
}

class AnalyticsService {
  private wsConnection: WebSocket | null = null
  private wsCallbacks: Array<(data: any) => void> = []

  /**
   * Get analytics dashboard data
   */
  async getDashboardData(): Promise<AnalyticsDashboard> {
    try {
      const response: AxiosResponse<AnalyticsDashboard> = await axios.get(
        `${LEARNING_BASE_URL}/dashboard`,
        {
          timeout: 10000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      )

      return response.data
    } catch (error: any) {
      console.warn('Learning API not available, falling back to mock data:', error.message)
      return this.getMockDashboardData()
    }
  }

  /**
   * Get Odoo analytics data
   */
  async getOdooAnalytics(dashboardType: 'executive' | 'ai_insights' | 'operational' = 'executive'): Promise<any> {
    try {
      const response = await axios.get(`${ANALYTICS_BASE_URL}/dashboard/${dashboardType}`, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      return response.data
    } catch (error: any) {
      console.warn('Odoo analytics API not available:', error.message)
      throw new Error(`Analytics service unavailable: ${error.message}`)
    }
  }

  /**
   * Refresh Odoo analytics dashboard
   */
  async refreshOdooAnalytics(): Promise<any> {
    try {
      const response = await axios.post(`${ANALYTICS_BASE_URL}/dashboard/refresh`, {}, {
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      return response.data
    } catch (error: any) {
      console.error('Failed to refresh Odoo analytics:', error.message)
      throw new Error(`Failed to refresh analytics: ${error.message}`)
    }
  }

  /**
   * Get scenario effectiveness data
   */
  async getScenarioEffectiveness(): Promise<any> {
    try {
      const response = await axios.get(`${ANALYTICS_BASE_URL}/scenario-effectiveness`, {
        timeout: 10000
      })

      return response.data
    } catch (error: any) {
      console.warn('Scenario effectiveness API not available:', error.message)
      return this.getMockScenarioEffectiveness()
    }
  }

  /**
   * Get AI recommendations
   */
  async getAIRecommendations(): Promise<AIRecommendation[]> {
    try {
      const response: AxiosResponse<AIRecommendation[]> = await axios.get(
        `${LEARNING_BASE_URL}/recommendations`,
        {
          timeout: 10000
        }
      )

      return response.data
    } catch (error: any) {
      console.warn('AI recommendations API not available:', error.message)
      return this.getMockRecommendations()
    }
  }

  /**
   * Submit exercise result for learning
   */
  async submitExerciseResult(exerciseData: any): Promise<any> {
    try {
      const response = await axios.post(`${LEARNING_BASE_URL}/exercise-result`, exerciseData, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      return response.data
    } catch (error: any) {
      console.error('Failed to submit exercise result:', error.message)
      throw new Error(`Failed to submit exercise result: ${error.message}`)
    }
  }

  /**
   * Get scenario insights
   */
  async getScenarioInsights(scenarioId: string): Promise<any> {
    try {
      const response = await axios.get(`${LEARNING_BASE_URL}/scenario/${scenarioId}/insights`, {
        timeout: 10000
      })

      return response.data
    } catch (error: any) {
      console.warn('Scenario insights API not available:', error.message)
      return this.getMockScenarioInsights(scenarioId)
    }
  }

  /**
   * Setup WebSocket connection for real-time updates
   */
  setupWebSocket(callback: (data: any) => void): void {
    this.wsCallbacks.push(callback)

    if (this.wsConnection) {
      return // Already connected
    }

    try {
      this.wsConnection = new WebSocket('ws://localhost:8085/ws/learning-updates')

      this.wsConnection.onopen = () => {
        console.log('Analytics WebSocket connected')
      }

      this.wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.wsCallbacks.forEach(cb => cb(data))
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.wsConnection.onclose = () => {
        console.log('Analytics WebSocket disconnected')
        this.wsConnection = null

        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          if (this.wsCallbacks.length > 0) {
            this.setupWebSocket(() => {}) // Reconnect with existing callbacks
          }
        }, 5000)
      }

      this.wsConnection.onerror = (error) => {
        console.warn('Analytics WebSocket error:', error)
      }

    } catch (error) {
      console.warn('WebSocket not available - continuing without real-time updates')
    }
  }

  /**
   * Close WebSocket connection
   */
  closeWebSocket(): void {
    if (this.wsConnection) {
      this.wsConnection.close()
      this.wsConnection = null
    }
    this.wsCallbacks = []
  }

  /**
   * Knowledge Base API methods
   */
  async getKnowledgeArticles(params: any = {}): Promise<any> {
    try {
      const response = await axios.get(`${KNOWLEDGE_BASE_URL}/api/knowledge/articles`, {
        params,
        timeout: 10000
      })

      return response.data
    } catch (error: any) {
      console.warn('Knowledge base API not available:', error.message)
      return this.getMockKnowledgeArticles()
    }
  }

  async searchKnowledge(query: string): Promise<any> {
    try {
      const response = await axios.get(`${KNOWLEDGE_BASE_URL}/api/knowledge/search`, {
        params: { q: query },
        timeout: 10000
      })

      return response.data
    } catch (error: any) {
      console.warn('Knowledge search API not available:', error.message)
      return { articles: [], total: 0 }
    }
  }

  async bookmarkArticle(articleId: string): Promise<any> {
    try {
      const response = await axios.post(`${KNOWLEDGE_BASE_URL}/api/knowledge/articles/${articleId}/bookmark`, {}, {
        timeout: 10000
      })

      return response.data
    } catch (error: any) {
      console.error('Failed to bookmark article:', error.message)
      throw new Error(`Failed to bookmark article: ${error.message}`)
    }
  }

  async generateArticleFromExercise(exerciseId: string): Promise<any> {
    try {
      const response = await axios.post(`${KNOWLEDGE_BASE_URL}/api/knowledge/generate-from-exercise`, {
        exercise_id: exerciseId
      }, {
        timeout: 30000
      })

      return response.data
    } catch (error: any) {
      console.error('Failed to generate article from exercise:', error.message)
      throw new Error(`Failed to generate article: ${error.message}`)
    }
  }

  // Mock data methods for fallback
  private getMockDashboardData(): AnalyticsDashboard {
    return {
      dashboard: {
        total_scenarios_with_data: 15,
        avg_platform_effectiveness: 78.5,
        total_exercises_completed: 45,
        total_scenarios: 23,
        total_exercises: 52,
        ai_generated_scenarios: 8,
        platform_effectiveness: 76.2
      },
      top_performing_scenarios: [
        {
          id: '1',
          title: 'Critical System Failure Response',
          avg_rating: 8.5,
          exercise_count: 12,
          ai_generated: true,
          category: 'IT Disaster',
          effectiveness: 85
        },
        {
          id: '2',
          title: 'Supply Chain Disruption',
          avg_rating: 7.8,
          exercise_count: 8,
          ai_generated: false,
          category: 'Business Continuity',
          effectiveness: 78
        },
        {
          id: '3',
          title: 'Pandemic Response Protocol',
          avg_rating: 9.1,
          exercise_count: 15,
          ai_generated: true,
          category: 'Health Emergency',
          effectiveness: 91
        }
      ],
      recommendations: this.getMockRecommendations(),
      charts: {
        effectiveness_trend: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Platform Effectiveness',
            data: [65, 70, 75, 72, 78, 80],
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          }]
        },
        scenario_performance: {
          labels: ['High (>80%)', 'Medium (60-80%)', 'Low (<60%)'],
          datasets: [{
            data: [12, 8, 3],
            backgroundColor: ['#10B981', '#F59E0B', '#EF4444']
          }]
        },
        exercise_type: {
          labels: ['Tabletop', 'Simulation', 'Full Scale', 'Walkthrough'],
          datasets: [{
            label: 'Effectiveness %',
            data: [75, 82, 88, 70],
            backgroundColor: 'rgba(147, 51, 234, 0.8)'
          }]
        },
        ai_vs_manual: {
          labels: ['AI Generated', 'Manual Created'],
          datasets: [{
            label: 'Count',
            data: [15, 25],
            backgroundColor: ['rgba(99, 102, 241, 0.8)', 'rgba(107, 114, 128, 0.8)']
          }]
        }
      }
    }
  }

  private getMockRecommendations(): AIRecommendation[] {
    return [
      {
        id: 'rec_001',
        type: 'Exercise Completion',
        priority: 'High',
        title: 'Improve Exercise Completion Rate',
        description: 'Current completion rate is 73%. Consider reviewing exercise complexity and providing better guidance to participants.',
        confidence: 85,
        expected_impact: 15
      },
      {
        id: 'rec_002',
        type: 'AI Enhancement',
        priority: 'Medium',
        title: 'Increase AI-Generated Scenarios',
        description: 'Only 35% of scenarios are AI-generated. Consider using AI to create more diverse scenarios for better coverage.',
        confidence: 75,
        expected_impact: 20
      },
      {
        id: 'rec_003',
        type: 'Performance',
        priority: 'Medium',
        title: 'Focus on Low-Performing Scenario Categories',
        description: 'IT Disaster scenarios show lower effectiveness. Review and update these scenarios with recent best practices.',
        confidence: 80,
        expected_impact: 12
      }
    ]
  }

  private getMockScenarioEffectiveness(): any {
    return {
      effectiveness_by_category: [
        { category: 'IT Disaster', effectiveness: 72, count: 8 },
        { category: 'Business Continuity', effectiveness: 85, count: 12 },
        { category: 'Health Emergency', effectiveness: 91, count: 5 },
        { category: 'Natural Disaster', effectiveness: 78, count: 6 }
      ],
      trend_data: {
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [{
          label: 'Effectiveness Trend',
          data: [72, 76, 78, 80],
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)'
        }]
      }
    }
  }

  private getMockScenarioInsights(scenarioId: string): any {
    return {
      scenario_id: scenarioId,
      insights: {
        total_executions: 12,
        avg_rating: 8.2,
        effectiveness: 82,
        improvement_areas: [
          'Response time optimization',
          'Communication protocols',
          'Resource allocation'
        ],
        strengths: [
          'Clear escalation procedures',
          'Well-defined roles',
          'Effective recovery strategies'
        ]
      },
      historical_performance: {
        labels: ['Ex1', 'Ex2', 'Ex3', 'Ex4', 'Ex5'],
        data: [7.5, 8.0, 8.2, 8.1, 8.5]
      }
    }
  }

  private getMockKnowledgeArticles(): any {
    return {
      articles: [
        {
          id: '1',
          title: 'Business Continuity Planning Best Practices',
          summary: 'Comprehensive guide to developing effective BCPs',
          category: 'Planning',
          view_count: 156,
          usefulness_score: 4.7,
          is_published: true,
          article_type: 'manual'
        },
        {
          id: '2',
          title: 'AI-Generated Crisis Communication Templates',
          summary: 'Templates for effective crisis communication',
          category: 'Communication',
          view_count: 89,
          usefulness_score: 4.3,
          is_published: true,
          article_type: 'ai_generated'
        }
      ],
      total: 2,
      categories: [
        { name: 'Planning', count: 15 },
        { name: 'Communication', count: 8 },
        { name: 'Recovery', count: 12 }
      ]
    }
  }
}

// Export singleton instance
export const analyticsService = new AnalyticsService()
export default analyticsService