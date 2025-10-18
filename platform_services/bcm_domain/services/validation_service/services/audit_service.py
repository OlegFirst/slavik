"""
Audit Service
Business logic for audit management and findings

Based on: /Users/MD/ISO-22301:>?8O/services/SERVICES/BCM/validation/main.py lines 1033-1257
ISO 22301:2019 Clause 9.2 - Internal audit
"""

from typing import List, Optional, Dict
from datetime import datetime
from repositories.repository import ValidationRepository
from workflows.audit_workflow import (
    can_start_audit,
    can_complete_fieldwork,
    can_issue_report,
    AuditWorkflowState,
    AuditWorkflowAction,
    validate_audit_transition
)
from models.database import (
    AuditPlan as AuditPlanDB,
    AuditFinding as AuditFindingDB,
    CAPA as CAPADB
)
from models.domain import (
    AuditStatus,
    AuditType,
    FindingSeverity,
    FindingType,
    CAPAType,
    CAPAStatus,
    CAPASource
)


class AuditService:
    """Audit business logic service"""

    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_audit(self, audit_data: Dict) -> AuditPlanDB:
        """
        Create new audit plan with validation

        Args:
            audit_data: Audit configuration data

        Returns:
            Created audit plan

        Raises:
            ValueError: If validation fails
        """
        # Validate scope is defined
        if not audit_data.get("audit_scope"):
            raise ValueError("Audit scope must be defined")

        # Set defaults
        audit_data["status"] = AuditStatus.PLANNED.value
        audit_data["findings_count"] = 0
        audit_data["major_findings"] = 0
        audit_data["minor_findings"] = 0
        audit_data["observations"] = 0
        audit_data["opportunities"] = 0
        audit_data["corrective_actions_required"] = 0
        audit_data["corrective_actions_completed"] = 0

        return await self.repo.create_audit(audit_data)

    async def start_fieldwork(self, audit_id: int) -> AuditPlanDB:
        """
        Start audit fieldwork with workflow validation

        Args:
            audit_id: Audit identifier

        Returns:
            Updated audit plan

        Raises:
            ValueError: If audit not found or cannot be started
        """
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Validate workflow transition
        can_start, error = can_start_audit(audit)
        if not can_start:
            raise ValueError(error)

        # Update audit status
        updates = {
            "status": AuditStatus.IN_PROGRESS.value,
            "actual_start_date": datetime.utcnow()
        }

        return await self.repo.update_audit(audit_id, updates)

    async def complete_fieldwork(self, audit_id: int) -> AuditPlanDB:
        """
        Complete audit fieldwork

        Args:
            audit_id: Audit identifier

        Returns:
            Updated audit plan

        Raises:
            ValueError: If audit not found or fieldwork cannot be completed
        """
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Validate workflow transition
        can_complete, error = can_complete_fieldwork(audit)
        if not can_complete:
            raise ValueError(error)

        # Update audit status
        updates = {
            "status": AuditStatus.FIELDWORK_COMPLETE.value,
            "fieldwork_end_date": datetime.utcnow()
        }

        return await self.repo.update_audit(audit_id, updates)

    async def draft_report(self, audit_id: int) -> AuditPlanDB:
        """
        Move audit to report draft status

        Args:
            audit_id: Audit identifier

        Returns:
            Updated audit plan

        Raises:
            ValueError: If audit not found or cannot draft report
        """
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        if audit.status != AuditStatus.FIELDWORK_COMPLETE.value:
            raise ValueError(f"Fieldwork must be complete before drafting report. Current status: {audit.status}")

        # Update audit status
        updates = {
            "status": AuditStatus.REPORT_DRAFT.value
        }

        return await self.repo.update_audit(audit_id, updates)

    async def add_finding(
        self,
        audit_id: int,
        finding_data: Dict
    ) -> AuditFindingDB:
        """
        Add finding to audit

        Args:
            audit_id: Audit identifier
            finding_data: Finding details

        Returns:
            Created finding

        Raises:
            ValueError: If audit not found
        """
        # Verify audit exists
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Set audit_id
        finding_data["audit_id"] = audit_id
        finding_data["status"] = "open"

        # Create finding
        finding = await self.repo.create_audit_finding(finding_data)

        # Update audit counts
        updates = {
            "findings_count": audit.findings_count + 1
        }

        severity = finding_data.get("severity")
        if isinstance(severity, str):
            severity_str = severity
        elif hasattr(severity, 'value'):
            severity_str = severity.value
        else:
            severity_str = str(severity)

        if severity_str == FindingSeverity.MAJOR.value:
            updates["major_findings"] = audit.major_findings + 1
        elif severity_str == FindingSeverity.MINOR.value:
            updates["minor_findings"] = audit.minor_findings + 1
        elif severity_str == FindingSeverity.OBSERVATION.value:
            updates["observations"] = audit.observations + 1

        if finding_data.get("corrective_action_required"):
            updates["corrective_actions_required"] = audit.corrective_actions_required + 1

        await self.repo.update_audit(audit_id, updates)

        # Auto-create CAPA for major findings
        if severity_str == FindingSeverity.MAJOR.value:
            await self._auto_create_capa_for_finding(audit, finding)

        # TODO: Publish event for finding created

        return finding

    async def generate_report(self, audit_id: int) -> Dict:
        """
        Generate audit report with findings analysis

        Args:
            audit_id: Audit identifier

        Returns:
            Dict with complete audit report data

        Raises:
            ValueError: If audit not found
        """
        # Get audit
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Get all findings
        findings = await self.repo.list_audit_findings(audit_id)

        # Calculate ISO clause coverage
        iso_clauses_covered = audit.iso_clauses_covered or []
        iso_clause_findings = {}
        for clause in iso_clauses_covered:
            clause_findings = [f for f in findings if f.iso_clause == clause]
            iso_clause_findings[clause] = {
                "total": len(clause_findings),
                "major": len([f for f in clause_findings if f.severity == FindingSeverity.MAJOR.value]),
                "minor": len([f for f in clause_findings if f.severity == FindingSeverity.MINOR.value]),
                "observations": len([f for f in clause_findings if f.severity == FindingSeverity.OBSERVATION.value])
            }

        # Group findings by severity
        findings_by_severity = {
            "critical": [f for f in findings if f.severity == FindingSeverity.CRITICAL.value],
            "major": [f for f in findings if f.severity == FindingSeverity.MAJOR.value],
            "minor": [f for f in findings if f.severity == FindingSeverity.MINOR.value],
            "observation": [f for f in findings if f.severity == FindingSeverity.OBSERVATION.value]
        }

        # Build report
        report = {
            "audit": {
                "audit_code": audit.audit_code,
                "audit_name": audit.audit_name,
                "audit_type": audit.audit_type if isinstance(audit.audit_type, str) else audit.audit_type.value,
                "planned_date": audit.planned_date.isoformat(),
                "actual_start_date": audit.actual_start_date.isoformat() if audit.actual_start_date else None,
                "lead_auditor": audit.lead_auditor_name,
                "audit_team": audit.audit_team,
                "status": audit.status if isinstance(audit.status, str) else audit.status.value,
            },
            "scope": {
                "audit_scope": audit.audit_scope,
                "iso_clauses": iso_clauses_covered,
                "processes": audit.processes_covered or [],
                "audit_criteria": audit.audit_criteria or [],
            },
            "findings_summary": {
                "total": audit.findings_count,
                "critical": len(findings_by_severity["critical"]),
                "major_nonconformities": audit.major_findings,
                "minor_nonconformities": audit.minor_findings,
                "observations": audit.observations,
                "opportunities": audit.opportunities or 0,
            },
            "iso_clause_analysis": iso_clause_findings,
            "findings": [
                {
                    "finding_number": f.finding_number,
                    "type": f.finding_type if isinstance(f.finding_type, str) else f.finding_type.value,
                    "severity": f.severity if isinstance(f.severity, str) else f.severity.value,
                    "iso_clause": f.iso_clause,
                    "title": f.title,
                    "description": f.description,
                    "evidence": f.evidence,
                    "requirement": f.requirement,
                    "corrective_action_required": f.corrective_action_required,
                    "assigned_to": f.assigned_to,
                    "due_date": f.due_date.isoformat() if f.due_date else None,
                    "status": f.status,
                }
                for f in findings
            ],
            "corrective_actions": {
                "required": audit.corrective_actions_required,
                "completed": audit.corrective_actions_completed,
            },
            "generated_at": datetime.utcnow().isoformat()
        }

        return report

    async def close_audit(self, audit_id: int) -> AuditPlanDB:
        """
        Close audit

        Args:
            audit_id: Audit identifier

        Returns:
            Updated audit plan

        Raises:
            ValueError: If audit not found or cannot be closed
        """
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Validate can close
        if audit.status != AuditStatus.REPORTED.value:
            raise ValueError(f"Audit must be reported before closing. Current status: {audit.status}")

        # Update audit status
        updates = {
            "status": AuditStatus.CLOSED.value,
            "closed_date": datetime.utcnow()
        }

        return await self.repo.update_audit(audit_id, updates)

    async def issue_report(self, audit_id: int, report_content: str) -> AuditPlanDB:
        """
        Issue audit report (move to REPORTED status)

        Args:
            audit_id: Audit identifier
            report_content: Report content/summary

        Returns:
            Updated audit plan

        Raises:
            ValueError: If audit not found or report cannot be issued
        """
        audit = await self.repo.get_audit(audit_id)
        if not audit:
            raise ValueError("Audit not found")

        # Validate workflow transition
        can_issue, error = can_issue_report(audit)
        if not can_issue:
            raise ValueError(error)

        # Update audit status
        updates = {
            "status": AuditStatus.REPORTED.value,
            "audit_report": report_content,
            "report_date": datetime.utcnow(),
            "report_distributed": True
        }

        # TODO: Distribute report to stakeholders
        # TODO: Publish event for report issued

        return await self.repo.update_audit(audit_id, updates)

    async def list_audits(
        self,
        tenant_id: str,
        status: Optional[AuditStatus] = None,
        audit_type: Optional[AuditType] = None
    ) -> List[AuditPlanDB]:
        """List audits with filters"""
        status_str = status.value if status else None
        type_str = audit_type.value if audit_type else None
        return await self.repo.list_audits(tenant_id, status_str, type_str)

    async def get_audit(self, audit_id: int) -> Optional[AuditPlanDB]:
        """Get audit by ID"""
        return await self.repo.get_audit(audit_id)

    async def get_audit_findings(self, audit_id: int) -> List[AuditFindingDB]:
        """Get all findings for an audit"""
        return await self.repo.list_audit_findings(audit_id)

    async def update_audit(self, audit_id: int, updates: Dict) -> AuditPlanDB:
        """
        Update audit

        Args:
            audit_id: Audit identifier
            updates: Fields to update

        Returns:
            Updated audit

        Raises:
            ValueError: If audit not found
        """
        audit = await self.repo.update_audit(audit_id, updates)
        if not audit:
            raise ValueError("Audit not found")

        return audit

    async def _auto_create_capa_for_finding(
        self,
        audit: AuditPlanDB,
        finding: AuditFindingDB
    ) -> CAPADB:
        """
        Auto-create CAPA for major audit finding

        Args:
            audit: Audit plan
            finding: Audit finding

        Returns:
            Created CAPA
        """
        # Generate CAPA number
        capa_number = f"CAPA-{audit.audit_code}-{finding.finding_number}"

        capa_data = {
            "tenant_id": audit.tenant_id,
            "capa_number": capa_number,
            "capa_type": CAPAType.CORRECTIVE.value,
            "source": CAPASource.AUDIT.value,
            "source_reference_id": finding.id,
            "source_reference_code": finding.finding_number,
            "title": f"Corrective Action for {finding.title}",
            "problem_description": finding.description,
            "root_cause_analysis": "To be determined during root cause analysis",
            "action_plan": "To be defined by assigned owner",
            "assigned_to": finding.assigned_to or audit.lead_auditor,
            "assigned_to_name": "TBD",
            "priority": "high" if finding.severity == FindingSeverity.MAJOR.value else "medium",
            "due_date": finding.due_date or datetime.utcnow(),
            "status": CAPAStatus.OPEN.value
        }

        return await self.repo.create_capa(capa_data)

    async def get_audit_statistics(self, tenant_id: str, from_date: datetime, to_date: datetime) -> Dict:
        """
        Get audit statistics for a period

        Args:
            tenant_id: Tenant identifier
            from_date: Start date
            to_date: End date

        Returns:
            Dict with audit statistics
        """
        # Get all audits in period
        all_audits = await self.repo.list_audits(tenant_id)

        # Filter by date
        audits = [
            a for a in all_audits
            if a.planned_date and from_date <= a.planned_date <= to_date
        ]

        # Calculate statistics
        total_audits = len(audits)
        completed_audits = len([a for a in audits if a.status in [
            AuditStatus.REPORTED.value,
            AuditStatus.CLOSED.value
        ]])

        total_findings = sum(a.findings_count for a in audits)
        total_major = sum(a.major_findings for a in audits)
        total_minor = sum(a.minor_findings for a in audits)
        total_observations = sum(a.observations or 0 for a in audits)

        by_type = {}
        for audit_type in AuditType:
            type_audits = [a for a in audits if a.audit_type == audit_type.value]
            by_type[audit_type.value] = len(type_audits)

        return {
            "period": {
                "from": from_date.isoformat(),
                "to": to_date.isoformat()
            },
            "total_audits": total_audits,
            "completed_audits": completed_audits,
            "completion_rate": (completed_audits / total_audits * 100) if total_audits > 0 else 0,
            "findings": {
                "total": total_findings,
                "major": total_major,
                "minor": total_minor,
                "observations": total_observations
            },
            "by_type": by_type,
            "audits": [
                {
                    "audit_code": a.audit_code,
                    "audit_name": a.audit_name,
                    "audit_type": a.audit_type if isinstance(a.audit_type, str) else a.audit_type.value,
                    "status": a.status if isinstance(a.status, str) else a.status.value,
                    "findings_count": a.findings_count,
                    "major_findings": a.major_findings
                }
                for a in audits
            ]
        }
