# -*- coding: utf-8 -*-
"""
Configuration for Simulation Adapter
"""

import os
from typing import Dict, Any

class Config:
    """Simulation Adapter Configuration"""

    def __init__(self):
        # Service configuration
        self.PORT = int(os.getenv('PORT', 8012))
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

        # External service URLs
        self.REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/5')
        self.EVENTBUS_URL = os.getenv('EVENTBUS_URL', 'http://eventbus:8001')
        self.EXERCISE_SIMULATORS_URL = os.getenv('EXERCISE_SIMULATORS_URL', 'http://exercise_simulators:8094')

        # AI Integration
        self.AI_ORCHESTRATOR_URL = os.getenv('AI_ORCHESTRATOR_URL', 'http://ai_orchestrator:8000')
        self.SCENARIO_ORCHESTRATOR_URL = os.getenv('SCENARIO_ORCHESTRATOR_URL', 'http://scenario_orchestrator:8085')

        # Simulation configuration
        self.MAX_CONCURRENT_SIMULATIONS = int(os.getenv('MAX_CONCURRENT_SIMULATIONS', 10))
        self.SIMULATION_TIMEOUT_SECONDS = int(os.getenv('SIMULATION_TIMEOUT_SECONDS', 3600))

        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'port': self.PORT,
            'host': self.HOST,
            'debug': self.DEBUG,
            'redis_url': self.REDIS_URL,
            'eventbus_url': self.EVENTBUS_URL,
            'exercise_simulators_url': self.EXERCISE_SIMULATORS_URL,
            'ai_orchestrator_url': self.AI_ORCHESTRATOR_URL,
            'max_concurrent_simulations': self.MAX_CONCURRENT_SIMULATIONS,
            'simulation_timeout': self.SIMULATION_TIMEOUT_SECONDS
        }