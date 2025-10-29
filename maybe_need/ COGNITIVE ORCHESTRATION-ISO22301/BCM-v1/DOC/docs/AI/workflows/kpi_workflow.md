# KPI Workflow - Performance Monitoring and Management Review

## Workflow Overview

The KPI (Key Performance Indicator) workflow enables the AI Assistant to monitor BCM system performance, calculate metrics, identify trends, and prepare management review materials according to ISO 22301 measurement requirements.

## Trigger Conditions

### Automatic Triggers
- **Monthly KPI Review Cycle**: Automated monthly performance assessment
- **KPI Threshold Breaches**: Metrics falling below acceptable levels
- **Management Review Due**: Quarterly review preparation requirements
- **Trend Analysis Alert**: Negative trends detected in key metrics
- **Performance Degradation**: Significant drops in multiple KPIs

### User-Initiated Triggers
- Direct request: "Calculate current BCM KPIs"
- Review preparation: "Prepare management review dashboard"
- Performance inquiry: "How are we performing against targets?"

## Core BCM KPIs and Calculations

### Primary Performance Indicators
```python
class BCMKPICalculator:
    def __init__(self, tenant_id, calculation_period):
        self.tenant_id = tenant_id
        self.period = calculation_period
        
    def calculate_all_kpis(self):
        return {
            "bia_coverage": self.calculate_bia_coverage(),
            "plans_up_to_date": self.calculate_plans_currency(),
            "capa_on_time": self.calculate_capa_performance(),
            "incident_response_time": self.calculate_incident_response_time(),
            "exercise_completion": self.calculate_exercise_completion(),
            "training_completion": self.calculate_training_completion(),
            "compliance_score": self.calculate_compliance_score(),
            "risk_mitigation": self.calculate_risk_mitigation_rate(),
            "stakeholder_satisfaction": self.calculate_stakeholder_satisfaction(),
            "bcm_maturity": self.calculate_bcm_maturity_level()
        }
    
    def calculate_bia_coverage(self):
        """BIA Coverage: % of critical processes with current BIA"""
        critical_processes = get_critical_processes(self.tenant_id)
        processes_with_current_bia = get_processes_with_current_bia(
            self.tenant_id, max_age_days=365
        )
        
        if not critical_processes:
            return 0.0
            
        coverage = len(processes_with_current_bia) / len(critical_processes)
        return round(coverage * 100, 1)
    
    def calculate_plans_currency(self):
        """Plans Up-to-date: % of plans updated within acceptable timeframe"""
        all_plans = get_active_plans(self.tenant_id)
        current_plans = get_plans_updated_within(
            self.tenant_id, max_age_days=180
        )
        
        if not all_plans:
            return 0.0
            
        currency = len(current_plans) / len(all_plans)
        return round(currency * 100, 1)
    
    def calculate_capa_performance(self):
        """CAPA On-time: % of CAPA items completed by due date"""
        completed_capa = get_completed_capa_items(self.tenant_id, self.period)
        on_time_capa = [c for c in completed_capa if c.completion_date <= c.due_date]
        
        if not completed_capa:
            return 100.0  # No overdue if no CAPA items
            
        performance = len(on_time_capa) / len(completed_capa)
        return round(performance * 100, 1)
    
    def calculate_incident_response_time(self):
        """Average incident response time in hours"""
        incidents = get_incidents(self.tenant_id, self.period)
        response_times = [
            (i.first_response_time - i.reported_time).total_seconds() / 3600
            for i in incidents if i.first_response_time
        ]
        
        if not response_times:
            return 0.0
            
        return round(sum(response_times) / len(response_times), 1)
```

## Workflow Steps

### Step 1: KPI Data Collection and Calculation
```python
# Collect performance data and calculate KPIs
POST /api/recommendations
{
    "context": "kpi_calculation",
    "data": {
        "action_type": "calculate_kpis", 
        "calculation_period": {
            "start_date": "2024-02-01",
            "end_date": "2024-02-29", 
            "period_type": "monthly"
        },
        "kpi_scope": "all_primary_indicators",
        "comparison_periods": [
            "previous_month",
            "same_month_last_year",
            "12_month_average"
        ],
        "analysis_requirements": {
            "trend_analysis": true,
            "threshold_assessment": true,
            "root_cause_indicators": true,
            "improvement_opportunities": true
        },
        "output_format": {
            "executive_summary": true,
            "detailed_metrics": true,
            "visual_dashboards": true,
            "action_recommendations": true
        }
    },
    "tenant_id": tenant_id,
    "user_id": user_id
}
```

**KPI Calculation Results**:
```
## BCM Performance Dashboard - February 2024

### 📊 Executive KPI Summary
**Overall BCM Health Score**: 78/100 (🟨 Good - Attention Areas Identified)

| KPI | Current | Target | Trend | Status |
|-----|---------|---------|-------|--------|
| BIA Coverage | 84% | ≥80% | ↗️ +6% | ✅ Above Target |
| Plans Up-to-date | 72% | ≥75% | ↘️ -3% | ⚠️ Below Target |
| CAPA On-time | 89% | ≥90% | ↗️ +2% | ⚠️ Near Target |
| Incident Response | 3.2h | <4h | ↗️ -0.5h | ✅ Above Target |
| Exercise Completion | 91% | ≥85% | → 0% | ✅ Above Target |
| Training Completion | 76% | ≥85% | ↘️ -4% | 🟥 Below Target |

### 🎯 Performance Highlights
**Strengths**:
- BIA coverage improved significantly (+6% vs last month)
- Incident response times consistently under target
- Exercise program exceeding completion targets

**Attention Areas**:
- Plan currency declining (3 consecutive months)
- Training completion below target for Q1
- CAPA completion rate approaching threshold

### 🚨 Threshold Breach Alerts
1. **Training Completion Rate**: 76% (Target: ≥85%)
   - **Impact**: Staff preparedness concerns
   - **Trend**: Declining 3 months (-12% vs Q4 2023)
   - **Root Cause**: Resource constraints, competing priorities

2. **Plans Up-to-date**: 72% (Target: ≥75%)
   - **Impact**: Response capability uncertainty
   - **Trend**: Gradual decline over 6 months
   - **Root Cause**: Plan review backlogs, process complexity

### 📈 12-Month Performance Trends
**Improving Areas**:
- BIA Coverage: 58% → 84% (+26% year-over-year)
- Incident Response: 5.1h → 3.2h (-37% improvement)
- Exercise Completion: 78% → 91% (+13% improvement)

**Declining Areas**:
- Training Completion: 88% → 76% (-12% decline)
- Plans Currency: 79% → 72% (-7% decline)

### 🎬 Recommended Actions
[PRIORITY: Address Training Gaps] (resource_allocation_needed)
[URGENT: Plan Review Acceleration] (process_improvement_required)  
[MONITOR: CAPA Process Enhancement] (threshold_approaching)
```

### Step 2: Trend Analysis and Performance Insights
```python
# Analyze performance trends and identify patterns
def analyze_kpi_trends(kpi_data, historical_periods):
    trend_analysis = {}
    
    for kpi_name, current_value in kpi_data.items():
        historical_values = get_historical_kpi_values(kpi_name, historical_periods)
        
        trend_characteristics = {
            "direction": calculate_trend_direction(historical_values),
            "velocity": calculate_trend_velocity(historical_values),
            "stability": assess_trend_stability(historical_values),
            "seasonality": detect_seasonal_patterns(historical_values),
            "forecast": generate_trend_forecast(historical_values, periods=3)
        }
        
        # Identify potential root causes for trends
        if trend_characteristics["direction"] == "declining":
            root_cause_indicators = analyze_decline_factors(kpi_name, historical_values)
            trend_characteristics["root_causes"] = root_cause_indicators
        
        trend_analysis[kpi_name] = trend_characteristics
    
    return generate_trend_insights(trend_analysis)
```

**Trend Analysis Results**:
```
## Performance Trend Analysis - 18 Month Deep Dive

### 📉 Declining Performance Patterns

#### Training Completion Rate Decline Analysis
**Pattern**: Consistent quarterly decline since Q2 2023
**Velocity**: -3.2% per quarter (accelerating)
**Forecast**: Projected 68% by Q2 2024 if trend continues

**Root Cause Analysis**:
1. **Resource Constraint Pattern**: Training budget reduced 15% in Q3 2023
2. **Competing Priority Pattern**: Major system implementation absorbed training resources
3. **Delivery Method Issues**: Online training completion rates 23% lower than in-person
4. **Seasonal Effects**: Q4 consistently lowest (holiday impact)

**Correlation Analysis**:
- **Strong Negative Correlation** (-0.78): Training completion vs project activity volume
- **Moderate Correlation** (+0.64): Training completion vs employee satisfaction scores

#### Plan Currency Decline Analysis  
**Pattern**: Gradual decline with acceleration in last 3 months
**Velocity**: -1.1% per month (steady)
**Forecast**: Will breach critical threshold (65%) by June 2024

**Contributing Factors**:
1. **Process Bottleneck**: Plan review process takes average 45 days (target: 30)
2. **Resource Allocation**: Only 60% of planned review resources allocated
3. **Complexity Growth**: Average plan length increased 35% without process adjustment
4. **Stakeholder Availability**: Key reviewers overcommitted, causing delays

### 📈 Improving Performance Patterns

#### BIA Coverage Success Analysis
**Pattern**: Dramatic improvement over 12 months
**Success Factors**:
1. **Process Automation**: BIA workflow automation reduced completion time 40%
2. **Resource Investment**: Dedicated BIA analyst position created
3. **Stakeholder Engagement**: Improved communication increased participation 25%
4. **Tool Enhancement**: New BIA software improved user experience significantly

**Lessons Learned**: Investment in automation and dedicated resources drives performance

#### Incident Response Time Excellence  
**Pattern**: Consistent improvement with sustained performance
**Excellence Factors**:
1. **Training Investment**: Regular simulation exercises maintain skill levels
2. **Process Optimization**: Response procedures refined based on lessons learned
3. **Technology Enhancement**: Automated alerting reduced detection time 60%
4. **Team Cohesion**: Stable incident response team with low turnover

### 🔮 Performance Forecasting (Next 6 Months)
**If Current Trends Continue**:
- Training Completion: ↘️ Will reach 68% (Critical breach)
- Plans Currency: ↘️ Will reach 65% (Critical breach)  
- BIA Coverage: ↗️ Will reach 90+ % (Excellent performance)
- CAPA Performance: → Will stabilize around 87-92%

**Intervention Impact Modeling**:
- Training resource increase (+30%): Projects 85% completion by Q3
- Plan review process improvement: Projects 80% currency by Q4
- Combined interventions: Projects overall health score >85
```

### Step 3: Management Review Preparation
```python
# Prepare comprehensive management review materials
def prepare_management_review(kpi_results, trend_analysis, period_summary):
    management_review_package = {
        "executive_summary": create_executive_summary(kpi_results),
        "performance_dashboard": create_visual_dashboard(kpi_results, trend_analysis),
        "strategic_insights": generate_strategic_insights(trend_analysis),
        "resource_recommendations": develop_resource_recommendations(kpi_results),
        "investment_priorities": identify_investment_priorities(trend_analysis),
        "risk_assessment": assess_performance_risks(kpi_results, trend_analysis),
        "action_plan": create_management_action_plan(kpi_results, trend_analysis)
    }
    
    # Prepare presentation materials
    presentation_materials = {
        "slides": generate_presentation_slides(management_review_package),
        "talking_points": create_talking_points(management_review_package),
        "appendices": compile_supporting_data(kpi_results, trend_analysis)
    }
    
    return compile_complete_review_package(management_review_package, presentation_materials)
```

**Management Review Package**:
```
## Q1 2024 BCM Management Review

### 📊 Executive Summary for Leadership

**BCM System Health**: 78/100 (Good performance with targeted improvements needed)

**Key Decisions Required**:
1. **Training Resource Investment**: $25,000 additional budget to address 9-point gap
2. **Plan Review Process Enhancement**: Process improvement initiative approval
3. **Performance Monitoring Automation**: $15,000 system enhancement investment

**Strategic Highlights**:
- BIA program transformation delivering excellent results (+26% coverage)
- Incident response capabilities consistently exceeding targets
- Two performance areas requiring immediate management attention

### 🎯 Leadership Dashboard

#### Financial Performance Impact
**Cost Avoidance Achieved**: $340,000 (faster incident response, improved planning)
**Investment Required**: $40,000 (training resources + process improvements)
**ROI Projection**: 8.5:1 over 12 months

#### Compliance and Risk Posture
**ISO 22301 Compliance**: 87% (Target: 90% by year-end)
**Risk Exposure**: Medium (concentrated in training and plan currency)
**Regulatory Standing**: Good (no significant compliance issues)

#### Organizational Readiness
**Staff Competency**: 76% (Below target, trending down)
**Process Maturity**: 84% (Above target, stable)
**Technology Enablement**: 91% (Excellent, continuing to improve)

### 💼 Strategic Recommendations for Leadership

#### Immediate Actions (Next 30 Days)
1. **Approve Training Resource Increase**
   - **Investment**: $25,000 additional Q1-Q2 budget
   - **Expected Impact**: Training completion 76% → 85%
   - **Risk Mitigation**: Addresses staff readiness concerns

2. **Initiate Plan Review Process Improvement**
   - **Resource Requirement**: 40 hours process analysis
   - **Expected Impact**: Plan currency 72% → 80%
   - **Timeline**: 60-day improvement initiative

#### Strategic Initiatives (Next 90 Days)
3. **Performance Monitoring System Enhancement**
   - **Investment**: $15,000 system upgrade
   - **Benefit**: Real-time alerting, predictive analytics
   - **Impact**: Proactive management of all KPIs

4. **BCM Center of Excellence Establishment**
   - **Resource**: 1 FTE dedicated BCM analyst
   - **Benefit**: Sustained performance improvement
   - **ROI**: Projected 12:1 over 24 months

### 🚨 Risk Assessment and Mitigation

#### High Priority Risks
**Risk #1: Training Competency Gap**
- **Probability**: High (trend deteriorating)
- **Impact**: High (affects response capability)
- **Mitigation**: Resource investment + delivery method revision

**Risk #2: Plan Currency Degradation**  
- **Probability**: Medium (manageable with process improvement)
- **Impact**: Medium (affects response effectiveness)
- **Mitigation**: Process streamlining + resource reallocation

#### Emerging Risks
**Risk #3: Performance Monitoring Gaps**
- **Early Warning**: Manual tracking limitations evident
- **Proactive Mitigation**: Automated monitoring system deployment

### 📅 Management Actions and Decisions

**Decision Point #1**: Training budget increase approval
- **Options**: A) $25K increase B) Status quo C) Alternative delivery methods
- **Recommendation**: Option A (highest ROI, addresses root cause)

**Decision Point #2**: Plan review process improvement
- **Options**: A) Process redesign B) Additional resources C) Technology solution
- **Recommendation**: Option A + C (combined approach)

**Decision Point #3**: Performance monitoring enhancement
- **Options**: A) System upgrade B) Manual process improvement C) Hybrid approach  
- **Recommendation**: Option A (long-term sustainability)

### 📈 Success Metrics and Accountability

**Q2 2024 Targets** (Post-intervention):
- Training Completion: 85% (vs current 76%)
- Plans Up-to-date: 80% (vs current 72%)  
- Overall Health Score: 85+ (vs current 78)

**Accountability Framework**:
- **BCM Manager**: Training program recovery + plan process improvement
- **IT Manager**: Performance monitoring system deployment
- **Senior Leadership**: Resource approval + strategic guidance

**Next Review**: June 15, 2024 (Q2 results + intervention effectiveness)
```

### Step 4: Performance Alerting and Automated Monitoring
```python
# Implement automated performance monitoring and alerting
def setup_performance_monitoring(kpi_thresholds, alert_configurations):
    monitoring_rules = []
    
    for kpi_name, threshold_config in kpi_thresholds.items():
        monitoring_rule = {
            "kpi": kpi_name,
            "thresholds": {
                "critical": threshold_config["critical"],
                "warning": threshold_config["warning"],
                "target": threshold_config["target"]
            },
            "trend_monitoring": {
                "consecutive_declines": 3,  # Alert after 3 consecutive declines
                "velocity_threshold": -5,   # Alert if declining >5% per period
                "forecast_breach": 60       # Alert if forecast shows breach in 60 days
            },
            "alert_actions": {
                "critical": ["immediate_notification", "escalation_protocol"],
                "warning": ["standard_notification", "trend_monitoring"], 
                "forecast": ["proactive_notification", "planning_alert"]
            }
        }
        monitoring_rules.append(monitoring_rule)
    
    # Deploy monitoring configuration
    deploy_monitoring_system(monitoring_rules)
    return activate_automated_alerting(monitoring_rules, alert_configurations)
```

### Step 5: Continuous Improvement Integration
```python
# Integrate KPI insights into continuous improvement cycle
def integrate_performance_insights(kpi_analysis, improvement_opportunities):
    improvement_actions = []
    
    # Generate improvement initiatives based on KPI trends
    for kpi_issue in improvement_opportunities:
        improvement_action = {
            "area": kpi_issue.kpi_name,
            "root_cause": kpi_issue.root_causes,
            "proposed_solution": generate_solution_options(kpi_issue),
            "resource_requirements": estimate_resource_needs(kpi_issue),
            "expected_impact": project_improvement_impact(kpi_issue),
            "implementation_timeline": create_implementation_plan(kpi_issue),
            "success_metrics": define_success_criteria(kpi_issue)
        }
        improvement_actions.append(improvement_action)
    
    # Prioritize improvements by impact and feasibility
    prioritized_improvements = prioritize_improvements(improvement_actions)
    
    # Create integrated improvement program
    improvement_program = create_improvement_program(prioritized_improvements)
    
    return launch_improvement_initiatives(improvement_program)
```

## Activity Logging and Integration

### KPI Workflow Events
```python
kpi_workflow_events = [
    {
        "event_type": "assistant.activity",
        "data": {
            "intent": "kpi_calculate",
            "workflow": "performance_monitoring",
            "phase": "calculation_complete",
            "kpi_results": {
                "bia_coverage": 84.0,
                "plans_up_to_date": 72.0,
                "capa_on_time": 89.0,
                "incident_response_time": 3.2,
                "training_completion": 76.0,
                "overall_health_score": 78
            },
            "threshold_breaches": [
                {"kpi": "training_completion", "current": 76, "target": 85, "severity": "warning"},
                {"kpi": "plans_up_to_date", "current": 72, "target": 75, "severity": "warning"}
            ],
            "trend_analysis": {
                "improving": ["bia_coverage", "incident_response_time"],
                "declining": ["training_completion", "plans_up_to_date"],
                "stable": ["capa_on_time", "exercise_completion"]
            },
            "status": "analysis_complete"
        }
    },
    {
        "event_type": "assistant.activity", 
        "data": {
            "intent": "management_review_prepare",
            "workflow": "management_reporting",
            "phase": "review_package_complete",
            "review_summary": {
                "period": "Q1_2024",
                "overall_health": 78,
                "decisions_required": 3,
                "investment_requested": 40000,
                "projected_roi": 8.5
            },
            "recommendations": [
                {"priority": "high", "area": "training_resources", "investment": 25000},
                {"priority": "high", "area": "plan_review_process", "investment": 0},
                {"priority": "medium", "area": "monitoring_automation", "investment": 15000}
            ],
            "next_review": "2024-06-15",
            "status": "ready_for_presentation"
        }
    }
]
```

## Integration with BCM Framework

### Data Sources for KPI Calculation
- **Odoo BCM Modules**: Process data, plan information, training records
- **EventBus History**: Incident timelines, response metrics, activity logs
- **Exercise Results**: Performance validation data, competency assessments
- **Document Analysis**: Compliance scores, document currency tracking
- **CAPA Management**: Corrective action completion rates and effectiveness

### KPI-Driven Workflow Triggers
- **Low BIA Coverage** → Trigger BIA generation workflow
- **Outdated Plans** → Trigger plan generation workflow
- **Poor Incident Response** → Trigger exercise scheduling workflow
- **CAPA Delays** → Trigger audit and corrective action workflow
- **Training Gaps** → Trigger competency development programs

### Management Integration
- **Strategic Planning**: KPI trends inform BCM strategy development
- **Resource Allocation**: Performance data guides budget and staffing decisions
- **Risk Management**: KPI degradation triggers risk assessments and mitigation
- **Compliance Management**: Performance metrics validate regulatory compliance
- **Continuous Improvement**: KPI analysis drives systematic enhancement programs

This comprehensive KPI workflow ensures data-driven BCM system management, enabling proactive performance management and strategic decision-making based on objective performance indicators.
