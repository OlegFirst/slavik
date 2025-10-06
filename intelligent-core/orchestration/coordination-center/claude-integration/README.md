# Claude Integration (Anthropic Governance Brain)

## Overview
Anthropic Claude integration for high-quality strategic governance analysis and executive decision support.

## Extracted From
- **Source**: `/intelligent-core/orchestration/anthropic_integration.py`
- **Date**: 2025-10-04
- **Original Size**: 258 lines

## What This Module Does
- Strategic governance analysis using Claude 3 Sonnet
- ISO 22301 policy analysis and compliance checking
- Executive board report generation
- Emergency governance crisis response
- Automatic fallback to local AI if Anthropic unavailable

## Status
**Production-Ready**

## Dependencies
- `httpx` - HTTP client for Anthropic API
- `ANTHROPIC_API_KEY` environment variable
- Fallback: Local AI Orchestrator at `http://ai_orchestrator:8000`

## Key Features

### 1. Governance Analysis
High-quality strategic intelligence for C-level decision making:
- ISO 22301 expertise
- Corporate governance best practices
- Risk management and compliance
- Crisis management

### 2. Policy Analysis
Comprehensive BCM policy review:
- ISO 22301 compliance assessment
- Strategic alignment check
- Implementation guidance
- Improvement recommendations

### 3. Board Report Generation
Executive-level reports with:
- Executive summary
- Strategic assessment
- Actionable recommendations (30/90/365 day timelines)
- Resource requirements
- Success metrics and KPIs

### 4. Emergency Mode
Fast-track crisis analysis:
- Immediate threat assessment
- 24-hour action plan
- Stakeholder communication strategy
- Risk mitigation measures

## Usage Example
```python
from claude_integration import anthropic_governance

# Strategic governance analysis
result = await anthropic_governance.governance_analysis(
    prompt="Analyze our BCM readiness for hybrid work",
    context={
        "company": "Acme Corp",
        "domain": "Remote Work Continuity",
        "priority": "High",
        "ai_personality": "wise_ruler"
    }
)

# Policy analysis
policy_result = await anthropic_governance.policy_analysis(
    policy_content="[Policy document text...]",
    policy_type="Business Continuity Policy",
    context={"company": "Acme Corp"}
)

# Emergency response
emergency = await anthropic_governance.emergency_governance_analysis(
    emergency_situation="Critical data center failure",
    context={"company": "Acme Corp"}
)
```

## Configuration
```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Model configuration (in code)
model = 'claude-3-sonnet-20240229'
temperature = 0.3  # Low for consistency
max_tokens = 4000
```

## Fallback Strategy
If Anthropic API is unavailable:
1. Tries local AI Orchestrator
2. Final fallback: Basic template response

## Integration Points
- **Anthropic API**: Primary intelligence source
- **Local AI Orchestrator**: Fallback intelligence
- **Governance Service**: Consumer of governance insights

## Next Steps
1. Add Claude 3 Opus support for highest-quality analysis
2. Implement response caching for similar queries
3. Add governance knowledge base (RAG)
4. Track analysis quality metrics
