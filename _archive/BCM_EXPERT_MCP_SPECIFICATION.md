# BCM Expert MCP Server Specification

**Status**: Specification
**Version**: 1.0.0
**Date**: 2025-10-09

## Context

Based on user feedback:
> "наш эксперт всм его основной интерфейс должен быть мсп сервер платформа уже нпосредсвено для храненния и управления данными и документами или симуляци все остальное можно в дестопной версии реализовать с клодом. напрмер интервью или обучение или что-то давай подумаем. акцент на коллективном обучении и комьюнити и удоьстве пользователю через конектор продолжить общаться с своим ассистентво на тему всм"

**Translation**: BCM Expert's main interface should be an MCP server. The platform handles data storage, documents, and simulations. Everything else (interviews, training, etc.) can be in desktop version with Claude. Focus on collective learning, community, and user convenience through connector to continue dialogue with BCM assistant.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Desktop                          │
│                                                             │
│  ┌────────────────────────────────────────────────┐        │
│  │         Claude Desktop / VS Code               │        │
│  │                                                │        │
│  │         Connected via MCP Connector            │        │
│  └────────────────┬───────────────────────────────┘        │
│                   │                                         │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    │ MCP Protocol
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              BCM Expert MCP Server                          │
│         (Persistent, Always Running)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │         MCP Server Interface                     │      │
│  │  • Tools: BIA, Risk, Plans, Scenarios, etc.     │      │
│  │  • Resources: Documents, Templates, Knowledge    │      │
│  │  • Prompts: Guided workflows                     │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     │                                       │
│  ┌──────────────────▼───────────────────────────────┐      │
│  │      Platform Integration Layer                  │      │
│  │  • Expertise Center (14 AI specialists)         │      │
│  │  • Collective Intelligence (347+ cases)         │      │
│  │  • RAG + LLM (Qdrant + Claude/GPT)             │      │
│  │  • Simulation Engine                            │      │
│  │  • EventBus for coordination                    │      │
│  └──────────────────┬───────────────────────────────┘      │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────┐
│               Platform Services                           │
│                                                           │
│  • Supabase (PostgreSQL) - Data storage                  │
│  • Qdrant - Vector embeddings                            │
│  • Digital Twin - Simulations                            │
│  • Document Service - Templates & storage                │
│  └──────────────────────────────────────────────────────┘
```

## Core Principle: MCP Server as Primary Interface

### What MCP Server Provides

**MCP Server Handles**:
1. **Tools** - Actions user can take (run BIA, create plan, simulate scenario)
2. **Resources** - Data user can access (documents, templates, knowledge base)
3. **Prompts** - Guided workflows (interview scripts, checklists)

**Platform Services Handle**:
1. **Data Storage** - PostgreSQL, Qdrant
2. **Document Management** - Templates, reports, exports
3. **Simulations** - Digital Twin scenarios
4. **AI Analysis** - Expertise Center, RAG, LLM

**Desktop Claude Handles**:
1. **Conversations** - Natural dialogue with user
2. **Interviews** - Guided data collection
3. **Training** - Educational content delivery
4. **Explanations** - Help and guidance

## MCP Server Tools

### Category 1: BIA Tools

#### `run_bia_analysis`
Execute Business Impact Analysis

**Input**:
```typescript
{
  organization_id: string
  scope?: string[]  // Process IDs to analyze
  mode?: "quick" | "detailed" | "comprehensive"
}
```

**Output**:
```typescript
{
  analysis_id: string
  status: "in_progress" | "completed"
  results?: {
    processes: ProcessAnalysis[]
    dependencies: Dependency[]
    impacts: ImpactAssessment[]
    rto_rpo: RecoveryObjectives[]
  }
  insights: string[]
  recommendations: string[]
}
```

**Platform Integration**:
- Calls Digital Twin for simulation
- Uses Expertise Center for analysis
- Stores results in Supabase
- Shares patterns with Collective Intelligence

#### `identify_business_processes`
Identify and catalog business processes

**Input**:
```typescript
{
  organization_id: string
  sector?: string
  methodology?: "interview" | "document_analysis" | "observation"
}
```

**Output**:
```typescript
{
  processes: BusinessProcess[]
  categorization: ProcessHierarchy
  suggestions: string[]
}
```

#### `assess_process_impact`
Assess impact of process disruption

**Input**:
```typescript
{
  process_id: string
  disruption_duration_hours: number
  scenario?: DisruptionScenario
}
```

**Output**:
```typescript
{
  financial_impact: MonetaryImpact
  operational_impact: OperationalImpact
  reputational_impact: ReputationalImpact
  regulatory_impact: RegulatoryImpact
  total_impact_score: number
  tier_classification: "tier_1" | "tier_2" | "tier_3"
}
```

### Category 2: Risk Assessment Tools

#### `run_risk_assessment`
Execute comprehensive risk assessment

**Input**:
```typescript
{
  organization_id: string
  scope?: RiskScope
  methodology?: "iso_27005" | "nist_rmf" | "fair"
}
```

**Output**:
```typescript
{
  assessment_id: string
  risks: IdentifiedRisk[]
  risk_matrix: RiskMatrix
  treatment_recommendations: TreatmentPlan[]
}
```

#### `analyze_threat_landscape`
Analyze current threat landscape

**Input**:
```typescript
{
  organization_id: string
  sector: string
  geography: string[]
}
```

**Output**:
```typescript
{
  threats: Threat[]
  trends: ThreatTrend[]
  sector_specific: SectorThreat[]
  recommendations: string[]
}
```

### Category 3: Plan Management Tools

#### `generate_bcp`
Generate Business Continuity Plan

**Input**:
```typescript
{
  organization_id: string
  template?: "iso_22301" | "nist_cpg" | "custom"
  sections?: string[]
}
```

**Output**:
```typescript
{
  plan_id: string
  document_url: string
  sections: PlanSection[]
  completeness_score: number
  gaps: string[]
}
```

#### `create_recovery_procedure`
Create recovery procedure for specific scenario

**Input**:
```typescript
{
  scenario: ScenarioType
  processes: string[]
  rto_hours: number
}
```

**Output**:
```typescript
{
  procedure_id: string
  steps: RecoveryStep[]
  resources_required: Resource[]
  estimated_duration: number
  dependencies: string[]
}
```

### Category 4: Simulation Tools

#### `run_scenario_simulation`
Simulate disruption scenario

**Input**:
```typescript
{
  scenario_id: string
  parameters: SimulationParameters
  duration_hours: number
}
```

**Output**:
```typescript
{
  simulation_id: string
  results: SimulationResults
  metrics: {
    recovery_time: number
    resource_utilization: number
    effectiveness_score: number
  }
  insights: string[]
  improvement_suggestions: string[]
}
```

#### `test_recovery_procedure`
Test recovery procedure in simulation

**Input**:
```typescript
{
  procedure_id: string
  scenario: TestScenario
  mode?: "validate" | "optimize" | "stress_test"
}
```

**Output**:
```typescript
{
  test_id: string
  success: boolean
  actual_recovery_time: number
  gaps_identified: Gap[]
  optimizations: Optimization[]
}
```

### Category 5: Knowledge & Learning Tools

#### `search_knowledge_base`
Search BCM knowledge base

**Input**:
```typescript
{
  query: string
  filters?: {
    type?: "case_study" | "best_practice" | "regulation" | "template"
    sector?: string
    iso_clause?: string
  }
  max_results?: number
}
```

**Output**:
```typescript
{
  results: KnowledgeItem[]
  related_cases: CaseStudy[]
  expert_recommendations: string[]
}
```

**Platform Integration**:
- Uses RAG (Qdrant + LLM)
- Queries Collective Intelligence (347+ cases)
- Consults Expertise Center

#### `get_expert_advice`
Get advice from AI BCM specialists

**Input**:
```typescript
{
  question: string
  context?: {
    organization_id?: string
    process_id?: string
    scenario?: string
  }
  specialist?: "bia" | "risk" | "recovery" | "compliance" | "all"
}
```

**Output**:
```typescript
{
  advice: ExpertAdvice[]
  reasoning: string
  references: string[]
  follow_up_questions: string[]
}
```

**Platform Integration**:
- Calls Expertise Center (14 AI specialists)
- Uses RAG for context
- Learns from user feedback

#### `share_case_study`
Share organization's case study with community

**Input**:
```typescript
{
  case_study: {
    scenario: string
    approach: string
    outcome: string
    lessons_learned: string[]
  }
  anonymize?: boolean
}
```

**Output**:
```typescript
{
  case_id: string
  contribution_score: number
  similar_cases: string[]
}
```

**Platform Integration**:
- Adds to Collective Intelligence
- Stores in Qdrant with embeddings
- Makes available for community learning

### Category 6: Compliance Tools

#### `check_iso_compliance`
Check compliance with ISO 22301

**Input**:
```typescript
{
  organization_id: string
  clauses?: string[]  // Specific clauses to check
}
```

**Output**:
```typescript
{
  compliance_score: number
  clause_results: ClauseCompliance[]
  gaps: ComplianceGap[]
  remediation_plan: RemediationAction[]
}
```

#### `generate_compliance_report`
Generate compliance report

**Input**:
```typescript
{
  organization_id: string
  standard: "iso_22301" | "iso_27001" | "nist_cpg"
  format?: "pdf" | "docx" | "html"
}
```

**Output**:
```typescript
{
  report_id: string
  document_url: string
  summary: ComplianceSummary
}
```

## MCP Server Resources

### Document Resources

#### `bcm://documents/templates/{template_id}`
Access BCM document templates

**Examples**:
- `bcm://documents/templates/bia_questionnaire`
- `bcm://documents/templates/bcp_iso22301`
- `bcm://documents/templates/recovery_procedure`

**Returns**: Template content with variables marked

#### `bcm://documents/plans/{plan_id}`
Access generated plans

**Returns**: Current version of BCP/DRP

#### `bcm://documents/reports/{report_id}`
Access reports and assessments

**Returns**: Report content with metadata

### Knowledge Resources

#### `bcm://knowledge/cases/{case_id}`
Access case studies from community

**Returns**: Case study with lessons learned

#### `bcm://knowledge/best_practices/{topic}`
Access best practices library

**Examples**:
- `bcm://knowledge/best_practices/bia_execution`
- `bcm://knowledge/best_practices/recovery_strategies`

#### `bcm://knowledge/regulations/{standard}/{clause}`
Access regulatory requirements

**Examples**:
- `bcm://knowledge/regulations/iso_22301/8.4.2`
- `bcm://knowledge/regulations/nist_cpg/recovery`

### Data Resources

#### `bcm://data/organization/{org_id}`
Access organization profile and data

**Returns**: Organization structure, processes, existing plans

#### `bcm://data/processes/{process_id}`
Access process details

**Returns**: Process definition, dependencies, metrics

#### `bcm://data/simulations/{sim_id}`
Access simulation results

**Returns**: Simulation data, metrics, insights

## MCP Server Prompts

### Guided Workflows

#### `bcm_initial_assessment`
Initial BCM assessment workflow

**Steps**:
1. Organization profile collection
2. Process identification
3. High-level risk assessment
4. Gap analysis
5. Roadmap generation

#### `bia_interview`
Guided BIA interview

**Steps**:
1. Process identification questions
2. Dependency mapping
3. Impact assessment questions
4. RTO/RPO determination
5. Results synthesis

#### `incident_response_drill`
Incident response drill facilitation

**Steps**:
1. Scenario selection
2. Team preparation
3. Drill execution
4. Observation recording
5. After-action review
6. Improvement identification

#### `compliance_gap_analysis`
ISO 22301 compliance gap analysis

**Steps**:
1. Current state assessment
2. Clause-by-clause review
3. Gap identification
4. Priority assignment
5. Remediation planning

## Desktop Claude Integration

### User Experience Flow

1. **User opens Claude Desktop**
   - MCP connector auto-connects to BCM Expert server
   - Context loaded (organization, current projects)

2. **Natural Conversation**
   ```
   User: "I need to do a BIA for my organization"

   Claude: "I'll help you with that. Let me start by understanding
           your organization better."

   [Uses bcm_initial_assessment prompt]

   Claude: "Based on your sector (healthcare) and size (200 employees),
           I recommend starting with identifying your critical
           processes. Shall we begin?"

   [Uses run_bia_analysis tool in background]
   ```

3. **Tool Execution**
   - Claude calls MCP tools transparently
   - Results streamed back to conversation
   - Claude interprets and explains results

4. **Document Generation**
   - Claude uses templates via resources
   - Fills in collected information
   - Generates final documents
   - Stores in platform via tools

5. **Continuous Learning**
   - Claude shares insights with community (if user consents)
   - Platform learns from interactions
   - Future recommendations improve

### Example Conversations

#### Example 1: BIA Execution
```
User: I need to start a BIA

Claude: Great! Let me guide you through the BIA process. First,
        I'll help identify your business processes.

[Calls identify_business_processes tool]

Claude: I've identified 12 potential critical processes based on
        your organization profile. Let's prioritize them:

        Top 5 Critical Processes:
        1. Patient Admissions (Healthcare Core)
        2. Electronic Health Records (Data Critical)
        3. Pharmacy Services (Safety Critical)
        4. Laboratory Services (Diagnostic Critical)
        5. Emergency Room Operations (Life Critical)

        Should we start detailed analysis with these five?

User: Yes, let's analyze the Emergency Room operations first

Claude: Perfect choice. Emergency Room is indeed your most critical
        process. Let me assess its impact...

[Calls assess_process_impact with process_id]

Claude: Analysis complete. Here's what we found:

        Impact of ER Disruption:
        • Financial: $50,000/hour in lost revenue
        • Operational: 95% of emergency cases diverted
        • Reputational: Severe - media coverage likely
        • Regulatory: Critical - EMTALA violations

        Classification: Tier 1 (Critical)
        Recommended RTO: 1 hour
        Recommended RPO: Near-zero (continuous)

        Would you like me to:
        1. Create a recovery procedure for ER disruption?
        2. Analyze dependencies (power, IT, staff)?
        3. Simulate a disruption scenario?
```

#### Example 2: Community Learning
```
User: We just recovered from a ransomware attack.
      Should we share our experience?

Claude: Absolutely! Sharing your experience helps the entire BCM
        community. Your insights could help other organizations
        prepare better.

        What would you like to share?
        • The attack scenario
        • Your response approach
        • What worked well
        • What you'd improve
        • Key lessons learned

User: [Provides details]

Claude: Thank you for sharing. I'll anonymize sensitive details
        and contribute your case study to the community.

[Calls share_case_study tool]

Claude: Your case study has been added!

        Community Impact:
        • Contribution Score: 8.5/10 (highly valuable)
        • Similar Cases Found: 3
        • Unique Insights: Your backup restoration strategy

        In return, here are 3 similar cases that might interest you:
        1. Hospital ransomware recovery (48-hour RTO achieved)
        2. Healthcare data breach response (HIPAA considerations)
        3. Backup validation lessons from clinic network

        Would you like to review any of these?
```

## Implementation Architecture

### Server Structure

```
/infrastructure/mcp-server/
├── bcm_expert_mcp.py          # Main MCP server
├── tools/
│   ├── bia_tools.py           # BIA tool implementations
│   ├── risk_tools.py          # Risk assessment tools
│   ├── plan_tools.py          # Plan management tools
│   ├── simulation_tools.py    # Simulation tools
│   ├── knowledge_tools.py     # Knowledge & learning tools
│   └── compliance_tools.py    # Compliance tools
├── resources/
│   ├── documents.py           # Document resource handlers
│   ├── knowledge.py           # Knowledge resource handlers
│   └── data.py                # Data resource handlers
├── prompts/
│   ├── workflows.py           # Guided workflow prompts
│   └── templates.py           # Prompt templates
├── platform/
│   ├── expertise_client.py    # Expertise Center integration
│   ├── collective_client.py   # Collective Intelligence integration
│   ├── rag_client.py          # RAG + LLM integration
│   └── simulation_client.py   # Digital Twin integration
└── config.py                  # Configuration
```

### Deployment

**MCP Server**:
- Runs persistently as service
- Listens on localhost:3000 (or configured port)
- Exposed via MCP protocol

**Platform Services**:
- Already deployed (system-bcm-service, etc.)
- Accessed via internal APIs

**Desktop Client**:
- Claude Desktop with MCP connector
- Configured to connect to localhost:3000

### Configuration Example

```json
{
  "mcpServers": {
    "bcm-expert": {
      "command": "python",
      "args": ["/path/to/bcm_expert_mcp.py"],
      "env": {
        "PLATFORM_API_URL": "http://localhost:8009",
        "SUPABASE_URL": "https://...",
        "SUPABASE_KEY": "...",
        "QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

## Benefits of MCP Approach

### For Users
1. **Familiar Interface**: Use Claude Desktop they already know
2. **Conversational**: Natural language, not forms
3. **Contextual**: Claude remembers previous conversations
4. **Guided**: Prompts lead through complex processes
5. **Persistent**: MCP server maintains state

### For Platform
1. **Separation of Concerns**: UI (Claude) vs Logic (Platform)
2. **Reusability**: Same tools work from any MCP client
3. **Scalability**: Platform services scale independently
4. **Maintainability**: Update server without changing client

### For Community
1. **Knowledge Sharing**: Easy contribution via conversation
2. **Learning**: Platform learns from all interactions
3. **Best Practices**: Crowd-sourced improvements
4. **Collective Intelligence**: Growing knowledge base

## Next Steps

1. **Implement Core MCP Server** (Priority 1)
   - Basic tool structure
   - Document resources
   - Platform integration

2. **Create BIA Tools** (Priority 2)
   - `run_bia_analysis`
   - `identify_business_processes`
   - `assess_process_impact`

3. **Test with Claude Desktop** (Priority 3)
   - Configure MCP connector
   - Run through BIA workflow
   - Gather user feedback

4. **Add Remaining Tools** (Priority 4)
   - Risk assessment
   - Plan management
   - Simulations
   - Knowledge tools

5. **Community Features** (Priority 5)
   - Case study sharing
   - Best practices library
   - Collaborative learning

## Success Metrics

- **Tool Usage**: Number of tool calls per session
- **Conversation Quality**: User satisfaction with guidance
- **Knowledge Contribution**: Cases shared by community
- **Platform Integration**: Successful calls to platform services
- **User Retention**: Repeat usage of MCP server

---

**Status**: Ready for implementation
**Dependencies**: Platform services (already deployed)
**Estimated Effort**: 2-3 weeks for core functionality
