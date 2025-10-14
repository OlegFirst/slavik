#!/bin/bash
# Analytics Specialist - Startup Script
# Fixes Python import issues by setting PYTHONPATH

export PYTHONPATH="/Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist:$PYTHONPATH"
cd /Users/MD/AI-Platform-ISO/infrastructure/AI-office-infrastructure/analytics-specialist

python3 main.py
