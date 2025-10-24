"""
Simulation Service Configuration
ISO 22301 Clause 8.5 - Exercising and Testing

Re-export settings from config submodule for consistency with other services.
"""

import sys
from pathlib import Path

# Add config directory to path
config_dir = Path(__file__).parent / "config"
if str(config_dir) not in sys.path:
    sys.path.insert(0, str(config_dir))

# Import settings from settings.py in config/ subdirectory
from settings import settings, Settings

# Export settings for compatibility
__all__ = ['settings', 'Settings']
