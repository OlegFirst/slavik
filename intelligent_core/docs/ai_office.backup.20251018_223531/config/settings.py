"""Settings configuration using pydantic-settings"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Anthropic Claude
    anthropic_api_key: str

    # Service
    service_port: int = 8031
    service_host: str = "0.0.0.0"
    log_level: str = "INFO"

    # Database
    postgres_url: str

    # Redis
    redis_url: str = "redis://redis:6379"

    # BCM Modules
    governance_url: str = "http://governance:8020"
    bia_url: str = "http://bia:8012"
    risk_url: str = "http://risk:8013"
    planning_url: str = "http://planning:8005"
    plans_url: str = "http://plans:8023"
    response_url: str = "http://response:8007"
    compliance_url: str = "http://compliance:8006"
    validation_url: str = "http://validation:8022"
    documents_url: str = "http://documents:8024"
    learning_url: str = "http://learning:8021"

    # EventBus
    eventbus_url: str = "http://eventbus:8001"

    # AI Configuration
    default_model: str = "sonnet"
    max_tokens: int = 4096
    temperature: float = 0.7

    # RAG Configuration
    max_context_items: int = 10
    context_retrieval_timeout: int = 10

    # Colleague Configuration
    enable_all_colleagues: bool = True
    default_colleague: str = "compliance_copilot"

    @property
    def bcm_module_urls(self) -> Dict[str, str]:
        """Get all BCM module URLs as dict"""
        return {
            "governance": self.governance_url,
            "bia": self.bia_url,
            "risk": self.risk_url,
            "planning": self.planning_url,
            "plans": self.plans_url,
            "response": self.response_url,
            "compliance": self.compliance_url,
            "validation": self.validation_url,
            "documents": self.documents_url,
            "learning": self.learning_url
        }


# Global settings instance
settings = Settings()
