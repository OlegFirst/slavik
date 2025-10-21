/**
 * Demo Mode for Digital Twin Module
 * Allows organizations to try ISO scenarios without registration
 */

import { TheoryOfChangeEngine } from './theory-of-change-engine.js';

export class DemoMode {
    constructor() {
        this.isDemoMode = true;
        this.tocEngine = new TheoryOfChangeEngine();
        this.demoOrganization = {
            id: 'demo-org-001',
            name: 'Demo Organization',
            type: 'foundation',
            size: 150,
            annual_budget: 25000000,
            programs: [
                { name: 'Community Health', budget: 8000000, beneficiaries: 150000 },
                { name: 'Digital Literacy', budget: 6000000, beneficiaries: 100000 },
                { name: 'Women Entrepreneurship', budget: 5000000, beneficiaries: 50000 }
            ]
        };
    }

    // ISO Scenario Templates
    getScenarios() {
        return {
            capacity: {
                name: 'Capacity & Staffing Optimization',
                description: 'Optimize staff allocation and service capacity',
                icon: '',
                params: {
                    arrival_rate: { value: 12, min: 5, max: 50, unit: 'per hour' },
                    agents: { value: 8, min: 2, max: 20, unit: 'agents' },
                    service_time: { value: 10, min: 5, max: 30, unit: 'minutes' },
                    sla_target: { value: 95, min: 80, max: 99, unit: '%' }
                },
                expectedResults: {
                    roi: 280,
                    efficiency_gain: 35,
                    cost_reduction: 25,
                    sla_improvement: 15
                }
            },
            bcm_outage: {
                name: 'Business Continuity - Outage Simulation',
                description: 'Test resilience against system failures',
                icon: '',
                params: {
                    rto_hours: { value: 24, min: 1, max: 72, unit: 'hours' },
                    rpo_hours: { value: 4, min: 1, max: 24, unit: 'hours' },
                    outage_type: { 
                        value: 'it_failure', 
                        options: ['it_failure', 'power_outage', 'cyber_attack', 'natural_disaster'] 
                    },
                    dependencies: { value: ['crm', 'email', 'database'], options: ['crm', 'email', 'database', 'payment'] }
                },
                expectedResults: {
                    downtime_hours: 18,
                    recovery_cost: 50000,
                    affected_services: 3,
                    data_loss_gb: 0.5
                }
            },
            grant_optimization: {
                name: 'Grant-KPI Optimization',
                description: 'Align grant disbursements with impact KPIs',
                icon: '',
                params: {
                    grant_amount: { value: 2000000, min: 100000, max: 10000000, unit: '$' },
                    kpi_targets: { value: 3, min: 1, max: 10, unit: 'indicators' },
                    disbursement_tranches: { value: 4, min: 1, max: 12, unit: 'payments' },
                    timeline_months: { value: 24, min: 6, max: 60, unit: 'months' }
                },
                expectedResults: {
                    kpi_achievement: 92,
                    cash_flow_efficiency: 85,
                    compliance_score: 98,
                    impact_multiplier: 2.5
                }
            },
            demand_surge: {
                name: 'Demand Surge Response',
                description: 'Handle sudden increase in service demand',
                icon: '',
                params: {
                    surge_factor: { value: 2.5, min: 1.5, max: 5, unit: 'x normal' },
                    duration_days: { value: 30, min: 7, max: 90, unit: 'days' },
                    current_capacity: { value: 100, min: 50, max: 500, unit: 'services/day' },
                    flex_resources: { value: true, options: [true, false] }
                },
                expectedResults: {
                    unmet_demand: 15,
                    overtime_cost: 75000,
                    sla_degradation: 8,
                    recovery_days: 14
                }
            },
            theory_of_change: {
                name: 'Theory of Change Optimizer',
                description: 'AI-driven impact maximization through causal optimization',
                icon: '',
                params: {
                    sms_intensity: { value: 1.0, min: 0, max: 3, unit: 'x', step: 0.1 },
                    transport_intensity: { value: 1.0, min: 0, max: 2, unit: 'x', step: 0.1 },
                    counseling_intensity: { value: 1.0, min: 0, max: 2, unit: 'x', step: 0.1 },
                    budget_cap: { value: 50000, min: 10000, max: 100000, unit: '$', step: 5000 },
                    objective: {
                        value: 'maximize_outcome_per_cost',
                        options: ['maximize_outcome_per_cost', 'maximize_coverage', 'minimize_cost_per_beneficiary', 'maximize_net_monetary_benefit']
                    }
                },
                expectedResults: {
                    coverage_improvement: 19,
                    cost_efficiency: 0.42,
                    confidence_level: 87,
                    roi: 350
                }
            }
        };
    }

    // Run demo simulation
    async runDemoSimulation(scenarioType, params = {}) {
        console.log(`[DEMO] Running ${scenarioType} simulation...`);
        
        const scenario = this.getScenarios()[scenarioType];
        if (!scenario) throw new Error('Unknown scenario type');
        
        // For Theory of Change, use the actual engine
        if (scenarioType === 'theory_of_change') {
            return await this.runTheoryOfChangeSimulation(params, scenario);
        }
        
        // Simulate processing delay for other scenarios
        await this.simulateDelay(2000);
        
        // Generate realistic mock results
        const results = this.generateMockResults(scenarioType, params);
        
        return {
            scenario: scenario.name,
            timestamp: new Date().toISOString(),
            params: params || scenario.params,
            results,
            recommendations: this.generateRecommendations(scenarioType, results),
            nextSteps: this.generateNextSteps(scenarioType)
        };
    }

    // Run Theory of Change simulation using actual engine
    async runTheoryOfChangeSimulation(params, scenario) {
        // Load ToC template
        await this.tocEngine.loadFromTemplate({
            nodes: [
                { id: 'need_access', type: 'problem', label: 'Low Service Access' },
                { id: 'awareness', type: 'mediator', label: 'Awareness' },
                { id: 'uptake', type: 'mediator', label: 'Uptake' },
                { id: 'adherence', type: 'mediator', label: 'Adherence' },
                { id: 'outcome_cov', type: 'outcome', label: 'Coverage' },
                { id: 'impact_morb', type: 'impact', label: 'Reduced Morbidity' }
            ],
            edges: [
                { from: 'need_access', to: 'awareness', effect: 'negative', elasticity: -0.3 },
                { from: 'awareness', to: 'uptake', effect: 'positive', elasticity: 0.5 },
                { from: 'uptake', to: 'adherence', effect: 'positive', elasticity: 0.4 },
                { from: 'adherence', to: 'outcome_cov', effect: 'positive', elasticity: 0.6 },
                { from: 'outcome_cov', to: 'impact_morb', effect: 'negative', elasticity: -0.2 }
            ],
            interventions: [
                { id: 'outreach_sms', label: 'SMS outreach', targets: ['awareness'], cost_per_unit: 0.12, effect_size: 0.2 },
                { id: 'transport_vouchers', label: 'Transport vouchers', targets: ['uptake'], cost_per_unit: 2.50, effect_size: 0.35 },
                { id: 'counseling', label: 'Individual counseling', targets: ['adherence'], cost_per_unit: 3.80, effect_size: 0.25 }
            ],
            indicators: [
                { id: 'cov', node: 'outcome_cov', baseline: 0.52, target: 0.70 },
                { id: 'morb', node: 'impact_morb', baseline: 0.18, target: 0.15 }
            ]
        });
        
        // Run optimization
        const optimizationResult = await this.tocEngine.optimizePolicy({
            objective: params.objective?.value || 'maximize_outcome_per_cost',
            budgetCap: params.budget_cap?.value || 50000,
            decisionVariables: [
                { id: 'outreach_sms', min: 0, max: params.sms_intensity?.max || 3, step: 0.1 },
                { id: 'transport_vouchers', min: 0, max: params.transport_intensity?.max || 2, step: 0.1 },
                { id: 'counseling', min: 0, max: params.counseling_intensity?.max || 2, step: 0.1 }
            ],
            monteCarloRuns: 1000
        });
        
        // Format results for demo display
        return {
            scenario: scenario.name,
            timestamp: new Date().toISOString(),
            params: params || scenario.params,
            results: {
                optimal_policy: optimizationResult.policy,
                coverage_forecast: optimizationResult.coverage_forecast,
                total_cost: optimizationResult.cost,
                net_monetary_benefit: optimizationResult.nmb,
                confidence: optimizationResult.confidence,
                achievement_probability: optimizationResult.achievement_probability,
                impact_visualization: 'Causal graph optimization complete'
            },
            recommendations: optimizationResult.recommendations || [],
            nextSteps: [
                '1. Review optimized intervention intensities',
                '2. Validate assumptions with your data',
                '3. Run sensitivity analysis on key parameters',
                '4. Implement pilot program with recommended settings',
                '5. Monitor and adjust based on real-world results'
            ]
        };
    }

    generateMockResults(scenarioType, params) {
        const baseResults = {
            capacity: {
                optimal_agents: Math.floor(Math.random() * 3) + parseInt(params.agents?.value || 8),
                sla_achieved: 94 + Math.random() * 5,
                cost_per_service: 45 + Math.random() * 20,
                wait_time_minutes: 2 + Math.random() * 5,
                throughput_improvement: 25 + Math.random() * 15,
                monthly_savings: 15000 + Math.random() * 10000,
                payback_months: 12 + Math.floor(Math.random() * 12),
                confidence_score: 0.85 + Math.random() * 0.14
            },
            bcm_outage: {
                estimated_downtime: 12 + Math.random() * 24,
                services_affected: Math.floor(Math.random() * 5) + 2,
                recovery_time: 18 + Math.random() * 12,
                data_at_risk_gb: Math.random() * 10,
                financial_impact: 25000 + Math.random() * 75000,
                reputation_score: 3 + Math.random() * 2,
                mitigation_effectiveness: 0.7 + Math.random() * 0.25,
                compliance_status: 'partial'
            },
            grant_optimization: {
                optimal_tranches: Math.floor(Math.random() * 3) + 3,
                kpi_forecast: 88 + Math.random() * 10,
                burn_rate_monthly: 50000 + Math.random() * 50000,
                milestone_alignment: 0.85 + Math.random() * 0.14,
                risk_score: 0.2 + Math.random() * 0.3,
                roi_percentage: 250 + Math.random() * 100,
                donor_confidence: 4.2 + Math.random() * 0.7,
                compliance_readiness: 0.92 + Math.random() * 0.07
            },
            demand_surge: {
                capacity_gap: 20 + Math.random() * 30,
                additional_resources_needed: Math.floor(Math.random() * 10) + 5,
                overflow_handling: 'queue_with_triage',
                estimated_wait_increase: 15 + Math.random() * 30,
                cost_surge: 50000 + Math.random() * 50000,
                sla_maintenance: 0.75 + Math.random() * 0.2,
                recovery_timeline_days: 7 + Math.floor(Math.random() * 21),
                customer_impact_score: 2 + Math.random() * 3
            },
            theory_of_change: {
                coverage_baseline: 0.52,
                coverage_optimized: 0.65 + Math.random() * 0.15,
                total_budget_used: 40000 + Math.random() * 10000,
                sms_optimal: 1.4 + Math.random() * 0.4,
                transport_optimal: 0.7 + Math.random() * 0.3,
                counseling_optimal: 1.0 + Math.random() * 0.2,
                net_benefit_ratio: 0.35 + Math.random() * 0.2,
                monte_carlo_confidence: 0.80 + Math.random() * 0.15,
                implementation_readiness: 0.85 + Math.random() * 0.1
            }
        };
        
        return baseResults[scenarioType] || baseResults.capacity;
    }

    generateRecommendations(scenarioType, results) {
        const recommendations = {
            capacity: [
                {
                    priority: 'HIGH',
                    action: `Increase staffing to ${results.optimal_agents} agents`,
                    impact: `Improve SLA by ${results.throughput_improvement.toFixed(0)}%`,
                    cost: `$${results.monthly_savings.toFixed(0)} monthly savings`
                },
                {
                    priority: 'MEDIUM',
                    action: 'Implement shift optimization algorithm',
                    impact: 'Reduce wait times by 45%',
                    cost: 'One-time investment of $25,000'
                },
                {
                    priority: 'LOW',
                    action: 'Add self-service options',
                    impact: 'Deflect 20% of routine requests',
                    cost: '$10,000 setup cost'
                }
            ],
            bcm_outage: [
                {
                    priority: 'CRITICAL',
                    action: 'Implement automated failover',
                    impact: `Reduce downtime to ${results.recovery_time.toFixed(0)} hours`,
                    cost: '$50,000 infrastructure investment'
                },
                {
                    priority: 'HIGH',
                    action: 'Establish backup data center',
                    impact: 'Achieve 99.9% uptime SLA',
                    cost: '$15,000 monthly'
                },
                {
                    priority: 'MEDIUM',
                    action: 'Quarterly BCM drills',
                    impact: 'Improve response time by 60%',
                    cost: '$5,000 per drill'
                }
            ],
            grant_optimization: [
                {
                    priority: 'HIGH',
                    action: `Restructure to ${results.optimal_tranches} disbursements`,
                    impact: `Achieve ${results.kpi_forecast.toFixed(0)}% KPI target`,
                    cost: 'No additional cost'
                },
                {
                    priority: 'MEDIUM',
                    action: 'Implement milestone-based payments',
                    impact: 'Improve donor confidence by 40%',
                    cost: '$2,000 legal review'
                }
            ],
            demand_surge: [
                {
                    priority: 'HIGH',
                    action: `Add ${results.additional_resources_needed} flex resources`,
                    impact: 'Handle 95% of surge demand',
                    cost: `$${results.cost_surge.toFixed(0)} for surge period`
                },
                {
                    priority: 'MEDIUM',
                    action: 'Implement dynamic queue management',
                    impact: 'Reduce wait time variance by 50%',
                    cost: '$15,000 software license'
                }
            ],
            theory_of_change: [
                {
                    priority: 'HIGH',
                    action: `Scale SMS outreach to ${(results.sms_optimal || 1.6).toFixed(1)}x intensity`,
                    impact: 'Highest ROI on awareness improvement',
                    cost: 'Low cost per beneficiary reached'
                },
                {
                    priority: 'HIGH',
                    action: `Optimize counseling to ${(results.counseling_optimal || 1.1).toFixed(1)}x intensity`,
                    impact: 'Critical for adherence and long-term impact',
                    cost: 'Moderate investment with high returns'
                },
                {
                    priority: 'MEDIUM',
                    action: `Adjust transport vouchers to ${(results.transport_optimal || 0.8).toFixed(1)}x`,
                    impact: 'Reallocation improves overall efficiency',
                    cost: 'Cost savings can fund other interventions'
                },
                {
                    priority: 'MEDIUM',
                    action: 'Implement continuous A/B testing',
                    impact: 'Validate and refine elasticity estimates',
                    cost: '$5,000 for measurement infrastructure'
                }
            ]
        };
        
        return recommendations[scenarioType] || recommendations.capacity;
    }

    generateNextSteps(scenarioType) {
        return [
            '1. Review simulation results with your team',
            '2. Schedule a consultation with SEH experts',
            '3. Request custom simulation with your actual data',
            '4. Get implementation roadmap and pricing',
            '5. Start with pilot program (3-month trial available)'
        ];
    }

    // Helper to simulate async delay
    simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Generate demo dashboard data
    getDemoDashboard() {
        return {
            organization: this.demoOrganization,
            health_score: 85,
            efficiency_score: 72,
            maturity_level: 3,
            available_scenarios: Object.keys(this.getScenarios()).length,
            recent_simulations: [
                {
                    scenario: 'Capacity Optimization',
                    date: new Date(Date.now() - 86400000).toISOString(),
                    result: 'Identified 25% efficiency gain',
                    status: 'completed'
                },
                {
                    scenario: 'BCM Outage Test',
                    date: new Date(Date.now() - 172800000).toISOString(),
                    result: 'RTO reduced to 18 hours',
                    status: 'completed'
                }
            ],
            metrics: {
                total_beneficiaries: 300000,
                programs_active: 3,
                budget_utilized: 0.75,
                impact_score: 8.5
            }
        };
    }

    // Check if user is in demo mode
    isDemoUser() {
        return !localStorage.getItem('user_token') || localStorage.getItem('demo_mode') === 'true';
    }

    // Enable demo mode
    enableDemoMode() {
        localStorage.setItem('demo_mode', 'true');
        console.log('[DEMO] Demo mode enabled');
    }

    // Exit demo mode (prompt for registration)
    exitDemoMode() {
        localStorage.removeItem('demo_mode');
        return {
            message: 'Ready to implement these solutions?',
            actions: [
                { label: 'Schedule Consultation', url: '/consultation' },
                { label: 'Create Account', url: '/register' },
                { label: 'Request Custom Demo', url: '/custom-demo' }
            ]
        };
    }
}

// Export for use in main module
export default DemoMode;