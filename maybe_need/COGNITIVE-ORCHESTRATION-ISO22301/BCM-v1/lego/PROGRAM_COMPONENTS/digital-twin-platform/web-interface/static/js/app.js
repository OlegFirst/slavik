/**
 * NASH 4.0 Digital Twin Web Interface
 * Main application JavaScript
 * 
 * Professional implementation following NASH standards
 */

// Application State
const DigitalTwinApp = {
    currentTwin: null,
    twins: new Map(),
    charts: {},
    network: null,
    
    // Initialize application
    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.initializeCharts();
        this.loadSystemStatus();
        this.addActivityLog('Digital Twin platform initialized');
        
        console.log('NASH Digital Twin Web Interface initialized');
    },
    
    // Navigation setup
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-btn');
        const sections = document.querySelectorAll('.content-section');
        
        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetSection = button.dataset.section;
                
                // Update nav buttons
                navButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update sections
                sections.forEach(section => section.classList.remove('active'));
                document.getElementById(targetSection).classList.add('active');
                
                // Load section specific data
                this.loadSectionData(targetSection);
            });
        });
    },
    
    // Event listeners setup
    setupEventListeners() {
        // Organization select
        const orgSelect = document.getElementById('organizationSelect');
        orgSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                this.loadOrganization(e.target.value);
            }
        });
        
        // Create twin form
        const createForm = document.getElementById('createTwinForm');
        createForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createDigitalTwin();
        });
        
        // Add department button
        document.getElementById('addDepartment').addEventListener('click', () => {
            this.addDepartmentField();
        });
        
        // Remove department buttons (delegated)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-dept')) {
                e.target.closest('.department-item').remove();
            }
        });
        
        // Visualization type change
        const vizSelect = document.getElementById('visualizationType');
        vizSelect.addEventListener('change', (e) => {
            this.updateVisualization(e.target.value);
        });
    },
    
    // Load system status
    async loadSystemStatus() {
        try {
            // Simulate API call to health endpoint
            const healthData = {
                status: 'active',
                twins: this.twins.size,
                uptime: Date.now(),
                memoryUsage: 11
            };
            
            document.getElementById('systemStatus').textContent = healthData.status;
            document.getElementById('twinCount').textContent = healthData.twins;
            
            this.addActivityLog(`System health check: ${healthData.status}`);
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.addActivityLog('System health check failed', 'error');
        }
    },
    
    // Create digital twin
    async createDigitalTwin() {
        this.showLoading(true);
        
        try {
            // Collect form data
            const formData = this.collectFormData();
            
            // Simulate API call to create twin
            const twinData = await this.simulateCreateTwin(formData);
            
            // Store twin data
            this.twins.set(twinData.twinId, twinData);
            
            // Update UI
            this.updateOrganizationSelect();
            this.loadOrganization(twinData.twinId);
            this.addActivityLog(`Digital twin created: ${twinData.name}`);
            
            // Switch to dashboard
            document.querySelector('[data-section="dashboard"]').click();
            
            // Show success message
            this.showNotification('Digital twin created successfully!', 'success');
            
        } catch (error) {
            console.error('Failed to create digital twin:', error);
            this.showNotification('Failed to create digital twin', 'error');
            this.addActivityLog('Twin creation failed', 'error');
        } finally {
            this.showLoading(false);
        }
    },
    
    // Collect form data
    collectFormData() {
        const form = document.getElementById('createTwinForm');
        const formData = new FormData(form);
        
        // Collect basic info
        const data = {
            organizationId: `org_${Date.now()}`,
            name: formData.get('organizationName'),
            mission: formData.get('organizationMission'),
            size: parseInt(formData.get('organizationSize')),
            annualBudget: parseInt(formData.get('annualBudget')),
            departments: [],
            technologyStack: []
        };
        
        // Collect departments
        const deptItems = document.querySelectorAll('.department-item');
        deptItems.forEach(item => {
            const name = item.querySelector('.dept-name').value;
            const headCount = parseInt(item.querySelector('.dept-headcount').value);
            const budget = parseInt(item.querySelector('.dept-budget').value);
            
            if (name && headCount && budget) {
                data.departments.push({
                    name,
                    headCount,
                    budget,
                    processes: ['general_operations']
                });
            }
        });
        
        // Collect technology stack
        const techCheckboxes = document.querySelectorAll('input[name="tech"]:checked');
        techCheckboxes.forEach(checkbox => {
            data.technologyStack.push(checkbox.value);
        });
        
        return data;
    },
    
    // Simulate creating twin (API call simulation)
    async simulateCreateTwin(data) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const twinId = `twin_${data.organizationId}_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`;
                
                // Calculate health metrics
                const healthMetrics = this.calculateHealthMetrics(data);
                
                const twinData = {
                    twinId,
                    ...data,
                    health: healthMetrics.health,
                    maturityLevel: healthMetrics.maturityLevel,
                    createdAt: new Date().toISOString(),
                    lastUpdated: new Date().toISOString()
                };
                
                resolve(twinData);
            }, 2000);
        });
    },
    
    // Calculate health metrics
    calculateHealthMetrics(data) {
        const techScore = data.technologyStack.length * 15;
        const sizeScore = Math.min(data.size * 2, 100);
        const budgetScore = Math.min(data.annualBudget / 10000, 100);
        const deptScore = data.departments.length * 20;
        
        const overallHealth = Math.min(Math.round((techScore + sizeScore + budgetScore + deptScore) / 4), 100);
        
        const health = {
            overallScore: overallHealth,
            financialHealth: Math.min(budgetScore + 20, 100),
            operationalHealth: Math.min(sizeScore + deptScore, 100),
            technologyHealth: Math.min(techScore + 30, 100),
            organizationalHealth: Math.min(deptScore + sizeScore / 2, 100)
        };
        
        let maturityLevel;
        if (overallHealth >= 80) maturityLevel = 'optimized';
        else if (overallHealth >= 60) maturityLevel = 'managed';
        else if (overallHealth >= 40) maturityLevel = 'defined';
        else maturityLevel = 'basic';
        
        return { health, maturityLevel };
    },
    
    // Load organization data
    loadOrganization(twinId) {
        const twin = this.twins.get(twinId);
        if (!twin) return;
        
        this.currentTwin = twin;
        
        // Update organization overview
        this.updateOrganizationOverview(twin);
        
        // Update health metrics
        this.updateHealthMetrics(twin.health);
        
        // Update visualization
        this.updateVisualization('network');
        
        // Update organization select
        document.getElementById('organizationSelect').value = twinId;
        
        this.addActivityLog(`Loaded organization: ${twin.name}`);
    },
    
    // Update organization overview
    updateOrganizationOverview(twin) {
        const container = document.getElementById('organizationOverview');
        
        const detailsHTML = `
            <div class="org-details">
                <div class="org-detail-item">
                    <div class="org-detail-label">Organization Name</div>
                    <div class="org-detail-value">${twin.name}</div>
                </div>
                <div class="org-detail-item">
                    <div class="org-detail-label">Size</div>
                    <div class="org-detail-value">${twin.size} employees</div>
                </div>
                <div class="org-detail-item">
                    <div class="org-detail-label">Annual Budget</div>
                    <div class="org-detail-value">$${twin.annualBudget.toLocaleString()}</div>
                </div>
                <div class="org-detail-item">
                    <div class="org-detail-label">Departments</div>
                    <div class="org-detail-value">${twin.departments.length}</div>
                </div>
                <div class="org-detail-item">
                    <div class="org-detail-label">Technology Stack</div>
                    <div class="org-detail-value">${twin.technologyStack.length} tools</div>
                </div>
                <div class="org-detail-item">
                    <div class="org-detail-label">Maturity Level</div>
                    <div class="org-detail-value">${twin.maturityLevel}</div>
                </div>
            </div>
            <div style="margin-top: 1rem; padding: 1rem; background: var(--background-color); border-radius: 0.375rem;">
                <div class="org-detail-label">Mission Statement</div>
                <p style="margin-top: 0.5rem; color: var(--text-primary);">${twin.mission}</p>
            </div>
        `;
        
        container.innerHTML = detailsHTML;
    },
    
    // Update health metrics display
    updateHealthMetrics(health) {
        const metrics = [
            { id: 'overallHealth', value: health.overallScore },
            { id: 'financialHealth', value: health.financialHealth },
            { id: 'operationalHealth', value: health.operationalHealth },
            { id: 'technologyHealth', value: health.technologyHealth }
        ];
        
        metrics.forEach(metric => {
            const valueElement = document.getElementById(metric.id);
            const barElement = document.getElementById(metric.id + 'Bar');
            
            if (valueElement && barElement) {
                valueElement.textContent = metric.value + '%';
                barElement.style.width = metric.value + '%';
                
                // Color coding
                if (metric.value >= 80) {
                    barElement.style.background = 'var(--success-color)';
                } else if (metric.value >= 60) {
                    barElement.style.background = 'var(--warning-color)';
                } else {
                    barElement.style.background = 'var(--error-color)';
                }
            }
        });
    },
    
    // Update organization select dropdown
    updateOrganizationSelect() {
        const select = document.getElementById('organizationSelect');
        
        // Clear existing options (except first)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add twin options
        this.twins.forEach((twin, twinId) => {
            const option = document.createElement('option');
            option.value = twinId;
            option.textContent = twin.name;
            select.appendChild(option);
        });
    },
    
    // Add department field
    addDepartmentField() {
        const container = document.getElementById('departmentsContainer');
        const departmentHTML = `
            <div class="department-item">
                <div class="form-row">
                    <input type="text" placeholder="Department Name" class="dept-name" required>
                    <input type="number" placeholder="Head Count" class="dept-headcount" min="1" required>
                    <input type="number" placeholder="Budget" class="dept-budget" min="1000" required>
                    <button type="button" class="remove-dept btn-secondary">Remove</button>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', departmentHTML);
    },
    
    // Load section specific data
    loadSectionData(section) {
        switch (section) {
            case 'visualization':
                if (this.currentTwin) {
                    this.updateVisualization('network');
                }
                break;
            case 'analytics':
                this.updateAnalyticsCharts();
                break;
            case 'scenarios':
                this.updateScenarioData();
                break;
            case 'impact-dashboard':
                this.loadImpactDashboard();
                break;
        }
    },
    
    // Add activity log entry
    addActivityLog(message, type = 'info') {
        const activityList = document.getElementById('activityList');
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        const activityHTML = `
            <div class="activity-item">
                <div class="activity-time">${timeString}</div>
                <div class="activity-text">${message}</div>
            </div>
        `;
        
        activityList.insertAdjacentHTML('afterbegin', activityHTML);
        
        // Keep only last 10 activities
        while (activityList.children.length > 10) {
            activityList.removeChild(activityList.lastChild);
        }
    },
    
    // Show loading overlay
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    },
    
    // Show notification
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 0.375rem;
            color: white;
            font-weight: 500;
            z-index: 1001;
            animation: slideInRight 0.3s ease;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success':
                notification.style.background = 'var(--success-color)';
                break;
            case 'error':
                notification.style.background = 'var(--error-color)';
                break;
            case 'warning':
                notification.style.background = 'var(--warning-color)';
                break;
            default:
                notification.style.background = 'var(--primary-color)';
        }
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    },
    
    // Initialize charts
    initializeCharts() {
        // Performance chart
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            this.charts.performance = new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Health Score',
                        data: [65, 70, 75, 78, 82, 85],
                        borderColor: 'rgb(37, 99, 235)',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        // Resource chart
        const resourceCtx = document.getElementById('resourceChart');
        if (resourceCtx) {
            this.charts.resource = new Chart(resourceCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Programs', 'Operations', 'Administration', 'Fundraising'],
                    datasets: [{
                        data: [45, 25, 15, 15],
                        backgroundColor: [
                            'rgb(37, 99, 235)',
                            'rgb(5, 150, 105)',
                            'rgb(217, 119, 6)',
                            'rgb(220, 38, 38)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    },
    
    // Update analytics charts
    updateAnalyticsCharts() {
        if (!this.currentTwin) return;
        
        // Update performance chart with twin data
        if (this.charts.performance) {
            const health = this.currentTwin.health;
            this.charts.performance.data.datasets[0].data = [
                health.overallScore - 20,
                health.overallScore - 10,
                health.overallScore - 5,
                health.overallScore,
                health.overallScore + 2,
                health.overallScore + 5
            ];
            this.charts.performance.update();
        }
        
        // Update insights
        this.updateInsights();
    },
    
    // Update insights
    updateInsights() {
        const insightsList = document.getElementById('insightsList');
        if (!this.currentTwin) return;
        
        const twin = this.currentTwin;
        const insights = [];
        
        // Generate insights based on twin data
        if (twin.health.technologyHealth < 70) {
            insights.push({
                type: 'Opportunity',
                text: 'Consider upgrading technology stack for improved efficiency',
                impact: 'High Impact'
            });
        }
        
        if (twin.health.operationalHealth < 80) {
            insights.push({
                type: 'Recommendation',
                text: 'Streamline operational processes to reduce overhead',
                impact: 'Medium Impact'
            });
        }
        
        if (twin.departments.length < 3) {
            insights.push({
                type: 'Growth',
                text: 'Organization structure suggests potential for departmental expansion',
                impact: 'Low Impact'
            });
        }
        
        // Update insights display
        const insightsHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-type">${insight.type}</div>
                <div class="insight-text">${insight.text}</div>
                <div class="insight-impact">${insight.impact}</div>
            </div>
        `).join('');
        
        insightsList.innerHTML = insightsHTML;
    },
    
    // Update scenario data
    updateScenarioData() {
        // Clear previous results
        document.getElementById('automationResults').innerHTML = '';
        document.getElementById('crisisResults').innerHTML = '';
        document.getElementById('expansionResults').innerHTML = '';
    },
    
    // Load Impact Dashboard
    loadImpactDashboard() {
        if (window.impactDashboard && this.currentTwin) {
            window.impactDashboard.initialize(this.currentTwin.id);
        } else {
            document.getElementById('impact-dashboard').innerHTML = `
                <div class="no-organization">
                    <h4>Impact Dashboard</h4>
                    <p>Выберите организацию для просмотра Impact Passport</p>
                </div>
            `;
        }
    }
};

// Quick action functions
function showCreateTwin() {
    document.querySelector('[data-section="create"]').click();
}

function generateReport() {
    if (!DigitalTwinApp.currentTwin) {
        DigitalTwinApp.showNotification('Please select an organization first', 'warning');
        return;
    }
    
    DigitalTwinApp.addActivityLog('Generating organization report...');
    DigitalTwinApp.showNotification('Report generation started', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        DigitalTwinApp.addActivityLog('Organization report generated');
        DigitalTwinApp.showNotification('Report generated successfully', 'success');
    }, 2000);
}

// Modal functions
function closeModal() {
    document.getElementById('resultsModal').style.display = 'none';
}

function showModal(title, content) {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('resultsModal').style.display = 'flex';
}

// CSS Animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    DigitalTwinApp.init();
});

// Export for use in other modules
window.DigitalTwinApp = DigitalTwinApp;

// Global functions for button onclick handlers
window.showCreateTwin = function() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.content-section');
    
    // Switch to create twin section
    navButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.section === 'create') {
            btn.classList.add('active');
        }
    });
    
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    const createSection = document.getElementById('create');
    if (createSection) {
        createSection.classList.add('active');
    }
};

window.runAutomationScenario = async function() {
    try {
        const response = await fetch('/api/impact/simulations/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                experiment: 'automation',
                params: {
                    investment: 50000,
                    timeline: 12,
                    efficiency_target: 0.85
                }
            })
        });
        
        const result = await response.json();
        showModal('Automation Scenario Results', formatResults(result));
    } catch (error) {
        console.error('Failed to run automation scenario:', error);
        showModal('Error', 'Failed to run automation scenario. Please try again.');
    }
};

window.runCrisisScenario = async function() {
    try {
        const response = await fetch('/api/impact/simulations/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                experiment: 'crisis',
                params: {
                    crisis_type: 'funding_loss',
                    severity: 0.3,
                    duration_months: 6
                }
            })
        });
        
        const result = await response.json();
        showModal('Crisis Scenario Results', formatResults(result));
    } catch (error) {
        console.error('Failed to run crisis scenario:', error);
        showModal('Error', 'Failed to run crisis scenario. Please try again.');
    }
};

window.runExpansionScenario = async function() {
    try {
        const response = await fetch('/api/impact/simulations/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                experiment: 'expansion',
                params: {
                    expansion_type: 'service_expansion',
                    budget: 100000,
                    target_regions: 3
                }
            })
        });
        
        const result = await response.json();
        showModal('Expansion Scenario Results', formatResults(result));
    } catch (error) {
        console.error('Failed to run expansion scenario:', error);
        showModal('Error', 'Failed to run expansion scenario. Please try again.');
    }
};

window.generateReport = async function() {
    try {
        const reportData = {
            organization: DigitalTwinApp.currentTwin,
            generated_at: new Date().toISOString(),
            metrics: {
                overall_health: document.getElementById('overallHealth').textContent,
                financial_health: document.getElementById('financialHealth').textContent,
                operational_health: document.getElementById('operationalHealth').textContent,
                technology_health: document.getElementById('technologyHealth').textContent
            }
        };
        
        showModal('Report Generated', `
            <h3>Digital Twin Report</h3>
            <p>Generated: ${new Date().toLocaleString()}</p>
            <h4>Health Metrics</h4>
            <ul>
                <li>Overall Health: ${reportData.metrics.overall_health}</li>
                <li>Financial Health: ${reportData.metrics.financial_health}</li>
                <li>Operational Health: ${reportData.metrics.operational_health}</li>
                <li>Technology Health: ${reportData.metrics.technology_health}</li>
            </ul>
        `);
    } catch (error) {
        console.error('Failed to generate report:', error);
        showModal('Error', 'Failed to generate report. Please try again.');
    }
};

window.showModal = function(title, content) {
    const modal = document.getElementById('resultsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    if (modal && modalTitle && modalBody) {
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modal.style.display = 'block';
    }
};

window.closeModal = function() {
    const modal = document.getElementById('resultsModal');
    if (modal) {
        modal.style.display = 'none';
    }
};

window.formatResults = function(result) {
    if (result.error) {
        return `<p class="error">Error: ${result.error}</p>`;
    }
    
    return `
        <div class="results-content">
            ${result.best ? `
                <h4>Optimal Solution</h4>
                <pre>${JSON.stringify(result.best, null, 2)}</pre>
            ` : ''}
            ${result.explain ? `
                <h4>Explanation</h4>
                <p>${result.explain}</p>
            ` : ''}
        </div>
    `;
};

window.startDemoMode = function() {
    // Full showcase demo implementation with all 30 functions
    const showcaseOrg = {
        name: 'Hope Foundation International',
        nameRu: 'Международный Фонд Надежды',
        type: 'International Foundation',
        founded: 2015,
        mission: 'Empowering communities through education, healthcare, and sustainable development',
        budget: 75000000,
        staff: 350,
        volunteers: 1500,
        programs: [
            { name: 'Digital Education for All', budget: 18000000, beneficiaries: 500000 },
            { name: 'Community Health Initiative', budget: 22000000, beneficiaries: 750000 },
            { name: 'Women Entrepreneurship', budget: 12000000, beneficiaries: 100000 },
            { name: 'Climate Action', budget: 8000000, beneficiaries: 250000 },
            { name: 'Emergency Response', budget: 6000000, beneficiaries: 100000 }
        ],
        branches: ['New York', 'London', 'Berlin', 'Tokyo', 'Moscow', 'São Paulo'],
        metrics: {
            overall: 91,
            financial: 88,
            operational: 85,
            technology: 93,
            impact: 94,
            sustainability: 87
        }
    };
    
    // Update Organization Overview
    document.getElementById('organizationOverview').innerHTML = `
        <div style="padding: 10px;">
            <h3 style="margin: 0 0 10px 0; color: #667eea;">${showcaseOrg.name}</h3>
            <p style="font-size: 12px; color: #666; margin: 5px 0;"><i>${showcaseOrg.nameRu}</i></p>
            <p style="font-size: 13px; margin: 8px 0;">${showcaseOrg.mission}</p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
                    <strong>Budget:</strong><br>
                    $${(showcaseOrg.budget/1000000).toFixed(0)}M annually
                </div>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
                    <strong>Team:</strong><br>
                    ${showcaseOrg.staff} staff + ${showcaseOrg.volunteers} volunteers
                </div>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
                    <strong>Founded:</strong><br>
                    ${showcaseOrg.founded} (${new Date().getFullYear() - showcaseOrg.founded} years)
                </div>
                <div style="background: #f8f9fa; padding: 8px; border-radius: 4px;">
                    <strong>Global Reach:</strong><br>
                    ${showcaseOrg.branches.length} offices worldwide
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <strong>Active Programs (${showcaseOrg.programs.length}):</strong>
                <ul style="margin: 5px 0; padding-left: 20px; font-size: 12px;">
                    ${showcaseOrg.programs.map(p => 
                        `<li>${p.name}<br>
                        <span style="color: #666;">$${(p.budget/1000000).toFixed(1)}M | ${(p.beneficiaries/1000).toFixed(0)}K beneficiaries</span></li>`
                    ).join('')}
                </ul>
            </div>
            
            <div style="margin-top: 15px; padding: 10px; background: linear-gradient(135deg, #667eea15, #764ba215); border-radius: 4px;">
                <strong>Available Experiments: 30</strong><br>
                <span style="font-size: 11px; color: #666;">
                    4 External Adapters | 22 Digital Twin Scenarios | 4 Internal Engines
                </span>
            </div>
        </div>
    `;
    
    // Update all metrics with animation
    const updateMetric = (id, barId, value) => {
        document.getElementById(id).textContent = value + '%';
        const bar = document.getElementById(barId);
        bar.style.width = '0%';
        bar.style.transition = 'width 1s ease-out';
        setTimeout(() => {
            bar.style.width = value + '%';
            // Color based on value
            if (value >= 90) bar.style.backgroundColor = '#10b981';
            else if (value >= 75) bar.style.backgroundColor = '#3b82f6';
            else if (value >= 60) bar.style.backgroundColor = '#f59e0b';
            else bar.style.backgroundColor = '#ef4444';
        }, 100);
    };
    
    updateMetric('overallHealth', 'overallHealthBar', showcaseOrg.metrics.overall);
    updateMetric('financialHealth', 'financialHealthBar', showcaseOrg.metrics.financial);
    updateMetric('operationalHealth', 'operationalHealthBar', showcaseOrg.metrics.operational);
    updateMetric('technologyHealth', 'technologyHealthBar', showcaseOrg.metrics.technology);
    
    // Add activity logs for demo
    DigitalTwinApp.addActivityLog('Demo mode activated: Hope Foundation International loaded');
    DigitalTwinApp.addActivityLog('All 30 experiments ready for demonstration');
    DigitalTwinApp.addActivityLog('5 active programs with 1.7M total beneficiaries');
    DigitalTwinApp.addActivityLog('Global presence: 6 offices across continents');
    
    // Update organization selector
    const selector = document.getElementById('organizationSelect');
    if (selector) {
        selector.innerHTML = `
            <option value="showcase" selected>${showcaseOrg.name}</option>
            <option value="">Create new organization...</option>
        `;
    }
    
    // Store in app state
    DigitalTwinApp.currentTwin = showcaseOrg;
    
    // Show welcome modal with capabilities
    showModal('Showcase Demo Activated', `
        <div style="max-height: 400px; overflow-y: auto;">
            <h3 style="color: #667eea; margin-top: 0;">${showcaseOrg.name}</h3>
            <p style="color: #666; font-style: italic;">${showcaseOrg.nameRu}</p>
            
            <p><strong>Organization loaded with full data for demonstrating all 30 capabilities:</strong></p>
            
            <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
                <h4 style="margin: 5px 0;">External SEH Adapters (4):</h4>
                <ul style="font-size: 13px; margin: 5px 0;">
                    <li>SimPy - Queue optimization for donor services</li>
                    <li>Mesa - Agent-based donor behavior modeling</li>
                    <li>EpiNow2 - Aid demand forecasting</li>
                    <li>AnyLogic - Hybrid organizational simulation with ML/AI</li>
                </ul>
            </div>
            
            <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
                <h4 style="margin: 5px 0;">Digital Twin Scenarios (22):</h4>
                <p style="font-size: 13px; margin: 5px 0;">
                    Process automation, Crisis management, Expansion planning, Digital transformation,
                    AI implementation, Cybersecurity, Compliance, Staff training, Process optimization,
                    Stakeholder engagement, Community outreach, Resource allocation, Capacity building,
                    M&E systems, Knowledge management, Innovation R&D, Partnership development,
                    Sustainability planning, Grant management, Funding diversification, Impact assessment
                </p>
            </div>
            
            <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
                <h4 style="margin: 5px 0;">Internal Optimization Engines (4):</h4>
                <ul style="font-size: 13px; margin: 5px 0;">
                    <li>Theory of Change optimizer</li>
                    <li>Capacity sweep analyzer</li>
                    <li>BCM outage simulator</li>
                    <li>Budget optimization engine</li>
                </ul>
            </div>
            
            <p style="margin-top: 15px; padding: 10px; background: linear-gradient(135deg, #667eea15, #764ba215); border-radius: 4px;">
                <strong>Ready to demonstrate:</strong> Click any Quick Action button or navigate to Scenarios section to test all capabilities with pre-configured optimal parameters.
            </p>
        </div>
    `);
};

// ========== AI Organs Monitor Functions ==========

// Mock AI organs data
const AI_ORGANS = {
    governance_brain: { name: 'Governance Brain', icon: '🧠', status: 'active' },
    emergency_response: { name: 'Emergency Response', icon: '🚨', status: 'active' },
    impact_oracle: { name: 'Impact Oracle', icon: '🔮', status: 'active' },
    scenario_creator: { name: 'Scenario Creator', icon: '📝', status: 'active' },
    risk_advisor: { name: 'Risk Advisor', icon: '⚡', status: 'active' },
    compliance_guardian: { name: 'Compliance Guardian', icon: '🛡️', status: 'active' },
    performance_analyst: { name: 'Performance Analyst', icon: '📊', status: 'active' },
    learning_coach: { name: 'Learning Coach', icon: '🎓', status: 'active' },
    plan_generator: { name: 'Plan Generator', icon: '📋', status: 'active' },
    lifecycle_monitor: { name: 'Lifecycle Monitor', icon: '💓', status: 'active' }
};

// AI Organs control functions
window.refreshAIStatus = async function() {
    try {
        const response = await fetch('/api/health');
        const healthData = await response.json();

        const statusContainer = document.getElementById('aiOrgansStatus');
        if (statusContainer) {
            const organsHTML = Object.entries(AI_ORGANS).map(([key, organ]) => {
                const confidence = Math.floor(Math.random() * 30) + 70;
                const responseTime = Math.floor(Math.random() * 800) + 200;
                const lastRun = new Date(Date.now() - Math.random() * 3600000).toLocaleTimeString();

                return `
                    <div class="ai-organ-item">
                        <div class="ai-organ-header">
                            <div>
                                <span class="ai-organ-icon">${organ.icon}</span>
                                <span class="ai-organ-name">${organ.name}</span>
                            </div>
                            <span class="ai-organ-status ${organ.status}">${organ.status}</span>
                        </div>
                        <div class="ai-organ-metrics">
                            <div class="ai-metric">
                                <span class="ai-metric-value">${confidence}%</span>
                                <span class="ai-metric-label">Confidence</span>
                            </div>
                            <div class="ai-metric">
                                <span class="ai-metric-value">${responseTime}ms</span>
                                <span class="ai-metric-label">Response</span>
                            </div>
                        </div>
                        <div style="font-size: 0.75rem; color: #666; margin-top: 0.5rem;">
                            Last run: ${lastRun}
                        </div>
                    </div>
                `;
            }).join('');

            statusContainer.innerHTML = organsHTML;
        }

        // Update last update time
        document.getElementById('lastAIUpdate').textContent = new Date().toLocaleTimeString();

        // Update system health
        updateSystemHealth(healthData);

        // Update AI insights
        updateAIInsights();

    } catch (error) {
        console.error('Failed to refresh AI status:', error);
        document.getElementById('aiOrgansStatus').innerHTML =
            '<div class="error">Failed to load AI organs status</div>';
    }
};

window.updateSystemHealth = function(healthData) {
    const healthContainer = document.getElementById('systemHealthMetrics');
    if (!healthContainer) return;

    const metrics = [
        { name: 'CPU Usage', value: Math.floor(Math.random() * 30) + 20, unit: '%' },
        { name: 'Memory', value: Math.floor(Math.random() * 40) + 30, unit: '%' },
        { name: 'API Calls', value: Math.floor(Math.random() * 5000) + 1000, unit: '/hr' },
        { name: 'Uptime', value: Math.floor(healthData.uptime / 3600), unit: 'hrs' },
        { name: 'Response Time', value: Math.floor(Math.random() * 200) + 50, unit: 'ms' },
        { name: 'Success Rate', value: 99.5 + Math.random() * 0.5, unit: '%' }
    ];

    const metricsHTML = metrics.map(metric => {
        let statusClass = 'good';
        if (metric.name === 'CPU Usage' && metric.value > 70) statusClass = 'warning';
        if (metric.name === 'Memory' && metric.value > 80) statusClass = 'warning';
        if (metric.name === 'Response Time' && metric.value > 200) statusClass = 'warning';

        return `
            <div class="health-metric">
                <span class="health-metric-value ${statusClass}">${metric.value}${metric.unit}</span>
                <span class="health-metric-label">${metric.name}</span>
            </div>
        `;
    }).join('');

    healthContainer.innerHTML = metricsHTML;
};

window.updateAIInsights = function() {
    const insightsContainer = document.getElementById('aiInsightsContainer');
    if (!insightsContainer) return;

    const sampleInsights = [
        {
            organ: 'Risk Advisor',
            text: 'Supply chain vulnerabilities detected. Recommend diversifying vendor base.',
            confidence: 87,
            priority: 'high'
        },
        {
            organ: 'Compliance Guardian',
            text: 'ISO 22301 compliance at 91%. Minor documentation gaps identified.',
            confidence: 94,
            priority: 'medium'
        },
        {
            organ: 'Performance Analyst',
            text: 'KPI optimization opportunities in donor engagement processes.',
            confidence: 73,
            priority: 'medium'
        },
        {
            organ: 'Impact Oracle',
            text: 'Predictive model indicates 23% improvement in program effectiveness.',
            confidence: 81,
            priority: 'high'
        }
    ];

    const insightsHTML = sampleInsights.map(insight => `
        <div class="insight-card">
            <div class="insight-header">
                <span class="insight-organ">${insight.organ}</span>
                <span class="insight-confidence">${insight.confidence}% confidence</span>
            </div>
            <div class="insight-text">${insight.text}</div>
            <span class="insight-priority ${insight.priority}">${insight.priority} priority</span>
        </div>
    `).join('');

    insightsContainer.innerHTML = insightsHTML;
};

window.updateAnalysisTimeline = function() {
    const timelineContainer = document.getElementById('analysisTimeline');
    if (!timelineContainer) return;

    const recentAnalyses = [
        {
            time: '14:23',
            title: 'Full AI Analysis Completed',
            description: 'All 10 AI organs processed organizational data'
        },
        {
            time: '14:15',
            title: 'Risk Assessment Updated',
            description: 'Risk Advisor identified new supply chain risks'
        },
        {
            time: '14:08',
            title: 'Compliance Check Passed',
            description: 'Compliance Guardian verified ISO 22301 status'
        },
        {
            time: '13:55',
            title: 'Performance Analysis',
            description: 'Performance Analyst generated optimization recommendations'
        },
        {
            time: '13:42',
            title: 'Impact Predictions Generated',
            description: 'Impact Oracle updated forecast models'
        }
    ];

    const timelineHTML = recentAnalyses.map(item => `
        <div class="timeline-item">
            <div class="timeline-time">${item.time}</div>
            <div class="timeline-content">
                <div class="timeline-title">${item.title}</div>
                <div class="timeline-description">${item.description}</div>
            </div>
        </div>
    `).join('');

    timelineContainer.innerHTML = timelineHTML;
};

// AI Control Functions
window.runFullAIAnalysis = async function() {
    showLoadingModal('Running Full AI Analysis', 'All 10 AI organs are analyzing the organization...');

    try {
        // Simulate API call to trigger all AI organs
        const response = await fetch('/api/digital-twins/123/ai-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ analysis_type: 'comprehensive' })
        });

        setTimeout(() => {
            closeModal();
            refreshAIStatus();
            updateAnalysisTimeline();
            showModal('AI Analysis Complete', `
                <div class="success">
                    <h3>✅ Full AI Analysis Completed</h3>
                    <p>All 10 AI organs have successfully analyzed the organization.</p>

                    <div style="margin: 15px 0; padding: 10px; background: #f0f9ff; border-radius: 4px;">
                        <h4>Analysis Summary:</h4>
                        <ul>
                            <li>🧠 Governance Brain: Strategic alignment recommendations</li>
                            <li>⚡ Risk Advisor: Supply chain vulnerabilities identified</li>
                            <li>🛡️ Compliance Guardian: 91% ISO 22301 compliance</li>
                            <li>📊 Performance Analyst: KPI optimization opportunities</li>
                            <li>🔮 Impact Oracle: 23% effectiveness improvement predicted</li>
                            <li>+ 5 more organs completed analysis</li>
                        </ul>
                    </div>

                    <p><strong>Confidence Level:</strong> 87% (High)</p>
                    <p><strong>Next Recommended Action:</strong> Review risk mitigation strategies</p>
                </div>
            `);
        }, 3000);

    } catch (error) {
        closeModal();
        showModal('Analysis Error', 'Failed to complete AI analysis. Please try again.');
    }
};

window.runRiskAnalysis = async function() {
    showLoadingModal('Risk Analysis', 'Risk Advisor is analyzing potential threats...');

    setTimeout(() => {
        closeModal();
        showModal('Risk Analysis Complete', `
            <div class="risk-results">
                <h3>⚠️ Risk Assessment Results</h3>

                <div style="margin: 15px 0; padding: 10px; background: #fff7ed; border-left: 4px solid #f59e0b; border-radius: 4px;">
                    <h4>High Priority Risks:</h4>
                    <ul>
                        <li><strong>Supply Chain Disruption</strong> - Probability: 35%, Impact: High</li>
                        <li><strong>Cybersecurity Threats</strong> - Probability: 28%, Impact: Medium</li>
                        <li><strong>Regulatory Changes</strong> - Probability: 45%, Impact: Medium</li>
                    </ul>
                </div>

                <div style="margin: 15px 0; padding: 10px; background: #f0f9ff; border-radius: 4px;">
                    <h4>Risk Mitigation Recommendations:</h4>
                    <ol>
                        <li>Diversify vendor base to reduce single points of failure</li>
                        <li>Implement advanced threat detection systems</li>
                        <li>Establish regulatory monitoring framework</li>
                    </ol>
                </div>

                <p><strong>Overall Risk Score:</strong> 45/100 (Moderate)</p>
                <p><strong>FAIR Analysis:</strong> Monte Carlo simulation completed</p>
            </div>
        `);
    }, 2000);
};

window.runComplianceCheck = async function() {
    showLoadingModal('Compliance Check', 'Compliance Guardian is verifying regulatory status...');

    setTimeout(() => {
        closeModal();
        showModal('Compliance Check Complete', `
            <div class="compliance-results">
                <h3>✅ Compliance Assessment</h3>

                <div style="margin: 15px 0; padding: 10px; background: #f0fdf4; border-left: 4px solid #10b981; border-radius: 4px;">
                    <h4>ISO 22301 Compliance: 91%</h4>
                    <ul>
                        <li>✅ Business Impact Analysis: Complete</li>
                        <li>✅ Risk Assessment: Up to date</li>
                        <li>✅ Business Continuity Plans: Current</li>
                        <li>⚠️ Training Records: Minor gaps identified</li>
                        <li>✅ Testing & Exercises: On schedule</li>
                    </ul>
                </div>

                <div style="margin: 15px 0; padding: 10px; background: #fefce8; border-radius: 4px;">
                    <h4>Improvement Areas:</h4>
                    <ol>
                        <li>Update staff training documentation</li>
                        <li>Complete Q4 business continuity exercise</li>
                        <li>Review third-party vendor compliance</li>
                    </ol>
                </div>

                <p><strong>Next Audit:</strong> Scheduled for Q1 2026</p>
                <p><strong>Certification Status:</strong> Active (expires Dec 2025)</p>
            </div>
        `);
    }, 2500);
};

window.generatePredictions = async function() {
    showLoadingModal('Generating Predictions', 'Impact Oracle is analyzing trends and patterns...');

    setTimeout(() => {
        closeModal();
        showModal('Predictions Generated', `
            <div class="predictions-results">
                <h3>🔮 AI Predictions & Forecasting</h3>

                <div style="margin: 15px 0; padding: 10px; background: #f0f9ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
                    <h4>6-Month Forecast:</h4>
                    <ul>
                        <li><strong>Program Effectiveness:</strong> +23% improvement expected</li>
                        <li><strong>Donor Engagement:</strong> +15% increase in retention</li>
                        <li><strong>Operational Efficiency:</strong> +18% cost reduction</li>
                        <li><strong>Digital Transformation:</strong> 85% completion by Q2</li>
                    </ul>
                </div>

                <div style="margin: 15px 0; padding: 10px; background: #fef3c7; border-radius: 4px;">
                    <h4>Scenario Probabilities:</h4>
                    <ul>
                        <li>Market Expansion Opportunity: 78% probability</li>
                        <li>Technology Upgrade Need: 65% probability</li>
                        <li>Partnership Opportunity: 45% probability</li>
                        <li>Regulatory Change Impact: 32% probability</li>
                    </ul>
                </div>

                <div style="margin: 15px 0; padding: 10px; background: #f0fdf4; border-radius: 4px;">
                    <h4>Recommended Actions:</h4>
                    <ol>
                        <li>Prepare for Q2 technology infrastructure upgrade</li>
                        <li>Initiate market research for expansion planning</li>
                        <li>Strengthen stakeholder partnership framework</li>
                    </ol>
                </div>

                <p><strong>Prediction Confidence:</strong> 84% (Very High)</p>
                <p><strong>Data Points Analyzed:</strong> 15,743</p>
            </div>
        `);
    }, 3500);
};

// Helper function for loading modal
window.showLoadingModal = function(title, message) {
    showModal(title, `
        <div style="text-align: center; padding: 20px;">
            <div class="loading-spinner" style="
                width: 40px;
                height: 40px;
                border: 4px solid #f3f4f6;
                border-top: 4px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            "></div>
            <p>${message}</p>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    `);
};

// Initialize AI Organs monitoring when section is loaded
DigitalTwinApp.loadSectionData = function(sectionName) {
    if (sectionName === 'ai-organs') {
        refreshAIStatus();
        updateAnalysisTimeline();

        // Initialize AI performance chart
        const canvas = document.getElementById('aiPerformanceChart');
        if (canvas && !this.charts.aiPerformance) {
            const ctx = canvas.getContext('2d');
            this.charts.aiPerformance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['12:00', '12:30', '13:00', '13:30', '14:00', '14:30'],
                    datasets: [{
                        label: 'AI Response Time (ms)',
                        data: [250, 320, 280, 310, 290, 270],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Confidence Score (%)',
                        data: [85, 87, 89, 86, 88, 90],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    }
                }
            });
        }
    }
};

// AI Consultant Functions
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');

    // Clear input
    input.value = '';

    // Show typing indicator
    showTypingIndicator();

    try {
        // Send to AI consultant API
        const response = await fetch('/api/ai-consultant/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                context: {
                    organizationId: currentOrganizationId || 1,
                    sessionId: sessionStorage.getItem('chatSessionId') || generateSessionId()
                }
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.success && data.response) {
            // Add AI response to chat
            addMessageToChat(data.response.text, 'ai');

            // Update insights if available
            if (data.response.insights) {
                updateAIInsights(data.response.insights);
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        addMessageToChat('Извините, произошла ошибка при отправке сообщения. Попробуйте еще раз.', 'ai');
    }
}

function addMessageToChat(text, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = type === 'user' ? 'user-message' : 'ai-message';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';

    const content = document.createElement('div');
    content.className = 'message-content';

    // Convert markdown-like formatting to HTML
    const formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/- (.*?)(?=<br>|$)/g, '<li>$1</li>');

    // Wrap list items in ul if present
    if (formattedText.includes('<li>')) {
        content.innerHTML = formattedText.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
    } else {
        content.innerHTML = `<p>${formattedText}</p>`;
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'ai-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function askQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendMessage();
}

function updateAIInsights(insights) {
    if (insights.riskLevel !== undefined) {
        document.getElementById('riskLevel').style.width = insights.riskLevel + '%';
        document.getElementById('riskPercent').textContent = insights.riskLevel + '%';
    }

    if (insights.priority) {
        document.getElementById('currentFocus').textContent = insights.priority;
    }

    if (insights.recommendation) {
        document.getElementById('aiRecommendation').textContent = insights.recommendation;
    }

    if (insights.nextSteps) {
        document.getElementById('monthlyForecast').textContent = insights.nextSteps;
    }
}

function generateSessionId() {
    const sessionId = 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('chatSessionId', sessionId);
    return sessionId;
}