"""
Database Security Monitor

Monitors database security, RLS policies, suspicious queries, and access patterns.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from sqlalchemy import text

logger = logging.getLogger(__name__)


@dataclass
class SecurityAlert:
    """Security alert"""
    alert_type: str  # rls_disabled, suspicious_query, connection_spike, etc.
    severity: str  # critical, high, medium, low
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    auto_mitigated: bool = False


class SecurityMonitor:
    """
    Monitors database security

    Responsibilities:
    - RLS policy verification
    - Suspicious query detection
    - Connection spike detection (DOS)
    - SQL injection attempts
    - Privilege escalation attempts
    - Deadlock detection
    """

    def __init__(self):
        self.alerts: List[SecurityAlert] = []
        self.suspicious_patterns = [
            "SELECT * FROM users WHERE password",
            "SELECT * FROM auth.users",
            "DROP TABLE",
            "DROP SCHEMA",
            "TRUNCATE",
            "DELETE FROM users",
            "pg_sleep(",
            "UNION SELECT",
            "' OR '1'='1",
            "'; DROP TABLE",
            "GRANT ALL",
            "ALTER USER",
            "CREATE USER",
        ]

    async def check_rls_policies(self, session) -> List[SecurityAlert]:
        """
        Verify that RLS is enabled on critical tables

        Returns alerts for tables without RLS
        """
        alerts = []

        try:
            # Check RLS on critical schemas
            result = await session.execute(text("""
                SELECT
                    schemaname,
                    tablename,
                    rowsecurity as rls_enabled
                FROM pg_tables
                WHERE schemaname IN ('public', 'bcm', 'intelligence', 'auth', 'core')
                AND rowsecurity = false
                ORDER BY schemaname, tablename
            """))

            tables_without_rls = result.fetchall()

            if tables_without_rls:
                alert = SecurityAlert(
                    alert_type="rls_disabled",
                    severity="critical",
                    message=f"RLS disabled on {len(tables_without_rls)} critical tables",
                    details={
                        "tables": [
                            {"schema": row[0], "table": row[1]}
                            for row in tables_without_rls
                        ],
                        "action": "ENABLE RLS IMMEDIATELY",
                        "command": "ALTER TABLE {schema}.{table} ENABLE ROW LEVEL SECURITY"
                    },
                    timestamp=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)

        except Exception as e:
            logger.error(f"RLS check failed: {e}")

        return alerts

    async def check_suspicious_queries(
        self,
        query_metrics: Dict
    ) -> List[SecurityAlert]:
        """
        Detect suspicious query patterns (SQL injection, privilege escalation)
        """
        alerts = []

        for query in query_metrics.values():
            query_text = query.query_text.upper()

            for pattern in self.suspicious_patterns:
                if pattern.upper() in query_text:
                    alert = SecurityAlert(
                        alert_type="suspicious_query",
                        severity="critical",
                        message=f"Suspicious query pattern detected: {pattern}",
                        details={
                            "query": query.query_text,
                            "pattern": pattern,
                            "execution_count": query.execution_count,
                            "last_executed": query.last_executed.isoformat(),
                            "action": "INVESTIGATE IMMEDIATELY - Possible SQL injection or malicious activity"
                        },
                        timestamp=datetime.now()
                    )
                    alerts.append(alert)
                    self.alerts.append(alert)
                    logger.critical(f"🚨 SECURITY: Suspicious query: {pattern}")
                    break  # One alert per query

        return alerts

    async def check_connection_spike(self, session) -> Optional[SecurityAlert]:
        """
        Detect abnormal connection spikes (possible DOS attack)
        """
        try:
            result = await session.execute(text("""
                SELECT
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
            """))

            row = result.fetchone()
            total = row[0]
            active = row[1]
            idle = row[2]

            # Supabase typically has max 100 connections
            # Alert if >80% utilized
            if total > 80:
                alert = SecurityAlert(
                    alert_type="connection_spike",
                    severity="critical",
                    message=f"Connection spike detected: {total} total connections",
                    details={
                        "total_connections": total,
                        "active": active,
                        "idle": idle,
                        "possible_cause": "DOS attack or connection leak",
                        "action": "Kill idle connections, investigate connection source"
                    },
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
                return alert

        except Exception as e:
            logger.error(f"Connection spike check failed: {e}")

        return None

    async def check_deadlocks(self, session) -> List[SecurityAlert]:
        """
        Detect deadlocks and blocked queries
        """
        alerts = []

        try:
            result = await session.execute(text("""
                SELECT
                    pid,
                    usename,
                    application_name,
                    pg_blocking_pids(pid) as blocked_by,
                    state,
                    query,
                    NOW() - query_start as duration
                FROM pg_stat_activity
                WHERE cardinality(pg_blocking_pids(pid)) > 0
            """))

            blocked_queries = result.fetchall()

            if blocked_queries:
                alert = SecurityAlert(
                    alert_type="deadlock",
                    severity="high",
                    message=f"{len(blocked_queries)} queries are blocked (possible deadlock)",
                    details={
                        "blocked_queries": [
                            {
                                "pid": row[0],
                                "user": row[1],
                                "application": row[2],
                                "blocked_by": row[3],
                                "state": row[4],
                                "query": row[5][:200],
                                "duration": str(row[6])
                            }
                            for row in blocked_queries
                        ],
                        "action": "Investigate blocking queries, consider killing long-running transactions"
                    },
                    timestamp=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)

        except Exception as e:
            logger.error(f"Deadlock check failed: {e}")

        return alerts

    async def check_privilege_violations(self, session) -> List[SecurityAlert]:
        """
        Check for unauthorized privilege grants
        """
        alerts = []

        try:
            # Check for superuser grants to non-admin users
            result = await session.execute(text("""
                SELECT
                    usename,
                    usesuper,
                    usecreatedb,
                    usecreaterole
                FROM pg_user
                WHERE usesuper = true
                AND usename NOT IN ('postgres', 'supabase_admin')
            """))

            unauthorized_superusers = result.fetchall()

            if unauthorized_superusers:
                alert = SecurityAlert(
                    alert_type="privilege_violation",
                    severity="critical",
                    message=f"{len(unauthorized_superusers)} unauthorized superusers detected",
                    details={
                        "users": [
                            {
                                "username": row[0],
                                "superuser": row[1],
                                "createdb": row[2],
                                "createrole": row[3]
                            }
                            for row in unauthorized_superusers
                        ],
                        "action": "REVOKE superuser privileges immediately"
                    },
                    timestamp=datetime.now()
                )
                alerts.append(alert)
                self.alerts.append(alert)

        except Exception as e:
            logger.error(f"Privilege check failed: {e}")

        return alerts

    async def check_failed_login_attempts(self, session) -> Optional[SecurityAlert]:
        """
        Monitor failed authentication attempts (if auth logs are available)
        """
        try:
            # This requires auth.audit_log_entries table (Supabase)
            result = await session.execute(text("""
                SELECT
                    COUNT(*) as failed_attempts,
                    payload->>'email' as email
                FROM auth.audit_log_entries
                WHERE created_at > NOW() - INTERVAL '1 hour'
                AND payload->>'action' = 'login'
                AND payload->>'result' = 'failed'
                GROUP BY email
                HAVING COUNT(*) > 5
            """))

            suspicious_logins = result.fetchall()

            if suspicious_logins:
                alert = SecurityAlert(
                    alert_type="brute_force_attempt",
                    severity="high",
                    message=f"{len(suspicious_logins)} accounts under brute force attack",
                    details={
                        "accounts": [
                            {"email": row[1], "failed_attempts": row[0]}
                            for row in suspicious_logins
                        ],
                        "action": "Consider temporary account lockout or CAPTCHA"
                    },
                    timestamp=datetime.now()
                )
                self.alerts.append(alert)
                return alert

        except Exception as e:
            # auth.audit_log_entries might not exist
            logger.debug(f"Failed login check skipped: {e}")

        return None

    async def run_all_checks(self, session, query_metrics: Dict) -> List[SecurityAlert]:
        """
        Run all security checks

        Returns list of all alerts generated
        """
        all_alerts = []

        # RLS verification
        rls_alerts = await self.check_rls_policies(session)
        all_alerts.extend(rls_alerts)

        # Suspicious queries
        suspicious_alerts = await self.check_suspicious_queries(query_metrics)
        all_alerts.extend(suspicious_alerts)

        # Connection spike
        connection_alert = await self.check_connection_spike(session)
        if connection_alert:
            all_alerts.append(connection_alert)

        # Deadlocks
        deadlock_alerts = await self.check_deadlocks(session)
        all_alerts.extend(deadlock_alerts)

        # Privilege violations
        privilege_alerts = await self.check_privilege_violations(session)
        all_alerts.extend(privilege_alerts)

        # Failed logins
        login_alert = await self.check_failed_login_attempts(session)
        if login_alert:
            all_alerts.append(login_alert)

        return all_alerts

    def get_recent_alerts(
        self,
        hours: int = 24,
        severity: Optional[str] = None
    ) -> List[SecurityAlert]:
        """Get recent security alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)

        alerts = [a for a in self.alerts if a.timestamp > cutoff]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of security alerts"""
        recent_alerts = self.get_recent_alerts(hours=24)

        return {
            "total_alerts_24h": len(recent_alerts),
            "critical": len([a for a in recent_alerts if a.severity == "critical"]),
            "high": len([a for a in recent_alerts if a.severity == "high"]),
            "medium": len([a for a in recent_alerts if a.severity == "medium"]),
            "low": len([a for a in recent_alerts if a.severity == "low"]),
            "by_type": {
                alert_type: len([a for a in recent_alerts if a.alert_type == alert_type])
                for alert_type in set(a.alert_type for a in recent_alerts)
            }
        }
