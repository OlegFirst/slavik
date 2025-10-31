import { odooService } from './odoo'
import { assistantService } from './assistant'

class BCMIntelligentBaseService {
  constructor() {
    this.model = 'bcm.intelligent.base'
  }

  // AI Model Management
  async getAiModels() {
    try {
      return await odooService.searchRead('bcm.ai.model', {
        domain: [],
        fields: [
          'id', 'name', 'model_type', 'status', 'version', 'accuracy',
          'training_data_size', 'last_trained', 'deployment_date',
          'inference_count', 'model_size', 'performance_metrics',
          'create_date', 'write_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching AI models:', error)
      throw error
    }
  }

  async deployModel(modelId, deploymentConfig) {
    try {
      return await odooService.callMethod('bcm.ai.model', 'deploy_model', [modelId, deploymentConfig])
    } catch (error) {
      console.error('Error deploying AI model:', error)
      throw error
    }
  }

  async trainModel(modelId, trainingConfig) {
    try {
      return await odooService.callMethod('bcm.ai.model', 'start_training', [modelId, trainingConfig])
    } catch (error) {
      console.error('Error training AI model:', error)
      throw error
    }
  }

  async getModelPerformance(modelId, timeframe = '30d') {
    try {
      return await odooService.callMethod('bcm.ai.model', 'get_performance_metrics', [modelId, timeframe])
    } catch (error) {
      console.error('Error fetching model performance:', error)
      throw error
    }
  }

  // Knowledge Base Management
  async getKnowledgeBase() {
    try {
      return await odooService.searchRead('bcm.knowledge.base', {
        domain: [],
        fields: [
          'id', 'title', 'category', 'content_type', 'status', 'tags',
          'view_count', 'last_updated', 'author_id', 'rating',
          'embedding_status', 'vector_id', 'create_date'
        ]
      })
    } catch (error) {
      console.error('Error fetching knowledge base:', error)
      throw error
    }
  }

  async createKnowledgeArticle(articleData) {
    try {
      const id = await odooService.create('bcm.knowledge.base', articleData)

      // Generate embeddings for semantic search
      await this.generateEmbeddings(id, articleData.content)

      return id
    } catch (error) {
      console.error('Error creating knowledge article:', error)
      throw error
    }
  }

  async generateEmbeddings(articleId, content) {
    try {
      return await assistantService.generateEmbeddings({
        articleId,
        content,
        vectorSpace: 'bcm_knowledge'
      })
    } catch (error) {
      console.error('Error generating embeddings:', error)
      throw error
    }
  }

  async searchKnowledge(query, filters = {}) {
    try {
      return await assistantService.semanticSearch({
        query,
        collection: 'bcm_knowledge',
        filters,
        limit: 10,
        threshold: 0.7
      })
    } catch (error) {
      console.error('Error searching knowledge base:', error)
      throw error
    }
  }

  // Automated Analysis
  async runAutomatedAnalysis(analysisType, parameters = {}) {
    try {
      return await assistantService.runAnalysis({
        type: analysisType,
        parameters,
        module: 'intelligent_base'
      })
    } catch (error) {
      console.error('Error running automated analysis:', error)
      throw error
    }
  }

  async getRiskAnalysis(scope = 'organization') {
    try {
      return await assistantService.analyzeRisks({
        scope,
        includeRecommendations: true,
        analysisDepth: 'comprehensive'
      })
    } catch (error) {
      console.error('Error getting risk analysis:', error)
      throw error
    }
  }

  async getComplianceAnalysis(standard = 'ISO22301') {
    try {
      return await assistantService.analyzeCompliance({
        standard,
        includeGaps: true,
        generateRemediation: true
      })
    } catch (error) {
      console.error('Error getting compliance analysis:', error)
      throw error
    }
  }

  async getTrendAnalysis(dataType, timeframe = '12M') {
    try {
      return await assistantService.analyzeTrends({
        dataType,
        timeframe,
        includeForecasting: true,
        confidence_threshold: 0.8
      })
    } catch (error) {
      console.error('Error getting trend analysis:', error)
      throw error
    }
  }

  // Predictive Analytics
  async getPredictiveInsights(targetMetric, timeHorizon = '6M') {
    try {
      return await assistantService.predictMetric({
        metric: targetMetric,
        horizon: timeHorizon,
        includeConfidenceIntervals: true,
        includeFactors: true
      })
    } catch (error) {
      console.error('Error getting predictive insights:', error)
      throw error
    }
  }

  async getAnomalyDetection(dataSource, sensitivity = 'medium') {
    try {
      return await assistantService.detectAnomalies({
        dataSource,
        sensitivity,
        timeframe: '30d',
        includeContext: true
      })
    } catch (error) {
      console.error('Error detecting anomalies:', error)
      throw error
    }
  }

  async getForecastingModels() {
    try {
      return await odooService.searchRead('bcm.forecasting.model', {
        domain: [['status', '=', 'active']],
        fields: [
          'id', 'name', 'model_type', 'target_metric', 'accuracy',
          'last_prediction', 'prediction_horizon', 'confidence_score'
        ]
      })
    } catch (error) {
      console.error('Error fetching forecasting models:', error)
      throw error
    }
  }

  // Natural Language Processing
  async processDocument(documentData) {
    try {
      return await assistantService.processDocument({
        content: documentData.content,
        documentType: documentData.type,
        extractEntities: true,
        extractSentiment: true,
        generateSummary: true,
        classifyContent: true
      })
    } catch (error) {
      console.error('Error processing document:', error)
      throw error
    }
  }

  async extractEntities(text, entityTypes = []) {
    try {
      return await assistantService.extractEntities({
        text,
        entityTypes,
        includeConfidence: true
      })
    } catch (error) {
      console.error('Error extracting entities:', error)
      throw error
    }
  }

  async analyzeSentiment(text) {
    try {
      return await assistantService.analyzeSentiment({
        text,
        includeEmotions: true,
        granularity: 'sentence'
      })
    } catch (error) {
      console.error('Error analyzing sentiment:', error)
      throw error
    }
  }

  async generateSummary(text, summaryType = 'extractive', length = 'medium') {
    try {
      return await assistantService.generateSummary({
        text,
        type: summaryType,
        length,
        includeKeywords: true
      })
    } catch (error) {
      console.error('Error generating summary:', error)
      throw error
    }
  }

  // Intelligent Recommendations
  async getPersonalizedRecommendations(userId, context = {}) {
    try {
      return await assistantService.getRecommendations({
        userId,
        context,
        module: 'intelligent_base',
        includeExplanations: true,
        maxRecommendations: 10
      })
    } catch (error) {
      console.error('Error getting recommendations:', error)
      throw error
    }
  }

  async getContextualSuggestions(currentContext, userBehavior = {}) {
    try {
      return await assistantService.getContextualSuggestions({
        context: currentContext,
        behavior: userBehavior,
        includeActions: true,
        prioritize: true
      })
    } catch (error) {
      console.error('Error getting contextual suggestions:', error)
      throw error
    }
  }

  async optimizeWorkflow(workflowData) {
    try {
      return await assistantService.optimizeWorkflow({
        workflow: workflowData,
        optimizationGoals: ['efficiency', 'compliance', 'cost'],
        includeAlternatives: true
      })
    } catch (error) {
      console.error('Error optimizing workflow:', error)
      throw error
    }
  }

  // Chatbot & Conversational AI
  async initializeChatbot(config = {}) {
    try {
      return await assistantService.initializeChat({
        context: 'bcm_intelligent_base',
        capabilities: ['knowledge_search', 'analysis', 'recommendations'],
        personalityTone: 'professional',
        ...config
      })
    } catch (error) {
      console.error('Error initializing chatbot:', error)
      throw error
    }
  }

  async sendChatMessage(sessionId, message, context = {}) {
    try {
      return await assistantService.processChat({
        sessionId,
        message,
        context,
        includeActions: true,
        generateFollowups: true
      })
    } catch (error) {
      console.error('Error sending chat message:', error)
      throw error
    }
  }

  async getChatHistory(sessionId, limit = 50) {
    try {
      return await odooService.searchRead('bcm.chat.message', {
        domain: [['session_id', '=', sessionId]],
        fields: ['id', 'message', 'response', 'timestamp', 'user_id'],
        order: 'timestamp desc',
        limit
      })
    } catch (error) {
      console.error('Error fetching chat history:', error)
      throw error
    }
  }

  // Learning & Training System
  async getTrainingModules() {
    try {
      return await odooService.searchRead('bcm.training.module', {
        domain: [['status', '=', 'active']],
        fields: [
          'id', 'title', 'category', 'difficulty', 'duration',
          'completion_rate', 'rating', 'prerequisite_ids',
          'learning_objectives', 'content_type'
        ]
      })
    } catch (error) {
      console.error('Error fetching training modules:', error)
      throw error
    }
  }

  async getUserLearningProgress(userId) {
    try {
      return await odooService.searchRead('bcm.user.progress', {
        domain: [['user_id', '=', userId]],
        fields: [
          'id', 'module_id', 'progress_percentage', 'status',
          'start_date', 'completion_date', 'score', 'attempts'
        ]
      })
    } catch (error) {
      console.error('Error fetching user learning progress:', error)
      throw error
    }
  }

  async generatePersonalizedLearningPath(userId, goals = []) {
    try {
      return await assistantService.generateLearningPath({
        userId,
        goals,
        currentSkills: await this.getUserSkillAssessment(userId),
        includeTimeline: true
      })
    } catch (error) {
      console.error('Error generating learning path:', error)
      throw error
    }
  }

  async getUserSkillAssessment(userId) {
    try {
      return await odooService.callMethod('bcm.user.skills', 'assess_skills', [userId])
    } catch (error) {
      console.error('Error getting skill assessment:', error)
      throw error
    }
  }

  // Integration & API Management
  async getIntegrationStatus() {
    try {
      return await odooService.searchRead('bcm.integration', {
        domain: [],
        fields: [
          'id', 'name', 'integration_type', 'status', 'last_sync',
          'sync_frequency', 'data_flow', 'error_count', 'health_score'
        ]
      })
    } catch (error) {
      console.error('Error fetching integration status:', error)
      throw error
    }
  }

  async syncExternalData(integrationId, syncType = 'incremental') {
    try {
      return await odooService.callMethod('bcm.integration', 'sync_data', [integrationId, syncType])
    } catch (error) {
      console.error('Error syncing external data:', error)
      throw error
    }
  }

  async getApiUsageMetrics(timeframe = '7d') {
    try {
      return await odooService.callMethod(this.model, 'get_api_metrics', [timeframe])
    } catch (error) {
      console.error('Error fetching API metrics:', error)
      throw error
    }
  }

  // System Monitoring & Health
  async getSystemHealth() {
    try {
      return await odooService.callMethod(this.model, 'get_system_health', [])
    } catch (error) {
      console.error('Error fetching system health:', error)
      throw error
    }
  }

  async getPerformanceMetrics(component = null) {
    try {
      return await odooService.callMethod(this.model, 'get_performance_metrics', [component])
    } catch (error) {
      console.error('Error fetching performance metrics:', error)
      throw error
    }
  }

  async runSystemDiagnostics() {
    try {
      return await odooService.callMethod(this.model, 'run_diagnostics', [])
    } catch (error) {
      console.error('Error running system diagnostics:', error)
      throw error
    }
  }

  async getResourceUtilization() {
    try {
      return await odooService.callMethod(this.model, 'get_resource_utilization', [])
    } catch (error) {
      console.error('Error fetching resource utilization:', error)
      throw error
    }
  }

  // Advanced Analytics Dashboard
  async getDashboardData(dashboardType = 'executive') {
    try {
      return await odooService.callMethod(this.model, 'get_dashboard_data', [dashboardType])
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      throw error
    }
  }

  async createCustomDashboard(dashboardConfig) {
    try {
      return await odooService.create('bcm.custom.dashboard', dashboardConfig)
    } catch (error) {
      console.error('Error creating custom dashboard:', error)
      throw error
    }
  }

  async getInsightReports() {
    try {
      return await odooService.searchRead('bcm.insight.report', {
        domain: [['status', '=', 'active']],
        fields: [
          'id', 'title', 'category', 'insights', 'recommendations',
          'confidence_score', 'generated_date', 'expires_date'
        ],
        order: 'generated_date desc'
      })
    } catch (error) {
      console.error('Error fetching insight reports:', error)
      throw error
    }
  }

  // Utility Methods
  formatConfidenceScore(score) {
    return `${Math.round(score * 100)}%`
  }

  formatModelAccuracy(accuracy) {
    return `${(accuracy * 100).toFixed(2)}%`
  }

  getModelStatusColor(status) {
    const colors = {
      training: '#ff9800',
      deployed: '#4caf50',
      failed: '#f44336',
      pending: '#2196f3',
      archived: '#666'
    }
    return colors[status] || '#666'
  }

  formatDataSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  getCategoryIcon(category) {
    const icons = {
      'risk': 'icon-risk',
      'compliance': 'icon-compliance',
      'incident': 'icon-incident',
      'business_continuity': 'icon-continuity',
      'training': 'icon-education',
      'general': 'icon-info'
    }
    return icons[category] || 'icon-info'
  }
}

export const bcmIntelligentBaseService = new BCMIntelligentBaseService()