"""
Audit Logger - ISO 22301 Compliance Logging
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from ..models.decision import Decision, DecisionRequest

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Логирование решений для ISO 22301 compliance

    Requirements (ISO 22301):
    - Immutable audit logs
    - 90-day retention minimum
    - Structured format (JSON)
    - Timestamp + decision details
    - Traceable decision chain

    Log format:
    {
        "timestamp": "2024-01-15T10:30:45.123Z",
        "event": "decision_made",
        "decision_id": "uuid",
        "request_id": "uuid",
        "service": "database",
        "action": "restart",
        "decision_type": "auto_approved",
        "outcome": "approved",
        "decided_by": "system",
        "justification": "Auto-approved by policy...",
        "context": {...},
        "policies_applied": {...}
    }
    """

    def __init__(
        self,
        log_dir: str = "/var/log/decision_center",
        retention_days: int = 90,
        storage: Optional['AuditStorage'] = None
    ):
        """
        Initialize Audit Logger

        Args:
            log_dir: Directory for audit logs
            retention_days: Retention period (default 90 days for ISO 22301)
            storage: Optional database storage for audit logs
        """
        self.log_dir = Path(log_dir)
        self.retention_days = retention_days
        self.storage = storage

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current log file (rotated daily)
        self.current_log_file = self._get_log_file_path()

        logger.info(
            f"Audit Logger initialized "
            f"(log_dir={log_dir}, retention_days={retention_days})"
        )

    async def log_decision(
        self,
        decision: Decision,
        request: DecisionRequest,
        policies: Optional[Dict[str, Any]] = None
    ):
        """
        Логирует принятое решение

        Args:
            decision: Decision object
            request: Original request
            policies: Applied policies
        """
        # Build audit log entry
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "decision_made",
            "decision_id": decision.decision_id,
            "request_id": decision.request_id,
            "service": request.service,
            "action": request.action,
            "decision_type": decision.decision_type.value,
            "outcome": decision.outcome.value,
            "decided_by": decision.decided_by,
            "justification": decision.justification,
            "priority": request.priority,
            "requester": request.requester,
            "context": request.context,
            "policies_applied": policies or {},
            "metadata": decision.metadata,
            "decided_at": decision.decided_at.isoformat() + "Z",
            "expires_at": decision.expires_at.isoformat() + "Z" if decision.expires_at else None
        }

        # Write to file (immutable append-only log)
        self._write_to_file(audit_entry)

        # Write to database storage if available
        if self.storage:
            await self.storage.store_audit_log(audit_entry)

        logger.debug(f"Audit log written: {decision.decision_id}")

    async def log_escalation(
        self,
        escalation_id: str,
        escalation_level: str,
        request: DecisionRequest,
        reason: str,
        urgency: int
    ):
        """
        Логирует эскалацию

        Args:
            escalation_id: Escalation ID
            escalation_level: Escalation level
            request: Original request
            reason: Escalation reason
            urgency: Urgency level
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "escalation_created",
            "escalation_id": escalation_id,
            "request_id": request.request_id,
            "service": request.service,
            "action": request.action,
            "escalation_level": escalation_level,
            "reason": reason,
            "urgency": urgency,
            "priority": request.priority,
            "requester": request.requester,
            "context": request.context
        }

        self._write_to_file(audit_entry)

        if self.storage:
            await self.storage.store_audit_log(audit_entry)

        logger.debug(f"Escalation audit log written: {escalation_id}")

    async def log_escalation_response(
        self,
        escalation_id: str,
        operator: str,
        approved: bool,
        resolution: str,
        response_time_seconds: int
    ):
        """
        Логирует ответ на эскалацию

        Args:
            escalation_id: Escalation ID
            operator: Operator who responded
            approved: Whether approved
            resolution: Resolution text
            response_time_seconds: Response time
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "escalation_resolved",
            "escalation_id": escalation_id,
            "operator": operator,
            "approved": approved,
            "resolution": resolution,
            "response_time_seconds": response_time_seconds
        }

        self._write_to_file(audit_entry)

        if self.storage:
            await self.storage.store_audit_log(audit_entry)

        logger.debug(f"Escalation response logged: {escalation_id}")

    async def log_policy_change(
        self,
        changed_by: str,
        service: str,
        old_policy: Dict[str, Any],
        new_policy: Dict[str, Any],
        reason: str
    ):
        """
        Логирует изменения в политиках

        Args:
            changed_by: Who changed the policy
            service: Service name
            old_policy: Old policy configuration
            new_policy: New policy configuration
            reason: Reason for change
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "policy_changed",
            "changed_by": changed_by,
            "service": service,
            "old_policy": old_policy,
            "new_policy": new_policy,
            "reason": reason
        }

        self._write_to_file(audit_entry)

        if self.storage:
            await self.storage.store_audit_log(audit_entry)

        logger.info(f"Policy change logged: {service} by {changed_by}")

    def _write_to_file(self, audit_entry: Dict[str, Any]):
        """
        Записывает audit entry в файл (append-only)

        Args:
            audit_entry: Audit log entry
        """
        try:
            # Rotate log file if needed (daily rotation)
            current_file = self._get_log_file_path()
            if current_file != self.current_log_file:
                logger.info(f"Rotating log file to: {current_file}")
                self.current_log_file = current_file

            # Write as JSON line (JSONL format)
            with open(self.current_log_file, "a") as f:
                json.dump(audit_entry, f, separators=(",", ":"))
                f.write("\n")

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)
            # Critical: audit logging failure should be noticed
            raise

    def _get_log_file_path(self) -> Path:
        """
        Получает путь к текущему log файлу (daily rotation)

        Returns:
            Path to current log file
        """
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / f"audit-{date_str}.jsonl"

    async def cleanup_old_logs(self):
        """
        Удаляет старые логи (retention policy)

        Keeps logs for retention_days (default 90 days for ISO 22301)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)

        logger.info(f"Cleaning up logs older than {cutoff_date.strftime('%Y-%m-%d')}")

        deleted_count = 0

        # Find and delete old log files
        for log_file in self.log_dir.glob("audit-*.jsonl"):
            try:
                # Extract date from filename
                date_str = log_file.stem.replace("audit-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff_date:
                    logger.info(f"Deleting old log file: {log_file}")
                    log_file.unlink()
                    deleted_count += 1

            except Exception as e:
                logger.error(f"Failed to process log file {log_file}: {e}")

        logger.info(f"Cleanup complete: {deleted_count} files deleted")

        return deleted_count

    async def query_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        service: Optional[str] = None,
        decision_type: Optional[str] = None,
        outcome: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Запрашивает audit logs (для анализа и отчетов)

        Args:
            start_date: Start date filter
            end_date: End date filter
            service: Service name filter
            decision_type: Decision type filter
            outcome: Outcome filter
            limit: Max results

        Returns:
            List of audit log entries
        """
        # Use database storage if available (faster queries)
        if self.storage:
            return await self.storage.query_audit_logs(
                start_date=start_date,
                end_date=end_date,
                service=service,
                decision_type=decision_type,
                outcome=outcome,
                limit=limit
            )

        # Fallback: read from files (slower)
        results = []

        # Determine which files to read
        if start_date and end_date:
            date_range = self._get_date_range(start_date, end_date)
        else:
            # Read last 7 days by default
            date_range = self._get_date_range(
                datetime.utcnow() - timedelta(days=7),
                datetime.utcnow()
            )

        # Read log files
        for date in date_range:
            log_file = self.log_dir / f"audit-{date.strftime('%Y-%m-%d')}.jsonl"

            if not log_file.exists():
                continue

            with open(log_file, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if service and entry.get("service") != service:
                            continue
                        if decision_type and entry.get("decision_type") != decision_type:
                            continue
                        if outcome and entry.get("outcome") != outcome:
                            continue

                        results.append(entry)

                        # Limit results
                        if len(results) >= limit:
                            return results

                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in audit log: {e}")

        return results

    def _get_date_range(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        Получает список дат между start и end

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of dates
        """
        dates = []
        current = start_date

        while current <= end_date:
            dates.append(current)
            current += timedelta(days=1)

        return dates

    async def get_decision_history(self, service: str, days: int = 30) -> Dict[str, Any]:
        """
        Получает историю решений для сервиса

        Args:
            service: Service name
            days: Number of days to look back

        Returns:
            Decision history statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        logs = await self.query_logs(
            start_date=start_date,
            service=service,
            limit=1000
        )

        # Calculate statistics
        stats = {
            "service": service,
            "period_days": days,
            "total_decisions": len(logs),
            "auto_approved": 0,
            "escalated": 0,
            "ai_consulted": 0,
            "requires_approval": 0,
            "rejected": 0,
            "outcomes": {
                "approved": 0,
                "rejected": 0,
                "pending": 0,
                "escalated": 0
            },
            "actions": {}
        }

        for log in logs:
            if log.get("event") != "decision_made":
                continue

            decision_type = log.get("decision_type", "")
            outcome = log.get("outcome", "")
            action = log.get("action", "")

            # Count decision types
            if decision_type == "auto_approved":
                stats["auto_approved"] += 1
            elif decision_type == "escalated":
                stats["escalated"] += 1
            elif decision_type == "ai_consulted":
                stats["ai_consulted"] += 1
            elif decision_type == "requires_approval":
                stats["requires_approval"] += 1
            elif decision_type == "rejected":
                stats["rejected"] += 1

            # Count outcomes
            if outcome in stats["outcomes"]:
                stats["outcomes"][outcome] += 1

            # Count actions
            stats["actions"][action] = stats["actions"].get(action, 0) + 1

        return stats
