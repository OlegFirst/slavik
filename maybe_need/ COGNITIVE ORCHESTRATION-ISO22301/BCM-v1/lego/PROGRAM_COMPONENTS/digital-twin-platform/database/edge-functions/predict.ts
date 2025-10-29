// Supabase Edge Function: Predict
// AI-powered predictions for digital twins

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface PredictionRequest {
  twinId: string
  predictionType: string
  targetDate?: string
  parameters?: Record<string, any>
}

serve(async (req) => {
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

    const { 
      twinId, 
      predictionType, 
      targetDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      parameters = {} 
    } = await req.json() as PredictionRequest

    // Verify twin access
    const { data: twin, error: twinError } = await supabaseClient
      .from('digital_twins')
      .select('*, organizations(*)')
      .eq('id', twinId)
      .single()

    if (twinError || !twin) {
      throw new Error('Twin not found or access denied')
    }

    // Get historical metrics for prediction
    const { data: historicalMetrics } = await supabaseClient
      .from('metrics')
      .select('*')
      .eq('twin_id', twinId)
      .order('timestamp', { ascending: false })
      .limit(100)

    // Get previous predictions for learning
    const { data: previousPredictions } = await supabaseClient
      .from('predictions')
      .select('*')
      .eq('twin_id', twinId)
      .eq('prediction_type', predictionType)
      .order('created_at', { ascending: false })
      .limit(10)

    // Generate prediction based on type
    const prediction = await generatePrediction(
      twin,
      predictionType,
      targetDate,
      historicalMetrics || [],
      previousPredictions || [],
      parameters
    )

    // Store prediction
    const { data: savedPrediction, error: saveError } = await supabaseClient
      .from('predictions')
      .insert({
        twin_id: twinId,
        prediction_type: predictionType,
        target_date: targetDate,
        predicted_value: prediction.value,
        confidence_interval: prediction.confidenceInterval,
        confidence_score: prediction.confidence,
        model_used: prediction.model,
        factors: prediction.factors,
      })
      .select()
      .single()

    if (saveError) {
      throw saveError
    }

    // Store learning data for model improvement
    await supabaseClient
      .from('ai_learning_data')
      .insert({
        twin_id: twinId,
        data_type: 'prediction',
        input_data: {
          historicalMetrics: historicalMetrics?.slice(0, 10),
          predictionType,
          parameters,
        },
        output_data: prediction,
        model_version: '1.0.0',
        accuracy_score: prediction.confidence,
      })

    return new Response(
      JSON.stringify({
        success: true,
        prediction: {
          id: savedPrediction.id,
          type: predictionType,
          targetDate,
          value: prediction.value,
          confidence: prediction.confidence,
          confidenceInterval: prediction.confidenceInterval,
          factors: prediction.factors,
          insights: prediction.insights,
        },
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

async function generatePrediction(
  twin: any,
  predictionType: string,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const predictors: Record<string, Function> = {
    budget_forecast: predictBudget,
    staff_turnover: predictStaffTurnover,
    grant_success: predictGrantSuccess,
    program_impact: predictProgramImpact,
    donor_retention: predictDonorRetention,
    operational_efficiency: predictOperationalEfficiency,
  }

  const predictor = predictors[predictionType] || genericPredictor
  return await predictor(twin, targetDate, historicalMetrics, previousPredictions, parameters)
}

async function predictBudget(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  // Extract budget-related metrics
  const budgetMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'budget' || m.metric_type === 'financial_health'
  )

  // Simple linear regression for trend
  const trend = calculateTrend(budgetMetrics.map(m => m.value))
  
  // Seasonal adjustment
  const seasonalFactor = getSeasonalFactor(new Date(targetDate).getMonth())
  
  // Calculate base prediction
  const lastValue = budgetMetrics[0]?.value || twin.organizations?.annual_budget || 1000000
  const daysDiff = Math.floor((new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
  const trendProjection = lastValue * (1 + trend * daysDiff / 365)
  const seasonalAdjusted = trendProjection * seasonalFactor

  // Add uncertainty
  const uncertainty = 0.1 * Math.random()
  const predictedValue = seasonalAdjusted * (1 + (Math.random() - 0.5) * uncertainty)

  // Calculate confidence based on data quality
  const dataPoints = budgetMetrics.length
  const confidence = Math.min(0.95, 0.5 + dataPoints * 0.01 + (1 - uncertainty) * 0.3)

  return {
    value: Math.round(predictedValue),
    confidence,
    confidenceInterval: {
      lower: Math.round(predictedValue * 0.85),
      upper: Math.round(predictedValue * 1.15),
    },
    model: 'linear_regression_seasonal',
    factors: [
      { name: 'historical_trend', impact: trend, weight: 0.4 },
      { name: 'seasonality', impact: seasonalFactor - 1, weight: 0.2 },
      { name: 'economic_conditions', impact: 0.02, weight: 0.2 },
      { name: 'grant_pipeline', impact: 0.05, weight: 0.2 },
    ],
    insights: [
      `Budget is trending ${trend > 0 ? 'upward' : 'downward'} at ${Math.abs(trend * 100).toFixed(1)}% annually`,
      `Seasonal factors suggest a ${((seasonalFactor - 1) * 100).toFixed(1)}% adjustment`,
      `Confidence level: ${(confidence * 100).toFixed(0)}% based on ${dataPoints} data points`,
    ],
  }
}

async function predictStaffTurnover(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const staffMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'staff_count' || m.metric_type === 'staff_satisfaction'
  )

  const currentStaff = twin.state?.staffCount || 50
  const avgSatisfaction = staffMetrics
    .filter(m => m.metric_type === 'staff_satisfaction')
    .reduce((sum, m) => sum + m.value, 0) / Math.max(1, staffMetrics.length) || 7

  // Turnover rate based on satisfaction
  const baseTurnoverRate = 0.15 // 15% annual baseline
  const satisfactionAdjustment = (10 - avgSatisfaction) * 0.02
  const predictedTurnoverRate = Math.max(0.05, Math.min(0.4, baseTurnoverRate + satisfactionAdjustment))

  const monthsUntilTarget = Math.floor((new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30))
  const predictedTurnover = Math.floor(currentStaff * predictedTurnoverRate * (monthsUntilTarget / 12))

  return {
    value: predictedTurnover,
    confidence: 0.72,
    confidenceInterval: {
      lower: Math.floor(predictedTurnover * 0.7),
      upper: Math.ceil(predictedTurnover * 1.3),
    },
    model: 'satisfaction_based_turnover',
    factors: [
      { name: 'staff_satisfaction', impact: avgSatisfaction / 10, weight: 0.5 },
      { name: 'market_conditions', impact: 0.1, weight: 0.2 },
      { name: 'compensation_competitiveness', impact: -0.05, weight: 0.3 },
    ],
    insights: [
      `Predicted ${predictedTurnover} staff departures by ${new Date(targetDate).toLocaleDateString()}`,
      `Current satisfaction score of ${avgSatisfaction.toFixed(1)}/10 influences retention`,
      `Annual turnover rate estimated at ${(predictedTurnoverRate * 100).toFixed(1)}%`,
    ],
  }
}

async function predictGrantSuccess(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const grantMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'grant_success_rate' || m.metric_type === 'grant_applications'
  )

  const historicalSuccessRate = grantMetrics
    .filter(m => m.metric_type === 'grant_success_rate')
    .reduce((sum, m) => sum + m.value, 0) / Math.max(1, grantMetrics.length) || 0.3

  const grantAmount = parameters.grantAmount || 100000
  const competitionLevel = parameters.competitionLevel || 'medium'

  const competitionFactors = {
    low: 1.2,
    medium: 1.0,
    high: 0.7,
    very_high: 0.4,
  }

  const adjustedSuccessRate = historicalSuccessRate * (competitionFactors[competitionLevel] || 1.0)
  const sizeAdjustment = grantAmount > 500000 ? 0.8 : grantAmount > 100000 ? 0.9 : 1.0
  const finalSuccessRate = Math.min(0.95, adjustedSuccessRate * sizeAdjustment)

  return {
    value: finalSuccessRate,
    confidence: 0.78,
    confidenceInterval: {
      lower: Math.max(0, finalSuccessRate - 0.15),
      upper: Math.min(1, finalSuccessRate + 0.15),
    },
    model: 'grant_success_predictor',
    factors: [
      { name: 'historical_performance', impact: historicalSuccessRate, weight: 0.4 },
      { name: 'competition_level', impact: competitionFactors[competitionLevel] - 1, weight: 0.3 },
      { name: 'grant_size', impact: sizeAdjustment - 1, weight: 0.2 },
      { name: 'proposal_quality', impact: 0.1, weight: 0.1 },
    ],
    insights: [
      `${(finalSuccessRate * 100).toFixed(0)}% probability of grant success`,
      `Historical success rate: ${(historicalSuccessRate * 100).toFixed(0)}%`,
      `Competition level (${competitionLevel}) affects probability by ${((competitionFactors[competitionLevel] - 1) * 100).toFixed(0)}%`,
    ],
  }
}

async function predictProgramImpact(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const programMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'program_beneficiaries' || m.metric_type === 'program_outcomes'
  )

  const currentImpact = programMetrics[0]?.value || 1000
  const growthRate = calculateTrend(programMetrics.map(m => m.value))
  const monthsUntilTarget = Math.floor((new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30))
  
  const projectedImpact = currentImpact * Math.pow(1 + growthRate, monthsUntilTarget / 12)

  return {
    value: Math.round(projectedImpact),
    confidence: 0.75,
    confidenceInterval: {
      lower: Math.round(projectedImpact * 0.8),
      upper: Math.round(projectedImpact * 1.2),
    },
    model: 'impact_growth_model',
    factors: [
      { name: 'current_reach', impact: currentImpact / 1000, weight: 0.3 },
      { name: 'growth_trajectory', impact: growthRate, weight: 0.4 },
      { name: 'resource_availability', impact: 0.1, weight: 0.3 },
    ],
    insights: [
      `Projected to reach ${Math.round(projectedImpact)} beneficiaries by target date`,
      `Current growth rate: ${(growthRate * 100).toFixed(1)}% annually`,
      `${monthsUntilTarget} months until target date`,
    ],
  }
}

async function predictDonorRetention(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const donorMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'donor_count' || m.metric_type === 'donor_retention_rate'
  )

  const currentRetentionRate = donorMetrics
    .filter(m => m.metric_type === 'donor_retention_rate')
    .reduce((sum, m) => sum + m.value, 0) / Math.max(1, donorMetrics.length) || 0.65

  const engagementScore = parameters.engagementScore || 0.7
  const communicationFrequency = parameters.communicationFrequency || 'monthly'

  const frequencyMultipliers = {
    weekly: 1.1,
    monthly: 1.0,
    quarterly: 0.9,
    annually: 0.7,
  }

  const adjustedRetention = currentRetentionRate * engagementScore * (frequencyMultipliers[communicationFrequency] || 1.0)

  return {
    value: Math.min(0.95, adjustedRetention),
    confidence: 0.8,
    confidenceInterval: {
      lower: Math.max(0.3, adjustedRetention - 0.1),
      upper: Math.min(0.95, adjustedRetention + 0.1),
    },
    model: 'donor_retention_model',
    factors: [
      { name: 'historical_retention', impact: currentRetentionRate, weight: 0.5 },
      { name: 'engagement_quality', impact: engagementScore, weight: 0.3 },
      { name: 'communication_frequency', impact: frequencyMultipliers[communicationFrequency] - 1, weight: 0.2 },
    ],
    insights: [
      `Predicted donor retention rate: ${(adjustedRetention * 100).toFixed(0)}%`,
      `Current retention rate: ${(currentRetentionRate * 100).toFixed(0)}%`,
      `Engagement and communication strategies can improve retention by ${((adjustedRetention / currentRetentionRate - 1) * 100).toFixed(0)}%`,
    ],
  }
}

async function predictOperationalEfficiency(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const efficiencyMetrics = historicalMetrics.filter(m => 
    m.metric_type === 'efficiency' || m.metric_type === 'operational_cost'
  )

  const currentEfficiency = twin.efficiency_score || 0.65
  const improvementRate = parameters.improvementRate || 0.02 // 2% per month
  const monthsUntilTarget = Math.floor((new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30))
  
  const projectedEfficiency = Math.min(0.95, currentEfficiency + (improvementRate * monthsUntilTarget))

  return {
    value: projectedEfficiency,
    confidence: 0.77,
    confidenceInterval: {
      lower: projectedEfficiency * 0.9,
      upper: Math.min(0.95, projectedEfficiency * 1.1),
    },
    model: 'efficiency_improvement_model',
    factors: [
      { name: 'current_efficiency', impact: currentEfficiency, weight: 0.4 },
      { name: 'improvement_initiatives', impact: improvementRate * 12, weight: 0.4 },
      { name: 'resource_optimization', impact: 0.05, weight: 0.2 },
    ],
    insights: [
      `Efficiency projected to reach ${(projectedEfficiency * 100).toFixed(0)}% by target date`,
      `Current efficiency: ${(currentEfficiency * 100).toFixed(0)}%`,
      `Monthly improvement rate: ${(improvementRate * 100).toFixed(1)}%`,
    ],
  }
}

async function genericPredictor(
  twin: any,
  targetDate: string,
  historicalMetrics: any[],
  previousPredictions: any[],
  parameters: Record<string, any>
): Promise<any> {
  const relevantMetrics = historicalMetrics.slice(0, 20)
  const avgValue = relevantMetrics.reduce((sum, m) => sum + m.value, 0) / Math.max(1, relevantMetrics.length) || 100
  const trend = calculateTrend(relevantMetrics.map(m => m.value))
  
  const monthsUntilTarget = Math.floor((new Date(targetDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30))
  const projectedValue = avgValue * Math.pow(1 + trend, monthsUntilTarget / 12)

  return {
    value: projectedValue,
    confidence: 0.65,
    confidenceInterval: {
      lower: projectedValue * 0.75,
      upper: projectedValue * 1.25,
    },
    model: 'generic_trend_model',
    factors: [
      { name: 'historical_average', impact: avgValue / 100, weight: 0.5 },
      { name: 'trend', impact: trend, weight: 0.5 },
    ],
    insights: [
      `Generic prediction based on ${relevantMetrics.length} data points`,
      `Trend analysis shows ${trend > 0 ? 'growth' : 'decline'} of ${Math.abs(trend * 100).toFixed(1)}% annually`,
    ],
  }
}

function calculateTrend(values: number[]): number {
  if (values.length < 2) return 0
  
  const n = values.length
  const sumX = n * (n - 1) / 2
  const sumY = values.reduce((a, b) => a + b, 0)
  const sumXY = values.reduce((sum, y, x) => sum + x * y, 0)
  const sumX2 = n * (n - 1) * (2 * n - 1) / 6

  const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  const avgY = sumY / n
  
  return avgY > 0 ? slope / avgY : 0
}

function getSeasonalFactor(month: number): number {
  // Typical NPO seasonal patterns
  const seasonalFactors = [
    0.95, // January
    0.92, // February
    0.98, // March
    1.02, // April
    1.05, // May
    1.08, // June
    0.96, // July
    0.94, // August
    1.03, // September
    1.06, // October
    1.10, // November (giving season)
    1.15, // December (year-end giving)
  ]
  
  return seasonalFactors[month] || 1.0
}