"""
Impact Passport Engine for Digital Twin Universal Service

Generates verifiable Impact Passports for organizations:
- Claims generation and validation
- Evidence collection
- Verification workflows
- QR code generation
- Blockchain anchoring (future)
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from core.models.base import (
    Organization,
    ImpactPassport,
    HealthScore,
    TheoryOfChange,
)

logger = logging.getLogger(__name__)


# ============================================
# IMPACT PASSPORT ENGINE
# ============================================

class ImpactPassportEngine:
    """
    Impact Passport Engine

    Generates verifiable digital passports documenting organizational impact
    """

    def __init__(self):
        logger.info("Impact Passport Engine initialized")

    async def generate_passport(
        self,
        organization: Organization,
        health_score: Optional[HealthScore] = None,
        toc: Optional[TheoryOfChange] = None,
        validity_months: int = 12
    ) -> ImpactPassport:
        """
        Generate Impact Passport for organization

        Args:
            organization: Organization digital twin
            health_score: Optional health score data
            toc: Optional Theory of Change
            validity_months: Passport validity period

        Returns:
            ImpactPassport with claims and evidence
        """
        logger.info(f"Generating Impact Passport for {organization.name}")

        # Generate claims
        claims = self._generate_claims(organization, health_score, toc)

        # Collect evidence
        evidence = self._collect_evidence(organization, claims)

        # Calculate verification status
        verification_status = self._assess_verification_status(claims, evidence)

        # Generate passport
        passport_number = self._generate_passport_number(organization)
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(days=validity_months * 30)

        # Generate QR code data
        qr_data = self._generate_qr_data(passport_number, organization.twin_id)

        # Generate verification URL
        verification_url = self._generate_verification_url(passport_number)

        passport = ImpactPassport(
            twin_id=organization.twin_id,
            passport_number=passport_number,
            organization_name=organization.name,
            claims=claims,
            evidence=evidence,
            verification_status=verification_status,
            issued_at=issued_at,
            expires_at=expires_at,
            qr_code=qr_data,
            verification_url=verification_url
        )

        logger.info(
            f"Impact Passport generated: {passport_number} "
            f"({len(claims)} claims, {len(evidence)} evidence items)"
        )

        return passport

    def _generate_claims(
        self,
        organization: Organization,
        health_score: Optional[HealthScore],
        toc: Optional[TheoryOfChange]
    ) -> List[Dict[str, Any]]:
        """Generate impact claims for organization"""
        claims = []

        # Claim 1: Organizational Resilience
        if health_score:
            claims.append({
                'id': str(uuid4()),
                'type': 'resilience',
                'category': 'organizational_health',
                'claim': 'Demonstrates organizational resilience and continuity preparedness',
                'metric': 'Overall Health Score',
                'value': health_score.overall,
                'unit': 'score',
                'benchmark': 70,
                'status': 'verified' if health_score.overall >= 70 else 'partial',
                'confidence': 'high' if health_score.overall >= 80 else 'medium',
                'timestamp': health_score.calculated_at
            })

        # Claim 2: Financial Health
        if organization.annual_revenue or organization.annual_budget:
            revenue = organization.annual_revenue or organization.annual_budget
            claims.append({
                'id': str(uuid4()),
                'type': 'financial',
                'category': 'sustainability',
                'claim': 'Maintains financial sustainability',
                'metric': 'Annual Financial Capacity',
                'value': revenue,
                'unit': 'USD',
                'benchmark': 100000,
                'status': 'verified' if revenue >= 100000 else 'partial',
                'confidence': 'high',
                'timestamp': organization.updated_at
            })

        # Claim 3: Operational Maturity
        claims.append({
            'id': str(uuid4()),
            'type': 'maturity',
            'category': 'capability',
            'claim': f'Operates at maturity level {organization.maturity_level}',
            'metric': 'Organizational Maturity',
            'value': organization.maturity_level,
            'unit': 'level',
            'benchmark': 3,
            'status': 'verified' if organization.maturity_level >= 3 else 'partial',
            'confidence': 'high',
            'timestamp': organization.updated_at
        })

        # Claim 4: Data Integration
        if len(organization.sources) > 0:
            claims.append({
                'id': str(uuid4()),
                'type': 'integration',
                'category': 'data_quality',
                'claim': 'Maintains integrated data systems',
                'metric': 'Data Source Integration',
                'value': len(organization.sources),
                'unit': 'sources',
                'benchmark': 3,
                'status': 'verified' if len(organization.sources) >= 3 else 'partial',
                'confidence': 'high',
                'timestamp': organization.updated_at
            })

        # Claim 5: Data Quality
        if organization.quality_score > 0:
            claims.append({
                'id': str(uuid4()),
                'type': 'quality',
                'category': 'data_quality',
                'claim': 'Maintains high data quality standards',
                'metric': 'Data Quality Score',
                'value': organization.quality_score,
                'unit': 'score',
                'benchmark': 75,
                'status': 'verified' if organization.quality_score >= 75 else 'partial',
                'confidence': 'high',
                'timestamp': organization.updated_at
            })

        # Claim 6: Staffing
        if organization.employee_count:
            claims.append({
                'id': str(uuid4()),
                'type': 'capacity',
                'category': 'resources',
                'claim': 'Maintains adequate staffing levels',
                'metric': 'Employee Count',
                'value': organization.employee_count,
                'unit': 'employees',
                'benchmark': 10,
                'status': 'verified' if organization.employee_count >= 10 else 'partial',
                'confidence': 'medium',
                'timestamp': organization.updated_at
            })

        # Claim 7: Geographic Reach
        if len(organization.locations) > 0:
            claims.append({
                'id': str(uuid4()),
                'type': 'reach',
                'category': 'impact',
                'claim': 'Operates across multiple locations',
                'metric': 'Geographic Presence',
                'value': len(organization.locations),
                'unit': 'locations',
                'benchmark': 1,
                'status': 'verified',
                'confidence': 'high',
                'timestamp': organization.updated_at
            })

        # Claim 8: BCM Preparedness
        if organization.bcm_data:
            bcm_indicators = ['business_continuity_plan', 'risk_register', 'incident_response_plan']
            available = sum(1 for ind in bcm_indicators if ind in organization.bcm_data)

            claims.append({
                'id': str(uuid4()),
                'type': 'preparedness',
                'category': 'business_continuity',
                'claim': 'Implements business continuity management',
                'metric': 'BCM Framework Completeness',
                'value': available,
                'unit': 'components',
                'benchmark': 2,
                'status': 'verified' if available >= 2 else 'partial',
                'confidence': 'high',
                'timestamp': organization.updated_at
            })

        # Claim 9: Theory of Change
        if toc:
            claims.append({
                'id': str(uuid4()),
                'type': 'impact_model',
                'category': 'impact',
                'claim': 'Has defined Theory of Change',
                'metric': 'ToC Completeness',
                'value': len(toc.inputs) + len(toc.activities) + len(toc.outputs),
                'unit': 'components',
                'benchmark': 10,
                'status': 'verified',
                'confidence': 'high',
                'timestamp': toc.created_at
            })

        # Claim 10: Risk Management
        if organization.risk_score >= 0:
            # Lower risk score = better (inverse)
            risk_level = 'low' if organization.risk_score < 30 else 'medium' if organization.risk_score < 60 else 'high'
            claims.append({
                'id': str(uuid4()),
                'type': 'risk',
                'category': 'risk_management',
                'claim': f'Maintains {risk_level} risk profile',
                'metric': 'Risk Score',
                'value': organization.risk_score,
                'unit': 'score',
                'benchmark': 50,
                'status': 'verified' if organization.risk_score < 50 else 'partial',
                'confidence': 'medium',
                'timestamp': organization.updated_at
            })

        return claims

    def _collect_evidence(
        self,
        organization: Organization,
        claims: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Collect evidence supporting claims"""
        evidence = []

        # Evidence 1: Digital Twin Data
        evidence.append({
            'id': str(uuid4()),
            'type': 'data',
            'source': 'digital_twin',
            'description': 'Digital Twin comprehensive data model',
            'supporting_claims': [c['id'] for c in claims],
            'verification_method': 'automated_data_collection',
            'timestamp': organization.updated_at,
            'reliability': 'high',
            'link': f'/api/v1/twins/{organization.twin_id}'
        })

        # Evidence 2: Data Sources
        for source in organization.sources:
            evidence.append({
                'id': str(uuid4()),
                'type': 'integration',
                'source': source.source_type.value,
                'description': f'Integrated data from {source.source_type.value}',
                'supporting_claims': [
                    c['id'] for c in claims
                    if c['category'] in ['data_quality', 'integration']
                ],
                'verification_method': 'api_integration',
                'timestamp': source.last_sync,
                'reliability': 'high' if source.sync_status == 'active' else 'medium',
                'link': f'/api/v1/collectors/{source.source_type.value}'
            })

        # Evidence 3: BCM Documentation
        if organization.bcm_data:
            evidence.append({
                'id': str(uuid4()),
                'type': 'documentation',
                'source': 'bcm_framework',
                'description': 'Business Continuity Management documentation',
                'supporting_claims': [
                    c['id'] for c in claims
                    if c['category'] == 'business_continuity'
                ],
                'verification_method': 'document_review',
                'timestamp': organization.updated_at,
                'reliability': 'high',
                'metadata': {
                    'components': list(organization.bcm_data.keys())
                }
            })

        # Evidence 4: Financial Records
        if organization.annual_revenue or organization.annual_budget:
            evidence.append({
                'id': str(uuid4()),
                'type': 'financial',
                'source': 'financial_records',
                'description': 'Annual financial data',
                'supporting_claims': [
                    c['id'] for c in claims
                    if c['category'] == 'sustainability'
                ],
                'verification_method': 'financial_audit',
                'timestamp': organization.updated_at,
                'reliability': 'high',
                'metadata': {
                    'amount': organization.annual_revenue or organization.annual_budget
                }
            })

        # Evidence 5: Organizational Records
        evidence.append({
            'id': str(uuid4()),
            'type': 'organizational',
            'source': 'org_records',
            'description': 'Organizational structure and staffing records',
            'supporting_claims': [
                c['id'] for c in claims
                if c['category'] in ['resources', 'capability']
            ],
            'verification_method': 'hr_records',
            'timestamp': organization.updated_at,
            'reliability': 'medium',
            'metadata': {
                'employee_count': organization.employee_count,
                'locations': len(organization.locations)
            }
        })

        return evidence

    def _assess_verification_status(
        self,
        claims: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]]
    ) -> str:
        """Assess overall verification status"""
        if not claims:
            return 'pending'

        # Count verified claims
        verified = sum(1 for c in claims if c['status'] == 'verified')
        total = len(claims)

        verification_rate = verified / total

        if verification_rate >= 0.8:
            return 'verified'
        elif verification_rate >= 0.5:
            return 'partial'
        else:
            return 'pending'

    def _generate_passport_number(self, organization: Organization) -> str:
        """Generate unique passport number"""
        # Format: IP-{ORG_TYPE}-{HASH}
        org_type_code = {
            'corporate': 'CRP',
            'government': 'GOV',
            'npo': 'NPO',
            'infrastructure': 'INF'
        }.get(organization.org_type.value, 'ORG')

        # Hash of twin_id for uniqueness
        hash_input = f"{organization.twin_id}{datetime.utcnow().isoformat()}"
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:8].upper()

        return f"IP-{org_type_code}-{hash_digest}"

    def _generate_qr_data(self, passport_number: str, twin_id: str) -> str:
        """Generate QR code data (JSON)"""
        qr_payload = {
            'passport': passport_number,
            'twin_id': twin_id,
            'issued': datetime.utcnow().isoformat(),
            'type': 'impact_passport',
            'version': '1.0'
        }

        # In production, this would be encoded as actual QR code image
        # For now, return JSON string that can be encoded
        return json.dumps(qr_payload)

    def _generate_verification_url(self, passport_number: str) -> str:
        """Generate verification URL"""
        # In production, this would be actual domain
        base_url = "https://verify.digitaltwin.platform"
        return f"{base_url}/passport/{passport_number}"

    async def verify_passport(
        self,
        passport: ImpactPassport,
        organization: Organization
    ) -> Dict[str, Any]:
        """
        Verify passport authenticity and validity

        Args:
            passport: Impact Passport to verify
            organization: Current organization state

        Returns:
            Verification result
        """
        logger.info(f"Verifying passport {passport.passport_number}")

        verification_result = {
            'passport_number': passport.passport_number,
            'verified': False,
            'checks': [],
            'issues': [],
            'timestamp': datetime.utcnow()
        }

        # Check 1: Passport not expired
        if datetime.utcnow() > passport.expires_at:
            verification_result['checks'].append({
                'name': 'expiry',
                'passed': False,
                'message': 'Passport has expired'
            })
            verification_result['issues'].append('Passport expired')
        else:
            verification_result['checks'].append({
                'name': 'expiry',
                'passed': True,
                'message': 'Passport is valid'
            })

        # Check 2: Twin ID matches
        if passport.twin_id != organization.twin_id:
            verification_result['checks'].append({
                'name': 'twin_id',
                'passed': False,
                'message': 'Twin ID mismatch'
            })
            verification_result['issues'].append('Organization mismatch')
        else:
            verification_result['checks'].append({
                'name': 'twin_id',
                'passed': True,
                'message': 'Organization verified'
            })

        # Check 3: Claims still valid
        claims_valid = self._verify_claims_current(passport.claims, organization)
        verification_result['checks'].append({
            'name': 'claims',
            'passed': claims_valid,
            'message': 'Claims verified' if claims_valid else 'Claims outdated'
        })

        if not claims_valid:
            verification_result['issues'].append('Claims may be outdated')

        # Check 4: Evidence availability
        evidence_valid = len(passport.evidence) > 0
        verification_result['checks'].append({
            'name': 'evidence',
            'passed': evidence_valid,
            'message': 'Evidence available' if evidence_valid else 'No evidence'
        })

        # Overall verification
        all_passed = all(check['passed'] for check in verification_result['checks'])
        verification_result['verified'] = all_passed

        logger.info(
            f"Verification {'PASSED' if all_passed else 'FAILED'}: "
            f"{passport.passport_number}"
        )

        return verification_result

    def _verify_claims_current(
        self,
        claims: List[Dict[str, Any]],
        organization: Organization
    ) -> bool:
        """Verify claims are still accurate"""
        # Check sample of claims
        for claim in claims[:3]:  # Check first 3 claims
            claim_type = claim.get('type')

            if claim_type == 'maturity':
                if claim['value'] != organization.maturity_level:
                    return False

            elif claim_type == 'integration':
                if claim['value'] != len(organization.sources):
                    return False

            elif claim_type == 'quality':
                # Allow some variance
                if abs(claim['value'] - organization.quality_score) > 10:
                    return False

        return True

    async def renew_passport(
        self,
        old_passport: ImpactPassport,
        organization: Organization,
        health_score: Optional[HealthScore] = None,
        toc: Optional[TheoryOfChange] = None
    ) -> ImpactPassport:
        """
        Renew expired or expiring passport

        Args:
            old_passport: Existing passport
            organization: Updated organization
            health_score: Updated health score
            toc: Updated Theory of Change

        Returns:
            New Impact Passport
        """
        logger.info(f"Renewing passport {old_passport.passport_number}")

        # Generate new passport
        new_passport = await self.generate_passport(
            organization,
            health_score,
            toc
        )

        logger.info(
            f"Passport renewed: {old_passport.passport_number} → {new_passport.passport_number}"
        )

        return new_passport
