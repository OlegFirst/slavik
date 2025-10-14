/**
 * BCM Exercise Service - Comprehensive Business Continuity Management Exercise Module
 * Handles exercise planning, execution, monitoring, and analysis
 */

import api from './api'
import eventBus from './eventbus'

class BCMExerciseService {
  constructor() {
    this.baseURL = '/api/v1/bcm/exercises'
    this.simulationAdapterURL = '/api/adapters/simulation'
    this.aiOrchestratorURL = '/api/ai/orchestrator'
  }

  // ==========================
  // Exercise Planning & Scheduling
  // ==========================

  /**
   * Get all exercises with optional filters
   */
  async getExercises(filters = {}) {
    try {
      const domain = []
      if (filters.company_id) domain.push(['company_id', '=', filters.company_id])
      if (filters.status) domain.push(['status', '=', filters.status])
      if (filters.exercise_type) domain.push(['exercise_type', '=', filters.exercise_type])
      if (filters.date_range) {
        domain.push(['scheduled_date', '>=', filters.date_range.start])
        domain.push(['scheduled_date', '<=', filters.date_range.end])
      }

      const exercises = await api.searchRead(
        'bcm.exercise',
        domain,
        [
          'name', 'description', 'exercise_type', 'status', 'scheduled_date', 'duration',
          'participants', 'scenario_id', 'objectives', 'success_criteria', 'created_date',
          'last_modified', 'facilitator_id', 'observers', 'exercise_scope', 'rto_target',
          'rpo_target', 'complexity_level', 'budget_allocated', 'location', 'resources_required'
        ]
      )

      return exercises.map(exercise => ({
        ...exercise,
        participants: exercise.participants ? JSON.parse(exercise.participants) : [],
        objectives: exercise.objectives ? JSON.parse(exercise.objectives) : [],
        success_criteria: exercise.success_criteria ? JSON.parse(exercise.success_criteria) : [],
        observers: exercise.observers ? JSON.parse(exercise.observers) : [],
        resources_required: exercise.resources_required ? JSON.parse(exercise.resources_required) : []
      }))
    } catch (error) {
      console.error('Failed to fetch exercises:', error)
      throw error
    }
  }

  /**
   * Create new exercise
   */
  async createExercise(exerciseData) {
    try {
      const payload = {
        ...exerciseData,
        participants: JSON.stringify(exerciseData.participants || []),
        objectives: JSON.stringify(exerciseData.objectives || []),
        success_criteria: JSON.stringify(exerciseData.success_criteria || []),
        observers: JSON.stringify(exerciseData.observers || []),
        resources_required: JSON.stringify(exerciseData.resources_required || []),
        status: 'planned',
        created_date: new Date().toISOString()
      }

      const exercise = await api.create('bcm.exercise', payload)

      // Publish event
      await eventBus.publish('bcm.exercise.created', {
        exercise_id: exercise.id,
        exercise_name: exercise.name,
        exercise_type: exercise.exercise_type,
        scheduled_date: exercise.scheduled_date
      })

      return exercise
    } catch (error) {
      console.error('Failed to create exercise:', error)
      throw error
    }
  }

  /**
   * Update exercise
   */
  async updateExercise(exerciseId, updateData) {
    try {
      const payload = { ...updateData }

      // Stringify complex fields if they exist
      if (payload.participants) payload.participants = JSON.stringify(payload.participants)
      if (payload.objectives) payload.objectives = JSON.stringify(payload.objectives)
      if (payload.success_criteria) payload.success_criteria = JSON.stringify(payload.success_criteria)
      if (payload.observers) payload.observers = JSON.stringify(payload.observers)
      if (payload.resources_required) payload.resources_required = JSON.stringify(payload.resources_required)

      payload.last_modified = new Date().toISOString()

      await api.write('bcm.exercise', [exerciseId], payload)

      // Publish event
      await eventBus.publish('bcm.exercise.updated', {
        exercise_id: exerciseId,
        changes: Object.keys(updateData)
      })

      return { success: true }
    } catch (error) {
      console.error('Failed to update exercise:', error)
      throw error
    }
  }

  // ==========================
  // Exercise Type Management
  // ==========================

  /**
   * Get available exercise types with configurations
   */
  getExerciseTypes() {
    return [
      {
        id: 'tabletop',
        name: 'Tabletop Exercise',
        description: 'Discussion-based session where team members meet in an informal setting to discuss their roles during an emergency and their responses to a particular emergency situation',
        duration_range: { min: 60, max: 240 }, // minutes
        complexity: 'low',
        participants_range: { min: 4, max: 15 },
        requirements: ['Meeting room', 'Scenario documentation', 'Facilitator'],
        objectives: [
          'Test decision-making processes',
          'Evaluate communication procedures',
          'Identify gaps in plans',
          'Build team familiarity with procedures'
        ]
      },
      {
        id: 'walkthrough',
        name: 'Walkthrough Exercise',
        description: 'Step-by-step review of emergency response procedures where participants walk through their roles and responsibilities',
        duration_range: { min: 120, max: 480 },
        complexity: 'medium',
        participants_range: { min: 6, max: 25 },
        requirements: ['Facilities access', 'Equipment checklist', 'Process documentation'],
        objectives: [
          'Validate operational procedures',
          'Test resource accessibility',
          'Practice coordination between teams',
          'Identify process bottlenecks'
        ]
      },
      {
        id: 'functional',
        name: 'Functional Exercise',
        description: 'Realistic simulation that tests specific functions in a coordinated response during a simulated emergency',
        duration_range: { min: 240, max: 720 },
        complexity: 'high',
        participants_range: { min: 10, max: 50 },
        requirements: ['Command center', 'Communication systems', 'Real-time monitoring'],
        objectives: [
          'Test full operational capability',
          'Evaluate multi-team coordination',
          'Assess decision-making under pressure',
          'Validate recovery time objectives'
        ]
      },
      {
        id: 'full_scale',
        name: 'Full-Scale Exercise',
        description: 'Comprehensive exercise involving all stakeholders, realistic scenario conditions, and actual resource deployment',
        duration_range: { min: 480, max: 1440 },
        complexity: 'maximum',
        participants_range: { min: 25, max: 200 },
        requirements: ['Multiple locations', 'External stakeholders', 'Real resource deployment', 'Safety personnel'],
        objectives: [
          'Test complete response capability',
          'Validate external coordination',
          'Assess resource deployment',
          'Evaluate public communication'
        ]
      }
    ]
  }

  // ==========================
  // Participant Management
  // ==========================

  /**
   * Get available participants from organization
   */
  async getAvailableParticipants(companyId) {
    try {
      const users = await api.searchRead(
        'res.users',
        [['company_id', '=', companyId], ['active', '=', true]],
        ['name', 'email', 'phone', 'job_title', 'department_id', 'manager_id']
      )

      return users.map(user => ({
        id: user.id,
        name: user.name,
        email: user.email,
        phone: user.phone,
        job_title: user.job_title,
        department: user.department_id ? user.department_id[1] : null,
        manager: user.manager_id ? user.manager_id[1] : null,
        available: true // This would be determined by calendar integration
      }))
    } catch (error) {
      console.error('Failed to fetch participants:', error)
      return []
    }
  }

  /**
   * Assign participants to exercise
   */
  async assignParticipants(exerciseId, participantAssignments) {
    try {
      const assignments = participantAssignments.map(assignment => ({
        exercise_id: exerciseId,
        user_id: assignment.user_id,
        role: assignment.role, // 'participant', 'observer', 'facilitator', 'evaluator'
        team: assignment.team,
        responsibilities: assignment.responsibilities,
        required_skills: assignment.required_skills,
        notification_preferences: assignment.notification_preferences
      }))

      // Create participant assignments
      for (const assignment of assignments) {
        await api.create('bcm.exercise.participant', assignment)
      }

      // Send notifications
      await this.sendParticipantNotifications(exerciseId, assignments)

      // Publish event
      await eventBus.publish('bcm.exercise.participants_assigned', {
        exercise_id: exerciseId,
        participants_count: assignments.length
      })

      return { success: true, assignments_created: assignments.length }
    } catch (error) {
      console.error('Failed to assign participants:', error)
      throw error
    }
  }

  /**
   * Send notifications to participants
   */
  async sendParticipantNotifications(exerciseId, assignments) {
    try {
      const exercise = await api.read('bcm.exercise', [exerciseId], ['name', 'scheduled_date', 'description'])[0]

      for (const assignment of assignments) {
        const user = await api.read('res.users', [assignment.user_id], ['name', 'email'])[0]

        // This would integrate with email/notification service
        await eventBus.publish('notification.send', {
          recipient: user.email,
          type: 'exercise_assignment',
          subject: `BCM Exercise Assignment: ${exercise.name}`,
          data: {
            user_name: user.name,
            exercise_name: exercise.name,
            exercise_date: exercise.scheduled_date,
            role: assignment.role,
            responsibilities: assignment.responsibilities
          }
        })
      }
    } catch (error) {
      console.error('Failed to send participant notifications:', error)
    }
  }

  // ==========================
  // Scenario Management
  // ==========================

  /**
   * Get available scenarios
   */
  async getScenarios(filters = {}) {
    try {
      const domain = []
      if (filters.scenario_type) domain.push(['scenario_type', '=', filters.scenario_type])
      if (filters.complexity) domain.push(['complexity_level', '=', filters.complexity])

      const scenarios = await api.searchRead(
        'bcm.scenario',
        domain,
        [
          'name', 'description', 'scenario_type', 'complexity_level', 'estimated_duration',
          'target_audience', 'learning_objectives', 'injects', 'success_criteria',
          'required_resources', 'simulation_parameters'
        ]
      )

      return scenarios.map(scenario => ({
        ...scenario,
        injects: scenario.injects ? JSON.parse(scenario.injects) : [],
        learning_objectives: scenario.learning_objectives ? JSON.parse(scenario.learning_objectives) : [],
        success_criteria: scenario.success_criteria ? JSON.parse(scenario.success_criteria) : [],
        required_resources: scenario.required_resources ? JSON.parse(scenario.required_resources) : [],
        simulation_parameters: scenario.simulation_parameters ? JSON.parse(scenario.simulation_parameters) : {}
      }))
    } catch (error) {
      console.error('Failed to fetch scenarios:', error)
      throw error
    }
  }

  /**
   * Customize scenario for specific exercise
   */
  async customizeScenario(scenarioId, customizations) {
    try {
      const baseScenario = await api.read('bcm.scenario', [scenarioId])[0]

      const customizedScenario = {
        ...baseScenario,
        name: `${baseScenario.name} - Customized`,
        description: customizations.description || baseScenario.description,
        injects: JSON.stringify(customizations.injects || JSON.parse(baseScenario.injects || '[]')),
        simulation_parameters: JSON.stringify({
          ...JSON.parse(baseScenario.simulation_parameters || '{}'),
          ...customizations.simulation_parameters
        }),
        customization_notes: customizations.notes,
        parent_scenario_id: scenarioId
      }

      const newScenario = await api.create('bcm.scenario', customizedScenario)
      return newScenario
    } catch (error) {
      console.error('Failed to customize scenario:', error)
      throw error
    }
  }

  // ==========================
  // Real-time Exercise Execution
  // ==========================

  /**
   * Start exercise execution
   */
  async startExercise(exerciseId) {
    try {
      // Update exercise status
      await api.write('bcm.exercise', [exerciseId], {
        status: 'in_progress',
        actual_start_time: new Date().toISOString()
      })

      // Initialize exercise session
      const session = await api.create('bcm.exercise.session', {
        exercise_id: exerciseId,
        started_at: new Date().toISOString(),
        status: 'active',
        real_time_data: JSON.stringify({
          phase: 'initialization',
          current_inject: null,
          participants_status: {},
          metrics: {
            response_times: [],
            decision_points: [],
            communication_logs: []
          }
        })
      })

      // Start simulation if configured
      const exercise = await api.read('bcm.exercise', [exerciseId])[0]
      if (exercise.scenario_id) {
        await this.initializeSimulation(exerciseId, exercise.scenario_id)
      }

      // Publish event
      await eventBus.publish('bcm.exercise.started', {
        exercise_id: exerciseId,
        session_id: session.id,
        started_at: new Date().toISOString()
      })

      return { success: true, session_id: session.id }
    } catch (error) {
      console.error('Failed to start exercise:', error)
      throw error
    }
  }

  /**
   * Initialize simulation integration
   */
  async initializeSimulation(exerciseId, scenarioId) {
    try {
      const scenario = await api.read('bcm.scenario', [scenarioId])[0]
      const simulationParams = JSON.parse(scenario.simulation_parameters || '{}')

      if (simulationParams.use_jaamsim) {
        // Initialize JaamSim integration
        const simResponse = await fetch(`${this.simulationAdapterURL}/jaamsim/initialize`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            exercise_id: exerciseId,
            scenario_id: scenarioId,
            parameters: simulationParams
          })
        })

        if (simResponse.ok) {
          const simData = await simResponse.json()
          await eventBus.publish('bcm.simulation.initialized', {
            exercise_id: exerciseId,
            simulation_id: simData.simulation_id
          })
        }
      }
    } catch (error) {
      console.error('Failed to initialize simulation:', error)
    }
  }

  /**
   * Get real-time exercise status
   */
  async getExerciseStatus(exerciseId) {
    try {
      const session = await api.searchRead(
        'bcm.exercise.session',
        [['exercise_id', '=', exerciseId], ['status', '=', 'active']],
        ['started_at', 'real_time_data', 'current_phase', 'progress_percentage']
      )[0]

      if (!session) {
        return { status: 'not_started' }
      }

      const realTimeData = JSON.parse(session.real_time_data || '{}')

      return {
        status: 'in_progress',
        session_id: session.id,
        started_at: session.started_at,
        current_phase: session.current_phase || 'initialization',
        progress_percentage: session.progress_percentage || 0,
        participants_status: realTimeData.participants_status || {},
        metrics: realTimeData.metrics || {},
        current_inject: realTimeData.current_inject
      }
    } catch (error) {
      console.error('Failed to get exercise status:', error)
      return { status: 'error' }
    }
  }

  /**
   * Execute scenario inject
   */
  async executeInject(exerciseId, injectData) {
    try {
      // Record inject execution
      await api.create('bcm.exercise.inject', {
        exercise_id: exerciseId,
        inject_name: injectData.name,
        inject_type: injectData.type,
        executed_at: new Date().toISOString(),
        content: injectData.content,
        expected_responses: JSON.stringify(injectData.expected_responses || []),
        actual_responses: JSON.stringify([])
      })

      // Update session status
      const session = await api.searchRead(
        'bcm.exercise.session',
        [['exercise_id', '=', exerciseId], ['status', '=', 'active']]
      )[0]

      if (session) {
        const realTimeData = JSON.parse(session.real_time_data || '{}')
        realTimeData.current_inject = injectData
        realTimeData.phase = 'inject_execution'

        await api.write('bcm.exercise.session', [session.id], {
          real_time_data: JSON.stringify(realTimeData)
        })
      }

      // Publish event for real-time updates
      await eventBus.publish('bcm.exercise.inject_executed', {
        exercise_id: exerciseId,
        inject: injectData,
        timestamp: new Date().toISOString()
      })

      return { success: true }
    } catch (error) {
      console.error('Failed to execute inject:', error)
      throw error
    }
  }

  // ==========================
  // Results Collection & Analysis
  // ==========================

  /**
   * Collect exercise results
   */
  async collectResults(exerciseId, resultsData) {
    try {
      const result = await api.create('bcm.exercise.result', {
        exercise_id: exerciseId,
        collected_at: new Date().toISOString(),
        objective_scores: JSON.stringify(resultsData.objective_scores || {}),
        timeline_events: JSON.stringify(resultsData.timeline_events || []),
        participant_feedback: JSON.stringify(resultsData.participant_feedback || []),
        observer_notes: JSON.stringify(resultsData.observer_notes || []),
        metrics_collected: JSON.stringify(resultsData.metrics || {}),
        issues_identified: JSON.stringify(resultsData.issues || []),
        recommendations: JSON.stringify(resultsData.recommendations || [])
      })

      // Calculate overall effectiveness score
      const effectivenessScore = this.calculateEffectivenessScore(resultsData)

      await api.write('bcm.exercise.result', [result.id], {
        effectiveness_score: effectivenessScore
      })

      // Publish event
      await eventBus.publish('bcm.exercise.results_collected', {
        exercise_id: exerciseId,
        result_id: result.id,
        effectiveness_score: effectivenessScore
      })

      return { success: true, result_id: result.id, effectiveness_score: effectivenessScore }
    } catch (error) {
      console.error('Failed to collect results:', error)
      throw error
    }
  }

  /**
   * Calculate exercise effectiveness score
   */
  calculateEffectivenessScore(resultsData) {
    const objectiveScores = resultsData.objective_scores || {}
    const scores = Object.values(objectiveScores)

    if (scores.length === 0) return 0

    const averageScore = scores.reduce((sum, score) => sum + score, 0) / scores.length

    // Apply weighting factors
    const timelinePenalty = (resultsData.timeline_events || [])
      .filter(event => event.type === 'delay' || event.type === 'missed_target')
      .length * 5 // 5% penalty per issue

    const issuesPenalty = (resultsData.issues || []).length * 3 // 3% penalty per issue

    const finalScore = Math.max(0, Math.min(100, averageScore - timelinePenalty - issuesPenalty))

    return Math.round(finalScore)
  }

  /**
   * Generate exercise analysis report
   */
  async generateAnalysisReport(exerciseId) {
    try {
      const exercise = await api.read('bcm.exercise', [exerciseId])[0]
      const results = await api.searchRead(
        'bcm.exercise.result',
        [['exercise_id', '=', exerciseId]],
        ['*']
      )

      if (results.length === 0) {
        throw new Error('No results found for exercise')
      }

      const result = results[0]
      const objectiveScores = JSON.parse(result.objective_scores || '{}')
      const timelineEvents = JSON.parse(result.timeline_events || '[]')
      const participantFeedback = JSON.parse(result.participant_feedback || '[]')
      const issues = JSON.parse(result.issues_identified || '[]')
      const recommendations = JSON.parse(result.recommendations || '[]')

      const analysis = {
        exercise_id: exerciseId,
        exercise_name: exercise.name,
        exercise_type: exercise.exercise_type,
        effectiveness_score: result.effectiveness_score,
        analysis_date: new Date().toISOString(),

        executive_summary: this.generateExecutiveSummary(exercise, result),

        performance_analysis: {
          objectives_met: Object.keys(objectiveScores).filter(key => objectiveScores[key] >= 70).length,
          total_objectives: Object.keys(objectiveScores).length,
          average_score: Object.values(objectiveScores).reduce((sum, score) => sum + score, 0) / Object.keys(objectiveScores).length,
          score_breakdown: objectiveScores
        },

        timeline_analysis: {
          total_events: timelineEvents.length,
          critical_delays: timelineEvents.filter(e => e.type === 'delay' && e.impact === 'critical').length,
          milestone_achievement: this.analyzeTimelinePerformance(timelineEvents)
        },

        participant_analysis: {
          response_rate: participantFeedback.length,
          satisfaction_score: participantFeedback.reduce((sum, fb) => sum + (fb.satisfaction || 0), 0) / participantFeedback.length,
          engagement_level: participantFeedback.reduce((sum, fb) => sum + (fb.engagement || 0), 0) / participantFeedback.length
        },

        issues_and_gaps: {
          total_issues: issues.length,
          critical_issues: issues.filter(i => i.severity === 'critical').length,
          categorized_issues: this.categorizeIssues(issues)
        },

        recommendations: {
          immediate_actions: recommendations.filter(r => r.priority === 'immediate'),
          short_term_actions: recommendations.filter(r => r.priority === 'short_term'),
          long_term_actions: recommendations.filter(r => r.priority === 'long_term')
        },

        next_steps: this.generateNextSteps(exercise, result, issues, recommendations)
      }

      // Store analysis report
      const reportRecord = await api.create('bcm.exercise.analysis', {
        exercise_id: exerciseId,
        analysis_data: JSON.stringify(analysis),
        generated_at: new Date().toISOString()
      })

      return { success: true, analysis: analysis, report_id: reportRecord.id }
    } catch (error) {
      console.error('Failed to generate analysis report:', error)
      throw error
    }
  }

  // ==========================
  // AI-Powered Recommendations
  // ==========================

  /**
   * Get AI-powered exercise recommendations
   */
  async getAIRecommendations(companyId, context = {}) {
    try {
      const response = await fetch(`${this.aiOrchestratorURL}/bcm/exercise-recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: companyId,
          context: context,
          request_type: 'exercise_planning'
        })
      })

      if (response.ok) {
        const data = await response.json()
        return {
          scenario_recommendations: data.recommended_scenarios || [],
          exercise_types: data.recommended_types || [],
          timing_suggestions: data.timing_recommendations || [],
          participant_suggestions: data.participant_recommendations || [],
          success_predictions: data.success_predictions || {},
          customization_suggestions: data.customization_ideas || []
        }
      } else {
        // Fallback to rule-based recommendations
        return this.getRuleBasedRecommendations(companyId, context)
      }
    } catch (error) {
      console.error('AI recommendations failed, using fallback:', error)
      return this.getRuleBasedRecommendations(companyId, context)
    }
  }

  /**
   * Rule-based recommendations fallback
   */
  async getRuleBasedRecommendations(companyId, context) {
    try {
      // Get company's previous exercises
      const previousExercises = await this.getExercises({ company_id: companyId })

      // Get company's risk profile
      const risks = await api.searchRead('bcm.risk', [['company_id', '=', companyId]], ['risk_type', 'severity'])

      const recommendations = {
        scenario_recommendations: this.recommendScenariosBasedOnRisk(risks),
        exercise_types: this.recommendExerciseTypes(previousExercises),
        timing_suggestions: this.recommendTiming(previousExercises),
        participant_suggestions: this.recommendParticipants(companyId, context),
        success_predictions: { confidence: 75, factors: ['Previous exercise performance', 'Team experience'] },
        customization_suggestions: ['Focus on communication protocols', 'Include external stakeholders']
      }

      return recommendations
    } catch (error) {
      console.error('Failed to generate rule-based recommendations:', error)
      return {
        scenario_recommendations: [],
        exercise_types: ['tabletop'],
        timing_suggestions: { recommended_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() },
        participant_suggestions: [],
        success_predictions: { confidence: 50 },
        customization_suggestions: []
      }
    }
  }

  // ==========================
  // Integration Methods
  // ==========================

  /**
   * Integrate with JaamSim simulation engine
   */
  async integrateWithJaamSim(exerciseId, simulationConfig) {
    try {
      const response = await fetch(`${this.simulationAdapterURL}/jaamsim/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise_id: exerciseId,
          config: simulationConfig,
          real_time: true
        })
      })

      if (response.ok) {
        const simResult = await response.json()

        // Update exercise with simulation data
        await eventBus.publish('bcm.exercise.simulation_updated', {
          exercise_id: exerciseId,
          simulation_data: simResult
        })

        return simResult
      }
    } catch (error) {
      console.error('JaamSim integration failed:', error)
      throw error
    }
  }

  /**
   * Connect to EventBus for real-time updates
   */
  setupRealTimeUpdates(exerciseId, callback) {
    eventBus.on(`bcm.exercise.${exerciseId}.*`, callback)
    eventBus.on('bcm.simulation.*', callback)
    eventBus.on('bcm.exercise.inject_executed', callback)
    eventBus.on('bcm.exercise.participant_response', callback)
  }

  /**
   * Disconnect real-time updates
   */
  disconnectRealTimeUpdates(exerciseId, callback) {
    eventBus.off(`bcm.exercise.${exerciseId}.*`, callback)
    eventBus.off('bcm.simulation.*', callback)
    eventBus.off('bcm.exercise.inject_executed', callback)
    eventBus.off('bcm.exercise.participant_response', callback)
  }

  // ==========================
  // Utility Methods
  // ==========================

  generateExecutiveSummary(exercise, result) {
    const score = result.effectiveness_score || 0
    let performance = 'Poor'
    if (score >= 90) performance = 'Excellent'
    else if (score >= 80) performance = 'Good'
    else if (score >= 70) performance = 'Satisfactory'
    else if (score >= 60) performance = 'Needs Improvement'

    return `${exercise.name} (${exercise.exercise_type}) achieved ${performance} performance with an effectiveness score of ${score}%. Key areas for improvement have been identified and actionable recommendations provided.`
  }

  analyzeTimelinePerformance(timelineEvents) {
    const milestones = timelineEvents.filter(e => e.type === 'milestone')
    const achieved = milestones.filter(m => m.status === 'achieved').length
    return {
      total_milestones: milestones.length,
      achieved_milestones: achieved,
      achievement_rate: milestones.length > 0 ? (achieved / milestones.length) * 100 : 0
    }
  }

  categorizeIssues(issues) {
    const categories = {}
    issues.forEach(issue => {
      const category = issue.category || 'General'
      if (!categories[category]) categories[category] = []
      categories[category].push(issue)
    })
    return categories
  }

  generateNextSteps(exercise, result, issues, recommendations) {
    const steps = []

    if (result.effectiveness_score < 70) {
      steps.push('Schedule follow-up training sessions for identified gaps')
    }

    if (issues.filter(i => i.severity === 'critical').length > 0) {
      steps.push('Address critical issues within 30 days')
    }

    steps.push('Update BCP based on lessons learned')
    steps.push('Schedule next exercise in 6-12 months')

    return steps
  }

  recommendScenariosBasedOnRisk(risks) {
    const highRisks = risks.filter(r => r.severity === 'high')
    return highRisks.map(risk => ({
      type: risk.risk_type,
      reason: `High severity risk identified: ${risk.risk_type}`
    }))
  }

  recommendExerciseTypes(previousExercises) {
    if (previousExercises.length === 0) return ['tabletop']

    const lastType = previousExercises[0]?.exercise_type
    const typeProgression = {
      'tabletop': 'walkthrough',
      'walkthrough': 'functional',
      'functional': 'full_scale',
      'full_scale': 'tabletop'
    }

    return [typeProgression[lastType] || 'tabletop']
  }

  recommendTiming(previousExercises) {
    const lastExercise = previousExercises[0]
    if (!lastExercise) {
      return { recommended_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() }
    }

    const lastDate = new Date(lastExercise.scheduled_date)
    const recommendedDate = new Date(lastDate.getTime() + 180 * 24 * 60 * 60 * 1000) // 6 months later

    return {
      recommended_date: recommendedDate.toISOString(),
      reason: 'Based on 6-month exercise cycle best practice'
    }
  }

  async recommendParticipants(companyId, context) {
    try {
      const users = await this.getAvailableParticipants(companyId)
      // Basic recommendation logic - include managers and key personnel
      return users
        .filter(user => user.job_title?.toLowerCase().includes('manager') || user.job_title?.toLowerCase().includes('lead'))
        .slice(0, 10)
    } catch (error) {
      console.error('Failed to recommend participants:', error)
      return []
    }
  }
}

export default new BCMExerciseService()