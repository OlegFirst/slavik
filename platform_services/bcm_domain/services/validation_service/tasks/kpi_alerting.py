"""
KPI Alerting Tasks
Celery tasks for KPI threshold monitoring and alerting
"""

from celery import shared_task
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from database import get_db, KPIDefinition, KPIMeasurement, KPIAlert

logger = logging.getLogger(__name__)


# ===== EMAIL CONFIGURATION =====

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "bcms-alerts@example.com")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"


# ===== HELPER FUNCTIONS =====

def calculate_kpi_status(value: float, kpi_def: KPIDefinition) -> str:
    """
    Calculate KPI performance status based on thresholds

    Args:
        value: Current KPI value
        kpi_def: KPI definition with thresholds

    Returns:
        Status: "excellent", "good", "warning", "critical"
    """
    target = kpi_def.target_value
    warning = kpi_def.warning_threshold
    critical = kpi_def.critical_threshold
    direction = kpi_def.performance_direction

    if direction == "higher_better":
        if value >= target:
            return "excellent"
        elif value >= warning:
            return "good"
        elif value >= critical:
            return "warning"
        else:
            return "critical"

    elif direction == "lower_better":
        if value <= target:
            return "excellent"
        elif value <= warning:
            return "good"
        elif value <= critical:
            return "warning"
        else:
            return "critical"

    elif direction == "target_value":
        deviation = abs(value - target)
        if deviation == 0:
            return "excellent"
        elif deviation <= abs(target - warning):
            return "good"
        elif deviation <= abs(target - critical):
            return "warning"
        else:
            return "critical"

    return "no_data"


def send_email_alert(
    to_emails: List[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None
):
    """
    Send email alert

    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
    """
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logger.warning("Email credentials not configured, skipping email send")
        return

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = ', '.join(to_emails)

        # Attach plain text
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)

        # Attach HTML if provided
        if html_body:
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)

        # Send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, to_emails, msg.as_string())

        logger.info(f" Email alert sent to {to_emails}")

    except Exception as e:
        logger.error(f" Failed to send email alert: {e}")


def create_alert_record(
    tenant_id: str,
    kpi_id: int,
    kpi_code: str,
    severity: str,
    message: str,
    current_value: float,
    threshold_breached: str,
    metadata: Optional[Dict] = None
):
    """
    Create alert record in database

    Args:
        tenant_id: Tenant ID
        kpi_id: KPI ID
        kpi_code: KPI code
        severity: Alert severity (warning, critical)
        message: Alert message
        current_value: Current KPI value
        threshold_breached: Which threshold was breached
        metadata: Additional metadata
    """
    try:
        db = next(get_db())

        alert = KPIAlert(
            tenant_id=tenant_id,
            kpi_id=kpi_id,
            kpi_code=kpi_code,
            alert_date=datetime.utcnow(),
            severity=severity,
            message=message,
            current_value=current_value,
            threshold_breached=threshold_breached,
            status="active",
            metadata=metadata or {}
        )

        db.add(alert)
        db.commit()

        logger.info(f" Alert created for KPI {kpi_code}: {severity}")

    except Exception as e:
        logger.error(f" Failed to create alert: {e}")
        db.rollback()


# ===== ALERTING TASKS =====

@shared_task(name='tasks.kpi_alerting.check_kpi_thresholds')
def check_kpi_thresholds(tenant_id: str, kpi_id: int):
    """
    Check if KPI breaches thresholds and send alerts

    Args:
        tenant_id: Tenant ID
        kpi_id: KPI ID to check
    """
    try:
        db = next(get_db())

        # Get KPI definition
        kpi_def = db.query(KPIDefinition).filter(
            KPIDefinition.id == kpi_id,
            KPIDefinition.tenant_id == tenant_id
        ).first()

        if not kpi_def:
            logger.warning(f"KPI {kpi_id} not found for tenant {tenant_id}")
            return

        # Get latest measurement
        latest_measurement = db.query(KPIMeasurement).filter(
            KPIMeasurement.kpi_id == kpi_id,
            KPIMeasurement.tenant_id == tenant_id
        ).order_by(KPIMeasurement.measurement_date.desc()).first()

        if not latest_measurement:
            logger.info(f"No measurements for KPI {kpi_def.kpi_code}")
            return

        # Calculate status
        status = calculate_kpi_status(latest_measurement.value, kpi_def)

        # Check if alert needed
        if status in ["warning", "critical"]:
            # Check if we already sent an alert recently (avoid spam)
            recent_alert = db.query(KPIAlert).filter(
                KPIAlert.kpi_id == kpi_id,
                KPIAlert.tenant_id == tenant_id,
                KPIAlert.status == "active",
                KPIAlert.alert_date >= datetime.utcnow() - timedelta(hours=24)
            ).first()

            if recent_alert:
                logger.info(f"Alert already sent for KPI {kpi_def.kpi_code} in last 24h")
                return

            # Create alert message
            threshold_name = "warning" if status == "warning" else "critical"
            threshold_value = kpi_def.warning_threshold if status == "warning" else kpi_def.critical_threshold

            message = f"""
KPI Alert: {kpi_def.kpi_name}

Status: {status.upper()}
Current Value: {latest_measurement.value:.2f} {kpi_def.unit_of_measure or ''}
{threshold_name.capitalize()} Threshold: {threshold_value:.2f} {kpi_def.unit_of_measure or ''}
Target Value: {kpi_def.target_value:.2f} {kpi_def.unit_of_measure or ''}

Measured at: {latest_measurement.measurement_date.strftime('%Y-%m-%d %H:%M:%S UTC')}

Action required: Please review and take corrective action.
            """.strip()

            # Create alert record
            create_alert_record(
                tenant_id=tenant_id,
                kpi_id=kpi_id,
                kpi_code=kpi_def.kpi_code,
                severity=status,
                message=message,
                current_value=latest_measurement.value,
                threshold_breached=threshold_name,
                metadata={
                    "kpi_name": kpi_def.kpi_name,
                    "measurement_date": latest_measurement.measurement_date.isoformat(),
                    "threshold_value": threshold_value
                }
            )

            # Send email alert if configured
            if kpi_def.alert_emails:
                html_body = f"""
<html>
<body>
<h2 style="color: {'orange' if status == 'warning' else 'red'};">KPI Alert: {kpi_def.kpi_name}</h2>
<p><strong>Status:</strong> <span style="color: {'orange' if status == 'warning' else 'red'};">{status.upper()}</span></p>
<table border="1" cellpadding="5" cellspacing="0">
    <tr><td><strong>Current Value</strong></td><td>{latest_measurement.value:.2f} {kpi_def.unit_of_measure or ''}</td></tr>
    <tr><td><strong>{threshold_name.capitalize()} Threshold</strong></td><td>{threshold_value:.2f} {kpi_def.unit_of_measure or ''}</td></tr>
    <tr><td><strong>Target Value</strong></td><td>{kpi_def.target_value:.2f} {kpi_def.unit_of_measure or ''}</td></tr>
    <tr><td><strong>Measured at</strong></td><td>{latest_measurement.measurement_date.strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
</table>
<p><strong>Action required:</strong> Please review and take corrective action.</p>
</body>
</html>
                """

                send_email_alert(
                    to_emails=kpi_def.alert_emails,
                    subject=f"[{status.upper()}] KPI Alert: {kpi_def.kpi_name}",
                    body=message,
                    html_body=html_body
                )

            logger.info(f" Alert triggered for KPI {kpi_def.kpi_code}: {status}")

        else:
            logger.info(f" KPI {kpi_def.kpi_code} is {status}, no alert needed")

    except Exception as e:
        logger.error(f" Failed to check KPI thresholds: {e}")


@shared_task(name='tasks.kpi_alerting.check_kpi_thresholds_hourly')
def check_kpi_thresholds_hourly():
    """
    Hourly task: Check all KPI thresholds for all tenants
    Runs every hour via Celery Beat
    """
    logger.info(" Starting hourly KPI threshold check")

    try:
        db = next(get_db())

        # Get all active KPIs
        kpis = db.query(KPIDefinition).filter(
            KPIDefinition.is_active == True
        ).all()

        checked = 0
        for kpi in kpis:
            check_kpi_thresholds.delay(kpi.tenant_id, kpi.id)
            checked += 1

        logger.info(f" Threshold checks queued for {checked} KPIs")

    except Exception as e:
        logger.error(f" Hourly threshold check failed: {e}")


@shared_task(name='tasks.kpi_alerting.send_kpi_alert')
def send_kpi_alert(alert_id: int):
    """
    Send alert notification for specific alert

    Args:
        alert_id: Alert ID
    """
    try:
        db = next(get_db())

        alert = db.query(KPIAlert).filter(KPIAlert.id == alert_id).first()

        if not alert:
            logger.warning(f"Alert {alert_id} not found")
            return

        # Get KPI definition for alert emails
        kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == alert.kpi_id).first()

        if not kpi_def or not kpi_def.alert_emails:
            logger.warning(f"No alert emails configured for KPI {alert.kpi_code}")
            return

        # Send email
        send_email_alert(
            to_emails=kpi_def.alert_emails,
            subject=f"[{alert.severity.upper()}] KPI Alert: {kpi_def.kpi_name}",
            body=alert.message
        )

        # Mark alert as notified
        alert.notified_at = datetime.utcnow()
        db.commit()

        logger.info(f" Alert {alert_id} notification sent")

    except Exception as e:
        logger.error(f" Failed to send alert notification: {e}")


@shared_task(name='tasks.kpi_alerting.auto_resolve_alerts')
def auto_resolve_alerts():
    """
    Auto-resolve alerts when KPI returns to acceptable levels
    Runs daily
    """
    logger.info(" Starting auto-resolve alerts task")

    try:
        db = next(get_db())

        # Get all active alerts
        active_alerts = db.query(KPIAlert).filter(
            KPIAlert.status == "active"
        ).all()

        resolved = 0
        for alert in active_alerts:
            # Get latest measurement
            latest_measurement = db.query(KPIMeasurement).filter(
                KPIMeasurement.kpi_id == alert.kpi_id
            ).order_by(KPIMeasurement.measurement_date.desc()).first()

            if not latest_measurement:
                continue

            # Get KPI definition
            kpi_def = db.query(KPIDefinition).filter(KPIDefinition.id == alert.kpi_id).first()

            if not kpi_def:
                continue

            # Check current status
            status = calculate_kpi_status(latest_measurement.value, kpi_def)

            # If status is good/excellent, resolve alert
            if status in ["good", "excellent"]:
                alert.status = "resolved"
                alert.resolved_at = datetime.utcnow()
                alert.resolution_notes = f"Auto-resolved: KPI returned to {status} status with value {latest_measurement.value:.2f}"
                resolved += 1

        db.commit()
        logger.info(f" Auto-resolved {resolved} alerts")

    except Exception as e:
        logger.error(f" Auto-resolve alerts failed: {e}")
        db.rollback()


@shared_task(name='tasks.kpi_alerting.send_daily_kpi_summary')
def send_daily_kpi_summary(tenant_id: str):
    """
    Send daily KPI summary email

    Args:
        tenant_id: Tenant ID
    """
    logger.info(f" Sending daily KPI summary for tenant {tenant_id}")

    try:
        db = next(get_db())

        # Get all KPIs for tenant
        kpis = db.query(KPIDefinition).filter(
            KPIDefinition.tenant_id == tenant_id,
            KPIDefinition.is_active == True
        ).all()

        if not kpis:
            logger.info(f"No active KPIs for tenant {tenant_id}")
            return

        # Collect summary data
        summary_data = []
        critical_count = 0
        warning_count = 0

        for kpi in kpis:
            latest = db.query(KPIMeasurement).filter(
                KPIMeasurement.kpi_id == kpi.id
            ).order_by(KPIMeasurement.measurement_date.desc()).first()

            if latest:
                status = calculate_kpi_status(latest.value, kpi)
                summary_data.append({
                    "name": kpi.kpi_name,
                    "code": kpi.kpi_code,
                    "value": latest.value,
                    "unit": kpi.unit_of_measure or '',
                    "target": kpi.target_value,
                    "status": status,
                    "measured_at": latest.measurement_date
                })

                if status == "critical":
                    critical_count += 1
                elif status == "warning":
                    warning_count += 1

        # Build email
        subject = f"Daily KPI Summary - {critical_count} Critical, {warning_count} Warning"

        body = f"""
Daily KPI Summary
Tenant: {tenant_id}
Date: {datetime.utcnow().strftime('%Y-%m-%d')}

Critical KPIs: {critical_count}
Warning KPIs: {warning_count}

KPI Details:
"""

        for data in summary_data:
            body += f"\n- {data['name']}: {data['value']:.2f} {data['unit']} ({data['status']})"

        # Send to configured recipients (you'd need to configure this)
        # For now, we'll log it
        logger.info(f"Daily KPI Summary:\n{body}")

    except Exception as e:
        logger.error(f" Failed to send daily KPI summary: {e}")
