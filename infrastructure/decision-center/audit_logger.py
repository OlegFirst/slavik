"""
Audit Logger (Phase 1.1)
========================

Full audit trail for ISO 22301 compliance

Features:
- Logs all decisions (automated and manual)
- Stores in database and file
- Includes reasoning, context, and policy references
- Queryable audit trail
- Retention policy enforcement
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from infrastructure.decision_center.decision_models import (
    Decision,
    DecisionAuditLog,
    EscalationRequest,
    ApprovalRequest
)

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Audit Logger for Decision Center

    Maintains comprehensive audit trail for all decisions,
    escalations, and approvals for ISO 22301 compliance.
    """

    def __init__(
        self,
        db_session_factory=None,
        log_dir: Optional[str] = None,
        retention_days: int = 90
    ):
        """
        Initialize Audit Logger

        Args:
            db_session_factory: SQLAlchemy session factory (optional)
            log_dir: Directory for file-based audit logs
            retention_days: Days to retain audit logs
        """
        self.db_session_factory = db_session_factory
        self.retention_days = retention_days

        # Setup file logging
        if log_dir is None:
            log_dir = Path(__file__).parent / "audit_logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current log file (rotated daily)
        self.current_log_file = self._get_log_file_path()

        logger.info(f"AuditLogger initialized (log_dir={self.log_dir}, retention={retention_days} days)")

    def _get_log_file_path(self) -> Path:
        """Get path to current day's log file"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{date_str}.jsonl"

    async def log_decision(self, decision: Decision) -> None:
        """
        Log a decision to audit trail

        Args:
            decision: Decision object to log
        """
        audit_entry = DecisionAuditLog(
            decision_id=decision.decision_id,
            decision_type=decision.decision_type.value,
            service_name=decision.service_name,
            action="decision_made",
            action_details=f"{decision.outcome.value}: {decision.action_type or 'N/A'}",
            trigger_event=decision.trigger_event_id,
            policy_applied=decision.policy_reference,
            reasoning=decision.reasoning,
            confidence_score=decision.confidence_score,
            automated=decision.approved_by is None,
            actor=decision.approved_by or "system",
            outcome=decision.outcome.value,
            success=decision.success,
            tenant_id=decision.tenant_id,
            correlation_id=decision.correlation_id,
            event_data={
                'trigger_data': decision.trigger_data,
                'parameters': decision.parameters,
                'result_data': decision.result_data,
                'metadata': decision.metadata
            }
        )

        await self._write_audit_log(audit_entry)

    async def log_escalation(self, escalation: EscalationRequest) -> None:
        """
        Log an escalation to audit trail

        Args:
            escalation: EscalationRequest object to log
        """
        audit_entry = DecisionAuditLog(
            decision_id=escalation.decision_id,
            decision_type="escalation",
            service_name=escalation.service_name,
            action="escalation_created",
            action_details=f"{escalation.escalation_type}: {escalation.reason}",
            reasoning=escalation.reason,
            automated=True,
            actor="system",
            outcome=escalation.status.value,
            tenant_id=escalation.tenant_id,
            correlation_id=escalation.correlation_id,
            event_data={
                'severity': escalation.severity,
                'context_data': escalation.context_data,
                'assigned_to': escalation.assigned_to,
                'assigned_team': escalation.assigned_team,
                'metadata': escalation.metadata
            }
        )

        await self._write_audit_log(audit_entry)

    async def log_approval(self, approval: ApprovalRequest, action: str = "approval_requested") -> None:
        """
        Log an approval request/decision to audit trail

        Args:
            approval: ApprovalRequest object to log
            action: Type of action (approval_requested, approval_granted, approval_rejected)
        """
        audit_entry = DecisionAuditLog(
            decision_id=approval.decision_id,
            decision_type="approval",
            service_name=approval.service_name,
            action=action,
            action_details=f"{approval.action_type}: {approval.requested_action}",
            reasoning=approval.justification,
            automated=action == "approval_requested",
            actor=approval.decision_by or "system",
            outcome=approval.status.value,
            tenant_id=approval.tenant_id,
            correlation_id=approval.correlation_id,
            event_data={
                'impact_assessment': approval.impact_assessment,
                'rollback_plan': approval.rollback_plan,
                'required_approvers': approval.required_approvers,
                'approvers': approval.approvers,
                'metadata': approval.metadata
            }
        )

        await self._write_audit_log(audit_entry)

    async def log_action_execution(
        self,
        decision_id: str,
        service_name: str,
        action: str,
        success: bool,
        details: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log execution of an action

        Args:
            decision_id: ID of the decision
            service_name: Name of the service
            action: Action taken
            success: Whether action succeeded
            details: Details of the execution
            before_state: State before action
            after_state: State after action
        """
        audit_entry = DecisionAuditLog(
            decision_id=decision_id,
            decision_type="execution",
            service_name=service_name,
            action="action_executed",
            action_details=f"{action}: {details}",
            reasoning=f"Executing decision {decision_id}",
            automated=True,
            actor="system",
            outcome="success" if success else "failure",
            success=success,
            before_state=before_state or {},
            after_state=after_state or {}
        )

        await self._write_audit_log(audit_entry)

    async def _write_audit_log(self, audit_entry: DecisionAuditLog) -> None:
        """
        Write audit log entry to both file and database

        Args:
            audit_entry: DecisionAuditLog to write
        """
        # Write to file
        await self._write_to_file(audit_entry)

        # Write to database (if available)
        if self.db_session_factory:
            await self._write_to_database(audit_entry)

        logger.debug(f"Audit log written: {audit_entry.action} for {audit_entry.service_name}")

    async def _write_to_file(self, audit_entry: DecisionAuditLog) -> None:
        """Write audit entry to JSONL file"""
        try:
            # Check if we need to rotate log file
            current_file = self._get_log_file_path()
            if current_file != self.current_log_file:
                self.current_log_file = current_file

            # Write as JSON line
            with open(self.current_log_file, 'a') as f:
                json.dump(audit_entry.to_dict(), f)
                f.write('\n')

        except Exception as e:
            logger.error(f"Failed to write audit log to file: {e}")

    async def _write_to_database(self, audit_entry: DecisionAuditLog) -> None:
        """Write audit entry to database"""
        try:
            async with self.db_session_factory() as session:
                # Insert into audit_logs table
                await session.execute(
                    text("""
                        INSERT INTO decision_audit_logs (
                            log_id, timestamp, decision_id, decision_type,
                            service_name, action, action_details, trigger_event,
                            policy_applied, reasoning, confidence_score,
                            automated, actor, outcome, success,
                            compliance_standard, compliance_clause,
                            before_state, after_state, event_data,
                            tenant_id, correlation_id, metadata
                        ) VALUES (
                            :log_id, :timestamp, :decision_id, :decision_type,
                            :service_name, :action, :action_details, :trigger_event,
                            :policy_applied, :reasoning, :confidence_score,
                            :automated, :actor, :outcome, :success,
                            :compliance_standard, :compliance_clause,
                            :before_state::jsonb, :after_state::jsonb, :event_data::jsonb,
                            :tenant_id, :correlation_id, :metadata::jsonb
                        )
                    """),
                    {
                        'log_id': audit_entry.log_id,
                        'timestamp': audit_entry.timestamp,
                        'decision_id': audit_entry.decision_id,
                        'decision_type': audit_entry.decision_type,
                        'service_name': audit_entry.service_name,
                        'action': audit_entry.action,
                        'action_details': audit_entry.action_details,
                        'trigger_event': audit_entry.trigger_event,
                        'policy_applied': audit_entry.policy_applied,
                        'reasoning': audit_entry.reasoning,
                        'confidence_score': audit_entry.confidence_score,
                        'automated': audit_entry.automated,
                        'actor': audit_entry.actor,
                        'outcome': audit_entry.outcome,
                        'success': audit_entry.success,
                        'compliance_standard': audit_entry.compliance_standard,
                        'compliance_clause': audit_entry.compliance_clause,
                        'before_state': json.dumps(audit_entry.before_state),
                        'after_state': json.dumps(audit_entry.after_state),
                        'event_data': json.dumps(audit_entry.event_data),
                        'tenant_id': audit_entry.tenant_id,
                        'correlation_id': audit_entry.correlation_id,
                        'metadata': json.dumps(audit_entry.metadata)
                    }
                )
                await session.commit()

        except Exception as e:
            logger.error(f"Failed to write audit log to database: {e}")
            # Don't raise - file log is primary, DB is secondary

    async def query_logs(
        self,
        service_name: Optional[str] = None,
        decision_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DecisionAuditLog]:
        """
        Query audit logs

        Args:
            service_name: Filter by service name
            decision_type: Filter by decision type
            start_date: Start date for query
            end_date: End date for query
            limit: Maximum results to return

        Returns:
            List of DecisionAuditLog entries
        """
        if not self.db_session_factory:
            # Fall back to file-based query
            return await self._query_from_files(service_name, decision_type, start_date, end_date, limit)

        try:
            async with self.db_session_factory() as session:
                query = "SELECT * FROM decision_audit_logs WHERE 1=1"
                params = {}

                if service_name:
                    query += " AND service_name = :service_name"
                    params['service_name'] = service_name

                if decision_type:
                    query += " AND decision_type = :decision_type"
                    params['decision_type'] = decision_type

                if start_date:
                    query += " AND timestamp >= :start_date"
                    params['start_date'] = start_date

                if end_date:
                    query += " AND timestamp <= :end_date"
                    params['end_date'] = end_date

                query += " ORDER BY timestamp DESC LIMIT :limit"
                params['limit'] = limit

                result = await session.execute(text(query), params)
                rows = result.fetchall()

                # Convert to DecisionAuditLog objects
                logs = []
                for row in rows:
                    # TODO: Proper ORM mapping
                    logs.append(row)

                return logs

        except Exception as e:
            logger.error(f"Failed to query audit logs from database: {e}")
            return []

    async def _query_from_files(
        self,
        service_name: Optional[str] = None,
        decision_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit logs from JSONL files"""
        results = []

        # Get list of log files in date range
        log_files = sorted(self.log_dir.glob("audit_*.jsonl"), reverse=True)

        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue

                        entry = json.loads(line)

                        # Apply filters
                        if service_name and entry.get('service_name') != service_name:
                            continue

                        if decision_type and entry.get('decision_type') != decision_type:
                            continue

                        if start_date:
                            entry_date = datetime.fromisoformat(entry['timestamp'])
                            if entry_date < start_date:
                                continue

                        if end_date:
                            entry_date = datetime.fromisoformat(entry['timestamp'])
                            if entry_date > end_date:
                                continue

                        results.append(entry)

                        if len(results) >= limit:
                            return results

            except Exception as e:
                logger.error(f"Error reading audit log file {log_file}: {e}")
                continue

        return results

    async def cleanup_old_logs(self) -> None:
        """
        Clean up old audit logs based on retention policy

        Removes logs older than retention_days from both file and database.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        logger.info(f"Cleaning up audit logs older than {cutoff_date.isoformat()}")

        # Clean up files
        deleted_files = 0
        for log_file in self.log_dir.glob("audit_*.jsonl"):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace("audit_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_files += 1
                    logger.debug(f"Deleted old audit log: {log_file.name}")

            except Exception as e:
                logger.error(f"Error cleaning up audit log file {log_file}: {e}")

        logger.info(f"Deleted {deleted_files} old audit log files")

        # Clean up database
        if self.db_session_factory:
            try:
                async with self.db_session_factory() as session:
                    result = await session.execute(
                        text("DELETE FROM decision_audit_logs WHERE timestamp < :cutoff_date"),
                        {'cutoff_date': cutoff_date}
                    )
                    await session.commit()
                    logger.info(f"Deleted {result.rowcount} old audit log entries from database")

            except Exception as e:
                logger.error(f"Error cleaning up audit logs from database: {e}")

    async def get_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate ISO 22301 compliance report

        Args:
            start_date: Start of reporting period
            end_date: End of reporting period

        Returns:
            Dict with compliance metrics
        """
        logs = await self.query_logs(start_date=start_date, end_date=end_date, limit=10000)

        # Calculate metrics
        total_decisions = len(logs)
        automated_decisions = sum(1 for log in logs if log.get('automated', True))
        manual_decisions = total_decisions - automated_decisions

        # Decisions by type
        by_type = {}
        for log in logs:
            dt = log.get('decision_type', 'unknown')
            by_type[dt] = by_type.get(dt, 0) + 1

        # Success rate
        decisions_with_outcome = [log for log in logs if log.get('success') is not None]
        successful = sum(1 for log in decisions_with_outcome if log.get('success'))
        success_rate = (successful / len(decisions_with_outcome) * 100) if decisions_with_outcome else 0

        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_decisions': total_decisions,
            'automated_decisions': automated_decisions,
            'manual_decisions': manual_decisions,
            'automation_rate': (automated_decisions / total_decisions * 100) if total_decisions > 0 else 0,
            'success_rate': success_rate,
            'decisions_by_type': by_type,
            'compliance_standard': 'ISO 22301:2019',
            'audit_retention_days': self.retention_days,
            'generated_at': datetime.utcnow().isoformat()
        }
