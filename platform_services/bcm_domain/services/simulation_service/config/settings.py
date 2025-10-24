"""
Configuration Management for Simulation Service
Uses Pydantic Settings for type-safe configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ============================================================================
    # SERVICE CONFIGURATION
    # ============================================================================
    port: int = Field(default=8024, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    environment: str = Field(default="development", env="ENVIRONMENT")
    service_name: str = Field(default="simulation-service", env="SERVICE_NAME")
    api_version: str = Field(default="v1", env="API_VERSION")

    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    database_url: str = Field(
        default="postgresql://simulation_user:simulation_pass@localhost:5432/simulation_db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_cache_ttl: int = Field(default=3600, env="REDIS_CACHE_TTL")

    # ============================================================================
    # PLATFORM INTEGRATION
    # ============================================================================
    eventbus_url: str = Field(default="http://localhost:8055", env="EVENTBUS_URL")
    eventbus_redis_url: str = Field(default="redis://localhost:6379/1", env="EVENTBUS_REDIS_URL")
    eventbus_enabled: bool = Field(default=True, env="EVENTBUS_ENABLED")

    ai_orchestrator_url: str = Field(default="http://localhost:8026", env="AI_ORCHESTRATOR_URL")
    ai_orchestrator_enabled: bool = Field(default=True, env="AI_ORCHESTRATOR_ENABLED")

    workflow_intelligence_url: str = Field(default="http://localhost:8037", env="WORKFLOW_INTELLIGENCE_URL")
    workflow_intelligence_enabled: bool = Field(default=True, env="WORKFLOW_INTELLIGENCE_ENABLED")

    knowledge_center_url: str = Field(default="http://localhost:8038", env="KNOWLEDGE_CENTER_URL")
    knowledge_center_enabled: bool = Field(default=True, env="KNOWLEDGE_CENTER_ENABLED")

    community_intelligence_url: str = Field(default="http://localhost:8030", env="COMMUNITY_INTELLIGENCE_URL")
    community_intelligence_enabled: bool = Field(default=True, env="COMMUNITY_INTELLIGENCE_ENABLED")

    predictive_journey_url: str = Field(default="http://localhost:8031", env="PREDICTIVE_JOURNEY_URL")
    predictive_journey_enabled: bool = Field(default=True, env="PREDICTIVE_JOURNEY_ENABLED")

    ai_foundation_url: str = Field(default="http://localhost:8025", env="AI_FOUNDATION_URL")
    ai_foundation_enabled: bool = Field(default=True, env="AI_FOUNDATION_ENABLED")

    digital_twin_url: str = Field(default="http://localhost:8096", env="DIGITAL_TWIN_URL")
    digital_twin_enabled: bool = Field(default=False, env="DIGITAL_TWIN_ENABLED")

    # Scenario Orchestrator (existing service with AI generation & learning)
    scenario_orchestrator_url: str = Field(default="http://localhost:8085", env="SCENARIO_ORCHESTRATOR_URL")
    scenario_orchestrator_enabled: bool = Field(default=True, env="SCENARIO_ORCHESTRATOR_ENABLED")

    # ============================================================================
    # SIMULATION ENGINES
    # ============================================================================
    jaamsim_enabled: bool = Field(default=True, env="JAAMSIM_ENABLED")
    jaamsim_path: str = Field(default="/opt/jaamsim", env="JAAMSIM_PATH")
    jaamsim_jar: str = Field(default="JaamSim2023-03.jar", env="JAAMSIM_JAR")

    simpy_enabled: bool = Field(default=True, env="SIMPY_ENABLED")

    simulation_working_dir: str = Field(default="/tmp/simulations", env="SIMULATION_WORKING_DIR")
    simulation_cleanup_after_days: int = Field(default=7, env="SIMULATION_CLEANUP_AFTER_DAYS")

    max_concurrent_simulations: int = Field(default=5, env="MAX_CONCURRENT_SIMULATIONS")
    max_simulation_duration_hours: int = Field(default=8, env="MAX_SIMULATION_DURATION_HOURS")
    max_memory_per_simulation_mb: int = Field(default=2048, env="MAX_MEMORY_PER_SIMULATION_MB")
    max_cpu_cores_per_simulation: int = Field(default=2, env="MAX_CPU_CORES_PER_SIMULATION")

    # ============================================================================
    # AI/ML CONFIGURATION
    # ============================================================================
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    model_runner_url: str = Field(default="http://localhost:8088", env="MODEL_RUNNER_URL")

    default_llm_model: str = Field(default="gemma3:latest", env="DEFAULT_LLM_MODEL")
    llm_temperature: float = Field(default=0.8, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, env="LLM_MAX_TOKENS")

    rag_enabled: bool = Field(default=True, env="RAG_ENABLED")
    rag_collection_name: str = Field(default="simulation_scenarios", env="RAG_COLLECTION_NAME")
    rag_similarity_threshold: float = Field(default=0.7, env="RAG_SIMILARITY_THRESHOLD")

    ml_prediction_enabled: bool = Field(default=True, env="ML_PREDICTION_ENABLED")
    ml_model_path: Optional[str] = Field(default=None, env="ML_MODEL_PATH")

    # ============================================================================
    # VISUALIZATION CONFIGURATION
    # ============================================================================
    websocket_ping_interval: int = Field(default=30, env="WEBSOCKET_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")

    dashboard_refresh_interval: int = Field(default=5, env="DASHBOARD_REFRESH_INTERVAL")
    dashboard_max_datapoints: int = Field(default=1000, env="DASHBOARD_MAX_DATAPOINTS")

    # ============================================================================
    # REPORTING CONFIGURATION
    # ============================================================================
    report_storage_path: str = Field(default="/reports", env="REPORT_STORAGE_PATH")
    report_retention_days: int = Field(default=90, env="REPORT_RETENTION_DAYS")
    report_template_dir: str = Field(default="./analytics/reporting/templates", env="REPORT_TEMPLATE_DIR")

    pdf_font: str = Field(default="Helvetica", env="PDF_FONT")
    pdf_page_size: str = Field(default="A4", env="PDF_PAGE_SIZE")

    # ============================================================================
    # SECURITY
    # ============================================================================
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # ============================================================================
    # MONITORING & OBSERVABILITY
    # ============================================================================
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")

    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_output: str = Field(default="stdout", env="LOG_OUTPUT")

    health_check_interval_seconds: int = Field(default=30, env="HEALTH_CHECK_INTERVAL_SECONDS")

    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    spec_generator_enabled: bool = Field(default=True, env="SPEC_GENERATOR_ENABLED")
    spec_generator_use_ai: bool = Field(default=True, env="SPEC_GENERATOR_USE_AI")

    scenario_generator_enabled: bool = Field(default=True, env="SCENARIO_GENERATOR_ENABLED")
    scenario_generator_use_rag: bool = Field(default=True, env="SCENARIO_GENERATOR_USE_RAG")
    scenario_generator_use_community: bool = Field(default=True, env="SCENARIO_GENERATOR_USE_COMMUNITY")

    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    benchmarking_enabled: bool = Field(default=True, env="BENCHMARKING_ENABLED")
    kpi_calculation_enabled: bool = Field(default=True, env="KPI_CALCULATION_ENABLED")

    auto_pdca_enabled: bool = Field(default=True, env="AUTO_PDCA_ENABLED")
    auto_knowledge_storage: bool = Field(default=True, env="AUTO_KNOWLEDGE_STORAGE")
    auto_community_contribution: bool = Field(default=True, env="AUTO_COMMUNITY_CONTRIBUTION")
    auto_contribution_min_quality_score: float = Field(default=8.0, env="AUTO_CONTRIBUTION_MIN_QUALITY_SCORE")

    # ============================================================================
    # DEVELOPMENT/TESTING
    # ============================================================================
    debug: bool = Field(default=False, env="DEBUG")
    reload: bool = Field(default=False, env="RELOAD")

    test_database_url: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    mock_external_services: bool = Field(default=False, env="MOCK_EXTERNAL_SERVICES")

    enable_api_docs: bool = Field(default=True, env="ENABLE_API_DOCS")
    enable_openapi: bool = Field(default=True, env="ENABLE_OPENAPI")

    # ============================================================================
    # VALIDATORS
    # ============================================================================
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()

    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment"""
        valid_envs = ['development', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()

    @field_validator('llm_temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate LLM temperature"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    # ============================================================================
    # COMPUTED PROPERTIES
    # ============================================================================
    @property
    def jaamsim_executable(self) -> str:
        """Full path to JaamSim executable"""
        return os.path.join(self.jaamsim_path, self.jaamsim_jar)

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    @property
    def api_prefix(self) -> str:
        """API route prefix"""
        return f"/api/{self.api_version}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance

    Returns:
        Settings: Application settings
    """
    return Settings()


# Global settings instance
settings = get_settings()
