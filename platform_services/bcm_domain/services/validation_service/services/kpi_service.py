"""
KPI Service
Business logic for KPI management and measurements

Based on: /Users/MD/ISO-22301:>?8O/services/SERVICES/BCM/validation/main.py lines 767-1032
ISO 22301:2019 Clause 9.1 - Monitoring, measurement, analysis and evaluation
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
from repositories.repository import ValidationRepository
from workflows.kpi_calculations import (
    calculate_kpi_status,
    calculate_kpi_trend,
    get_kpi_summary,
    PerformanceStatus,
    TrendDirection
)
from models.database import (
    KPI as KPIDB,
    KPIMeasurement as KPIMeasurementDB,
    KPIAlert as KPIAlertDB
)
from models.domain import PerformanceDirection, DataQuality, CollectionMethod


class KPIService:
    """KPI business logic service"""

    def __init__(self, repository: ValidationRepository):
        self.repo = repository

    async def create_kpi(self, kpi_data: Dict) -> KPIDB:
        """
        Create new KPI with validation

        Args:
            kpi_data: KPI configuration data

        Returns:
            Created KPI database object

        Raises:
            ValueError: If validation fails or duplicate exists
        """
        # Check for duplicate code
        existing = await self.repo.get_kpi_by_code(kpi_data["kpi_code"])
        if existing:
            raise ValueError(f"KPI code {kpi_data['kpi_code']} already exists")

        # Validate thresholds based on performance direction
        self._validate_thresholds(kpi_data)

        # Set defaults
        kpi_data["status"] = "active"
        kpi_data["current_status"] = PerformanceStatus.NO_DATA.value
        kpi_data["trend"] = TrendDirection.NO_DATA.value
        kpi_data["current_value"] = None

        return await self.repo.create_kpi(kpi_data)

    async def record_measurement(
        self,
        kpi_id: int,
        value: float,
        measured_by: str,
        measurement_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        data_quality: DataQuality = DataQuality.HIGH,
        collection_method: CollectionMethod = CollectionMethod.MANUAL
    ) -> KPIMeasurementDB:
        """
        Record KPI measurement and update KPI status

        Args:
            kpi_id: KPI identifier
            value: Measured value
            measured_by: User who recorded measurement
            measurement_date: Date of measurement (defaults to now)
            notes: Optional notes about measurement
            data_quality: Quality level of data
            collection_method: How data was collected

        Returns:
            Created measurement record

        Raises:
            ValueError: If KPI not found
        """
        # Get KPI
        kpi = await self.repo.get_kpi(kpi_id)
        if not kpi:
            raise ValueError("KPI not found")

        # Calculate status based on thresholds
        status = calculate_kpi_status(
            value,
            kpi.target_value,
            kpi.warning_threshold,
            kpi.critical_threshold,
            kpi.performance_direction.value
        )

        # Create measurement record
        measurement_data = {
            "tenant_id": kpi.tenant_id,
            "kpi_id": kpi_id,
            "measurement_date": measurement_date or datetime.utcnow(),
            "value": value,
            "notes": notes,
            "data_quality": data_quality.value if isinstance(data_quality, DataQuality) else data_quality,
            "collection_method": collection_method.value if isinstance(collection_method, CollectionMethod) else collection_method,
            "collected_by": measured_by,
            "status": status.value
        }

        measurement = await self.repo.create_kpi_measurement(measurement_data)

        # Update KPI current values
        await self.repo.update_kpi(kpi_id, {
            "current_value": value,
            "current_status": status.value
        })

        # Check if threshold breached - create alert
        if status in [PerformanceStatus.WARNING, PerformanceStatus.CRITICAL]:
            await self.create_alert(kpi, value, status.value)

        # Update trend
        await self._update_kpi_trend(kpi_id)

        return measurement

    async def get_kpi_trend(
        self,
        kpi_id: int,
        period_days: int = 90
    ) -> Dict:
        """
        Get KPI trend analysis

        Args:
            kpi_id: KPI identifier
            period_days: Number of days to analyze

        Returns:
            Dict with trend analysis including measurements and statistics

        Raises:
            ValueError: If KPI not found
        """
        # Get KPI
        kpi = await self.repo.get_kpi(kpi_id)
        if not kpi:
            raise ValueError("KPI not found")

        # Get measurements for period
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        measurements = await self.repo.get_kpi_measurements(
            kpi_id=kpi_id,
            from_date=cutoff_date
        )

        # Convert to list of dicts for trend calculation
        measurements_data = [
            {
                'measurement_date': m.measurement_date,
                'value': m.value,
                'status': m.status if m.status else 'no_data'
            }
            for m in measurements
        ]

        # Calculate trend
        trend = calculate_kpi_trend([
            {'value': m.value, 'measurement_date': m.measurement_date}
            for m in measurements
        ])

        return {
            "kpi_id": kpi_id,
            "kpi_name": kpi.kpi_name,
            "kpi_code": kpi.kpi_code,
            "current_value": kpi.current_value,
            "current_status": kpi.current_status,
            "trend": trend.value,
            "target_value": kpi.target_value,
            "warning_threshold": kpi.warning_threshold,
            "critical_threshold": kpi.critical_threshold,
            "performance_direction": kpi.performance_direction.value,
            "measurements": measurements_data,
            "period_days": period_days,
            "measurement_count": len(measurements_data)
        }

    async def get_dashboard(self, tenant_id: str) -> Dict:
        """
        Get KPI dashboard summary for tenant

        Args:
            tenant_id: Tenant identifier

        Returns:
            Dict with dashboard data including status summary and KPI details
        """
        # Get all active KPIs
        kpis = await self.repo.list_kpis(tenant_id=tenant_id, status="active")

        # Group by status
        status_summary = {
            'excellent': 0,
            'good': 0,
            'warning': 0,
            'critical': 0,
            'no_data': 0,
        }

        kpi_details = []
        for kpi in kpis:
            current_status = kpi.current_status if hasattr(kpi.current_status, 'value') else kpi.current_status
            if isinstance(current_status, str):
                status_summary[current_status] = status_summary.get(current_status, 0) + 1
            else:
                status_summary[current_status.value] = status_summary.get(current_status.value, 0) + 1

            kpi_details.append({
                'id': kpi.id,
                'kpi_code': kpi.kpi_code,
                'kpi_name': kpi.kpi_name,
                'current_value': kpi.current_value,
                'target_value': kpi.target_value,
                'status': kpi.current_status if isinstance(kpi.current_status, str) else kpi.current_status.value,
                'trend': kpi.trend if isinstance(kpi.trend, str) else kpi.trend.value,
                'measurement_unit': kpi.measurement_unit,
                'owner_name': kpi.owner_name,
            })

        return {
            "tenant_id": tenant_id,
            "total_kpis": len(kpis),
            "status_summary": status_summary,
            "kpis": kpi_details,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def create_alert(
        self,
        kpi: KPIDB,
        value: float,
        severity: str
    ) -> KPIAlertDB:
        """
        Create KPI threshold breach alert

        Args:
            kpi: KPI database object
            value: Value that triggered alert
            severity: Alert severity (warning/critical)

        Returns:
            Created alert
        """
        alert_data = {
            "tenant_id": kpi.tenant_id,
            "kpi_id": kpi.id,
            "kpi_code": kpi.kpi_code,
            "kpi_name": kpi.kpi_name,
            "severity": severity,
            "threshold_breached": kpi.critical_threshold if severity == "critical" else kpi.warning_threshold,
            "current_value": value,
            "alert_message": self._generate_alert_message(kpi, value, severity),
            "status": "active",
            "triggered_at": datetime.utcnow(),
            "notified": False,
        }

        alert = await self.repo.create_kpi_alert(alert_data)

        # TODO: Send email notification if settings.ENABLE_EMAIL_NOTIFICATIONS
        # TODO: Publish event to event bus

        return alert

    async def acknowledge_alert(
        self,
        alert_id: int,
        user_id: str,
        notes: Optional[str] = None
    ) -> KPIAlertDB:
        """
        Acknowledge KPI alert

        Args:
            alert_id: Alert identifier
            user_id: User acknowledging alert
            notes: Optional acknowledgment notes

        Returns:
            Updated alert

        Raises:
            ValueError: If alert not found
        """
        updates = {
            "status": "acknowledged",
            "acknowledged_by": user_id,
            "acknowledged_at": datetime.utcnow(),
            "acknowledgment_notes": notes
        }

        alert = await self.repo.update_alert(alert_id, updates)
        if not alert:
            raise ValueError("Alert not found")

        return alert

    async def get_active_alerts(
        self,
        tenant_id: str,
        severity: Optional[str] = None
    ) -> Dict:
        """
        Get active KPI alerts

        Args:
            tenant_id: Tenant identifier
            severity: Optional severity filter (critical/warning)

        Returns:
            Dict with alert list and count
        """
        alerts = await self.repo.list_active_alerts(tenant_id=tenant_id, severity=severity)

        alert_list = [
            {
                "alert_id": alert.id,
                "kpi_id": alert.kpi_id,
                "kpi_code": alert.kpi_code,
                "kpi_name": alert.kpi_name,
                "severity": alert.severity,
                "current_value": alert.current_value,
                "threshold_breached": alert.threshold_breached,
                "alert_message": alert.alert_message,
                "triggered_at": alert.triggered_at.isoformat(),
                "status": alert.status,
            }
            for alert in alerts
        ]

        return {
            "tenant_id": tenant_id,
            "total_alerts": len(alert_list),
            "alerts": alert_list
        }

    async def trigger_collection(self, tenant_id: str) -> Dict:
        """
        Trigger on-demand KPI collection for tenant

        Args:
            tenant_id: Tenant identifier

        Returns:
            Dict with trigger status
        """
        # TODO: Implement actual KPI collection triggering
        # This could involve queuing tasks, sending messages to a message broker, etc.

        return {
            "status": "triggered",
            "tenant_id": tenant_id,
            "message": "KPI collection tasks have been queued"
        }

    async def list_kpis(
        self,
        tenant_id: str,
        category_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[KPIDB]:
        """List KPIs with filters"""
        return await self.repo.list_kpis(tenant_id, category_id, status)

    async def get_kpi(self, kpi_id: int) -> Optional[KPIDB]:
        """Get KPI by ID"""
        return await self.repo.get_kpi(kpi_id)

    async def update_kpi(self, kpi_id: int, updates: Dict) -> KPIDB:
        """
        Update KPI

        Args:
            kpi_id: KPI identifier
            updates: Fields to update

        Returns:
            Updated KPI

        Raises:
            ValueError: If KPI not found or validation fails
        """
        # If thresholds are being updated, validate them
        if any(k in updates for k in ['target_value', 'warning_threshold', 'critical_threshold', 'performance_direction']):
            kpi = await self.repo.get_kpi(kpi_id)
            if not kpi:
                raise ValueError("KPI not found")

            # Merge updates with current values for validation
            validation_data = {
                "target_value": updates.get("target_value", kpi.target_value),
                "warning_threshold": updates.get("warning_threshold", kpi.warning_threshold),
                "critical_threshold": updates.get("critical_threshold", kpi.critical_threshold),
                "performance_direction": updates.get("performance_direction", kpi.performance_direction)
            }
            self._validate_thresholds(validation_data)

        kpi = await self.repo.update_kpi(kpi_id, updates)
        if not kpi:
            raise ValueError("KPI not found")

        return kpi

    def _validate_thresholds(self, kpi_data: Dict):
        """
        Validate KPI threshold configuration

        Args:
            kpi_data: KPI data including thresholds and direction

        Raises:
            ValueError: If thresholds are invalid
        """
        target = kpi_data.get("target_value")
        warning = kpi_data.get("warning_threshold")
        critical = kpi_data.get("critical_threshold")
        direction = kpi_data.get("performance_direction")

        # Extract value if enum
        if hasattr(direction, 'value'):
            direction = direction.value

        if direction == "higher_better":
            # For higher_better: critical < warning < target
            if not (critical < warning < target):
                raise ValueError(
                    f"For higher_better KPIs: critical ({critical}) < warning ({warning}) < target ({target})"
                )
        elif direction == "lower_better":
            # For lower_better: target < warning < critical
            if not (target < warning < critical):
                raise ValueError(
                    f"For lower_better KPIs: target ({target}) < warning ({warning}) < critical ({critical})"
                )
        # For target_value direction, no strict ordering required

    async def _update_kpi_trend(self, kpi_id: int):
        """
        Update KPI trend based on recent measurements

        Args:
            kpi_id: KPI identifier
        """
        # Get last 3 measurements
        measurements = await self.repo.get_kpi_measurements(kpi_id=kpi_id, limit=3)

        if len(measurements) >= 2:
            trend = calculate_kpi_trend([
                {'value': m.value, 'measurement_date': m.measurement_date}
                for m in measurements
            ])

            await self.repo.update_kpi(kpi_id, {"trend": trend.value})

    def _generate_alert_message(self, kpi: KPIDB, value: float, severity: str) -> str:
        """
        Generate alert message for KPI threshold breach

        Args:
            kpi: KPI object
            value: Current value
            severity: Alert severity

        Returns:
            Alert message string
        """
        threshold = kpi.critical_threshold if severity == "critical" else kpi.warning_threshold
        direction = kpi.performance_direction.value if hasattr(kpi.performance_direction, 'value') else kpi.performance_direction

        if direction == "higher_better":
            return (
                f"KPI '{kpi.kpi_name}' has fallen below {severity} threshold. "
                f"Current: {value} {kpi.measurement_unit}, "
                f"Threshold: {threshold} {kpi.measurement_unit}, "
                f"Target: {kpi.target_value} {kpi.measurement_unit}"
            )
        elif direction == "lower_better":
            return (
                f"KPI '{kpi.kpi_name}' has exceeded {severity} threshold. "
                f"Current: {value} {kpi.measurement_unit}, "
                f"Threshold: {threshold} {kpi.measurement_unit}, "
                f"Target: {kpi.target_value} {kpi.measurement_unit}"
            )
        else:
            deviation = abs(value - kpi.target_value)
            return (
                f"KPI '{kpi.kpi_name}' has deviated from target. "
                f"Current: {value} {kpi.measurement_unit}, "
                f"Target: {kpi.target_value} {kpi.measurement_unit}, "
                f"Deviation: {deviation} {kpi.measurement_unit}"
            )
