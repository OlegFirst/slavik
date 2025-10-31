/**
 * NASH 4.0 Digital Twin Visualization Module
 * Interactive organization structure visualization
 */

const DigitalTwinVisualization = {
    network: null,
    nodes: null,
    edges: null,
    
    // Initialize visualization
    init() {
        this.setupVisualization();
    },
    
    // Setup visualization container
    setupVisualization() {
        const container = document.getElementById('networkVisualization');
        if (!container) return;
        
        // Initialize empty network
        this.nodes = new vis.DataSet([]);
        this.edges = new vis.DataSet([]);
        
        const data = {
            nodes: this.nodes,
            edges: this.edges
        };
        
        const options = {
            nodes: {
                shape: 'box',
                margin: 10,
                font: {
                    size: 14,
                    color: '#0f172a'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: {
                    color: '#64748b',
                    highlight: '#2563eb'
                },
                arrows: {
                    to: {
                        enabled: true,
                        scaleFactor: 0.5
                    }
                },
                smooth: {
                    type: 'cubicBezier',
                    forceDirection: 'vertical',
                    roundness: 0.4
                }
            },
            layout: {
                hierarchical: {
                    direction: 'UD',
                    sortMethod: 'directed',
                    nodeSpacing: 200,
                    levelSeparation: 150
                }
            },
            physics: {
                enabled: false
            },
            interaction: {
                hover: true,
                selectConnectedEdges: false
            }
        };
        
        this.network = new vis.Network(container, data, options);
        
        // Event handlers
        this.network.on('select', (params) => {
            if (params.nodes.length > 0) {
                this.onNodeSelect(params.nodes[0]);
            }
        });
    },
    
    // Update visualization based on type
    updateVisualization(type) {
        if (!DigitalTwinApp.currentTwin) {
            this.clearVisualization();
            return;
        }
        
        switch (type) {
            case 'network':
                this.createNetworkDiagram();
                break;
            case 'hierarchy':
                this.createHierarchyDiagram();
                break;
            case 'process':
                this.createProcessDiagram();
                break;
        }
    },
    
    // Create network diagram
    createNetworkDiagram() {
        const twin = DigitalTwinApp.currentTwin;
        const nodes = [];
        const edges = [];
        
        // Organization root node
        nodes.push({
            id: 'org',
            label: twin.name,
            color: {
                background: '#2563eb',
                border: '#1d4ed8'
            },
            font: { color: 'white' },
            level: 0
        });
        
        // Department nodes
        twin.departments.forEach((dept, index) => {
            const deptId = `dept_${index}`;
            nodes.push({
                id: deptId,
                label: `${dept.name}\n${dept.headCount} people\n$${dept.budget.toLocaleString()}`,
                color: {
                    background: '#059669',
                    border: '#047857'
                },
                font: { color: 'white' },
                level: 1
            });
            
            edges.push({
                from: 'org',
                to: deptId
            });
            
            // Process nodes for each department
            if (dept.processes) {
                dept.processes.forEach((process, pIndex) => {
                    const processId = `process_${index}_${pIndex}`;
                    nodes.push({
                        id: processId,
                        label: process.replace('_', ' ').toUpperCase(),
                        color: {
                            background: '#d97706',
                            border: '#b45309'
                        },
                        font: { color: 'white' },
                        level: 2,
                        size: 25
                    });
                    
                    edges.push({
                        from: deptId,
                        to: processId
                    });
                });
            }
        });
        
        // Technology nodes
        if (twin.technologyStack && twin.technologyStack.length > 0) {
            nodes.push({
                id: 'tech',
                label: 'Technology\nInfrastructure',
                color: {
                    background: '#7c3aed',
                    border: '#6d28d9'
                },
                font: { color: 'white' },
                level: 1
            });
            
            edges.push({
                from: 'org',
                to: 'tech'
            });
            
            twin.technologyStack.forEach((tech, index) => {
                const techId = `tech_${index}`;
                nodes.push({
                    id: techId,
                    label: tech,
                    color: {
                        background: '#db2777',
                        border: '#be185d'
                    },
                    font: { color: 'white' },
                    level: 2,
                    size: 20
                });
                
                edges.push({
                    from: 'tech',
                    to: techId
                });
            });
        }
        
        this.updateNodes(nodes, edges);
    },
    
    // Create hierarchy diagram
    createHierarchyDiagram() {
        const twin = DigitalTwinApp.currentTwin;
        const nodes = [];
        const edges = [];
        
        // CEO/Director level
        nodes.push({
            id: 'ceo',
            label: 'Executive Director',
            color: {
                background: '#dc2626',
                border: '#b91c1c'
            },
            font: { color: 'white' },
            level: 0
        });
        
        // Department heads
        twin.departments.forEach((dept, index) => {
            const headId = `head_${index}`;
            nodes.push({
                id: headId,
                label: `${dept.name}\nDirector`,
                color: {
                    background: '#2563eb',
                    border: '#1d4ed8'
                },
                font: { color: 'white' },
                level: 1
            });
            
            edges.push({
                from: 'ceo',
                to: headId
            });
            
            // Staff members
            const staffCount = Math.min(dept.headCount - 1, 5); // Show max 5 staff
            for (let i = 0; i < staffCount; i++) {
                const staffId = `staff_${index}_${i}`;
                nodes.push({
                    id: staffId,
                    label: `Staff Member\n${i + 1}`,
                    color: {
                        background: '#059669',
                        border: '#047857'
                    },
                    font: { color: 'white' },
                    level: 2,
                    size: 25
                });
                
                edges.push({
                    from: headId,
                    to: staffId
                });
            }
            
            if (dept.headCount > 6) {
                const moreId = `more_${index}`;
                nodes.push({
                    id: moreId,
                    label: `+${dept.headCount - 6} more`,
                    color: {
                        background: '#64748b',
                        border: '#475569'
                    },
                    font: { color: 'white' },
                    level: 2,
                    size: 20
                });
                
                edges.push({
                    from: headId,
                    to: moreId
                });
            }
        });
        
        this.updateNodes(nodes, edges);
    },
    
    // Create process flow diagram
    createProcessDiagram() {
        const twin = DigitalTwinApp.currentTwin;
        const nodes = [];
        const edges = [];
        
        // Start node
        nodes.push({
            id: 'start',
            label: 'Donor\nInquiry',
            color: {
                background: '#059669',
                border: '#047857'
            },
            font: { color: 'white' },
            shape: 'ellipse'
        });
        
        // Process nodes
        const processes = [
            { id: 'intake', label: 'Intake\nProcess', level: 1 },
            { id: 'assessment', label: 'Needs\nAssessment', level: 2 },
            { id: 'proposal', label: 'Proposal\nDevelopment', level: 3 },
            { id: 'approval', label: 'Internal\nApproval', level: 4 },
            { id: 'funding', label: 'Funding\nDecision', level: 5 }
        ];
        
        processes.forEach((process, index) => {
            nodes.push({
                id: process.id,
                label: process.label,
                color: {
                    background: '#2563eb',
                    border: '#1d4ed8'
                },
                font: { color: 'white' },
                shape: 'box'
            });
            
            if (index === 0) {
                edges.push({
                    from: 'start',
                    to: process.id
                });
            } else {
                edges.push({
                    from: processes[index - 1].id,
                    to: process.id
                });
            }
        });
        
        // Decision points
        nodes.push({
            id: 'decision',
            label: 'Approved?',
            color: {
                background: '#d97706',
                border: '#b45309'
            },
            font: { color: 'white' },
            shape: 'diamond'
        });
        
        edges.push({
            from: 'funding',
            to: 'decision'
        });
        
        // End nodes
        nodes.push({
            id: 'accept',
            label: 'Grant\nAwarded',
            color: {
                background: '#059669',
                border: '#047857'
            },
            font: { color: 'white' },
            shape: 'ellipse'
        });
        
        nodes.push({
            id: 'reject',
            label: 'Application\nRejected',
            color: {
                background: '#dc2626',
                border: '#b91c1c'
            },
            font: { color: 'white' },
            shape: 'ellipse'
        });
        
        edges.push({
            from: 'decision',
            to: 'accept',
            label: 'Yes',
            color: { color: '#059669' }
        });
        
        edges.push({
            from: 'decision',
            to: 'reject',
            label: 'No',
            color: { color: '#dc2626' }
        });
        
        // Update layout for process flow
        this.network.setOptions({
            layout: {
                hierarchical: {
                    direction: 'LR',
                    sortMethod: 'directed',
                    nodeSpacing: 150,
                    levelSeparation: 200
                }
            }
        });
        
        this.updateNodes(nodes, edges);
    },
    
    // Update nodes and edges
    updateNodes(nodes, edges) {
        try {
            this.nodes.clear();
            this.edges.clear();
            this.nodes.add(nodes);
            this.edges.add(edges);
            
            // Fit the network
            setTimeout(() => {
                if (this.network) {
                    this.network.fit();
                }
            }, 100);
        } catch (error) {
            console.error('Error updating visualization:', error);
        }
    },
    
    // Clear visualization
    clearVisualization() {
        if (this.nodes && this.edges) {
            this.nodes.clear();
            this.edges.clear();
        }
    },
    
    // Handle node selection
    onNodeSelect(nodeId) {
        const twin = DigitalTwinApp.currentTwin;
        if (!twin) return;
        
        let nodeInfo = '';
        
        if (nodeId === 'org') {
            nodeInfo = `
                <h4>${twin.name}</h4>
                <p><strong>Mission:</strong> ${twin.mission}</p>
                <p><strong>Size:</strong> ${twin.size} employees</p>
                <p><strong>Budget:</strong> $${twin.annualBudget.toLocaleString()}</p>
                <p><strong>Health Score:</strong> ${twin.health.overallScore}%</p>
            `;
        } else if (nodeId.startsWith('dept_')) {
            const deptIndex = parseInt(nodeId.split('_')[1]);
            const dept = twin.departments[deptIndex];
            if (dept) {
                nodeInfo = `
                    <h4>${dept.name} Department</h4>
                    <p><strong>Staff:</strong> ${dept.headCount} people</p>
                    <p><strong>Budget:</strong> $${dept.budget.toLocaleString()}</p>
                    <p><strong>Processes:</strong> ${dept.processes ? dept.processes.length : 0}</p>
                `;
            }
        } else if (nodeId.startsWith('tech_')) {
            const techIndex = parseInt(nodeId.split('_')[1]);
            const tech = twin.technologyStack[techIndex];
            if (tech) {
                nodeInfo = `
                    <h4>${tech}</h4>
                    <p>Technology component of the organization's digital infrastructure.</p>
                `;
            }
        }
        
        if (nodeInfo) {
            // Create a tooltip or info panel
            this.showNodeInfo(nodeInfo);
        }
    },
    
    // Show node information
    showNodeInfo(info) {
        // Remove existing info panel
        const existingPanel = document.querySelector('.node-info-panel');
        if (existingPanel) {
            existingPanel.remove();
        }
        
        // Create new info panel
        const panel = document.createElement('div');
        panel.className = 'node-info-panel';
        panel.innerHTML = info;
        panel.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: var(--shadow-lg);
            max-width: 300px;
            z-index: 100;
        `;
        
        const container = document.getElementById('networkVisualization').parentElement;
        container.style.position = 'relative';
        container.appendChild(panel);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (panel.parentElement) {
                panel.remove();
            }
        }, 5000);
    }
};

// Extend DigitalTwinApp with visualization methods
DigitalTwinApp.updateVisualization = function(type) {
    DigitalTwinVisualization.updateVisualization(type);
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for vis.js to load
    if (typeof vis !== 'undefined') {
        DigitalTwinVisualization.init();
    } else {
        // Retry after a short delay
        setTimeout(() => {
            if (typeof vis !== 'undefined') {
                DigitalTwinVisualization.init();
            }
        }, 1000);
    }
});

window.DigitalTwinVisualization = DigitalTwinVisualization;