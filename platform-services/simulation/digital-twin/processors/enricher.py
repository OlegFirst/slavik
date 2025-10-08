"""
Data Enricher

Enriches organization data from external sources (Clearbit, Google Maps, etc.)
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================
# ENRICHMENT PROVIDERS
# ============================================

class EnrichmentProvider:
    """Base class for enrichment providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize HTTP client"""
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()

    async def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich data (to be implemented by subclasses)"""
        raise NotImplementedError


class ClearbitEnricher(EnrichmentProvider):
    """
    Clearbit Company Enrichment

    Enriches company data using Clearbit API
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://company.clearbit.com/v2/companies/find"

    async def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich company data

        Args:
            data: Organization data with 'domain' or 'name'

        Returns:
            Enriched data
        """
        if not self.api_key:
            return {}

        domain = data.get('website') or data.get('domain')
        if not domain:
            return {}

        try:
            # Clean domain
            domain = domain.replace('http://', '').replace('https://', '').split('/')[0]

            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }

            response = await self._client.get(
                self.base_url,
                params={'domain': domain},
                headers=headers
            )

            if response.status_code == 200:
                clearbit_data = response.json()

                enriched = {
                    'name': clearbit_data.get('name'),
                    'description': clearbit_data.get('description'),
                    'logo': clearbit_data.get('logo'),
                    'employee_count': clearbit_data.get('metrics', {}).get('employees'),
                    'annual_revenue': clearbit_data.get('metrics', {}).get('annualRevenue'),
                    'industry': clearbit_data.get('category', {}).get('industry'),
                    'founded_year': clearbit_data.get('foundedYear'),
                    'linkedin': clearbit_data.get('linkedin', {}).get('handle'),
                    'twitter': clearbit_data.get('twitter', {}).get('handle'),
                    'tech_stack': clearbit_data.get('tech', []),
                }

                # Remove None values
                return {k: v for k, v in enriched.items() if v is not None}

            return {}

        except Exception as e:
            logger.error(f"Clearbit enrichment failed: {e}")
            return {}


class GoogleMapsEnricher(EnrichmentProvider):
    """
    Google Maps Geocoding

    Enriches location data using Google Maps API
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"

    async def enrich(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich location data

        Args:
            data: Organization data with address information

        Returns:
            Enriched location data
        """
        if not self.api_key:
            return {}

        # Build address string
        address_parts = []
        if data.get('address'):
            address_parts.append(data['address'])
        if data.get('city'):
            address_parts.append(data['city'])
        if data.get('state'):
            address_parts.append(data['state'])
        if data.get('country'):
            address_parts.append(data['country'])

        if not address_parts:
            return {}

        address = ', '.join(address_parts)

        try:
            response = await self._client.get(
                self.base_url,
                params={
                    'address': address,
                    'key': self.api_key
                }
            )

            if response.status_code == 200:
                result = response.json()

                if result.get('status') == 'OK' and result.get('results'):
                    location = result['results'][0]

                    enriched = {
                        'formatted_address': location.get('formatted_address'),
                        'latitude': location.get('geometry', {}).get('location', {}).get('lat'),
                        'longitude': location.get('geometry', {}).get('location', {}).get('lng'),
                        'place_id': location.get('place_id'),
                        'types': location.get('types', []),
                    }

                    # Extract address components
                    components = {}
                    for comp in location.get('address_components', []):
                        types = comp.get('types', [])
                        if 'country' in types:
                            components['country'] = comp.get('long_name')
                            components['country_code'] = comp.get('short_name')
                        elif 'administrative_area_level_1' in types:
                            components['state'] = comp.get('long_name')
                        elif 'locality' in types:
                            components['city'] = comp.get('long_name')
                        elif 'postal_code' in types:
                            components['postal_code'] = comp.get('long_name')

                    enriched['address_components'] = components

                    return {k: v for k, v in enriched.items() if v is not None}

            return {}

        except Exception as e:
            logger.error(f"Google Maps enrichment failed: {e}")
            return {}


# ============================================
# DATA ENRICHER
# ============================================

class DataEnricher:
    """
    Data Enricher

    Enriches organization data from external sources
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize data enricher

        Args:
            config: Configuration with API keys
        """
        self.config = config or {}

        # Initialize providers
        self.providers: Dict[str, EnrichmentProvider] = {}

        # Clearbit
        clearbit_key = self.config.get('clearbit_api_key')
        if clearbit_key:
            self.providers['clearbit'] = ClearbitEnricher(clearbit_key)

        # Google Maps
        google_key = self.config.get('google_maps_api_key')
        if google_key:
            self.providers['google_maps'] = GoogleMapsEnricher(google_key)

        # Statistics
        self.stats = {
            'enrichments_performed': 0,
            'by_provider': {},
            'fields_enriched': 0
        }

        logger.info(f"Data Enricher initialized with {len(self.providers)} providers")

    async def initialize(self) -> None:
        """Initialize all providers"""
        for name, provider in self.providers.items():
            try:
                await provider.initialize()
                logger.info(f"Initialized provider: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")

    async def close(self) -> None:
        """Close all providers"""
        for provider in self.providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.error(f"Error closing provider: {e}")

    async def enrich(
        self,
        data: Dict[str, Any],
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enrich data using available providers

        Args:
            data: Organization data
            providers: List of provider names (None = all)

        Returns:
            Enriched data
        """
        logger.info(f"Enriching data with providers: {providers or 'all'}")

        enriched_data = data.copy()
        enrichment_metadata = {
            'enriched_at': datetime.utcnow().isoformat(),
            'providers_used': [],
            'fields_added': []
        }

        # Select providers
        providers_to_use = providers or list(self.providers.keys())

        for provider_name in providers_to_use:
            if provider_name not in self.providers:
                logger.warning(f"Provider not available: {provider_name}")
                continue

            provider = self.providers[provider_name]

            try:
                logger.info(f"Enriching with {provider_name}")

                enrichment = await provider.enrich(data)

                if enrichment:
                    # Merge enrichment data
                    fields_before = len(enriched_data)

                    for key, value in enrichment.items():
                        # Don't overwrite existing non-null values
                        if key not in enriched_data or enriched_data[key] is None:
                            enriched_data[key] = value
                            enrichment_metadata['fields_added'].append({
                                'field': key,
                                'provider': provider_name
                            })

                    fields_after = len(enriched_data)
                    fields_added = fields_after - fields_before

                    enrichment_metadata['providers_used'].append(provider_name)

                    # Update stats
                    self.stats['enrichments_performed'] += 1
                    self.stats['by_provider'][provider_name] = \
                        self.stats['by_provider'].get(provider_name, 0) + 1
                    self.stats['fields_enriched'] += fields_added

                    logger.info(f"Enriched with {provider_name}: +{fields_added} fields")

            except Exception as e:
                logger.error(f"Enrichment failed with {provider_name}: {e}", exc_info=True)
                continue

        # Add enrichment metadata
        enriched_data['_enrichment'] = enrichment_metadata

        return enriched_data

    async def enrich_batch(
        self,
        records: List[Dict[str, Any]],
        providers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich batch of records

        Args:
            records: List of organization records
            providers: List of provider names

        Returns:
            List of enriched records
        """
        logger.info(f"Enriching batch of {len(records)} records")

        enriched_records = []

        for record in records:
            try:
                enriched = await self.enrich(record, providers)
                enriched_records.append(enriched)
            except Exception as e:
                logger.error(f"Failed to enrich record: {e}")
                # Keep original record
                enriched_records.append(record)

        logger.info(f"Enriched {len(enriched_records)} records")

        return enriched_records

    def register_provider(
        self,
        name: str,
        provider: EnrichmentProvider
    ) -> None:
        """
        Register custom enrichment provider

        Args:
            name: Provider name
            provider: Provider instance
        """
        self.providers[name] = provider
        logger.info(f"Registered enrichment provider: {name}")

    def get_available_providers(self) -> List[str]:
        """
        Get list of available providers

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get enricher statistics

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'available_providers': self.get_available_providers()
        }

    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
