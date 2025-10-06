"""
Assessment Engine - Core compliance scoring logic

Migrated from: /services/BCM_1/compliance_checker/app.py:240-308
Date: 2025-10-01
Enhanced with: async, database, workflow integration, EventBus

Scoring Algorithm (PRODUCTION-TESTED):
- evidence_coverage = provided_evidence / required_evidence
- verification_rate = verified_evidence / total_evidence
- score = (evidence_coverage * 0.7 + verification_rate * 0.3) * 100

Status determination:
- COMPLIANT: coverage >= 0.9 AND verification >= 0.8
- PARTIAL: coverage >= 0.6
- NON_COMPLIANT: coverage < 0.6
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import logging

from compliance.models.database import EvidenceModel, AssessmentModel
from compliance.models.enums import ComplianceStatus, AssessmentStatus, EvidenceStatus
from compliance.standards.iso_22301 import ISO_22301_REQUIREMENTS, get_total_weight
from compliance.integrations.eventbus import EventBusService

logger = logging.getLogger(__name__)


class AssessmentEngine:
    """
    Core assessment engine for ISO 22301 compliance scoring

    This engine implements the proven scoring algorithm from compliance_checker
    with enhancements for production use: async operations, database persistence,
    workflow integration, and event-driven notifications.
    """

    def __init__(self, db: AsyncSession, eventbus: Optional[EventBusService] = None):
        """
        Initialize assessment engine

        Args:
            db: Async database session
            eventbus: Optional EventBus client for publishing events
        """
        self.db = db
        self.eventbus = eventbus

    async def assess_requirement(
        self,
        requirement_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Assess compliance for a single ISO 22301 requirement

        Args:
            requirement_id: ISO clause number (e.g., "8.2", "10.1")
            tenant_id: Tenant ID for multi-tenancy

        Returns:
            Assessment result dictionary with:
            - requirement_id: Clause number
            - requirement_title: Requirement title
            - status: ComplianceStatus (COMPLIANT/PARTIAL/NON_COMPLIANT)
            - score: Compliance score 0-100
            - evidence_coverage: % of required evidence provided
            - verification_rate: % of evidence verified
            - provided_evidence_count: Number of evidence items
            - required_evidence_count: Number of required evidence types
            - missing_evidence: List of missing evidence types
            - assessment_notes: List of assessment notes
            - weight: Requirement weight for scoring

        Raises:
            ValueError: If requirement_id is not valid ISO 22301 clause
        """
        # Get requirement from standards database
        requirement = ISO_22301_REQUIREMENTS.get(requirement_id)
        if not requirement:
            raise ValueError(f"Unknown ISO 22301 requirement: {requirement_id}")

        # Get evidence for this requirement (VERIFIED or SUBMITTED only)
        stmt = select(EvidenceModel).where(
            and_(
                EvidenceModel.requirement_id == requirement_id,
                EvidenceModel.tenant_id == tenant_id,
                EvidenceModel.status.in_([
                    EvidenceStatus.VERIFIED.value,
                    EvidenceStatus.SUBMITTED.value
                ])
            )
        )
        result = await self.db.execute(stmt)
        evidence_records = result.scalars().all()

        logger.info(
            f"Assessing requirement {requirement_id}: "
            f"found {len(evidence_records)} evidence records"
        )

        # Calculate evidence coverage
        # (Algorithm from compliance_checker:248-255)
        provided_evidence_types = set(e.evidence_type for e in evidence_records)
        required_evidence_types = set(requirement.evidence_required)

        if not required_evidence_types:
            evidence_coverage = 1.0
        else:
            coverage_intersection = provided_evidence_types.intersection(
                required_evidence_types
            )
            evidence_coverage = len(coverage_intersection) / len(required_evidence_types)

        # Calculate verification rate
        # (Algorithm from compliance_checker:257-259)
        verified_evidence = [
            e for e in evidence_records
            if e.status == EvidenceStatus.VERIFIED.value
        ]
        verification_rate = len(verified_evidence) / max(1, len(evidence_records))

        # Determine compliance status
        # (Algorithm from compliance_checker:261-269)
        if evidence_coverage >= 0.9 and verification_rate >= 0.8:
            status = ComplianceStatus.COMPLIANT
        elif evidence_coverage >= 0.6:
            status = ComplianceStatus.PARTIAL
        else:
            status = ComplianceStatus.NON_COMPLIANT

        # Calculate score (PROVEN FORMULA)
        # (Algorithm from compliance_checker:272)
        score = (evidence_coverage * 0.7 + verification_rate * 0.3) * 100

        # Generate assessment notes
        notes = self._generate_assessment_notes(
            requirement, evidence_coverage, verification_rate
        )

        # Identify missing evidence
        missing_evidence = list(required_evidence_types - provided_evidence_types)

        # Build result
        result_data = {
            "requirement_id": requirement_id,
            "requirement_title": requirement.title,
            "status": status,
            "score": round(score, 2),
            "evidence_coverage": round(evidence_coverage * 100, 2),
            "verification_rate": round(verification_rate * 100, 2),
            "provided_evidence_count": len(evidence_records),
            "required_evidence_count": len(requirement.evidence_required),
            "missing_evidence": missing_evidence,
            "assessment_notes": notes,
            "weight": requirement.weight
        }

        # Publish event to EventBus
        if self.eventbus:
            try:
                await self.eventbus.publish({
                    "event_type": "bcm.compliance.requirement.assessed",
                    "tenant_id": tenant_id,
                    "data": {
                        "requirement_id": requirement_id,
                        "score": result_data["score"],
                        "status": status.value,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            except Exception as e:
                logger.error(f"Failed to publish assessment event: {e}")

        logger.info(
            f"Requirement {requirement_id} assessed: "
            f"score={score:.2f}, status={status.value}"
        )

        return result_data

    async def assess_all_requirements(
        self,
        assessment_id: str,
        tenant_id: str,
        scope_clause_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assess all requirements in scope and calculate overall compliance

        This method orchestrates the complete assessment process:
        1. Assesses each requirement individually
        2. Calculates weighted overall score
        3. Determines overall compliance status
        4. Updates assessment record in database
        5. Publishes completion event

        Args:
            assessment_id: UUID of assessment record
            tenant_id: Tenant ID
            scope_clause_ids: Optional list of clause IDs to assess
                            (if None, assesses all 13 ISO requirements)

        Returns:
            Overall assessment results with:
            - assessment_id: Assessment record ID
            - overall_score: Weighted average score
            - overall_status: Overall compliance status
            - total_requirements: Number of requirements assessed
            - results: List of individual requirement results
            - compliant_count: Number of compliant requirements
            - partial_count: Number of partially compliant
            - non_compliant_count: Number of non-compliant
        """
        # Default scope: all ISO 22301 requirements
        if scope_clause_ids is None:
            scope_clause_ids = list(ISO_22301_REQUIREMENTS.keys())

        logger.info(
            f"Starting assessment {assessment_id}: "
            f"{len(scope_clause_ids)} requirements in scope"
        )

        assessment_results = []
        total_weighted_score = 0.0
        total_weight = 0.0

        # Assess each requirement
        for clause_id in scope_clause_ids:
            try:
                result = await self.assess_requirement(clause_id, tenant_id)
                assessment_results.append(result)

                # Weighted score calculation
                total_weighted_score += result["score"] * result["weight"]
                total_weight += result["weight"]

            except Exception as e:
                logger.error(f"Error assessing requirement {clause_id}: {e}")
                # Continue with other requirements
                continue

        # Calculate overall score (weighted average)
        overall_score = (
            total_weighted_score / total_weight if total_weight > 0 else 0
        )

        # Determine overall compliance status
        if overall_score >= 85:
            overall_status = ComplianceStatus.COMPLIANT
        elif overall_score >= 60:
            overall_status = ComplianceStatus.PARTIAL
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT

        # Count by status
        compliant_count = len([
            r for r in assessment_results
            if r["status"] == ComplianceStatus.COMPLIANT
        ])
        partial_count = len([
            r for r in assessment_results
            if r["status"] == ComplianceStatus.PARTIAL
        ])
        non_compliant_count = len([
            r for r in assessment_results
            if r["status"] == ComplianceStatus.NON_COMPLIANT
        ])

        # Update assessment record in database
        stmt = select(AssessmentModel).where(
            AssessmentModel.id == assessment_id
        )
        db_result = await self.db.execute(stmt)
        assessment = db_result.scalar_one_or_none()

        if assessment:
            assessment.overall_score = overall_score
            assessment.overall_status = overall_status.value
            assessment.status = AssessmentStatus.COMPLETED.value
            assessment.completed_at = datetime.utcnow()
            assessment.results_summary = {
                "total_requirements": len(assessment_results),
                "compliant": compliant_count,
                "partial": partial_count,
                "non_compliant": non_compliant_count
            }
            await self.db.commit()
        else:
            logger.warning(f"Assessment record {assessment_id} not found")

        # Publish completion event
        if self.eventbus:
            try:
                await self.eventbus.publish({
                    "event_type": "bcm.compliance.assessment.completed",
                    "tenant_id": tenant_id,
                    "data": {
                        "assessment_id": assessment_id,
                        "overall_score": round(overall_score, 2),
                        "overall_status": overall_status.value,
                        "requirements_assessed": len(assessment_results),
                        "compliant_count": compliant_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            except Exception as e:
                logger.error(f"Failed to publish assessment completion event: {e}")

        logger.info(
            f"Assessment {assessment_id} completed: "
            f"overall_score={overall_score:.2f}, status={overall_status.value}"
        )

        return {
            "assessment_id": assessment_id,
            "overall_score": round(overall_score, 2),
            "overall_status": overall_status,
            "total_requirements": len(assessment_results),
            "results": assessment_results,
            "compliant_count": compliant_count,
            "partial_count": partial_count,
            "non_compliant_count": non_compliant_count
        }

    def _generate_assessment_notes(
        self,
        requirement,
        evidence_coverage: float,
        verification_rate: float
    ) -> List[str]:
        """
        Generate smart assessment notes based on coverage and verification

        Source: compliance_checker/app.py:286-308
        This method provides human-readable feedback on the assessment.

        Args:
            requirement: ISO 22301 requirement object
            evidence_coverage: Evidence coverage ratio (0-1)
            verification_rate: Verification rate ratio (0-1)

        Returns:
            List of assessment notes (in Russian)
        """
        notes = []

        # Coverage-based notes
        if evidence_coverage < 0.5:
            notes.append("Критический недостаток доказательств соответствия")
        elif evidence_coverage < 0.8:
            notes.append("Частичное предоставление требуемых доказательств")

        # Verification-based notes
        if verification_rate < 0.5:
            notes.append("Большинство доказательств не верифицировано")
        elif verification_rate < 0.8:
            notes.append("Требуется дополнительная верификация доказательств")

        # Mandatory requirement warning
        if requirement.mandatory and evidence_coverage < 0.9:
            notes.append(
                "Обязательное требование - необходимо полное соответствие"
            )

        # Success note
        if not notes:
            notes.append("Требование выполнено в полном объеме")

        return notes
