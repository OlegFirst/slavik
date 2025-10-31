"""
Consolidated Pydantic Models
Combines strict typing (from colleagues) with our flexible orchestration
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator


# ===== ENUMS =====

class OrchestratorType(str, Enum):
    SYSTEM = "system"
    BRIDGE = "bridge"
    PROGRAM = "program"
    CLIENT = "client"
    SANDBOX = "sandbox"


class RequestType(str, Enum):
    # System-level
    HEALTH_CHECK = "health-check"
    METRICS = "metrics"
    EVENT_PROCESS = "event-process"

    # Bridge-level
    TRANSLATE = "translate"
    ENRICH_CONTEXT = "enrich-context"
    INTELLIGENT_ROUTE = "intelligent-route"

    # Program-level
    BUSINESS_LOGIC = "business-logic"
    DOMAIN_OPERATION = "domain-operation"
    MODULE_EXECUTE = "module-execute"

    # Client-level
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    SECURITY_CHECK = "security-check"

    # Sandbox-level
    EXPERIMENT = "experiment"
    EVOLVE = "evolve"
    OPTIMIZE = "optimize"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    ERROR = "error"


class ExperimentStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ===== BASE MODELS =====

class BaseRequest(BaseModel):
    """Base request model for all orchestrators"""
    type: RequestType
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = {}

    class Config:
        use_enum_values = True


class BaseResponse(BaseModel):
    """Base response model for all orchestrators"""
    success: bool
    request_id: Optional[str] = None
    duration: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_by: Optional[str] = None

    class Config:
        use_enum_values = True


# ===== SYSTEM ORCHESTRATOR MODELS =====

class SystemRequest(BaseRequest):
    """System-level requests (events, workflows, data, AI, monitoring)"""
    component: Optional[str] = None
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = {}
    priority: Optional[int] = 1

    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Priority must be between 1 and 10')
        return v


class SystemResponse(BaseResponse):
    """System orchestrator response"""
    component: Optional[str] = None
    events: List[Dict[str, Any]] = []
    metrics: Optional[Dict[str, Any]] = None


# ===== BRIDGE ORCHESTRATOR MODELS =====

class BridgeRequest(BaseRequest):
    """AI-powered bridge requests (translation, enrichment, routing)"""
    from_level: Optional[str] = None
    to_level: Optional[str] = None
    data: Dict[str, Any]
    translation_needed: Optional[bool] = None
    enrichment_level: Optional[str] = "standard"

    @validator('enrichment_level')
    def validate_enrichment(cls, v):
        allowed = ["minimal", "standard", "comprehensive"]
        if v not in allowed:
            raise ValueError(f'Enrichment level must be one of: {allowed}')
        return v


class BridgeResponse(BaseResponse):
    """Bridge orchestrator response with AI insights"""
    original_data: Dict[str, Any]
    translated_data: Optional[Dict[str, Any]] = None
    enriched_context: Optional[Dict[str, Any]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    cached: Optional[bool] = False


# ===== PROGRAM ORCHESTRATOR MODELS =====

class ProgramRequest(BaseRequest):
    """Program/business logic requests"""
    domain: str = Field(..., description="Domain (e.g., 'bcm', 'security')")
    module: str = Field(..., description="Module name")
    action: str = Field(..., description="Action to perform")
    data: Dict[str, Any] = Field(default_factory=dict)
    user_context: Optional[Dict[str, Any]] = {}

    @validator('domain')
    def validate_domain(cls, v):
        # Allow any domain for universal architecture
        if not v or len(v) < 2:
            raise ValueError('Domain must be at least 2 characters')
        return v.lower()


class ProgramResponse(BaseResponse):
    """Program orchestrator response"""
    domain: str
    module: str
    action: str
    result: Dict[str, Any]
    user_personalization: Optional[Dict[str, Any]] = None


# ===== CLIENT ORCHESTRATOR MODELS =====

class ClientRequest(BaseRequest):
    """Client infrastructure requests (auth, security, API)"""
    client_id: Optional[str] = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = {}

    class Config:
        fields = {'credentials': {'write_only': True}}


class ClientResponse(BaseResponse):
    """Client orchestrator response"""
    authenticated: Optional[bool] = None
    authorized: Optional[bool] = None
    security_passed: Optional[bool] = None
    session_data: Optional[Dict[str, Any]] = None
    rate_limit_remaining: Optional[int] = None


# ===== SANDBOX ORCHESTRATOR MODELS =====

class ExperimentConstraints(BaseModel):
    """Safety constraints for sandbox experiments"""
    max_memory_mb: Optional[int] = 512
    max_cpu_seconds: Optional[int] = 30
    max_network_calls: Optional[int] = 10
    allowed_domains: List[str] = []
    blocked_operations: List[str] = ["file_write", "system_call"]


class SandboxRequest(BaseRequest):
    """Sandbox experimentation requests"""
    experiment_type: Optional[str] = "performance"
    code: Optional[str] = None
    component: Optional[str] = None
    constraints: Optional[ExperimentConstraints] = None
    auto_run: Optional[bool] = False
    generations: Optional[int] = 10

    @validator('generations')
    def validate_generations(cls, v):
        if v is not None and (v < 1 or v > 1000):
            raise ValueError('Generations must be between 1 and 1000')
        return v


class ExperimentResult(BaseModel):
    """Experiment execution result"""
    experiment_id: str
    status: ExperimentStatus
    output: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    resource_usage: Optional[Dict[str, Any]] = None
    errors: List[str] = []
    warnings: List[str] = []
    improvement_factor: Optional[float] = None


class SandboxResponse(BaseResponse):
    """Sandbox orchestrator response"""
    experiment: Optional[ExperimentResult] = None
    evolution_result: Optional[Dict[str, Any]] = None
    optimization_suggestions: List[str] = []


# ===== SPECIALIZED BCM MODELS =====

class BusinessLogicRequest(BaseRequest):
    """BCM-specific business logic request"""
    module: str = Field(..., description="BCM module (e.g., 'risk-assessment')")
    action: str = Field(..., description="Action (e.g., 'assess', 'calculate')")
    data: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = {}

    @validator('module')
    def validate_bcm_module(cls, v):
        bcm_modules = [
            "risk-assessment", "business-impact-analysis", "incident-management",
            "plans", "training", "audit", "governance", "reporting"
        ]
        if v not in bcm_modules:
            # Allow any module for extensibility, just warn
            pass
        return v


class ExperimentRequest(BaseRequest):
    """Experiment creation request"""
    name: Optional[str] = None
    code: str = Field(..., description="Code to experiment with")
    experiment_type: Optional[str] = "performance"
    constraints: Optional[ExperimentConstraints] = None
    expected_outcome: Optional[Dict[str, Any]] = None
    auto_run: Optional[bool] = True


# ===== SYSTEM STATUS MODELS =====

class OrchestratorHealth(BaseModel):
    """Individual orchestrator health"""
    name: str
    status: HealthStatus
    services_loaded: int
    services_healthy: int
    uptime: float
    memory_usage: Optional[Dict[str, Any]] = None
    last_error: Optional[str] = None


class InfrastructureHealth(BaseModel):
    """Infrastructure component health"""
    redis: bool
    postgres: bool
    docker: bool
    details: Optional[Dict[str, Any]] = {}


class HealthResponse(BaseResponse):
    """Comprehensive system health response"""
    status: HealthStatus
    cognitive_orchestrators: Optional[Dict[str, OrchestratorHealth]] = {}
    infrastructure: Optional[InfrastructureHealth] = None
    error: Optional[str] = None


class MetricsData(BaseModel):
    """System metrics data"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    uptime: float = 0.0


class MetricsResponse(BaseResponse):
    """Comprehensive metrics response"""
    cognitive: Optional[MetricsData] = None
    infrastructure: Optional[Dict[str, Any]] = {}
    recent_operations: List[Dict[str, Any]] = []


# ===== EVOLUTION MODELS =====

class EvolutionParameters(BaseModel):
    """Parameters for AI evolution"""
    population_size: Optional[int] = 50
    generations: Optional[int] = 100
    mutation_rate: Optional[float] = 0.1
    crossover_rate: Optional[float] = 0.8
    selection_pressure: Optional[float] = 0.7
    fitness_threshold: Optional[float] = 0.8

    @validator('mutation_rate', 'crossover_rate', 'selection_pressure', 'fitness_threshold')
    def validate_rates(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Rate values must be between 0.0 and 1.0')
        return v


# ===== ERROR MODELS =====

class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = False
    error: ErrorDetail
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== CONFIGURATION MODELS =====

class OrchestratorConfig(BaseModel):
    """Configuration for individual orchestrators"""
    max_concurrent_requests: Optional[int] = 100
    request_timeout: Optional[int] = 30
    retry_attempts: Optional[int] = 3
    fallback_enabled: Optional[bool] = True
    caching_enabled: Optional[bool] = True
    cache_ttl: Optional[int] = 300


class SystemConfig(BaseModel):
    """Overall system configuration"""
    redis_url: Optional[str] = "redis://localhost:6379"
    postgres_url: Optional[str] = "postgresql://localhost:5432/cognitive_orchestration"
    docker_socket: Optional[str] = "unix:///var/run/docker.sock"
    log_level: Optional[str] = "INFO"
    orchestrators: Optional[Dict[str, OrchestratorConfig]] = {}


# Model exports for easy importing
__all__ = [
    # Enums
    "OrchestratorType", "RequestType", "HealthStatus", "ExperimentStatus",

    # Base models
    "BaseRequest", "BaseResponse",

    # Orchestrator models
    "SystemRequest", "SystemResponse",
    "BridgeRequest", "BridgeResponse",
    "ProgramRequest", "ProgramResponse",
    "ClientRequest", "ClientResponse",
    "SandboxRequest", "SandboxResponse",

    # Specialized models
    "BusinessLogicRequest", "ExperimentRequest",
    "ExperimentConstraints", "ExperimentResult",
    "EvolutionParameters",

    # Status models
    "HealthResponse", "MetricsResponse",
    "OrchestratorHealth", "InfrastructureHealth",
    "MetricsData",

    # Error models
    "ErrorDetail", "ErrorResponse",

    # Config models
    "OrchestratorConfig", "SystemConfig"
]