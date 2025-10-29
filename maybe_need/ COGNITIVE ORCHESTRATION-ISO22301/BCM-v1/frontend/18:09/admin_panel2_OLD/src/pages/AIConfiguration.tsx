import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Brain,
  Save,
  RefreshCw,
  Settings,
  MessageSquare,
  Workflow,
  User,
  AlertTriangle,
  CheckCircle,
  Copy,
  Trash2,
  Plus,
  Code,
  FileText,
  Zap
} from 'lucide-react';

interface AIOrganConfig {
  id: string;
  name: string;
  description: string;
  systemPrompt: string;
  temperature: number;
  maxTokens: number;
  role: string;
  workflows: string[];
  responsePatterns: string[];
  enabled: boolean;
}

const AIConfiguration: React.FC = () => {
  const [selectedOrgan, setSelectedOrgan] = useState<string>('ai_orchestrator');
  const [configs, setConfigs] = useState<Record<string, AIOrganConfig>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // Default AI Organ configurations
  const defaultConfigs: Record<string, AIOrganConfig> = {
    'ai_orchestrator': {
      id: 'ai_orchestrator',
      name: 'AI Orchestrator Core',
      description: 'Main coordination hub for all AI operations',
      systemPrompt: `You are the AI Orchestrator Core for a comprehensive Business Continuity Management system integrated with 27 BCM modules in Odoo.

Your role is to coordinate between different AI agents, manage BCM workflows, and ensure seamless operation across:
- BCM Base, Core, and Governance modules
- Risk Management and Business Impact Analysis
- Incident Management and Emergency Response
- Training, Exercises, and Compliance modules
- Document Control and Communication systems

Key BCM Responsibilities:
- Orchestrate incident response workflows according to ISO 22301
- Coordinate between risk assessment, impact analysis, and recovery planning
- Manage communication between stakeholders during disruptions
- Ensure compliance tracking and audit readiness
- Monitor RTO (Recovery Time Objective) and RPO (Recovery Point Objective) metrics

Always prioritize business continuity, data integrity, and stakeholder safety.
Respond in a professional, technical manner with BCM terminology.`,
      temperature: 0.7,
      maxTokens: 2000,
      role: 'System Coordinator',
      workflows: ['incident_response', 'risk_assessment', 'compliance_check'],
      responsePatterns: ['technical', 'detailed', 'action-oriented'],
      enabled: true
    },
    'unified_ai': {
      id: 'unified_ai',
      name: 'Unified AI Service',
      description: 'Centralized AI processing and decision-making',
      systemPrompt: `You are the Unified AI Service managing integrated AI operations.
Process requests efficiently and provide unified responses across all domains.
Maintain consistency in decision-making and reporting.`,
      temperature: 0.6,
      maxTokens: 1500,
      role: 'AI Integration Manager',
      workflows: ['data_analysis', 'report_generation', 'decision_support'],
      responsePatterns: ['analytical', 'comprehensive', 'data-driven'],
      enabled: true
    },
    'pdca_assistant': {
      id: 'pdca_assistant',
      name: 'PDCA Assistant',
      description: 'Plan-Do-Check-Act cycle management',
      systemPrompt: `You are the PDCA Assistant focused on continuous improvement.
Guide users through Plan-Do-Check-Act cycles for business processes.
Provide actionable recommendations and track improvement metrics.`,
      temperature: 0.5,
      maxTokens: 1000,
      role: 'Process Improvement Specialist',
      workflows: ['planning', 'execution', 'monitoring', 'adjustment'],
      responsePatterns: ['structured', 'methodical', 'improvement-focused'],
      enabled: true
    },
    'bia_engine': {
      id: 'bia_engine',
      name: 'BIA Engine',
      description: 'Business Impact Analysis and assessment',
      systemPrompt: `You are the Business Impact Analysis (BIA) Engine for ISO 22301 compliant BCM system.

Core BIA Functions:
- Analyze critical business processes and their interdependencies
- Calculate financial impacts of disruptions (MTD - Maximum Tolerable Downtime)
- Determine Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)
- Assess resource requirements for business continuity
- Identify minimum staffing levels and critical suppliers

BIA Methodologies:
- Process mapping and dependency analysis
- Quantitative and qualitative impact assessment
- Peak period analysis and seasonal variations
- Regulatory and legal requirement impact
- Reputation and customer impact evaluation

Integration with BCM Modules:
- Connect with bcm_bia module for data persistence
- Feed results to bcm_plans for recovery strategy development
- Support bcm_risk_management with impact probabilities
- Provide input to bcm_exercise for scenario testing

Always provide actionable insights with specific timeframes, financial figures, and risk ratings.
Use ISO 22301 terminology and maintain audit trail documentation.`,
      temperature: 0.4,
      maxTokens: 2500,
      role: 'Impact Analyst',
      workflows: ['impact_assessment', 'criticality_analysis', 'recovery_planning'],
      responsePatterns: ['analytical', 'risk-focused', 'strategic'],
      enabled: true
    },
    'compliance_checker': {
      id: 'compliance_checker',
      name: 'Compliance Checker',
      description: 'ISO 22301 compliance validation',
      systemPrompt: `You are the ISO 22301:2019 Compliance Checker for Business Continuity Management Systems.

ISO 22301 Compliance Areas:
- Context of the organization (Clause 4)
- Leadership and commitment (Clause 5)
- Planning and risk assessment (Clause 6)
- Support and resources (Clause 7)
- Operation and incident response (Clause 8)
- Performance evaluation (Clause 9)
- Improvement and corrective actions (Clause 10)

Key Compliance Checks:
- BCMS policy and objectives alignment
- Risk assessment and business impact analysis completeness
- Business continuity strategies and procedures validation
- Exercise and testing program compliance
- Management review and audit findings
- Competence and awareness requirements
- Document control and records management

Integration with BCM Modules:
- Validate bcm_governance for leadership requirements
- Check bcm_compliance module for audit trails
- Review bcm_training for competence evidence
- Assess bcm_exercise for testing compliance
- Monitor bcm_incident_management for response capability

Provide specific clause references, compliance ratings (1-5), gap analysis, and remediation timelines.
Maintain certification readiness and audit evidence.`,
      temperature: 0.3,
      maxTokens: 1500,
      role: 'Compliance Officer',
      workflows: ['audit', 'validation', 'gap_analysis', 'reporting'],
      responsePatterns: ['formal', 'regulatory', 'precise'],
      enabled: true
    },
    'document_processor': {
      id: 'document_processor',
      name: 'Document Processor',
      description: 'Document analysis and processing',
      systemPrompt: `You are the Document Processor AI.
Extract, analyze, and process business continuity documents.
Maintain document version control and compliance.`,
      temperature: 0.4,
      maxTokens: 2000,
      role: 'Document Analyst',
      workflows: ['extraction', 'analysis', 'classification', 'storage'],
      responsePatterns: ['detailed', 'accurate', 'structured'],
      enabled: true
    },
    'scenario_orchestrator': {
      id: 'scenario_orchestrator',
      name: 'Scenario Orchestrator',
      description: 'Crisis scenario simulation and management',
      systemPrompt: `You are the Scenario Orchestrator for crisis simulations.
Design and execute business disruption scenarios.
Guide response teams through exercises and training.`,
      temperature: 0.8,
      maxTokens: 3000,
      role: 'Scenario Designer',
      workflows: ['scenario_creation', 'simulation', 'evaluation', 'training'],
      responsePatterns: ['creative', 'scenario-based', 'educational'],
      enabled: true
    },
    'exercise_simulators': {
      id: 'exercise_simulators',
      name: 'Exercise Simulators',
      description: 'Training exercise execution',
      systemPrompt: `You are the Exercise Simulator AI.
Conduct realistic business continuity exercises.
Evaluate team performance and provide feedback.`,
      temperature: 0.7,
      maxTokens: 2000,
      role: 'Training Coordinator',
      workflows: ['exercise_setup', 'execution', 'monitoring', 'debriefing'],
      responsePatterns: ['instructional', 'evaluative', 'constructive'],
      enabled: true
    },
    'mcp_server': {
      id: 'mcp_server',
      name: 'BCM MCP Server',
      description: 'Model Context Protocol server',
      systemPrompt: `You are the MCP Server managing model contexts.
Handle AI model communications and context management.
Ensure efficient protocol operations.`,
      temperature: 0.5,
      maxTokens: 1000,
      role: 'Protocol Manager',
      workflows: ['context_management', 'routing', 'optimization'],
      responsePatterns: ['technical', 'efficient', 'protocol-based'],
      enabled: true
    },
    'github_integration': {
      id: 'github_integration',
      name: 'GitHub Integration',
      description: 'Code repository and version control',
      systemPrompt: `You are the GitHub Integration AI.
Manage code repositories and version control for BCM systems.
Track changes and facilitate collaboration.`,
      temperature: 0.4,
      maxTokens: 1500,
      role: 'DevOps Assistant',
      workflows: ['version_control', 'ci_cd', 'code_review', 'deployment'],
      responsePatterns: ['technical', 'developer-friendly', 'git-focused'],
      enabled: true
    },
    'bcm_governance_brain': {
      id: 'bcm_governance_brain',
      name: 'BCM Governance Brain',
      description: 'BCM governance and strategic decision making',
      systemPrompt: `You are the BCM Governance Brain responsible for strategic oversight of the Business Continuity Management System.

Governance Responsibilities:
- Strategic BCM policy development and review
- BCMS governance framework implementation
- Senior management reporting and dashboards
- Resource allocation and budget planning
- Stakeholder engagement and communication
- Performance measurement and KPI tracking

Integration with BCM Modules:
- Leverage bcm_governance for policy management
- Connect with bcm_compliance for governance metrics
- Use bcm_monitoring for performance oversight
- Support bcm_communication for stakeholder updates

Decision-Making Framework:
- Risk-based decision making aligned with ISO 22301
- Business impact consideration in all recommendations
- Regulatory compliance in governance decisions
- Cost-benefit analysis for BCM investments

Provide executive-level insights, governance recommendations, and strategic guidance.
Maintain oversight of enterprise-wide BCM maturity and effectiveness.`,
      temperature: 0.6,
      maxTokens: 2000,
      role: 'Governance Advisor',
      workflows: ['policy_development', 'strategic_planning', 'oversight', 'reporting'],
      responsePatterns: ['strategic', 'executive-level', 'governance-focused'],
      enabled: true
    },
    'incident_response_brain': {
      id: 'incident_response_brain',
      name: 'Incident Response Brain',
      description: 'Emergency response and incident management',
      systemPrompt: `You are the Incident Response Brain for emergency situations and business disruptions.

Incident Response Capabilities:
- Real-time incident assessment and classification
- Emergency response team coordination
- Business continuity plan activation
- Stakeholder notification and communication
- Resource mobilization and logistics
- Recovery progress monitoring

BCM Integration:
- Execute workflows from bcm_incident_management
- Coordinate with bcm_plans for response procedures
- Use bcm_communication for stakeholder alerts
- Track metrics in bcm_monitoring

Response Protocols:
- Immediate impact assessment and triage
- RTO/RPO monitoring and reporting
- Escalation procedures and authority levels
- Cross-functional team coordination
- Post-incident analysis and lessons learned

Crisis Communication:
- Internal team coordination
- External stakeholder updates
- Media and public relations support
- Regulatory notification compliance

Respond with urgency, clarity, and actionable directives during incidents.
Maintain calm leadership while ensuring swift response execution.`,
      temperature: 0.5,
      maxTokens: 2500,
      role: 'Incident Commander',
      workflows: ['incident_assessment', 'response_coordination', 'recovery_management', 'communication'],
      responsePatterns: ['urgent', 'directive', 'crisis-focused'],
      enabled: true
    },
    'risk_assessment_brain': {
      id: 'risk_assessment_brain',
      name: 'Risk Assessment Brain',
      description: 'Enterprise risk analysis and threat assessment',
      systemPrompt: `You are the Risk Assessment Brain for comprehensive enterprise risk analysis.

Risk Assessment Functions:
- Threat identification and analysis
- Vulnerability assessment and mapping
- Likelihood and impact evaluation
- Risk treatment option development
- Risk register maintenance and updates
- Scenario-based risk modeling

BCM Risk Categories:
- Operational risks (IT failures, supply chain, facilities)
- Environmental risks (natural disasters, climate events)
- Human risks (key person dependency, cyber threats)
- Strategic risks (market changes, regulatory shifts)
- Emerging risks (technology, geopolitical, pandemic)

Risk Assessment Methodologies:
- Qualitative and quantitative analysis
- Bow-tie analysis for critical scenarios
- Monte Carlo simulation for complex risks
- Heat mapping and risk matrices
- Horizon scanning for emerging threats

Integration with BCM:
- Connect with bcm_risk_management for data persistence
- Feed into bcm_bia for impact assessment
- Support bcm_plans with risk-based strategies
- Inform bcm_exercise scenarios and testing

Provide evidence-based risk insights with treatment recommendations.
Maintain ISO 31000 and ISO 22301 compliance in all assessments.`,
      temperature: 0.4,
      maxTokens: 2000,
      role: 'Risk Analyst',
      workflows: ['threat_analysis', 'vulnerability_assessment', 'risk_evaluation', 'treatment_planning'],
      responsePatterns: ['analytical', 'evidence-based', 'risk-focused'],
      enabled: true
    }
  };

  useEffect(() => {
    // Load saved configs from localStorage
    const savedConfigs = localStorage.getItem('ai_organ_configs');
    if (savedConfigs) {
      setConfigs(JSON.parse(savedConfigs));
    } else {
      setConfigs(defaultConfigs);
    }
  }, []);

  const handleConfigChange = (organId: string, field: keyof AIOrganConfig, value: any) => {
    setConfigs(prev => ({
      ...prev,
      [organId]: {
        ...prev[organId],
        [field]: value
      }
    }));
    setHasChanges(true);
  };

  const saveConfigs = async () => {
    setSaveStatus('saving');

    try {
      // Save to localStorage
      localStorage.setItem('ai_organ_configs', JSON.stringify(configs));

      // TODO: Save to backend API
      // await fetch('/api/ai-configs', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(configs)
      // });

      setSaveStatus('saved');
      setHasChanges(false);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to save configs:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const resetToDefaults = () => {
    if (confirm('Reset all configurations to defaults? This will lose your changes.')) {
      setConfigs(defaultConfigs);
      setHasChanges(true);
    }
  };

  const currentConfig = configs[selectedOrgan] || defaultConfigs[selectedOrgan];

  const addWorkflow = () => {
    const newWorkflow = prompt('Enter new workflow name:');
    if (newWorkflow) {
      handleConfigChange(selectedOrgan, 'workflows', [...currentConfig.workflows, newWorkflow]);
    }
  };

  const removeWorkflow = (index: number) => {
    const newWorkflows = currentConfig.workflows.filter((_, i) => i !== index);
    handleConfigChange(selectedOrgan, 'workflows', newWorkflows);
  };

  const copyPrompt = () => {
    navigator.clipboard.writeText(currentConfig.systemPrompt);
    alert('System prompt copied to clipboard!');
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">AI Configuration</h1>
          <p className="text-slate-600 mt-1">Configure prompts, workflows, and behaviors for AI organs</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={resetToDefaults}
            disabled={!hasChanges}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </Button>
          <Button
            onClick={saveConfigs}
            disabled={!hasChanges}
            className={saveStatus === 'saved' ? 'bg-green-600' : ''}
          >
            {saveStatus === 'saving' ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : saveStatus === 'saved' ? (
              <CheckCircle className="h-4 w-4 mr-2" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saveStatus === 'saved' ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {/* Status Alert */}
      {hasChanges && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Unsaved Changes</AlertTitle>
          <AlertDescription>
            You have unsaved configuration changes. Save them to apply to the AI organs.
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Organ Selector */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>AI Organs</CardTitle>
            <CardDescription>Select an organ to configure</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="space-y-1">
              {Object.values(configs).map((config) => (
                <button
                  key={config.id}
                  onClick={() => setSelectedOrgan(config.id)}
                  className={`w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors ${
                    selectedOrgan === config.id ? 'bg-slate-100 border-l-4 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{config.name}</div>
                      <div className="text-sm text-slate-500">{config.role}</div>
                    </div>
                    {config.enabled ? (
                      <Badge variant="default" className="bg-green-500">Active</Badge>
                    ) : (
                      <Badge variant="secondary">Disabled</Badge>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Configuration Panel */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  {currentConfig.name}
                </CardTitle>
                <CardDescription>{currentConfig.description}</CardDescription>
              </div>
              <Badge variant={currentConfig.enabled ? 'default' : 'secondary'}>
                {currentConfig.enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="prompt" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="prompt">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Prompt
                </TabsTrigger>
                <TabsTrigger value="parameters">
                  <Settings className="h-4 w-4 mr-2" />
                  Parameters
                </TabsTrigger>
                <TabsTrigger value="workflows">
                  <Workflow className="h-4 w-4 mr-2" />
                  Workflows
                </TabsTrigger>
                <TabsTrigger value="advanced">
                  <Code className="h-4 w-4 mr-2" />
                  Advanced
                </TabsTrigger>
              </TabsList>

              {/* Prompt Configuration */}
              <TabsContent value="prompt" className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <Label>System Prompt</Label>
                    <Button size="sm" variant="outline" onClick={copyPrompt}>
                      <Copy className="h-4 w-4 mr-1" />
                      Copy
                    </Button>
                  </div>
                  <textarea
                    value={currentConfig.systemPrompt}
                    onChange={(e) => handleConfigChange(selectedOrgan, 'systemPrompt', e.target.value)}
                    className="w-full h-64 p-3 border rounded-md font-mono text-sm"
                    placeholder="Enter the system prompt for this AI organ..."
                  />
                  <p className="text-sm text-slate-500 mt-2">
                    This prompt defines the behavior and role of the AI organ.
                  </p>
                </div>

                <div>
                  <Label>Response Patterns</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {currentConfig.responsePatterns.map((pattern, i) => (
                      <Badge key={i} variant="outline">
                        {pattern}
                      </Badge>
                    ))}
                  </div>
                </div>
              </TabsContent>

              {/* Parameters */}
              <TabsContent value="parameters" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Temperature</Label>
                    <div className="flex items-center gap-2 mt-2">
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={currentConfig.temperature}
                        onChange={(e) => handleConfigChange(selectedOrgan, 'temperature', parseFloat(e.target.value))}
                        className="flex-1"
                      />
                      <span className="w-12 text-right">{currentConfig.temperature}</span>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">
                      Higher = more creative, Lower = more focused
                    </p>
                  </div>

                  <div>
                    <Label>Max Tokens</Label>
                    <Input
                      type="number"
                      value={currentConfig.maxTokens}
                      onChange={(e) => handleConfigChange(selectedOrgan, 'maxTokens', parseInt(e.target.value))}
                      className="mt-2"
                    />
                    <p className="text-sm text-slate-500 mt-1">
                      Maximum response length in tokens
                    </p>
                  </div>
                </div>

                <div>
                  <Label>Role</Label>
                  <Input
                    value={currentConfig.role}
                    onChange={(e) => handleConfigChange(selectedOrgan, 'role', e.target.value)}
                    className="mt-2"
                    placeholder="Enter the role description..."
                  />
                </div>

                <div>
                  <Label>Status</Label>
                  <Select
                    value={currentConfig.enabled ? 'enabled' : 'disabled'}
                    onValueChange={(value) => handleConfigChange(selectedOrgan, 'enabled', value === 'enabled')}
                  >
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="enabled">Enabled</SelectItem>
                      <SelectItem value="disabled">Disabled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </TabsContent>

              {/* Workflows */}
              <TabsContent value="workflows" className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <Label>Configured Workflows</Label>
                    <Button size="sm" onClick={addWorkflow}>
                      <Plus className="h-4 w-4 mr-1" />
                      Add Workflow
                    </Button>
                  </div>
                  <div className="space-y-2">
                    {currentConfig.workflows.map((workflow, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-md">
                        <div className="flex items-center gap-3">
                          <Zap className="h-4 w-4 text-blue-500" />
                          <span className="font-medium">{workflow}</span>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeWorkflow(index)}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </TabsContent>

              {/* Advanced Settings */}
              <TabsContent value="advanced" className="space-y-4">
                <Alert>
                  <Code className="h-4 w-4" />
                  <AlertTitle>Advanced Configuration</AlertTitle>
                  <AlertDescription>
                    These settings will be sent to the AI Orchestrator API for processing.
                    Changes here directly affect the AI organ's behavior.
                  </AlertDescription>
                </Alert>

                <div>
                  <Label>Configuration JSON</Label>
                  <pre className="mt-2 p-4 bg-slate-100 rounded-md overflow-x-auto">
                    <code>{JSON.stringify(currentConfig, null, 2)}</code>
                  </pre>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      const json = JSON.stringify(currentConfig, null, 2);
                      navigator.clipboard.writeText(json);
                      alert('Configuration copied to clipboard!');
                    }}
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy JSON
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      const url = `http://localhost:8000/ai/agents/${currentConfig.id}/config`;
                      window.open(url, '_blank');
                    }}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    View in API
                  </Button>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AIConfiguration;