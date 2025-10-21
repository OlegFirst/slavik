#!/usr/bin/env python3
"""
Repository for saving analysis reports to database
"""

from typing import Dict, Optional, List
from datetime import datetime
import uuid
import logging

from models.database import (
    AnalysisReport,
    AnalysisType,
    ServiceDiscovery,
    SecurityScanResult,
    CodeComplexityResult,
    DependencyAnalysisResult
)
from database import get_db

logger = logging.getLogger(__name__)


class ReportsRepository:
    """Сохранение отчётов анализа в БД"""

    @staticmethod
    def save_analysis_report(
        analysis_type: AnalysisType,
        results: Dict,
        summary: Optional[Dict] = None,
        duration_seconds: Optional[float] = None,
        triggered_by: str = "scheduler"
    ) -> str:
        """
        Сохранить отчёт анализа

        Returns:
            report_id (UUID)
        """
        report_id = str(uuid.uuid4())

        with get_db() as db:
            report = AnalysisReport(
                report_id=report_id,
                analysis_type=analysis_type,
                results=results,
                summary=summary or {},
                duration_seconds=duration_seconds,
                items_analyzed=results.get('total', 0),
                issues_found=results.get('issues_found', 0),
                high_severity_issues=results.get('high_severity', 0),
                triggered_by=triggered_by
            )
            db.add(report)

        logger.info(f" Saved {analysis_type} report: {report_id}")
        return report_id

    @staticmethod
    def save_service_discovery(
        total_services: int,
        monitored_services: int,
        unmonitored_services: int,
        coverage_percentage: float,
        services_list: List[Dict],
        scan_duration_seconds: Optional[float] = None
    ) -> str:
        """Сохранить результат service discovery"""
        discovery_id = str(uuid.uuid4())

        with get_db() as db:
            discovery = ServiceDiscovery(
                discovery_id=discovery_id,
                total_services=total_services,
                monitored_services=monitored_services,
                unmonitored_services=unmonitored_services,
                coverage_percentage=coverage_percentage,
                services_list=services_list,
                scan_duration_seconds=scan_duration_seconds
            )
            db.add(discovery)

        logger.info(f" Saved service discovery: {discovery_id}")
        return discovery_id

    @staticmethod
    def save_security_scan(
        high_count: int,
        medium_count: int,
        low_count: int,
        high_issues: List[Dict],
        all_issues: List[Dict],
        scan_duration_seconds: Optional[float] = None
    ) -> str:
        """Сохранить результат security scan"""
        scan_id = str(uuid.uuid4())

        status = "clean" if high_count == 0 and medium_count == 0 else "issues_found"

        with get_db() as db:
            scan = SecurityScanResult(
                scan_id=scan_id,
                high_severity_count=high_count,
                medium_severity_count=medium_count,
                low_severity_count=low_count,
                total_issues=high_count + medium_count + low_count,
                high_issues=high_issues,
                all_issues=all_issues,
                scan_duration_seconds=scan_duration_seconds,
                scan_status=status
            )
            db.add(scan)

        logger.info(f" Saved security scan: {scan_id} (status: {status})")
        return scan_id

    @staticmethod
    def save_complexity_analysis(
        service_name: str,
        avg_complexity: float,
        max_complexity: int,
        high_complexity_count: int,
        high_complexity_functions: List[Dict]
    ) -> str:
        """Сохранить результат анализа сложности"""
        analysis_id = str(uuid.uuid4())

        with get_db() as db:
            complexity = CodeComplexityResult(
                analysis_id=analysis_id,
                service_name=service_name,
                avg_complexity=avg_complexity,
                max_complexity=max_complexity,
                high_complexity_count=high_complexity_count,
                high_complexity_functions=high_complexity_functions
            )
            db.add(complexity)

        logger.info(f" Saved complexity analysis: {analysis_id} for {service_name}")
        return analysis_id

    @staticmethod
    def save_dependency_analysis(
        total_modules: int,
        total_dependencies: int,
        circular_dependencies_count: int,
        circular_dependencies: List,
        dependency_graph: Dict
    ) -> str:
        """Сохранить результат анализа зависимостей"""
        analysis_id = str(uuid.uuid4())

        with get_db() as db:
            dep_analysis = DependencyAnalysisResult(
                analysis_id=analysis_id,
                total_modules=total_modules,
                total_dependencies=total_dependencies,
                circular_dependencies_count=circular_dependencies_count,
                circular_dependencies=circular_dependencies,
                dependency_graph=dependency_graph
            )
            db.add(dep_analysis)

        logger.info(f" Saved dependency analysis: {analysis_id}")
        return analysis_id

    @staticmethod
    def get_latest_reports(analysis_type: Optional[AnalysisType] = None, limit: int = 10) -> List[AnalysisReport]:
        """Получить последние отчёты"""
        with get_db() as db:
            query = db.query(AnalysisReport)
            if analysis_type:
                query = query.filter(AnalysisReport.analysis_type == analysis_type)

            reports = query.order_by(AnalysisReport.created_at.desc()).limit(limit).all()
            return reports

    @staticmethod
    def get_security_trend(days: int = 7) -> List[SecurityScanResult]:
        """Получить тренд security issues"""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with get_db() as db:
            scans = db.query(SecurityScanResult)\
                .filter(SecurityScanResult.scanned_at >= cutoff_date)\
                .order_by(SecurityScanResult.scanned_at.desc())\
                .all()
            return scans
