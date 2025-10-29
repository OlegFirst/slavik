/**
 * Theory of Change (ToC) Engine
 * Implements causal graph optimization for impact measurement
 * Based on SEH specification
 */

export class TheoryOfChangeEngine {
    constructor() {
        this.nodes = new Map();
        this.edges = [];
        this.interventions = [];
        this.indicators = [];
    }

    /**
     * Load ToC from YAML template
     */
    async loadFromTemplate(template) {
        // Parse nodes (problems, mediators, outcomes, impacts)
        template.nodes.forEach(node => {
            this.nodes.set(node.id, {
                ...node,
                value: 0,
                uncertainty: 0.1
            });
        });

        // Parse edges (causal relationships)
        this.edges = template.edges.map(edge => ({
            ...edge,
            strength: edge.elasticity || 0.5,
            confidence: 0.8
        }));

        // Parse interventions
        this.interventions = template.interventions || [];
        
        // Parse indicators
        this.indicators = template.indicators || [];
        
        return this;
    }

    /**
     * Run Monte Carlo simulation
     */
    async runMonteCarlo(params = {}) {
        const {
            runs = 1000,
            interventionIntensities = {},
            budget = 50000
        } = params;

        const results = [];
        
        for (let i = 0; i < runs; i++) {
            // Add uncertainty to parameters
            const scenario = this.createScenarioWithUncertainty();
            
            // Apply interventions
            const appliedInterventions = this.applyInterventions(
                interventionIntensities,
                budget,
                scenario
            );
            
            // Propagate effects through causal graph
            const outcomes = this.propagateEffects(
                appliedInterventions,
                scenario
            );
            
            results.push(outcomes);
        }
        
        return this.analyzeResults(results);
    }

    /**
     * Optimize policy to maximize impact
     */
    async optimizePolicy(config) {
        const {
            objective = 'maximize_outcome_per_cost',
            budgetCap = 50000,
            decisionVariables = [],
            monteCarloRuns = 1000
        } = config;

        let bestPolicy = null;
        let bestScore = -Infinity;
        
        // Grid search over decision variables
        const policies = this.generatePolicySpace(decisionVariables);
        
        for (const policy of policies) {
            // Check budget constraint
            const cost = this.calculatePolicyCost(policy);
            if (cost > budgetCap) continue;
            
            // Run simulation for this policy
            const results = await this.runMonteCarlo({
                runs: monteCarloRuns,
                interventionIntensities: policy,
                budget: budgetCap
            });
            
            // Calculate objective score
            const score = this.calculateObjective(results, cost, objective);
            
            if (score > bestScore) {
                bestScore = score;
                bestPolicy = {
                    policy,
                    results,
                    cost,
                    score
                };
            }
        }
        
        return this.formatOptimizationResult(bestPolicy);
    }

    /**
     * Create scenario with uncertainty
     */
    createScenarioWithUncertainty() {
        const scenario = {
            nodes: new Map(),
            edges: []
        };
        
        // Add noise to node values
        this.nodes.forEach((node, id) => {
            scenario.nodes.set(id, {
                ...node,
                value: node.value + this.gaussianRandom() * node.uncertainty
            });
        });
        
        // Add noise to edge strengths
        scenario.edges = this.edges.map(edge => ({
            ...edge,
            strength: edge.strength + this.gaussianRandom() * 0.1
        }));
        
        return scenario;
    }

    /**
     * Apply interventions to the system
     */
    applyInterventions(intensities, budget, scenario) {
        const applied = [];
        let totalCost = 0;
        
        this.interventions.forEach(intervention => {
            const intensity = intensities[intervention.id] || 0;
            if (intensity === 0) return;
            
            const cost = intervention.cost_per_unit * intensity;
            if (totalCost + cost > budget) return;
            
            // Apply effect to target nodes
            intervention.targets.forEach(targetId => {
                const node = scenario.nodes.get(targetId);
                if (node) {
                    node.value += intervention.effect_size * intensity;
                }
            });
            
            applied.push({
                ...intervention,
                intensity,
                cost
            });
            
            totalCost += cost;
        });
        
        return applied;
    }

    /**
     * Propagate effects through causal graph
     */
    propagateEffects(interventions, scenario) {
        const iterations = 10; // Propagation iterations
        
        for (let i = 0; i < iterations; i++) {
            scenario.edges.forEach(edge => {
                const fromNode = scenario.nodes.get(edge.from);
                const toNode = scenario.nodes.get(edge.to);
                
                if (fromNode && toNode) {
                    const effect = fromNode.value * edge.strength;
                    toNode.value += effect * (edge.effect === 'positive' ? 1 : -1);
                }
            });
        }
        
        // Extract outcome values
        const outcomes = {};
        this.indicators.forEach(indicator => {
            const node = scenario.nodes.get(indicator.node);
            if (node) {
                outcomes[indicator.id] = {
                    value: node.value,
                    baseline: indicator.baseline,
                    target: indicator.target,
                    achievement: (node.value - indicator.baseline) / 
                                (indicator.target - indicator.baseline)
                };
            }
        });
        
        return outcomes;
    }

    /**
     * Analyze Monte Carlo results
     */
    analyzeResults(results) {
        const aggregated = {};
        
        // Get all outcome keys
        const outcomeKeys = Object.keys(results[0] || {});
        
        outcomeKeys.forEach(key => {
            const values = results.map(r => r[key].value);
            values.sort((a, b) => a - b);
            
            aggregated[key] = {
                mean: this.mean(values),
                median: values[Math.floor(values.length / 2)],
                p10: values[Math.floor(values.length * 0.1)],
                p90: values[Math.floor(values.length * 0.9)],
                confidence: this.calculateConfidence(values),
                achievement: this.mean(results.map(r => r[key].achievement))
            };
        });
        
        return aggregated;
    }

    /**
     * Generate policy space for optimization
     */
    generatePolicySpace(variables) {
        const policies = [];
        
        // Simple grid search (can be replaced with genetic algorithm)
        const generateCombinations = (index = 0, current = {}) => {
            if (index >= variables.length) {
                policies.push({ ...current });
                return;
            }
            
            const variable = variables[index];
            for (let v = variable.min; v <= variable.max; v += variable.step) {
                current[variable.id] = v;
                generateCombinations(index + 1, current);
            }
        };
        
        generateCombinations();
        
        // Limit to reasonable number
        if (policies.length > 1000) {
            // Random sampling if too many
            const sampled = [];
            for (let i = 0; i < 1000; i++) {
                sampled.push(policies[Math.floor(Math.random() * policies.length)]);
            }
            return sampled;
        }
        
        return policies;
    }

    /**
     * Calculate policy cost
     */
    calculatePolicyCost(policy) {
        let totalCost = 0;
        
        this.interventions.forEach(intervention => {
            const intensity = policy[intervention.id] || 0;
            totalCost += intervention.cost_per_unit * intensity;
        });
        
        return totalCost;
    }

    /**
     * Calculate objective function
     */
    calculateObjective(results, cost, objective) {
        switch (objective) {
            case 'maximize_outcome_per_cost':
                const outcomeValue = results.cov?.mean || 0;
                return outcomeValue / (cost / 10000); // Normalize cost
                
            case 'maximize_coverage':
                return results.cov?.mean || 0;
                
            case 'minimize_cost_per_beneficiary':
                const beneficiaries = (results.cov?.mean || 0.5) * 100000; // Assume 100k population
                return beneficiaries / cost;
                
            case 'maximize_net_monetary_benefit':
                const benefit = (results.cov?.mean || 0) * 100000; // Value per coverage point
                return benefit - cost;
                
            default:
                return results.cov?.mean || 0;
        }
    }

    /**
     * Format optimization result
     */
    formatOptimizationResult(bestPolicy) {
        if (!bestPolicy) {
            return {
                error: 'No feasible policy found within budget constraints'
            };
        }
        
        const { policy, results, cost, score } = bestPolicy;
        
        // Format policy intensities
        const formattedPolicy = {};
        Object.keys(policy).forEach(key => {
            formattedPolicy[key.replace('_intensity', '')] = policy[key].toFixed(1);
        });
        
        return {
            policy: formattedPolicy,
            coverage_forecast: {
                mean: results.cov?.mean.toFixed(2) || 0,
                p10: results.cov?.p10.toFixed(2) || 0,
                p90: results.cov?.p90.toFixed(2) || 0
            },
            cost: Math.round(cost),
            nmb: (score / 100).toFixed(2), // Net Monetary Benefit
            confidence: results.cov?.confidence.toFixed(2) || 0,
            achievement_probability: (results.cov?.achievement * 100).toFixed(0) + '%',
            assumptions: [
                'Elasticities stable within pilot range',
                'No negative spillover effects',
                'Linear cost scaling'
            ],
            recommendations: this.generateRecommendations(policy, results)
        };
    }

    /**
     * Generate actionable recommendations
     */
    generateRecommendations(policy, results) {
        const recommendations = [];
        
        // High intensity interventions
        Object.keys(policy).forEach(key => {
            if (policy[key] > 1.5) {
                recommendations.push({
                    priority: 'HIGH',
                    intervention: key,
                    action: `Scale up ${key} to ${policy[key].toFixed(1)}x current level`,
                    rationale: 'High impact on outcome achievement'
                });
            }
        });
        
        // Low confidence areas
        if (results.cov?.confidence < 0.7) {
            recommendations.push({
                priority: 'MEDIUM',
                intervention: 'data_collection',
                action: 'Improve measurement systems',
                rationale: 'Low confidence in current estimates'
            });
        }
        
        // Achievement gap
        if (results.cov?.achievement < 0.8) {
            recommendations.push({
                priority: 'HIGH',
                intervention: 'review',
                action: 'Review Theory of Change assumptions',
                rationale: 'Target achievement below 80%'
            });
        }
        
        return recommendations;
    }

    // Utility functions
    gaussianRandom() {
        let u = 0, v = 0;
        while (u === 0) u = Math.random();
        while (v === 0) v = Math.random();
        return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    mean(values) {
        return values.reduce((a, b) => a + b, 0) / values.length;
    }

    calculateConfidence(values) {
        const m = this.mean(values);
        const variance = values.reduce((sum, v) => sum + Math.pow(v - m, 2), 0) / values.length;
        const std = Math.sqrt(variance);
        return Math.max(0, Math.min(1, 1 - (std / m)));
    }
}

export default TheoryOfChangeEngine;