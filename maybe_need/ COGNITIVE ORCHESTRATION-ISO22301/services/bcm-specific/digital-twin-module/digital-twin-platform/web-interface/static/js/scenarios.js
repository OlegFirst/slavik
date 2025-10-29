/**
 * NASH 4.0 Digital Twin Scenario Simulation Module
 * Interactive scenario planning and simulation
 */

const DigitalTwinScenarios = {
    
    // Run automation scenario
    async runAutomationScenario() {
        if (!DigitalTwinApp.currentTwin) {
            DigitalTwinApp.showNotification('Please select an organization first', 'warning');
            return;
        }
        
        const investment = parseInt(document.getElementById('automationInvestment').value) || 50000;
        const timeline = parseInt(document.getElementById('automationTimeline').value) || 12;
        
        DigitalTwinApp.showLoading(true);
        DigitalTwinApp.addActivityLog('Running automation scenario simulation...');
        
        try {
            // Simulate API call
            const results = await this.simulateAutomationScenario(investment, timeline);
            this.displayAutomationResults(results);
            DigitalTwinApp.addActivityLog('Automation scenario completed');
        } catch (error) {
            console.error('Automation scenario failed:', error);
            DigitalTwinApp.showNotification('Scenario simulation failed', 'error');
        } finally {
            DigitalTwinApp.showLoading(false);
        }
    },
    
    // Simulate automation scenario
    async simulateAutomationScenario(investment, timeline) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const twin = DigitalTwinApp.currentTwin;
                
                // Calculate automation potential
                const automationRate = Math.min(0.8, investment / 100000);
                const currentProcesses = twin.departments.reduce((total, dept) => 
                    total + (dept.processes ? dept.processes.length : 1), 0);
                
                const newAutomatedProcesses = Math.floor(currentProcesses * automationRate);
                const laborSavings = newAutomatedProcesses * 2000 * 12;
                const implementationCost = investment;
                const ongoingCosts = newAutomatedProcesses * 100 * 12;
                const netSavings = laborSavings - implementationCost - ongoingCosts;
                const roi = ((netSavings / implementationCost) * 100);
                const paybackPeriod = implementationCost / (laborSavings / 12);
                
                const results = {
                    investment,
                    timeline,
                    current_state: {
                        total_processes: currentProcesses,
                        automated_processes: 2,
                        manual_processes: currentProcesses - 2,
                        efficiency_score: 25
                    },
                    projected_state: {
                        total_processes: currentProcesses,
                        automated_processes: 2 + newAutomatedProcesses,
                        manual_processes: currentProcesses - 2 - newAutomatedProcesses,
                        efficiency_score: Math.min(95, 25 + (automationRate * 70))
                    },
                    financial_impact: {
                        investment_required: investment,
                        annual_savings: Math.max(0, laborSavings),
                        roi_percentage: Math.round(roi),
                        payback_months: Math.max(1, Math.round(paybackPeriod)),
                        net_savings: netSavings
                    },
                    recommendations: [
                        {
                            priority: 'high',
                            description: 'Start with donor management automation for quick wins'
                        },
                        {
                            priority: 'medium',
                            description: 'Implement reporting automation to reduce administrative overhead'
                        },
                        {
                            priority: 'low',
                            description: 'Consider workflow automation for program delivery'
                        }
                    ],
                    timeline_milestones: [
                        { month: 1, milestone: 'Process analysis and tool selection' },
                        { month: 3, milestone: 'Pilot automation implementation' },
                        { month: 6, milestone: 'First phase rollout' },
                        { month: 9, milestone: 'Staff training and optimization' },
                        { month: 12, milestone: 'Full implementation and evaluation' }
                    ]
                };
                
                resolve(results);
            }, 2000);
        });
    },
    
    // Display automation results
    displayAutomationResults(results) {
        const container = document.getElementById('automationResults');
        
        const html = `
            <div class="scenario-results-content">
                <h4>Automation Scenario Results</h4>
                
                <div class="results-grid">
                    <div class="result-card">
                        <h5>Current State</h5>
                        <div class="metric">
                            <span class="metric-label">Automated Processes:</span>
                            <span class="metric-value">${results.current_state.automated_processes}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Manual Processes:</span>
                            <span class="metric-value">${results.current_state.manual_processes}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Efficiency Score:</span>
                            <span class="metric-value">${results.current_state.efficiency_score}%</span>
                        </div>
                    </div>
                    
                    <div class="result-card">
                        <h5>Projected State</h5>
                        <div class="metric">
                            <span class="metric-label">Automated Processes:</span>
                            <span class="metric-value success">${results.projected_state.automated_processes}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Manual Processes:</span>
                            <span class="metric-value">${results.projected_state.manual_processes}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Efficiency Score:</span>
                            <span class="metric-value success">${Math.round(results.projected_state.efficiency_score)}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="financial-impact">
                    <h5>Financial Impact</h5>
                    <div class="financial-grid">
                        <div class="financial-item">
                            <span class="financial-label">Investment:</span>
                            <span class="financial-value">$${results.financial_impact.investment_required.toLocaleString()}</span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">Annual Savings:</span>
                            <span class="financial-value success">$${results.financial_impact.annual_savings.toLocaleString()}</span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">ROI:</span>
                            <span class="financial-value ${results.financial_impact.roi_percentage > 0 ? 'success' : 'warning'}">
                                ${results.financial_impact.roi_percentage}%
                            </span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">Payback Period:</span>
                            <span class="financial-value">${results.financial_impact.payback_months} months</span>
                        </div>
                    </div>
                </div>
                
                <div class="recommendations">
                    <h5>Recommendations</h5>
                    ${results.recommendations.map(rec => `
                        <div class="recommendation-item priority-${rec.priority}">
                            <span class="priority-badge">${rec.priority.toUpperCase()}</span>
                            <span class="recommendation-text">${rec.description}</span>
                        </div>
                    `).join('')}
                </div>
                
                <button class="btn-primary" onclick="showModal('Automation Scenario Details', DigitalTwinScenarios.getDetailedAutomationReport())">
                    View Detailed Report
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        this.lastAutomationResults = results;
    },
    
    // Run crisis scenario
    async runCrisisScenario() {
        if (!DigitalTwinApp.currentTwin) {
            DigitalTwinApp.showNotification('Please select an organization first', 'warning');
            return;
        }
        
        const crisisType = document.getElementById('crisisType').value;
        const severity = parseFloat(document.getElementById('crisisSeverity').value);
        
        DigitalTwinApp.showLoading(true);
        DigitalTwinApp.addActivityLog('Running crisis scenario simulation...');
        
        try {
            const results = await this.simulateCrisisScenario(crisisType, severity);
            this.displayCrisisResults(results);
            DigitalTwinApp.addActivityLog('Crisis scenario completed');
        } catch (error) {
            console.error('Crisis scenario failed:', error);
            DigitalTwinApp.showNotification('Crisis simulation failed', 'error');
        } finally {
            DigitalTwinApp.showLoading(false);
        }
    },
    
    // Simulate crisis scenario
    async simulateCrisisScenario(crisisType, severity) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const twin = DigitalTwinApp.currentTwin;
                const monthlyBurn = twin.annualBudget / 12;
                const reserves = twin.annualBudget * 0.15; // Assume 15% reserves
                
                const impactMultiplier = severity;
                const fundingLoss = twin.annualBudget * impactMultiplier;
                const adjustedBudget = twin.annualBudget - fundingLoss;
                const survivalMonths = Math.max(0, (adjustedBudget + reserves) / monthlyBurn);
                
                const results = {
                    crisis_type: crisisType,
                    severity,
                    impact_analysis: {
                        funding_loss: fundingLoss,
                        remaining_budget: adjustedBudget,
                        monthly_burn: monthlyBurn,
                        available_reserves: reserves
                    },
                    survival_analysis: {
                        months_of_operation: Math.round(survivalMonths * 10) / 10,
                        staff_reductions_needed: severity > 0.4 ? Math.round(twin.size * (severity - 0.2)) : 0,
                        program_cuts_required: severity > 0.3,
                        critical_threshold: survivalMonths < 6
                    },
                    risk_assessment: {
                        overall_risk: severity > 0.5 ? 'high' : severity > 0.3 ? 'medium' : 'low',
                        financial_stability: survivalMonths > 12 ? 'stable' : survivalMonths > 6 ? 'at_risk' : 'critical',
                        operational_continuity: severity < 0.4 ? 'maintained' : 'reduced'
                    },
                    mitigation_strategies: [
                        {
                            strategy: 'Emergency fundraising campaign',
                            timeframe: '1-3 months',
                            potential_impact: 'High'
                        },
                        {
                            strategy: 'Temporary expense reduction',
                            timeframe: 'Immediate',
                            potential_impact: 'Medium'
                        },
                        {
                            strategy: 'Partnership with other NPOs',
                            timeframe: '2-6 months',
                            potential_impact: 'Medium'
                        }
                    ]
                };
                
                resolve(results);
            }, 2000);
        });
    },
    
    // Display crisis results
    displayCrisisResults(results) {
        const container = document.getElementById('crisisResults');
        
        const html = `
            <div class="scenario-results-content">
                <h4>Crisis Scenario Results</h4>
                <p class="crisis-type">Crisis Type: <strong>${results.crisis_type.replace('_', ' ').toUpperCase()}</strong></p>
                
                <div class="survival-analysis">
                    <h5>Survival Analysis</h5>
                    <div class="survival-metric">
                        <span class="survival-label">Months of Operation:</span>
                        <span class="survival-value ${results.survival_analysis.critical_threshold ? 'critical' : 'stable'}">
                            ${results.survival_analysis.months_of_operation}
                        </span>
                    </div>
                    <div class="survival-metric">
                        <span class="survival-label">Risk Level:</span>
                        <span class="survival-value risk-${results.risk_assessment.overall_risk}">
                            ${results.risk_assessment.overall_risk.toUpperCase()}
                        </span>
                    </div>
                    <div class="survival-metric">
                        <span class="survival-label">Financial Stability:</span>
                        <span class="survival-value">${results.risk_assessment.financial_stability.replace('_', ' ')}</span>
                    </div>
                </div>
                
                <div class="impact-details">
                    <h5>Impact Details</h5>
                    <div class="impact-grid">
                        <div class="impact-item">
                            <span class="impact-label">Funding Loss:</span>
                            <span class="impact-value warning">$${results.impact_analysis.funding_loss.toLocaleString()}</span>
                        </div>
                        <div class="impact-item">
                            <span class="impact-label">Remaining Budget:</span>
                            <span class="impact-value">$${results.impact_analysis.remaining_budget.toLocaleString()}</span>
                        </div>
                        ${results.survival_analysis.staff_reductions_needed > 0 ? `
                        <div class="impact-item">
                            <span class="impact-label">Staff Reductions:</span>
                            <span class="impact-value warning">${results.survival_analysis.staff_reductions_needed} positions</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="mitigation-strategies">
                    <h5>Recommended Mitigation Strategies</h5>
                    ${results.mitigation_strategies.map(strategy => `
                        <div class="strategy-item">
                            <div class="strategy-name">${strategy.strategy}</div>
                            <div class="strategy-details">
                                <span class="strategy-timeframe">Timeframe: ${strategy.timeframe}</span>
                                <span class="strategy-impact impact-${strategy.potential_impact.toLowerCase()}">
                                    ${strategy.potential_impact} Impact
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <button class="btn-warning" onclick="showModal('Crisis Response Plan', DigitalTwinScenarios.getDetailedCrisisReport())">
                    View Response Plan
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        this.lastCrisisResults = results;
    },
    
    // Run expansion scenario
    async runExpansionScenario() {
        if (!DigitalTwinApp.currentTwin) {
            DigitalTwinApp.showNotification('Please select an organization first', 'warning');
            return;
        }
        
        const expansionType = document.getElementById('expansionType').value;
        const budget = parseInt(document.getElementById('expansionBudget').value) || 100000;
        
        DigitalTwinApp.showLoading(true);
        DigitalTwinApp.addActivityLog('Running expansion scenario simulation...');
        
        try {
            const results = await this.simulateExpansionScenario(expansionType, budget);
            this.displayExpansionResults(results);
            DigitalTwinApp.addActivityLog('Expansion scenario completed');
        } catch (error) {
            console.error('Expansion scenario failed:', error);
            DigitalTwinApp.showNotification('Expansion simulation failed', 'error');
        } finally {
            DigitalTwinApp.showLoading(false);
        }
    },
    
    // Simulate expansion scenario
    async simulateExpansionScenario(expansionType, budget) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const twin = DigitalTwinApp.currentTwin;
                
                const expansionMultiplier = budget / 100000;
                const newStaffNeeded = Math.round(expansionMultiplier * 10);
                const additionalPrograms = Math.round(expansionMultiplier * 2);
                const revenueIncrease = budget * 0.3; // Conservative 30% revenue increase
                
                const results = {
                    expansion_type: expansionType,
                    investment: budget,
                    growth_projections: {
                        new_staff: newStaffNeeded,
                        additional_programs: additionalPrograms,
                        service_area_expansion: expansionMultiplier > 1.5 ? 'significant' : 'moderate',
                        capacity_increase: Math.round(expansionMultiplier * 40) // % increase
                    },
                    financial_projections: {
                        revenue_increase: revenueIncrease,
                        operational_costs: budget * 0.7,
                        net_impact: revenueIncrease - (budget * 0.7),
                        break_even_months: Math.round(budget / (revenueIncrease / 12))
                    },
                    implementation_plan: [
                        {
                            phase: 'Planning Phase',
                            duration: '1-2 months',
                            activities: ['Market research', 'Stakeholder engagement', 'Resource planning']
                        },
                        {
                            phase: 'Preparation Phase',
                            duration: '2-3 months',
                            activities: ['Staff recruitment', 'Infrastructure setup', 'Program development']
                        },
                        {
                            phase: 'Launch Phase',
                            duration: '1 month',
                            activities: ['Service launch', 'Marketing campaign', 'Community outreach']
                        },
                        {
                            phase: 'Evaluation Phase',
                            duration: 'Ongoing',
                            activities: ['Performance monitoring', 'Impact assessment', 'Optimization']
                        }
                    ],
                    risk_factors: [
                        {
                            risk: 'Market competition',
                            probability: 'medium',
                            mitigation: 'Unique value proposition development'
                        },
                        {
                            risk: 'Funding shortfalls',
                            probability: 'low',
                            mitigation: 'Diversified funding strategy'
                        }
                    ]
                };
                
                resolve(results);
            }, 2000);
        });
    },
    
    // Display expansion results
    displayExpansionResults(results) {
        const container = document.getElementById('expansionResults');
        
        const html = `
            <div class="scenario-results-content">
                <h4>Expansion Scenario Results</h4>
                <p class="expansion-type">Expansion Type: <strong>${results.expansion_type.replace('_', ' ').toUpperCase()}</strong></p>
                
                <div class="growth-projections">
                    <h5>Growth Projections</h5>
                    <div class="projection-grid">
                        <div class="projection-item">
                            <span class="projection-label">New Staff:</span>
                            <span class="projection-value success">+${results.growth_projections.new_staff}</span>
                        </div>
                        <div class="projection-item">
                            <span class="projection-label">Additional Programs:</span>
                            <span class="projection-value success">+${results.growth_projections.additional_programs}</span>
                        </div>
                        <div class="projection-item">
                            <span class="projection-label">Capacity Increase:</span>
                            <span class="projection-value success">+${results.growth_projections.capacity_increase}%</span>
                        </div>
                    </div>
                </div>
                
                <div class="financial-projections">
                    <h5>Financial Projections</h5>
                    <div class="financial-grid">
                        <div class="financial-item">
                            <span class="financial-label">Investment:</span>
                            <span class="financial-value">$${results.investment.toLocaleString()}</span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">Revenue Increase:</span>
                            <span class="financial-value success">$${results.financial_projections.revenue_increase.toLocaleString()}</span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">Net Impact:</span>
                            <span class="financial-value ${results.financial_projections.net_impact > 0 ? 'success' : 'warning'}">
                                $${results.financial_projections.net_impact.toLocaleString()}
                            </span>
                        </div>
                        <div class="financial-item">
                            <span class="financial-label">Break-even:</span>
                            <span class="financial-value">${results.financial_projections.break_even_months} months</span>
                        </div>
                    </div>
                </div>
                
                <div class="implementation-timeline">
                    <h5>Implementation Timeline</h5>
                    ${results.implementation_plan.map(phase => `
                        <div class="timeline-phase">
                            <div class="phase-header">
                                <strong>${phase.phase}</strong>
                                <span class="phase-duration">(${phase.duration})</span>
                            </div>
                            <div class="phase-activities">
                                ${phase.activities.map(activity => `<span class="activity-tag">${activity}</span>`).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <button class="btn-success" onclick="showModal('Expansion Implementation Plan', DigitalTwinScenarios.getDetailedExpansionReport())">
                    View Implementation Plan
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        this.lastExpansionResults = results;
    },
    
    // Get detailed automation report
    getDetailedAutomationReport() {
        if (!this.lastAutomationResults) return 'No automation results available.';
        
        const results = this.lastAutomationResults;
        return `
            <div class="detailed-report">
                <h4>Automation Implementation Roadmap</h4>
                
                <div class="timeline-section">
                    <h5>Implementation Timeline</h5>
                    ${results.timeline_milestones.map(milestone => `
                        <div class="timeline-item">
                            <strong>Month ${milestone.month}:</strong> ${milestone.milestone}
                        </div>
                    `).join('')}
                </div>
                
                <div class="cost-breakdown">
                    <h5>Cost-Benefit Analysis</h5>
                    <p><strong>Initial Investment:</strong> $${results.financial_impact.investment_required.toLocaleString()}</p>
                    <p><strong>Annual Labor Savings:</strong> $${results.financial_impact.annual_savings.toLocaleString()}</p>
                    <p><strong>Net 3-Year Value:</strong> $${((results.financial_impact.annual_savings * 3) - results.financial_impact.investment_required).toLocaleString()}</p>
                </div>
                
                <div class="next-steps">
                    <h5>Recommended Next Steps</h5>
                    <ol>
                        <li>Conduct detailed process mapping for targeted departments</li>
                        <li>Research and evaluate automation tools</li>
                        <li>Develop pilot implementation plan</li>
                        <li>Secure stakeholder buy-in and budget approval</li>
                        <li>Begin with highest-impact, lowest-risk processes</li>
                    </ol>
                </div>
            </div>
        `;
    },
    
    // Get detailed crisis report
    getDetailedCrisisReport() {
        if (!this.lastCrisisResults) return 'No crisis results available.';
        
        const results = this.lastCrisisResults;
        return `
            <div class="detailed-report">
                <h4>Crisis Response Action Plan</h4>
                
                <div class="immediate-actions">
                    <h5>Immediate Actions (0-30 days)</h5>
                    <ul>
                        <li>Activate crisis management team</li>
                        <li>Implement emergency expense controls</li>
                        <li>Communicate with key stakeholders</li>
                        <li>Launch emergency fundraising efforts</li>
                    </ul>
                </div>
                
                <div class="medium-term-actions">
                    <h5>Medium-term Actions (1-6 months)</h5>
                    <ul>
                        <li>Develop alternative funding sources</li>
                        <li>Restructure operations if necessary</li>
                        <li>Negotiate with vendors and partners</li>
                        <li>Explore collaboration opportunities</li>
                    </ul>
                </div>
                
                <div class="financial-overview">
                    <h5>Financial Survival Analysis</h5>
                    <p><strong>Current Reserves:</strong> $${results.impact_analysis.available_reserves.toLocaleString()}</p>
                    <p><strong>Monthly Burn Rate:</strong> $${results.impact_analysis.monthly_burn.toLocaleString()}</p>
                    <p><strong>Survival Timeline:</strong> ${results.survival_analysis.months_of_operation} months</p>
                </div>
            </div>
        `;
    },
    
    // Get detailed expansion report
    getDetailedExpansionReport() {
        if (!this.lastExpansionResults) return 'No expansion results available.';
        
        const results = this.lastExpansionResults;
        return `
            <div class="detailed-report">
                <h4>Detailed Expansion Implementation Plan</h4>
                
                <div class="resource-requirements">
                    <h5>Resource Requirements</h5>
                    <p><strong>Additional Staff:</strong> ${results.growth_projections.new_staff} positions</p>
                    <p><strong>New Programs:</strong> ${results.growth_projections.additional_programs} programs</p>
                    <p><strong>Capacity Increase:</strong> ${results.growth_projections.capacity_increase}%</p>
                </div>
                
                <div class="success-metrics">
                    <h5>Success Metrics</h5>
                    <ul>
                        <li>Revenue growth: $${results.financial_projections.revenue_increase.toLocaleString()} annually</li>
                        <li>Break-even achieved within ${results.financial_projections.break_even_months} months</li>
                        <li>Service capacity increased by ${results.growth_projections.capacity_increase}%</li>
                        <li>Market presence expanded in target areas</li>
                    </ul>
                </div>
                
                <div class="risk-mitigation">
                    <h5>Risk Mitigation Strategies</h5>
                    ${results.risk_factors.map(risk => `
                        <div class="risk-item">
                            <strong>${risk.risk}:</strong> ${risk.mitigation}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
};

// Global functions for scenario buttons
function runAutomationScenario() {
    DigitalTwinScenarios.runAutomationScenario();
}

function runCrisisScenario() {
    DigitalTwinScenarios.runCrisisScenario();
}

function runExpansionScenario() {
    DigitalTwinScenarios.runExpansionScenario();
}

window.DigitalTwinScenarios = DigitalTwinScenarios;