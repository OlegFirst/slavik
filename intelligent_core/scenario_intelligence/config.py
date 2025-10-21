"""
Configuration Management for Scenario Intelligence

Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = os.getenv('DATABASE_URL', '')

    @property
    def is_configured(self) -> bool:
        return bool(self.url)


@dataclass
class LLMConfig:
    """LLM configuration for L4 generation"""
    anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')

    provider: str = os.getenv('LLM_PROVIDER', 'anthropic')
    model_anthropic: str = os.getenv('LLM_MODEL_ANTHROPIC', 'claude-3-5-sonnet-20241022')
    model_openai: str = os.getenv('LLM_MODEL_OPENAI', 'gpt-4-turbo-preview')

    @property
    def is_configured(self) -> bool:
        if 'anthropic' in self.provider and self.anthropic_api_key:
            return True
        if 'openai' in self.provider and self.openai_api_key:
            return True
        return False


@dataclass
class QdrantConfig:
    """Qdrant vector database configuration"""
    host: str = os.getenv('QDRANT_HOST', 'localhost')
    port: int = int(os.getenv('QDRANT_PORT', '6333'))
    api_key: Optional[str] = os.getenv('QDRANT_API_KEY')

    collection: str = os.getenv('QDRANT_COLLECTION', 'scenario_intelligence')
    embedding_model: str = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.port)


@dataclass
class EventBusConfig:
    """EventBus configuration"""
    host: str = os.getenv('EVENTBUS_HOST', 'localhost')
    port: int = int(os.getenv('EVENTBUS_PORT', '6379'))
    enabled: bool = os.getenv('EVENTBUS_ENABLED', 'true').lower() == 'true'

    channel_catalog_updates: str = os.getenv('EVENTBUS_CHANNEL_CATALOG_UPDATES', 'catalog.service.updated')
    channel_scenario_generated: str = os.getenv('EVENTBUS_CHANNEL_SCENARIO_GENERATED', 'scenario.generated')
    channel_scenario_executed: str = os.getenv('EVENTBUS_CHANNEL_SCENARIO_EXECUTED', 'scenario.executed')

    @property
    def is_configured(self) -> bool:
        return self.enabled and bool(self.host and self.port)


@dataclass
class ServiceConfig:
    """API service configuration"""
    host: str = os.getenv('API_HOST', '0.0.0.0')
    port: int = int(os.getenv('API_PORT', '8060'))


@dataclass
class StorageConfig:
    """Storage backends configuration"""
    backends: List[str] = None
    default_storage: str = os.getenv('DEFAULT_STORAGE', 'postgres')

    def __post_init__(self):
        if self.backends is None:
            backends_str = os.getenv('STORAGE_BACKENDS', 'memory,postgres')
            self.backends = [b.strip() for b in backends_str.split(',')]

    @property
    def use_memory(self) -> bool:
        return 'memory' in self.backends

    @property
    def use_postgres(self) -> bool:
        return 'postgres' in self.backends

    @property
    def use_qdrant(self) -> bool:
        return 'qdrant' in self.backends


@dataclass
class GenerationConfig:
    """Scenario generation configuration"""
    auto_regeneration_enabled: bool = os.getenv('AUTO_REGENERATION_ENABLED', 'true').lower() == 'true'
    auto_regeneration_batch_window: int = int(os.getenv('AUTO_REGENERATION_BATCH_WINDOW_SECONDS', '30'))
    auto_regeneration_max_batch_size: int = int(os.getenv('AUTO_REGENERATION_MAX_BATCH_SIZE', '50'))

    timeout_seconds: int = int(os.getenv('GENERATION_TIMEOUT_SECONDS', '300'))


@dataclass
class ExecutionConfig:
    """Scenario execution configuration"""
    timeout_seconds: int = int(os.getenv('EXECUTION_TIMEOUT_SECONDS', '300'))
    max_retries: int = int(os.getenv('EXECUTION_MAX_RETRIES', '3'))
    save_to_db: bool = os.getenv('EXECUTION_SAVE_TO_DB', 'true').lower() == 'true'
    mock_actions: bool = os.getenv('EXECUTION_MOCK_ACTIONS', 'false').lower() == 'true'


@dataclass
class MonitoringConfig:
    """Monitoring and observability configuration"""
    mio_manager_host: str = os.getenv('MIO_MANAGER_HOST', 'localhost')
    mio_manager_port: int = int(os.getenv('MIO_MANAGER_PORT', '8020'))
    mio_manager_enabled: bool = os.getenv('MIO_MANAGER_ENABLED', 'true').lower() == 'true'

    metrics_port: int = int(os.getenv('METRICS_PORT', '9090'))
    metrics_path: str = os.getenv('METRICS_PATH', '/metrics')

    @property
    def is_configured(self) -> bool:
        return self.mio_manager_enabled and bool(self.mio_manager_host)


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    format: str = os.getenv('LOG_FORMAT', 'json')
    file: Optional[str] = os.getenv('LOG_FILE')


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling features"""
    l4_generation: bool = os.getenv('FEATURE_L4_GENERATION', 'true').lower() == 'true'
    semantic_search: bool = os.getenv('FEATURE_SEMANTIC_SEARCH', 'true').lower() == 'true'
    auto_regeneration: bool = os.getenv('FEATURE_AUTO_REGENERATION', 'true').lower() == 'true'
    execution_engine: bool = os.getenv('FEATURE_EXECUTION_ENGINE', 'true').lower() == 'true'


@dataclass
class Config:
    """Main configuration class"""
    database: DatabaseConfig
    llm: LLMConfig
    qdrant: QdrantConfig
    eventbus: EventBusConfig
    service: ServiceConfig
    storage: StorageConfig
    generation: GenerationConfig
    execution: ExecutionConfig
    monitoring: MonitoringConfig
    logging: LoggingConfig
    features: FeatureFlags

    # Development settings
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    reload: bool = os.getenv('RELOAD', 'false').lower() == 'true'
    environment: str = os.getenv('ENVIRONMENT', 'production')

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from environment"""
        return cls(
            database=DatabaseConfig(),
            llm=LLMConfig(),
            qdrant=QdrantConfig(),
            eventbus=EventBusConfig(),
            service=ServiceConfig(),
            storage=StorageConfig(),
            generation=GenerationConfig(),
            execution=ExecutionConfig(),
            monitoring=MonitoringConfig(),
            logging=LoggingConfig(),
            features=FeatureFlags()
        )

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of warnings/errors

        Returns:
            List of validation messages
        """
        messages = []

        # Check critical dependencies
        if self.storage.use_postgres and not self.database.is_configured:
            messages.append("️  PostgreSQL storage enabled but DATABASE_URL not configured")

        if self.features.l4_generation and not self.llm.is_configured:
            messages.append("️  L4 generation enabled but LLM API keys not configured")

        if self.features.semantic_search and not self.qdrant.is_configured:
            messages.append("️  Semantic search enabled but Qdrant not configured")

        if self.features.auto_regeneration and not self.eventbus.is_configured:
            messages.append("️  Auto-regeneration enabled but EventBus not configured")

        # Check monitoring
        if not self.monitoring.is_configured:
            messages.append("ℹ️  MIO Manager monitoring not configured (optional)")

        return messages

    def print_summary(self):
        """Print configuration summary"""
        print("=" * 70)
        print("SCENARIO INTELLIGENCE - Configuration Summary")
        print("=" * 70)

        print(f"\n Environment: {self.environment}")
        print(f" Debug Mode: {self.debug}")

        print("\n Storage Backends:")
        print(f"   - Memory: {'' if self.storage.use_memory else ''}")
        print(f"   - PostgreSQL: {'' if self.storage.use_postgres else ''} {'' if self.database.is_configured else '(NOT CONFIGURED)'}")
        print(f"   - Qdrant: {'' if self.storage.use_qdrant else ''} {'' if self.qdrant.is_configured else '(NOT CONFIGURED)'}")
        print(f"   - Default: {self.storage.default_storage}")

        print("\n AI Features:")
        print(f"   - L4 Generation: {'' if self.features.l4_generation else ''} {'' if self.llm.is_configured else '(NOT CONFIGURED)'}")
        print(f"   - Semantic Search: {'' if self.features.semantic_search else ''}")
        print(f"   - Auto-Regeneration: {'' if self.features.auto_regeneration else ''}")
        print(f"   - Execution Engine: {'' if self.features.execution_engine else ''}")

        print("\n Integrations:")
        print(f"   - EventBus: {'' if self.eventbus.is_configured else ''}")
        print(f"   - MIO Manager: {'' if self.monitoring.is_configured else ''}")

        print("\n Service:")
        print(f"   - Host: {self.service.host}")
        print(f"   - Port: {self.service.port}")

        # Validation warnings
        warnings = self.validate()
        if warnings:
            print("\n️  Configuration Warnings:")
            for warning in warnings:
                print(f"   {warning}")
        else:
            print("\n Configuration is valid!")

        print("=" * 70)


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config():
    """Reload configuration from environment"""
    global _config
    _config = Config.load()
    return _config


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    config.print_summary()
