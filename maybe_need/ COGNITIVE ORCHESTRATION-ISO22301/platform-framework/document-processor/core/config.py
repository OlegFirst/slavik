"""Configuration for Document Processor Adapter"""

import os
from typing import List, Optional

class Config:
    """Configuration management for Document Processor"""
    
    # Redis and EventBus
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    EVENTBUS_URL: str = os.getenv("EVENTBUS_URL", "http://localhost:8001")
    
    # Document Processing
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB default
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "doc", "txt", "md"]
    
    # Storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, azure
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage/documents")
    
    # AWS S3 (if STORAGE_TYPE=s3)
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: Optional[str] = os.getenv("S3_BUCKET")
    
    # Document Analysis Engine
    ANALYSIS_ENGINE: str = os.getenv("ANALYSIS_ENGINE", "local")  # local, openai, azure
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # ISO 22301 Compliance Analysis
    ISO_CLAUSES_PATH: str = os.getenv("ISO_CLAUSES_PATH", "./data/iso_22301_clauses.json")
    COMPLIANCE_THRESHOLD: float = float(os.getenv("COMPLIANCE_THRESHOLD", "0.7"))
    
    # OCR Settings (for PDF processing)
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() == "true"
    TESSERACT_PATH: Optional[str] = os.getenv("TESSERACT_PATH")
    OCR_LANGUAGES: str = os.getenv("OCR_LANGUAGES", "eng+rus")
    
    # Database (for metadata storage)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./documents.db")
    
    # Processing Limits
    MAX_CONCURRENT_ANALYSES: int = int(os.getenv("MAX_CONCURRENT_ANALYSES", "5"))
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT", "300"))  # 5 minutes
    
    # Retry Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "5"))  # seconds
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Security
    API_KEY: Optional[str] = os.getenv("API_KEY")  # Optional API key for authentication
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:8081").split(",")
    
    def __init__(self):
        """Initialize configuration and validate required settings"""
        self._validate_config()
        self._ensure_directories()
    
    def _validate_config(self):
        """Validate configuration settings"""
        if self.STORAGE_TYPE == "s3":
            if not self.AWS_ACCESS_KEY_ID or not self.AWS_SECRET_ACCESS_KEY or not self.S3_BUCKET:
                raise ValueError("S3 configuration incomplete. Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET")
        
        if self.ANALYSIS_ENGINE == "openai":
            if not self.OPENAI_API_KEY:
                raise ValueError("OpenAI API key required when ANALYSIS_ENGINE=openai")
    
    def _ensure_directories(self):
        """Create necessary directories"""
        if self.STORAGE_TYPE == "local":
            os.makedirs(self.STORAGE_PATH, exist_ok=True)
        
        # Create data directory for ISO clauses
        os.makedirs(os.path.dirname(self.ISO_CLAUSES_PATH), exist_ok=True)
    
    @property
    def redis_config(self) -> dict:
        """Redis connection configuration"""
        return {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "max_connections": 20
        }
    
    @property
    def database_config(self) -> dict:
        """Database connection configuration"""
        return {
            "url": self.DATABASE_URL,
            "echo": False,  # Set to True for SQL debugging
            "pool_pre_ping": True
        }
    
    @property
    def analysis_config(self) -> dict:
        """Document analysis configuration"""
        return {
            "engine": self.ANALYSIS_ENGINE,
            "model": self.OPENAI_MODEL,
            "api_key": self.OPENAI_API_KEY,
            "compliance_threshold": self.COMPLIANCE_THRESHOLD,
            "iso_clauses_path": self.ISO_CLAUSES_PATH,
            "max_concurrent": self.MAX_CONCURRENT_ANALYSES,
            "timeout": self.ANALYSIS_TIMEOUT
        }
