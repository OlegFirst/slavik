/**
 * Demo Mode Integration for Digital Twin
 * Allows organizations to try ISO scenarios without setup
 */

// Demo mode functionality (standalone without imports)
const DemoMode = {
    isDemoUser: () => sessionStorage.getItem('demoMode') === 'true',
    setDemoMode: (value) => sessionStorage.setItem('demoMode', value)
};

let currentScenario = null;

// Start demo mode
function startDemoMode() {
    // Check if already in demo
    if (DemoMode.isDemoUser()) {
        showDemoPanel();
    } else {
        // Show welcome dialog
        showDemoWelcome();
    }
}

// Show welcome dialog
function showDemoWelcome() {
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    modal.innerHTML = `
        <div class="demo-modal-content">
            <h2>Welcome to Digital Twin Demo</h2>
            <p>Experience the power of ISO 22301 scenarios and AI-driven optimization without any setup!</p>
            
            <div class="demo-features">
                <div class="feature-item">
                    <span class="feature-icon">📊</span>
                    <h4>Capacity Planning</h4>
                    <p>Optimize staff allocation and service levels</p>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">🔥</span>
                    <h4>BCM Scenarios</h4>
                    <p>Test business continuity and resilience</p>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">💰</span>
                    <h4>Grant Optimization</h4>
                    <p>Align funding with impact KPIs</p>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">📈</span>
                    <h4>Demand Management</h4>
                    <p>Handle service surges effectively</p>
                </div>
            </div>
            
            <div class="demo-actions">
                <button class="btn-primary" onclick="enterDemoMode()">Start Demo</button>
                <button class="btn-secondary" onclick="closeDemoModal()">Maybe Later</button>
            </div>
            
            <p class="demo-note">No registration required • Takes 5 minutes • Real simulation results</p>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Enter demo mode
function enterDemoMode() {
    demo.enableDemoMode();
    closeDemoModal();
    showDemoPanel();
}

// Show demo panel
function showDemoPanel() {
    // Hide regular sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Create or show demo section
    let demoSection = document.getElementById('demo-section');
    if (!demoSection) {
        demoSection = createDemoSection();
        document.querySelector('.main-content').appendChild(demoSection);
    }
    demoSection.classList.add('active');
    
    // Load demo dashboard
    loadDemoDashboard();
}

// Create demo section
function createDemoSection() {
    const section = document.createElement('section');
    section.id = 'demo-section';
    section.className = 'content-section';
    section.innerHTML = `
        <div class="demo-header">
            <h2>Demo Organization - ISO Scenario Simulator</h2>
            <button class="exit-demo" onclick="exitDemo()">Exit Demo</button>
        </div>
        
        <div class="demo-dashboard">
            <!-- Organization Overview -->
            <div class="demo-org-card">
                <h3>Demo Foundation Profile</h3>
                <div id="demo-org-info"></div>
            </div>
            
            <!-- Scenario Selector -->
            <div class="scenario-selector">
                <h3>Select Scenario to Simulate</h3>
                <div id="scenario-cards"></div>
            </div>
            
            <!-- Simulation Panel -->
            <div class="simulation-panel" id="simulation-panel" style="display:none;">
                <h3>Scenario Configuration</h3>
                <div id="scenario-params"></div>
                <button class="btn-run" onclick="runDemoSimulation()">Run Simulation</button>
            </div>
            
            <!-- Results Panel -->
            <div class="results-panel" id="results-panel" style="display:none;">
                <h3>Simulation Results</h3>
                <div id="simulation-results"></div>
                <canvas id="demo-chart"></canvas>
            </div>
        </div>
    `;
    return section;
}

// Load demo dashboard
function loadDemoDashboard() {
    const dashboard = demo.getDemoDashboard();
    
    // Display organization info
    document.getElementById('demo-org-info').innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <span class="label">Organization:</span>
                <span class="value">${dashboard.organization.name}</span>
            </div>
            <div class="info-item">
                <span class="label">Annual Budget:</span>
                <span class="value">$${(dashboard.organization.annual_budget/1000000).toFixed(1)}M</span>
            </div>
            <div class="info-item">
                <span class="label">Staff Size:</span>
                <span class="value">${dashboard.organization.size}</span>
            </div>
            <div class="info-item">
                <span class="label">Programs:</span>
                <span class="value">${dashboard.organization.programs.length}</span>
            </div>
            <div class="info-item">
                <span class="label">Beneficiaries:</span>
                <span class="value">${dashboard.metrics.total_beneficiaries.toLocaleString()}</span>
            </div>
            <div class="info-item">
                <span class="label">Health Score:</span>
                <span class="value">${dashboard.health_score}%</span>
            </div>
        </div>
    `;
    
    // Display scenario cards
    const scenarios = demo.getScenarios();
    const scenarioCards = Object.entries(scenarios).map(([key, scenario]) => `
        <div class="scenario-card" onclick="selectScenario('${key}')">
            <div class="scenario-icon">${scenario.icon}</div>
            <h4>${scenario.name}</h4>
            <p>${scenario.description}</p>
            <div class="scenario-metrics">
                <span class="metric">ROI: ${scenario.expectedResults.roi || 'N/A'}%</span>
                <span class="metric">Efficiency: +${scenario.expectedResults.efficiency_gain || 'N/A'}%</span>
            </div>
        </div>
    `).join('');
    
    document.getElementById('scenario-cards').innerHTML = scenarioCards;
}

// Select scenario
function selectScenario(scenarioKey) {
    currentScenario = scenarioKey;
    const scenarios = demo.getScenarios();
    const scenario = scenarios[scenarioKey];
    
    // Show simulation panel
    document.getElementById('simulation-panel').style.display = 'block';
    
    // Build parameter inputs
    const paramsHtml = Object.entries(scenario.params).map(([key, param]) => {
        if (param.options) {
            // Dropdown or checkboxes
            return `
                <div class="param-group">
                    <label>${key.replace(/_/g, ' ').toUpperCase()}</label>
                    <select id="param-${key}">
                        ${param.options.map(opt => 
                            `<option value="${opt}" ${opt === param.value ? 'selected' : ''}>${opt}</option>`
                        ).join('')}
                    </select>
                </div>
            `;
        } else {
            // Slider or input
            return `
                <div class="param-group">
                    <label>${key.replace(/_/g, ' ').toUpperCase()}</label>
                    <div class="param-input-group">
                        <input type="range" id="param-${key}" 
                               min="${param.min}" max="${param.max}" 
                               value="${param.value}" 
                               oninput="updateParamValue('${key}', this.value)">
                        <span class="param-value" id="value-${key}">${param.value} ${param.unit}</span>
                    </div>
                </div>
            `;
        }
    }).join('');
    
    document.getElementById('scenario-params').innerHTML = paramsHtml;
    
    // Scroll to simulation panel
    document.getElementById('simulation-panel').scrollIntoView({ behavior: 'smooth' });
}

// Update parameter value display
function updateParamValue(key, value) {
    const scenarios = demo.getScenarios();
    const param = scenarios[currentScenario].params[key];
    document.getElementById(`value-${key}`).textContent = `${value} ${param.unit}`;
}

// Run demo simulation
async function runDemoSimulation() {
    if (!currentScenario) return;
    
    // Collect parameters
    const scenarios = demo.getScenarios();
    const scenario = scenarios[currentScenario];
    const params = {};
    
    Object.keys(scenario.params).forEach(key => {
        const element = document.getElementById(`param-${key}`);
        if (element) {
            params[key] = { value: element.value };
        }
    });
    
    // Show loading
    document.getElementById('results-panel').style.display = 'block';
    document.getElementById('simulation-results').innerHTML = '<div class="loading">Running simulation...</div>';
    
    // Run simulation
    const results = await demo.runDemoSimulation(currentScenario, params);
    
    // Display results
    displayDemoResults(results);
}

// Display demo results
function displayDemoResults(results) {
    // Format results
    const resultsHtml = `
        <div class="results-header">
            <h4>${results.scenario}</h4>
            <span class="timestamp">${new Date(results.timestamp).toLocaleString()}</span>
        </div>
        
        <div class="results-metrics">
            ${Object.entries(results.results).map(([key, value]) => `
                <div class="result-metric">
                    <span class="metric-label">${key.replace(/_/g, ' ')}</span>
                    <span class="metric-value">${formatValue(value)}</span>
                </div>
            `).join('')}
        </div>
        
        <div class="recommendations">
            <h4>AI Recommendations</h4>
            ${results.recommendations.map(rec => `
                <div class="recommendation ${rec.priority.toLowerCase()}">
                    <span class="priority">${rec.priority}</span>
                    <div class="rec-content">
                        <strong>${rec.action}</strong>
                        <p>Impact: ${rec.impact}</p>
                        <p>Cost: ${rec.cost}</p>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="next-steps">
            <h4>Next Steps</h4>
            <ol>
                ${results.nextSteps.map(step => `<li>${step}</li>`).join('')}
            </ol>
        </div>
        
        <div class="demo-cta">
            <button class="btn-primary" onclick="scheduleConsultation()">Schedule Consultation</button>
            <button class="btn-secondary" onclick="requestCustomDemo()">Request Custom Demo</button>
        </div>
    `;
    
    document.getElementById('simulation-results').innerHTML = resultsHtml;
    
    // Create visualization chart
    createDemoChart(results);
    
    // Scroll to results
    document.getElementById('results-panel').scrollIntoView({ behavior: 'smooth' });
}

// Format value for display
function formatValue(value) {
    if (typeof value === 'number') {
        if (value > 1000) return `${(value/1000).toFixed(1)}K`;
        if (value < 1) return `${(value * 100).toFixed(1)}%`;
        return value.toFixed(1);
    }
    return value;
}

// Create demo chart
function createDemoChart(results) {
    const ctx = document.getElementById('demo-chart').getContext('2d');
    
    // Generate chart data based on results
    const labels = Object.keys(results.results).slice(0, 6);
    const data = labels.map(key => {
        const value = results.results[key];
        return typeof value === 'number' ? value : 0;
    });
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels.map(l => l.replace(/_/g, ' ')),
            datasets: [{
                label: 'Simulation Results',
                data: data,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Exit demo
function exitDemo() {
    const exitInfo = demo.exitDemoMode();
    
    // Show exit modal with CTAs
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    modal.innerHTML = `
        <div class="demo-modal-content">
            <h2>${exitInfo.message}</h2>
            <div class="exit-actions">
                ${exitInfo.actions.map(action => 
                    `<a href="${action.url}" class="btn-primary">${action.label}</a>`
                ).join('')}
            </div>
            <button class="btn-secondary" onclick="closeDemoModal()">Continue Exploring</button>
        </div>
    `;
    document.body.appendChild(modal);
}

// Close demo modal
function closeDemoModal() {
    const modal = document.querySelector('.demo-modal');
    if (modal) modal.remove();
}

// Schedule consultation
function scheduleConsultation() {
    window.open('https://calendly.com/seh-foundation/consultation', '_blank');
}

// Request custom demo
function requestCustomDemo() {
    window.location.href = '/contact?subject=custom-demo';
}

// Make functions global
window.startDemoMode = startDemoMode;
window.enterDemoMode = enterDemoMode;
window.closeDemoModal = closeDemoModal;
window.selectScenario = selectScenario;
window.updateParamValue = updateParamValue;
window.runDemoSimulation = runDemoSimulation;
window.exitDemo = exitDemo;
window.scheduleConsultation = scheduleConsultation;
window.requestCustomDemo = requestCustomDemo;