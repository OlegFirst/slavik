"""Configuration for TheHive Adapter"""

import os
from typing import Optional, Dict, List

class Config:
    """Configuration management for TheHive Adapter"""
    
    # Redis and EventBus
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    EVENTBUS_URL: str = os.getenv("EVENTBUS_URL", "http://localhost:8001")
    
    # TheHive Configuration
    THEHIVE_URL: str = os.getenv("THEHIVE_URL", "http://localhost:9000")
    THEHIVE_API_KEY: str = os.getenv("THEHIVE_API_KEY", "")
    THEHIVE_ORG: str = os.getenv("THEHIVE_ORG", "bcm-platform")
    
    # Integration Settings
    AUTO_CREATE_CASES: bool = os.getenv("AUTO_CREATE_CASES", "true").lower() == "true"
    AUTO_CLOSE_CASES: bool = os.getenv("AUTO_CLOSE_CASES", "true").lower() == "true"
    SYNC_CASE_UPDATES: bool = os.getenv("SYNC_CASE_UPDATES", "true").lower() == "true"
    
    # Default Case Settings
    DEFAULT_SEVERITY: int = int(os.getenv("DEFAULT_SEVERITY", "2"))  # Medium
    DEFAULT_TLP: int = int(os.getenv("DEFAULT_TLP", "2"))  # AMBER
    DEFAULT_PAP: int = int(os.getenv("DEFAULT_PAP", "2"))  # AMBER
    
    # Task Automation
    CREATE_INITIAL_TASKS: bool = os.getenv("CREATE_INITIAL_TASKS", "true").lower() == "true"
    
    # Webhook Configuration
    WEBHOOK_SECRET: Optional[str] = os.getenv("WEBHOOK_SECRET")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8004"))
    
    # Processing Limits
    MAX_CONCURRENT_CASES: int = int(os.getenv("MAX_CONCURRENT_CASES", "10"))
    CASE_CREATION_TIMEOUT: int = int(os.getenv("CASE_CREATION_TIMEOUT", "30"))  # seconds
    
    # Retry Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "5"))  # seconds
    BACKOFF_MULTIPLIER: float = float(os.getenv("BACKOFF_MULTIPLIER", "2.0"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    API_KEY: Optional[str] = os.getenv("API_KEY")
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8081").split(",")
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    def __init__(self):
        """Initialize configuration and validate settings"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        if not self.THEHIVE_URL:
            raise ValueError("THEHIVE_URL is required")
        
        if not self.THEHIVE_API_KEY:
            raise ValueError("THEHIVE_API_KEY is required")
        
        if self.DEFAULT_SEVERITY not in [1, 2, 3, 4]:
            raise ValueError("DEFAULT_SEVERITY must be 1-4")
        
        if self.DEFAULT_TLP not in [0, 1, 2, 3]:
            raise ValueError("DEFAULT_TLP must be 0-3")
        
        if self.DEFAULT_PAP not in [0, 1, 2, 3]:
            raise ValueError("DEFAULT_PAP must be 0-3")
    
    @property
    def redis_config(self) -> Dict[str, any]:
        """Redis connection configuration"""
        return {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "max_connections": 20,
            "retry_on_timeout": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5
        }
    
    @property
    def thehive_config(self) -> Dict[str, any]:
        """TheHive client configuration"""
        return {
            "url": self.THEHIVE_URL,
            "api_key": self.THEHIVE_API_KEY,
            "org": self.THEHIVE_ORG,
            "timeout": self.CASE_CREATION_TIMEOUT,
            "max_retries": self.MAX_RETRIES,
            "retry_delay": self.RETRY_DELAY
        }
    
    @property
    def case_defaults(self) -> Dict[str, any]:
        """Default case settings"""
        return {
            "severity": self.DEFAULT_SEVERITY,
            "tlp": self.DEFAULT_TLP,
            "pap": self.DEFAULT_PAP,
            "source": "BCM Platform",
            "create_tasks": self.CREATE_INITIAL_TASKS
        }
    
    @property
    def task_templates(self) -> Dict[str, List[str]]:
        """Task templates by incident type"""
        return {
            "security": [
                "Initial triage and assessment",
                "Containment and isolation",
                "Evidence preservation",
                "Malware analysis",
                "Impact assessment",
                "Stakeholder notification",
                "Recovery planning",
                "Lessons learned documentation"
            ],
            "operational": [
                "Service impact assessment",
                "Immediate response actions",
                "Root cause investigation", 
                "Service restoration",
                "Business impact analysis",
                "Communication plan execution",
                "Post-incident review"
            ],
            "compliance": [
                "Compliance gap analysis",
                "Regulatory notification",
                "Evidence collection",
                "Remediation planning",
                "Audit trail documentation",
                "Management reporting"
            ],
            "technical": [
                "Technical investigation",
                "System diagnostics",
                "Performance analysis",
                "Configuration review",
                "Fix implementation",
                "Testing and validation"
            ],
            "business": [
                "Business impact assessment",
                "Stakeholder communication",
                "Resource allocation",
                "Continuity plan activation",
                "Recovery coordination",
                "Business resumption"
            ]
        }
    
    @property
    def severity_mapping(self) -> Dict[str, int]:
        """BCM to TheHive severity mapping"""
        return {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
    
    @property
    def observable_type_mapping(self) -> Dict[str, str]:
        """BCM to TheHive observable type mapping"""
        return {
            "ip_address": "ip",
            "domain_name": "domain",
            "url": "url",
            "email": "mail",
            "file_hash": "hash",
            "filename": "filename",
            "registry_key": "registry",
            "user_agent": "user-agent",
            "other": "other"
        }
    
    def get_task_template(self, incident_type: str) -> List[str]:
        """Get task template for incident type"""
        return self.task_templates.get(incident_type.lower(), self.task_templates["operational"])
    
    def map_severity(self, bcm_severity: str) -> int:
        """Map BCM severity to TheHive severity"""
        return self.severity_mapping.get(bcm_severity.lower(), self.DEFAULT_SEVERITY)
    
    def map_observable_type(self, bcm_type: str) -> str:
        """Map BCM observable type to TheHive type"""
        return self.observable_type_mapping.get(bcm_type.lower(), "other")
