// Supabase Edge Function: Simulate
// Runs simulations for digital twins

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface SimulationRequest {
  twinId: string
  scenario: string
  parameters?: Record<string, any>
  timeHorizon?: number
}

interface SimulationResult {
  simulationId: string
  results: Record<string, any>
  recommendations: any[]
  confidence: number
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const { twinId, scenario, parameters = {}, timeHorizon = 365 } = await req.json() as SimulationRequest

    // Verify twin exists and user has access
    const { data: twin, error: twinError } = await supabaseClient
      .from('digital_twins')
      .select('*')
      .eq('id', twinId)
      .single()

    if (twinError || !twin) {
      throw new Error('Twin not found or access denied')
    }

    // Get scenario configuration
    const { data: scenarioConfig } = await supabaseClient
      .from('scenarios')
      .select('*')
      .eq('scenario_id', scenario)
      .single()

    // Create simulation record
    const simulationId = `sim_${Date.now()}_${Math.random().toString(36).substring(7)}`
    
    const { error: insertError } = await supabaseClient
      .from('simulations')
      .insert({
        simulation_id: simulationId,
        twin_id: twinId,
        scenario: scenario,
        parameters: parameters,
        status: 'running',
        started_at: new Date().toISOString(),
      })

    if (insertError) {
      throw insertError
    }

    // Run simulation logic
    const results = await runSimulation(twin, scenario, parameters, timeHorizon)

    // Update simulation with results
    await supabaseClient
      .from('simulations')
      .update({
        status: 'completed',
        results: results.data,
        recommendations: results.recommendations,
        confidence_score: results.confidence,
        completed_at: new Date().toISOString(),
        duration_ms: Date.now() - new Date().getTime(),
      })
      .eq('simulation_id', simulationId)

    // Store new metrics
    if (results.metrics) {
      const metricsToInsert = results.metrics.map((metric: any) => ({
        twin_id: twinId,
        metric_type: metric.type,
        value: metric.value,
        unit: metric.unit,
        metadata: metric.metadata,
      }))

      await supabaseClient
        .from('metrics')
        .insert(metricsToInsert)
    }

    // Update twin scores
    const healthScore = await calculateHealthScore(supabaseClient, twinId)
    await supabaseClient
      .from('digital_twins')
      .update({
        health_score: healthScore,
        last_simulation_at: new Date().toISOString(),
        total_simulations: twin.total_simulations + 1,
      })
      .eq('id', twinId)

    return new Response(
      JSON.stringify({
        success: true,
        simulationId,
        results: results.data,
        recommendations: results.recommendations,
        confidence: results.confidence,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      }
    )
  }
})

async function runSimulation(
  twin: any,
  scenario: string,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  // Simulation logic based on scenario
  const scenarios: Record<string, Function> = {
    budget_optimization: simulateBudgetOptimization,
    crisis_management: simulateCrisisManagement,
    scaling_analysis: simulateScalingAnalysis,
    efficiency_improvement: simulateEfficiencyImprovement,
    grant_impact: simulateGrantImpact,
    staff_reorganization: simulateStaffReorganization,
  }

  const simulationFn = scenarios[scenario] || simulateGeneric
  return await simulationFn(twin, parameters, timeHorizon)
}

async function simulateBudgetOptimization(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const currentBudget = twin.state?.budget || 1000000
  const targetReduction = parameters.targetReduction || 0.1
  
  // Monte Carlo simulation for budget scenarios
  const scenarios = []
  for (let i = 0; i < 100; i++) {
    const variation = (Math.random() - 0.5) * 0.2
    const optimizedBudget = currentBudget * (1 - targetReduction + variation)
    const impactScore = calculateImpact(optimizedBudget, currentBudget)
    
    scenarios.push({
      budget: optimizedBudget,
      impact: impactScore,
      feasibility: Math.random() * 0.3 + 0.7,
    })
  }

  // Select best scenario
  const bestScenario = scenarios.sort((a, b) => 
    (a.impact * a.feasibility) - (b.impact * b.feasibility)
  )[0]

  return {
    data: {
      currentBudget,
      optimizedBudget: bestScenario.budget,
      savings: currentBudget - bestScenario.budget,
      impactScore: bestScenario.impact,
      scenarios: scenarios.slice(0, 10),
    },
    recommendations: [
      {
        priority: 'high',
        category: 'cost_reduction',
        action: 'Reduce non-essential expenses',
        expectedSavings: currentBudget * 0.05,
        timeframe: '3 months',
      },
      {
        priority: 'medium',
        category: 'efficiency',
        action: 'Automate administrative tasks',
        expectedSavings: currentBudget * 0.03,
        timeframe: '6 months',
      },
      {
        priority: 'low',
        category: 'revenue',
        action: 'Explore new funding sources',
        expectedRevenue: currentBudget * 0.1,
        timeframe: '12 months',
      },
    ],
    metrics: [
      {
        type: 'budget_efficiency',
        value: bestScenario.impact,
        unit: 'score',
        metadata: { scenario: 'budget_optimization' },
      },
      {
        type: 'cost_savings',
        value: currentBudget - bestScenario.budget,
        unit: 'USD',
        metadata: { projected: true },
      },
    ],
    confidence: 0.75 + Math.random() * 0.2,
  }
}

async function simulateCrisisManagement(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const crisisType = parameters.crisisType || 'financial'
  const severity = parameters.severity || 'moderate'
  
  const impactFactors = {
    financial: { budget: -0.3, staff: -0.1, operations: -0.2 },
    operational: { budget: -0.1, staff: -0.2, operations: -0.4 },
    reputational: { budget: -0.2, staff: -0.15, operations: -0.15 },
  }

  const severityMultipliers = {
    mild: 0.5,
    moderate: 1.0,
    severe: 1.5,
  }

  const impacts = impactFactors[crisisType] || impactFactors.financial
  const multiplier = severityMultipliers[severity] || 1.0

  return {
    data: {
      crisisType,
      severity,
      immediateImpact: {
        budget: impacts.budget * multiplier,
        staff: impacts.staff * multiplier,
        operations: impacts.operations * multiplier,
      },
      recoveryTimeline: {
        immediate: '0-30 days',
        shortTerm: '1-3 months',
        mediumTerm: '3-6 months',
        longTerm: '6-12 months',
      },
    },
    recommendations: [
      {
        priority: 'critical',
        phase: 'immediate',
        action: 'Activate crisis response team',
        timeline: '24 hours',
      },
      {
        priority: 'high',
        phase: 'immediate',
        action: 'Secure emergency funding',
        timeline: '1 week',
      },
      {
        priority: 'high',
        phase: 'short-term',
        action: 'Implement cost containment measures',
        timeline: '1 month',
      },
    ],
    metrics: [
      {
        type: 'crisis_impact',
        value: Math.abs(impacts.budget + impacts.staff + impacts.operations) * multiplier,
        unit: 'severity_score',
      },
    ],
    confidence: 0.7 + Math.random() * 0.15,
  }
}

async function simulateScalingAnalysis(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const currentSize = twin.state?.staffCount || 50
  const targetGrowth = parameters.targetGrowth || 1.5
  
  return {
    data: {
      currentSize,
      targetSize: Math.floor(currentSize * targetGrowth),
      requiredBudgetIncrease: currentSize * targetGrowth * 50000,
      scalabilityScore: 0.7 + Math.random() * 0.2,
      bottlenecks: ['funding', 'talent_acquisition', 'infrastructure'],
    },
    recommendations: [
      {
        priority: 'high',
        action: 'Develop phased growth plan',
        timeline: '2 months',
      },
      {
        priority: 'medium',
        action: 'Strengthen infrastructure',
        timeline: '6 months',
      },
    ],
    metrics: [
      {
        type: 'scalability_score',
        value: 0.75,
        unit: 'score',
      },
    ],
    confidence: 0.8,
  }
}

async function simulateEfficiencyImprovement(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const currentEfficiency = twin.efficiency_score || 0.6
  const targetImprovement = parameters.targetImprovement || 0.2
  
  return {
    data: {
      currentEfficiency,
      projectedEfficiency: Math.min(1, currentEfficiency + targetImprovement),
      improvementAreas: [
        { area: 'process_automation', potential: 0.3 },
        { area: 'resource_allocation', potential: 0.25 },
        { area: 'communication', potential: 0.2 },
      ],
    },
    recommendations: [
      {
        priority: 'high',
        action: 'Implement workflow automation',
        expectedImprovement: 0.15,
      },
    ],
    metrics: [
      {
        type: 'efficiency_improvement',
        value: targetImprovement,
        unit: 'percentage',
      },
    ],
    confidence: 0.82,
  }
}

async function simulateGrantImpact(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const grantAmount = parameters.grantAmount || 100000
  const grantPurpose = parameters.purpose || 'general'
  
  return {
    data: {
      grantAmount,
      projectedImpact: {
        beneficiaries: Math.floor(grantAmount / 1000),
        programsExpanded: Math.floor(grantAmount / 25000),
        sustainabilityMonths: Math.floor(grantAmount / 10000),
      },
      roi: 2.5 + Math.random(),
    },
    recommendations: [
      {
        priority: 'high',
        action: 'Allocate funds strategically',
        allocation: {
          programs: 0.6,
          operations: 0.25,
          reserves: 0.15,
        },
      },
    ],
    metrics: [
      {
        type: 'grant_roi',
        value: 2.8,
        unit: 'multiplier',
      },
    ],
    confidence: 0.78,
  }
}

async function simulateStaffReorganization(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  const currentStaff = twin.state?.staffCount || 50
  const reorganizationType = parameters.type || 'optimization'
  
  return {
    data: {
      currentStructure: {
        total: currentStaff,
        departments: 5,
        avgPerDepartment: currentStaff / 5,
      },
      proposedStructure: {
        total: currentStaff,
        departments: 4,
        avgPerDepartment: currentStaff / 4,
      },
      expectedEfficiencyGain: 0.15,
      transitionRisk: 0.3,
    },
    recommendations: [
      {
        priority: 'high',
        action: 'Conduct skills assessment',
        timeline: '1 month',
      },
      {
        priority: 'medium',
        action: 'Implement cross-training program',
        timeline: '3 months',
      },
    ],
    metrics: [
      {
        type: 'reorganization_efficiency',
        value: 0.15,
        unit: 'percentage',
      },
    ],
    confidence: 0.73,
  }
}

async function simulateGeneric(
  twin: any,
  parameters: Record<string, any>,
  timeHorizon: number
): Promise<any> {
  return {
    data: {
      scenario: 'generic',
      parameters,
      timeHorizon,
      baselineMetrics: twin.state,
    },
    recommendations: [
      {
        priority: 'medium',
        action: 'Review and optimize current processes',
      },
    ],
    metrics: [],
    confidence: 0.65,
  }
}

function calculateImpact(optimized: number, current: number): number {
  const ratio = optimized / current
  if (ratio >= 0.9) return 0.95
  if (ratio >= 0.8) return 0.85
  if (ratio >= 0.7) return 0.7
  return 0.5
}

async function calculateHealthScore(client: any, twinId: string): Promise<number> {
  const { data: metrics } = await client
    .from('metrics')
    .select('metric_type, value')
    .eq('twin_id', twinId)
    .gte('timestamp', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString())

  if (!metrics || metrics.length === 0) return 0.5

  const scores = metrics.map((m: any) => {
    switch (m.metric_type) {
      case 'efficiency': return m.value
      case 'financial_health': return m.value / 100
      case 'staff_satisfaction': return m.value / 10
      case 'grant_success_rate': return m.value
      default: return 0.5
    }
  })

  return scores.reduce((a, b) => a + b, 0) / scores.length
}