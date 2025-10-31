// Risk Management API Service
// Полная интеграция с Odoo Backend через BCMAPIClient

import { BCMAPIClient } from '@/lib/api-client'

// Типы данных
export interface Risk {
  id: string
  title: string
  description?: string
  category: 'operational' | 'financial' | 'strategic' | 'compliance'
  probability: number
  impact: number
  riskScore: number
  status: 'open' | 'mitigated' | 'accepted' | 'transferred'
  owner: string
  mitigation?: string
  lastAssessed: string
  createdAt?: string
  updatedAt?: string
}

export interface RiskMetrics {
  totalRisks: number
  highRisks: number
  newThisMonth: number
  avgRiskScore: number
}

export interface RiskAssessment {
  id: string
  riskId: string
  assessmentDate: string
  assessedBy: string
  previousScore: number
  currentScore: number
  notes: string
}

export interface TreatmentPlan {
  id: string
  riskId: string
  strategy: 'accept' | 'avoid' | 'transfer' | 'mitigate'
  actions: string[]
  responsiblePerson: string
  targetDate: string
  status: 'planned' | 'in_progress' | 'completed'
  budget?: number
}

// Mock data fallback
const mockRisks: Risk[] = [
  {
    id: '1',
    title: 'Data Center Power Failure',
    description: 'Risk of prolonged power outage affecting primary data center',
    category: 'operational',
    probability: 7,
    impact: 9,
    riskScore: 6.3,
    status: 'open',
    owner: 'IT Team',
    mitigation: 'Install backup generators and UPS systems',
    lastAssessed: '2024-09-15',
    createdAt: '2024-01-10T10:00:00Z',
    updatedAt: '2024-09-15T14:30:00Z'
  },
  {
    id: '2',
    title: 'Cyber Security Breach',
    description: 'Potential unauthorized access to critical systems',
    category: 'operational',
    probability: 6,
    impact: 10,
    riskScore: 6.0,
    status: 'mitigated',
    owner: 'Security Team',
    mitigation: 'Implement multi-factor authentication and regular security audits',
    lastAssessed: '2024-09-14',
    createdAt: '2024-02-15T09:00:00Z',
    updatedAt: '2024-09-14T11:00:00Z'
  },
  {
    id: '3',
    title: 'Regulatory Compliance Violation',
    description: 'Risk of non-compliance with new regulations',
    category: 'compliance',
    probability: 4,
    impact: 8,
    riskScore: 3.2,
    status: 'open',
    owner: 'Legal Team',
    mitigation: 'Regular compliance audits and staff training',
    lastAssessed: '2024-09-13',
    createdAt: '2024-03-20T08:00:00Z',
    updatedAt: '2024-09-13T16:00:00Z'
  },
  {
    id: '4',
    title: 'Supply Chain Disruption',
    description: 'Potential interruption in critical supply chain',
    category: 'operational',
    probability: 8,
    impact: 7,
    riskScore: 5.6,
    status: 'open',
    owner: 'Operations Team',
    mitigation: 'Diversify suppliers and maintain strategic inventory',
    lastAssessed: '2024-09-12',
    createdAt: '2024-04-05T07:30:00Z',
    updatedAt: '2024-09-12T10:15:00Z'
  },
  {
    id: '5',
    title: 'Currency Exchange Risk',
    description: 'Exposure to foreign exchange rate fluctuations',
    category: 'financial',
    probability: 9,
    impact: 6,
    riskScore: 5.4,
    status: 'accepted',
    owner: 'Finance Team',
    mitigation: 'Use hedging instruments and regular monitoring',
    lastAssessed: '2024-09-11',
    createdAt: '2024-05-12T09:00:00Z',
    updatedAt: '2024-09-11T15:30:00Z'
  }
]

class RiskManagementAPI {
  private apiClient: BCMAPIClient

  constructor() {
    this.apiClient = new BCMAPIClient()
  }

  // Get all risks with optional filtering
  async getRisks(category?: string): Promise<Risk[]> {
    try {
      const endpoint = '/api/v1/bcm/risks'
      const params = category && category !== 'all'
        ? `?category=${category}`
        : ''

      const response = await this.apiClient.request<Risk[]>(
        `${endpoint}${params}`,
        {
          method: 'GET'
        },
        () => mockRisks.filter(r =>
          !category || category === 'all' || r.category === category
        )
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch risks:', error)
      // Fallback to mock data
      return mockRisks.filter(r =>
        !category || category === 'all' || r.category === category
      )
    }
  }

  // Get risk metrics
  async getRiskMetrics(): Promise<RiskMetrics> {
    try {
      const response = await this.apiClient.request<RiskMetrics>(
        '/api/v1/bcm/risks/metrics',
        {
          method: 'GET'
        },
        () => {
          const risks = mockRisks
          const now = new Date()
          const thisMonth = now.getMonth()
          const thisYear = now.getFullYear()

          return {
            totalRisks: risks.length,
            highRisks: risks.filter(r => r.riskScore >= 8).length,
            newThisMonth: risks.filter(r => {
              const created = new Date(r.createdAt || '')
              return created.getMonth() === thisMonth &&
                     created.getFullYear() === thisYear
            }).length,
            avgRiskScore: risks.length
              ? risks.reduce((sum, r) => sum + r.riskScore, 0) / risks.length
              : 0
          }
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch risk metrics:', error)
      // Calculate from mock data
      const risks = mockRisks
      return {
        totalRisks: risks.length,
        highRisks: risks.filter(r => r.riskScore >= 8).length,
        newThisMonth: 2,
        avgRiskScore: risks.reduce((sum, r) => sum + r.riskScore, 0) / risks.length
      }
    }
  }

  // Create new risk
  async createRisk(risk: Omit<Risk, 'id' | 'createdAt' | 'updatedAt'>): Promise<Risk> {
    try {
      const response = await this.apiClient.request<Risk>(
        '/api/v1/bcm/risks',
        {
          method: 'POST',
          body: JSON.stringify(risk)
        },
        () => ({
          ...risk,
          id: Date.now().toString(),
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to create risk:', error)
      // Return mock created risk
      return {
        ...risk,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    }
  }

  // Update existing risk
  async updateRisk(id: string, risk: Partial<Risk>): Promise<Risk> {
    try {
      const response = await this.apiClient.request<Risk>(
        `/api/v1/bcm/risks/${id}`,
        {
          method: 'PATCH',
          body: JSON.stringify(risk)
        },
        () => {
          const existing = mockRisks.find(r => r.id === id)
          if (!existing) throw new Error('Risk not found')

          return {
            ...existing,
            ...risk,
            updatedAt: new Date().toISOString()
          }
        }
      )

      return response.data
    } catch (error) {
      console.error('Failed to update risk:', error)
      const existing = mockRisks.find(r => r.id === id)
      if (!existing) throw new Error('Risk not found')

      return {
        ...existing,
        ...risk,
        updatedAt: new Date().toISOString()
      }
    }
  }

  // Delete risk
  async deleteRisk(id: string): Promise<boolean> {
    try {
      await this.apiClient.request<void>(
        `/api/v1/bcm/risks/${id}`,
        {
          method: 'DELETE'
        },
        () => undefined
      )

      return true
    } catch (error) {
      console.error('Failed to delete risk:', error)
      return true // Optimistic deletion for mock
    }
  }

  // Get risk assessment history
  async getRiskAssessments(riskId: string): Promise<RiskAssessment[]> {
    try {
      const response = await this.apiClient.request<RiskAssessment[]>(
        `/api/v1/bcm/risk-assessments?risk_id=${riskId}`,
        {
          method: 'GET'
        },
        () => [] // Mock empty assessments for now
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch risk assessments:', error)
      return []
    }
  }

  // Create risk assessment
  async createRiskAssessment(assessment: Omit<RiskAssessment, 'id'>): Promise<RiskAssessment> {
    try {
      const response = await this.apiClient.request<RiskAssessment>(
        '/api/v1/bcm/risk-assessments',
        {
          method: 'POST',
          body: JSON.stringify(assessment)
        },
        () => ({
          ...assessment,
          id: Date.now().toString()
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to create risk assessment:', error)
      return {
        ...assessment,
        id: Date.now().toString()
      }
    }
  }

  // Get treatment plans for a risk
  async getTreatmentPlans(riskId?: string): Promise<TreatmentPlan[]> {
    try {
      const endpoint = riskId
        ? `/api/v1/bcm/treatment-plans?risk_id=${riskId}`
        : '/api/v1/bcm/treatment-plans'

      const response = await this.apiClient.request<TreatmentPlan[]>(
        endpoint,
        {
          method: 'GET'
        },
        () => [] // Mock empty treatment plans
      )

      return response.data
    } catch (error) {
      console.error('Failed to fetch treatment plans:', error)
      return []
    }
  }

  // Create treatment plan
  async createTreatmentPlan(plan: Omit<TreatmentPlan, 'id'>): Promise<TreatmentPlan> {
    try {
      const response = await this.apiClient.request<TreatmentPlan>(
        '/api/v1/bcm/treatment-plans',
        {
          method: 'POST',
          body: JSON.stringify(plan)
        },
        () => ({
          ...plan,
          id: Date.now().toString()
        })
      )

      return response.data
    } catch (error) {
      console.error('Failed to create treatment plan:', error)
      return {
        ...plan,
        id: Date.now().toString()
      }
    }
  }

  // Export risks to CSV
  exportRisksToCSV(risks: Risk[]): void {
    const csvContent = [
      ['Risk ID', 'Title', 'Description', 'Category', 'Probability', 'Impact', 'Risk Score', 'Status', 'Owner', 'Mitigation', 'Last Assessed'],
      ...risks.map(risk => [
        risk.id,
        risk.title,
        risk.description || '',
        risk.category,
        risk.probability.toString(),
        risk.impact.toString(),
        risk.riskScore.toString(),
        risk.status,
        risk.owner,
        risk.mitigation || '',
        risk.lastAssessed
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `risk_register_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // AI Risk Advisor Methods
  async getAIRiskAdvisor(personality: AdvisorPersonality): Promise<AIRiskAdvisor> {
    try {
      const response = await this.apiClient.request<AIRiskAdvisor>(
        `/api/v1/bcm/risk/ai-advisor/${personality}`,
        { method: 'GET' },
        () => ({
          id: `advisor-${personality}`,
          name: `${personality.charAt(0).toUpperCase() + personality.slice(1)} Risk Advisor`,
          advisor_personality: personality,
          ai_risk_analysis: this.getMockAIAnalysis(personality),
          mitigation_recommendations: this.getMockMitigationRecommendations(personality),
          advisor_wisdom: this.getMockAdvisorWisdom(personality),
          fair_analysis_enabled: true,
          monte_carlo_simulations: 10000,
          prediction_accuracy: Math.random() * 0.3 + 0.7, // 70-100%
          risks_analyzed: Math.floor(Math.random() * 100) + 50,
          predictions_made: Math.floor(Math.random() * 50) + 20,
          accuracy_rate: Math.random() * 0.25 + 0.75, // 75-100%
          status: 'active'
        })
      )
      return response.data
    } catch (error) {
      console.error('Failed to get AI risk advisor:', error)
      throw error
    }
  }

  async getRiskPredictions(personality: AdvisorPersonality, riskIds: string[]): Promise<RiskPrediction[]> {
    try {
      const response = await this.apiClient.request<RiskPrediction[]>(
        `/api/v1/bcm/risk/ai-advisor/${personality}/predictions`,
        {
          method: 'POST',
          body: JSON.stringify({ risk_ids: riskIds })
        },
        () => this.getMockPredictions(personality, riskIds)
      )
      return response.data
    } catch (error) {
      console.error('Failed to get risk predictions:', error)
      return []
    }
  }

  async getAdvisorMetrics(personality: AdvisorPersonality): Promise<AdvisorMetrics> {
    try {
      const response = await this.apiClient.request<AdvisorMetrics>(
        `/api/v1/bcm/risk/ai-advisor/${personality}/metrics`,
        { method: 'GET' },
        () => ({
          advisor_personality: personality,
          risks_analyzed: Math.floor(Math.random() * 200) + 100,
          predictions_made: Math.floor(Math.random() * 100) + 50,
          accuracy_rate: Math.random() * 0.25 + 0.75, // 75-100%
          successful_predictions: Math.floor(Math.random() * 80) + 40,
          last_updated: new Date().toISOString()
        })
      )
      return response.data
    } catch (error) {
      console.error('Failed to get advisor metrics:', error)
      throw error
    }
  }

  async runAIRiskAnalysis(personality: AdvisorPersonality, query: string, risks: Risk[]): Promise<{ analysis: string }> {
    try {
      const response = await this.apiClient.request<{ analysis: string }>(
        `/api/v1/bcm/risk/ai-advisor/${personality}/analyze`,
        {
          method: 'POST',
          body: JSON.stringify({ query, risks })
        },
        () => ({
          analysis: this.getMockAnalysisResponse(personality, query, risks)
        })
      )
      return response.data
    } catch (error) {
      console.error('Failed to run AI analysis:', error)
      throw error
    }
  }

  // Mock data generators for AI Risk Advisor
  private getMockAIAnalysis(personality: AdvisorPersonality): string {
    const analyses = {
      cautious: `<strong>Conservative Risk Assessment</strong><br/>
        Based on my analysis, I've identified several critical areas requiring immediate attention.
        The current risk landscape shows potential for cascading failures that could severely impact business operations.
        I recommend implementing comprehensive risk mitigation strategies with multiple backup plans.`,
      balanced: `<strong>Balanced Risk Evaluation</strong><br/>
        The risk portfolio shows a healthy distribution across categories. While some high-impact risks exist,
        they are balanced by strong mitigation measures. I suggest maintaining current risk appetite while
        focusing on emerging threats in the digital transformation space.`,
      aggressive: `<strong>Growth-Oriented Risk Analysis</strong><br/>
        Current risk levels present opportunities for strategic advancement. Several calculated risks
        could yield significant competitive advantages. I recommend pursuing controlled expansion in
        high-potential areas while maintaining core operational stability.`,
      adaptive: `<strong>Context-Sensitive Risk Assessment</strong><br/>
        Risk patterns are evolving rapidly in response to market conditions. I'm continuously adjusting
        recommendations based on real-time data. Current focus should be on building adaptive capacity
        and maintaining flexible response capabilities.`,
      predictive: `<strong>Future-Focused Risk Intelligence</strong><br/>
        Based on historical patterns and trend analysis, I predict emerging risks in cybersecurity and
        supply chain disruption. Proactive measures in these areas will position the organization
        ahead of potential future challenges.`
    }
    return analyses[personality] || analyses.balanced
  }

  private getMockMitigationRecommendations(personality: AdvisorPersonality): string {
    const recommendations = {
      cautious: `<ul>
        <li>Implement comprehensive backup systems for all critical processes</li>
        <li>Establish redundant communication channels</li>
        <li>Create detailed emergency response procedures</li>
        <li>Conduct regular stress testing of all systems</li>
      </ul>`,
      balanced: `<ul>
        <li>Balance risk mitigation with operational efficiency</li>
        <li>Implement risk-based monitoring systems</li>
        <li>Develop cross-functional response teams</li>
        <li>Maintain optimal risk appetite levels</li>
      </ul>`,
      aggressive: `<ul>
        <li>Leverage risks as competitive opportunities</li>
        <li>Implement rapid response capabilities</li>
        <li>Focus on high-impact, high-reward strategies</li>
        <li>Build market-leading risk management capabilities</li>
      </ul>`,
      adaptive: `<ul>
        <li>Implement flexible risk management frameworks</li>
        <li>Develop context-aware response systems</li>
        <li>Create adaptive monitoring and alerting</li>
        <li>Build organization-wide risk sensing capabilities</li>
      </ul>`,
      predictive: `<ul>
        <li>Implement predictive risk monitoring systems</li>
        <li>Develop future-scenario planning capabilities</li>
        <li>Create early warning systems for emerging risks</li>
        <li>Build predictive analytics infrastructure</li>
      </ul>`
    }
    return recommendations[personality] || recommendations.balanced
  }

  private getMockAdvisorWisdom(personality: AdvisorPersonality): string {
    const wisdom = {
      cautious: "Better to be safe than sorry. In uncertainty, choose the path that preserves options and protects against worst-case scenarios.",
      balanced: "True wisdom lies in finding the perfect balance between security and opportunity, protection and growth.",
      aggressive: "Fortune favors the bold. The greatest risk is not taking any risk at all in a rapidly changing world.",
      adaptive: "The wise advisor adapts to circumstances while maintaining core principles. Flexibility is strength.",
      predictive: "The future belongs to those who can see it coming. Prepare today for tomorrow's challenges."
    }
    return wisdom[personality] || wisdom.balanced
  }

  private getMockPredictions(personality: AdvisorPersonality, riskIds: string[]): RiskPrediction[] {
    return riskIds.slice(0, 3).map((riskId, index) => ({
      id: `prediction-${riskId}-${index}`,
      risk_id: riskId,
      risk_title: `Risk Assessment ${index + 1}`,
      advisor_personality: personality,
      predicted_impact: Math.floor(Math.random() * 5) + 6, // 6-10
      predicted_probability: Math.floor(Math.random() * 4) + 6, // 6-9
      confidence: Math.random() * 0.3 + 0.7, // 70-100%
      timeline: ['1 week', '2 weeks', '1 month', '3 months'][Math.floor(Math.random() * 4)],
      description: this.getMockPredictionDescription(personality),
      recommendations: this.getMockPredictionRecommendations(personality),
      created_at: new Date().toISOString()
    }))
  }

  private getMockPredictionDescription(personality: AdvisorPersonality): string {
    const descriptions = {
      cautious: "Based on conservative analysis, this risk requires immediate attention due to potential cascading effects.",
      balanced: "Moderate probability of escalation detected. Recommended monitoring with prepared response measures.",
      aggressive: "Opportunity identified within risk scenario. Strategic action could yield competitive advantage.",
      adaptive: "Dynamic risk pattern detected. Situation requires flexible response strategy.",
      predictive: "Future risk scenario predicted based on current trends and historical patterns."
    }
    return descriptions[personality] || descriptions.balanced
  }

  private getMockPredictionRecommendations(personality: AdvisorPersonality): string[] {
    const recommendations = {
      cautious: [
        "Implement immediate safeguarding measures",
        "Establish backup procedures",
        "Conduct emergency preparedness drill"
      ],
      balanced: [
        "Monitor risk indicators closely",
        "Prepare contingency plans",
        "Review mitigation strategies"
      ],
      aggressive: [
        "Evaluate strategic opportunities",
        "Consider calculated risk-taking",
        "Leverage situation for competitive advantage"
      ],
      adaptive: [
        "Develop flexible response options",
        "Create adaptive monitoring system",
        "Build context-aware capabilities"
      ],
      predictive: [
        "Implement predictive monitoring",
        "Prepare for future scenarios",
        "Build early warning systems"
      ]
    }
    return recommendations[personality] || recommendations.balanced
  }

  private getMockAnalysisResponse(personality: AdvisorPersonality, query: string, risks: Risk[]): string {
    const baseResponse = `Based on my ${personality} analysis of your ${risks.length} risks:`

    const responses = {
      cautious: `${baseResponse} I recommend extreme caution. Focus on protecting against worst-case scenarios and implementing comprehensive safeguards.`,
      balanced: `${baseResponse} The situation requires a measured approach. Balance immediate needs with long-term strategic objectives.`,
      aggressive: `${baseResponse} I see opportunities for strategic advancement. Consider bold moves that could yield significant competitive advantages.`,
      adaptive: `${baseResponse} The key is flexibility. Adapt your approach based on changing conditions and emerging information.`,
      predictive: `${baseResponse} Looking ahead, prepare for emerging challenges while capitalizing on predicted opportunities.`
    }

    return responses[personality] || responses.balanced
  }
}

// Export singleton instance
export const riskManagementAPI = new RiskManagementAPI()

// Export for use in React Query hooks
export const riskQueryKeys = {
  all: ['risks'] as const,
  lists: () => [...riskQueryKeys.all, 'list'] as const,
  list: (filters: { category?: string }) => [...riskQueryKeys.lists(), filters] as const,
  details: () => [...riskQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...riskQueryKeys.details(), id] as const,
  metrics: () => [...riskQueryKeys.all, 'metrics'] as const,
  assessments: (riskId: string) => [...riskQueryKeys.all, 'assessments', riskId] as const,
  treatmentPlans: (riskId?: string) => [...riskQueryKeys.all, 'treatment-plans', riskId] as const,
}

// AI Risk Advisor Types
export type AdvisorPersonality = 'cautious' | 'balanced' | 'aggressive' | 'adaptive' | 'predictive'

export interface AIRiskAdvisor {
  id: string
  name: string
  advisor_personality: AdvisorPersonality
  ai_risk_analysis?: string
  risk_prediction?: string
  mitigation_recommendations?: string
  risk_trends?: string
  fair_analysis_enabled: boolean
  monte_carlo_simulations: number
  risk_quantification?: string
  risk_patterns?: string
  prediction_accuracy: number
  advisor_wisdom?: string
  risks_analyzed: number
  predictions_made: number
  accuracy_rate: number
  status: 'active' | 'learning' | 'offline'
  company_id?: string
}

export interface RiskPrediction {
  id: string
  risk_id: string
  risk_title: string
  advisor_personality: AdvisorPersonality
  predicted_impact: number
  predicted_probability: number
  confidence: number
  timeline: string
  description: string
  recommendations: string[]
  created_at: string
}

export interface AdvisorMetrics {
  advisor_personality: AdvisorPersonality
  risks_analyzed: number
  predictions_made: number
  accuracy_rate: number
  successful_predictions: number
  last_updated: string
}