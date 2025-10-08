"""
Analytics Models
================

Data models for Analytics Specialist AI Colleague.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class SeverityLevel(str, Enum):
    """Severity level for insights"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompetencyLevel(str, Enum):
    """Analytics Specialist competency level"""
    JUNIOR = "junior"      # Week 1-2: Basic process mining
    MIDDLE = "middle"      # Week 3-6: Platform intelligence
    SENIOR = "senior"      # Week 7+: Predictive analytics
    EXPERT = "expert"      # Month 4+: Digital twin foundation


class AnalysisType(str, Enum):
    """Type of analysis"""
    PLATFORM_HEALTH = "platform_health"
    PROCESS_MINING = "process_mining"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    SERVICE_DISCOVERY = "service_discovery"
    INCIDENT_INVESTIGATION = "incident_investigation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    CODE_QUALITY = "code_quality"
    PREDICTIVE = "predictive"


class InsightCategory(str, Enum):
    """Category of insight"""
    BOTTLENECK = "bottleneck"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_ISSUE = "security_issue"
    QUALITY_ISSUE = "quality_issue"
    IMPROVEMENT_OPPORTUNITY = "improvement_opportunity"
    PREDICTED_FAILURE = "predicted_failure"
    ANOMALY = "anomaly"


# ============================================================================
# CORE MODELS
# ============================================================================

class AnalyticsInsight(BaseModel):
    """
    A single analytics insight

    Represents a finding from analysis that requires attention.
    """
    id: str = Field(..., description="Unique insight ID")
    category: InsightCategory = Field(..., description="Insight category")
    severity: SeverityLevel = Field(..., description="Severity level")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")
    affected_components: List[str] = Field(default_factory=list, description="Affected services/modules")
    impact: str = Field(..., description="Impact description")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence/data")
    created_at: datetime = Field(default_factory=datetime.now, description="When insight was created")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "insight_001",
                "category": "bottleneck",
                "severity": "high",
                "title": "Approval step bottleneck detected",
                "description": "The approval_step in BIA workflow averages 48 hours",
                "affected_components": ["workflow_intelligence", "bia_workflow"],
                "impact": "Delays BIA completion by 2x SLA",
                "evidence": {"avg_duration_hours": 48, "sla_hours": 24},
                "created_at": "2025-10-08T10:00:00Z"
            }
        }


class AnalyticsRecommendation(BaseModel):
    """
    A recommended action based on insights

    Actionable recommendation to address insights.
    """
    id: str = Field(..., description="Unique recommendation ID")
    related_insight_id: str = Field(..., description="Related insight ID")
    action_type: str = Field(..., description="Type of action (fix, optimize, investigate)")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="What to do")
    priority: SeverityLevel = Field(..., description="Priority level")
    estimated_effort: str = Field(..., description="Effort estimate (low, medium, high)")
    expected_impact: str = Field(..., description="Expected impact")
    automated: bool = Field(default=False, description="Can be automated?")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rec_001",
                "related_insight_id": "insight_001",
                "action_type": "optimize",
                "title": "Allocate additional approvers",
                "description": "Add 2 more approvers to BIA approval step",
                "priority": "high",
                "estimated_effort": "low",
                "expected_impact": "Reduce approval time by 50%",
                "automated": True,
                "created_at": "2025-10-08T10:00:00Z"
            }
        }


class AnalyticsReport(BaseModel):
    """
    Complete analytics report

    Contains insights, recommendations, and metadata from analysis.
    """
    id: str = Field(..., description="Unique report ID")
    analysis_type: AnalysisType = Field(..., description="Type of analysis")
    generated_at: datetime = Field(default_factory=datetime.now, description="When report was generated")
    generated_by: CompetencyLevel = Field(..., description="Competency level of specialist")

    summary: str = Field(..., description="Executive summary")
    overall_health_score: Optional[float] = Field(None, ge=0, le=100, description="Overall health score (0-100)")

    insights: List[AnalyticsInsight] = Field(default_factory=list, description="All insights found")
    recommendations: List[AnalyticsRecommendation] = Field(default_factory=list, description="All recommendations")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def critical_insights(self) -> List[AnalyticsInsight]:
        """Get only critical insights"""
        return [i for i in self.insights if i.severity == SeverityLevel.CRITICAL]

    @property
    def high_severity_insights(self) -> List[AnalyticsInsight]:
        """Get high and critical insights"""
        return [i for i in self.insights if i.severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "report_20251008_100000",
                "analysis_type": "platform_health",
                "generated_at": "2025-10-08T10:00:00Z",
                "generated_by": "middle",
                "summary": "Found 3 bottlenecks, 2 dependency conflicts",
                "overall_health_score": 78.5,
                "insights": [],
                "recommendations": [],
                "metadata": {"total_services_analyzed": 15}
            }
        }


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """Request for analysis"""
    analysis_type: AnalysisType = Field(..., description="Type of analysis to perform")
    target: Optional[str] = Field(None, description="Specific target (service, module, incident_id)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")
    requester: str = Field(..., description="Who requested (service name or user)")


class HealthCheckResponse(BaseModel):
    """Response from health check endpoint"""
    status: str = Field(..., description="Health status (healthy, degraded, unhealthy)")
    version: str = Field(..., description="Service version")
    competency_level: CompetencyLevel = Field(..., description="Current competency level")
    available_tools: List[str] = Field(..., description="Available analysis tools")
    uptime_seconds: float = Field(..., description="Uptime in seconds")


class InsightsResponse(BaseModel):
    """Response containing insights"""
    insights: List[AnalyticsInsight] = Field(..., description="Insights")
    recommendations: List[AnalyticsRecommendation] = Field(..., description="Recommendations")
    total_count: int = Field(..., description="Total insights")
    critical_count: int = Field(..., description="Critical insights count")


# ============================================================================
# MIO MANAGER INTEGRATION MODELS
# ============================================================================

class MIOEventInsight(BaseModel):
    """
    Event insight to report to MIO Manager

    Follows MIO Manager's expected format for event insights.
    """
    source: str = Field(default="analytics-specialist", description="Source service")
    event_type: str = Field(..., description="Event type (health_check, incident_investigation, etc)")
    severity: SeverityLevel = Field(..., description="Severity level")

    critical_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Critical issues found")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Recommended actions")

    summary: str = Field(..., description="Summary of insights")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "analytics-specialist",
                "event_type": "daily_health_check",
                "severity": "high",
                "critical_issues": [
                    {
                        "title": "3 workflow bottlenecks detected",
                        "affected_components": ["workflow_intelligence"],
                        "impact": "2x SLA delays"
                    }
                ],
                "recommendations": [
                    {
                        "action": "allocate_additional_resources",
                        "target": "approval_step",
                        "automated": True
                    }
                ],
                "summary": "Platform health: 78.5/100. Found 3 bottlenecks, 2 conflicts.",
                "metadata": {"health_score": 78.5},
                "timestamp": "2025-10-08T10:00:00Z"
            }
        }


class MIOTaskDelegation(BaseModel):
    """
    Task delegation request to MIO Manager

    Request MIO Manager to delegate task to Orchestrator.
    """
    title: str = Field(..., description="Task title")
    source: str = Field(default="analytics-specialist", description="Source")
    priority: str = Field(..., description="Priority (low, medium, high, critical)")
    actions: List[Dict[str, Any]] = Field(..., description="Actions to take")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Fix critical platform bottlenecks",
                "source": "analytics-specialist",
                "priority": "high",
                "actions": [
                    {
                        "type": "allocate_resources",
                        "target": "approval_step",
                        "count": 2
                    }
                ],
                "metadata": {"related_insights": ["insight_001", "insight_002"]}
            }
        }


# ============================================================================
# TOOL MODELS
# ============================================================================

class ToolMetadata(BaseModel):
    """Metadata about an analysis tool"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="What tool does")
    competency_required: CompetencyLevel = Field(..., description="Minimum competency level")
    enabled: bool = Field(default=True, description="Is tool enabled?")
    last_used: Optional[datetime] = Field(None, description="When last used")
    usage_count: int = Field(default=0, description="How many times used")


class PlatformHealthMetrics(BaseModel):
    """Platform health metrics"""
    health_score: float = Field(..., ge=0, le=100, description="Overall health (0-100)")
    total_services: int = Field(..., description="Total services analyzed")
    healthy_services: int = Field(..., description="Healthy services")
    degraded_services: int = Field(..., description="Degraded services")
    unhealthy_services: int = Field(..., description="Unhealthy services")
    total_bottlenecks: int = Field(..., description="Total bottlenecks found")
    total_conflicts: int = Field(..., description="Total conflicts found")
    total_warnings: int = Field(..., description="Total warnings")
    timestamp: datetime = Field(default_factory=datetime.now)


class ProcessMiningMetrics(BaseModel):
    """Process mining analysis results"""
    process_id: str = Field(..., description="Process ID")
    total_executions: int = Field(..., description="Total executions analyzed")
    avg_duration_minutes: float = Field(..., description="Average duration")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate (0-1)")
    bottlenecks: List[Dict[str, Any]] = Field(default_factory=list, description="Bottlenecks found")
    patterns: List[Dict[str, Any]] = Field(default_factory=list, description="Patterns discovered")
    deviations: List[Dict[str, Any]] = Field(default_factory=list, description="Deviations detected")


class DependencyAnalysisResult(BaseModel):
    """Dependency analysis results"""
    total_services: int = Field(..., description="Total services")
    total_dependencies: int = Field(..., description="Total dependencies")
    circular_dependencies: List[List[str]] = Field(default_factory=list, description="Circular deps")
    missing_dependencies: List[Dict[str, str]] = Field(default_factory=list, description="Missing deps")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Version conflicts")
    health_score: float = Field(..., ge=0, le=100, description="Dependency health (0-100)")
