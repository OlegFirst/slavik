"""
GitHub Integration Prometheus Metrics
====================================
"""

from prometheus_client import Counter, Histogram, Gauge, Info

# Service Info
github_info = Info('github_integration', 'GitHub Integration Service')
github_info.info({'version': '2.0.0'})

# Webhook Metrics
webhooks_received_total = Counter(
    'github_webhooks_received_total',
    'Total webhooks received',
    ['event_type']
)

webhooks_processed_total = Counter(
    'github_webhooks_processed_total',
    'Total webhooks processed',
    ['event_type', 'status']
)

webhook_processing_duration = Histogram(
    'github_webhook_processing_duration_seconds',
    'Webhook processing duration',
    ['event_type']
)

# GitHub API Metrics
github_api_requests_total = Counter(
    'github_api_requests_total',
    'Total GitHub API requests',
    ['method', 'status']
)

github_api_duration = Histogram(
    'github_api_duration_seconds',
    'GitHub API request duration',
    ['method']
)

github_rate_limit_remaining = Gauge(
    'github_rate_limit_remaining',
    'GitHub API rate limit remaining'
)

# Installation Metrics
github_installations_total = Gauge(
    'github_installations_total',
    'Total GitHub App installations'
)

installation_token_cache_hits = Counter(
    'github_installation_token_cache_hits_total',
    'Installation token cache hits'
)
