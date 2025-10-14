#!/usr/bin/env python3
"""
Temporal Client Provider for MIO Manager
=========================================

Provides Temporal client connection with proper authentication.

Supports:
- API Key authentication (Temporal Cloud)
- mTLS authentication (self-hosted)
- Local development (no auth)
"""

import os
from temporalio.client import Client, TLSConfig
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv('/Users/MD/AI-Platform-ISO/.env')


async def get_temporal_client() -> Client:
    """
    Get Temporal client with proper authentication.

    Checks in order:
    1. mTLS (cert + key) - for self-hosted with mTLS
    2. API Key - for Temporal Cloud
    3. No auth - for local development

    Environment variables:
    - TEMPORAL_ADDRESS: Temporal server address
    - TEMPORAL_NAMESPACE: Namespace to use
    - TEMPORAL_API_KEY: API key for Temporal Cloud
    - TEMPORAL_TLS_CERT: Path to client cert (mTLS)
    - TEMPORAL_TLS_KEY: Path to client key (mTLS)

    Returns:
        Connected Temporal client
    """
    cert_path = os.getenv("TEMPORAL_TLS_CERT")
    key_path = os.getenv("TEMPORAL_TLS_KEY")
    api_key = os.getenv("TEMPORAL_API_KEY")
    address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")

    # Check for mTLS authentication
    if cert_path and key_path:
        print(f"🔐 Connecting to Temporal with mTLS: {address}")
        with open(cert_path, "rb") as f:
            client_cert = f.read()
        with open(key_path, "rb") as f:
            client_key = f.read()

        return await Client.connect(
            address,
            namespace=namespace,
            tls=TLSConfig(
                client_cert=client_cert,
                client_private_key=client_key,
            ),
        )

    # Check for API Key authentication (Temporal Cloud)
    elif api_key:
        print(f"🔐 Connecting to Temporal Cloud with API Key: {address}")
        return await Client.connect(
            address,
            namespace=namespace,
            api_key=api_key,
            tls=True,
        )

    # Local development (no auth)
    else:
        print(f"🔧 Connecting to local Temporal: {address}")
        return await Client.connect(
            address,
            namespace=namespace,
        )
