#!/usr/bin/env python3
"""
Repository for saving MIO Manager actions to database
"""

from typing import Dict, Optional, List
from datetime import datetime
import uuid
import logging

from models.database import (
    MIOAction,
    ActionType,
    ActionStatus,
    TaskDelegation,
    IssueTracking,
    IssueSeverity,
    MetricsSnapshot
)
from database import get_db

logger = logging.getLogger(__name__)


class ActionsRepository:
    """Сохранение действий MIO Manager в БД"""

    @staticmethod
    def create_action(
        action_type: ActionType,
        target_service: str,
        action_details: Dict,
        triggered_by: str = "scheduler",
        triggered_by_report_id: Optional[str] = None
    ) -> str:
        """
        Создать новое действие

        Returns:
            action_id (UUID)
        """
        action_id = str(uuid.uuid4())

        with get_db() as db:
            action = MIOAction(
                action_id=action_id,
                action_type=action_type,
                target_service=target_service,
                action_details=action_details,
                status=ActionStatus.PENDING,
                triggered_by=triggered_by,
                triggered_by_report_id=triggered_by_report_id
            )
            db.add(action)

        logger.info(f" Created action: {action_id} ({action_type})")
        return action_id

    @staticmethod
    def update_action_status(
        action_id: str,
        status: ActionStatus,
        success: Optional[bool] = None,
        error_message: Optional[str] = None,
        result_data: Optional[Dict] = None
    ):
        """Обновить статус действия"""
        with get_db() as db:
            action = db.query(MIOAction).filter(MIOAction.action_id == action_id).first()
            if not action:
                logger.error(f" Action not found: {action_id}")
                return

            action.status = status

            if status == ActionStatus.IN_PROGRESS and not action.started_at:
                action.started_at = datetime.utcnow()

            if status in [ActionStatus.COMPLETED, ActionStatus.FAILED]:
                action.completed_at = datetime.utcnow()
                if action.started_at:
                    duration = (action.completed_at - action.started_at).total_seconds()
                    action.duration_seconds = duration

            if success is not None:
                action.success = success

            if error_message:
                action.error_message = error_message

            if result_data:
                action.result_data = result_data

        logger.info(f" Updated action {action_id}: {status}")

    @staticmethod
    def save_task_delegation(
        task_type: str,
        task_details: Dict,
        priority: str,
        mio_action_id: Optional[str] = None
    ) -> str:
        """Сохранить делегированную задачу"""
        task_id = str(uuid.uuid4())

        with get_db() as db:
            task = TaskDelegation(
                task_id=task_id,
                task_type=task_type,
                priority=priority,
                task_details=task_details,
                status="pending",
                mio_action_id=mio_action_id
            )
            db.add(task)

        logger.info(f" Saved task delegation: {task_id}")
        return task_id

    @staticmethod
    def update_task_delegation(
        task_id: str,
        status: str,
        orchestrator_response: Optional[Dict] = None,
        assigned_to: Optional[str] = None
    ):
        """Обновить статус делегированной задачи"""
        with get_db() as db:
            task = db.query(TaskDelegation).filter(TaskDelegation.task_id == task_id).first()
            if not task:
                logger.error(f" Task not found: {task_id}")
                return

            task.status = status

            if status == "completed":
                task.completed_at = datetime.utcnow()

            if orchestrator_response:
                task.orchestrator_response = orchestrator_response

            if assigned_to:
                task.assigned_to = assigned_to

        logger.info(f" Updated task {task_id}: {status}")

    @staticmethod
    def create_issue(
        issue_type: str,
        severity: IssueSeverity,
        description: str,
        affected_service: str,
        issue_details: Dict,
        discovered_by_report_id: Optional[str] = None
    ) -> str:
        """Создать новую проблему"""
        issue_id = str(uuid.uuid4())

        with get_db() as db:
            issue = IssueTracking(
                issue_id=issue_id,
                issue_type=issue_type,
                severity=severity,
                description=description,
                affected_service=affected_service,
                issue_details=issue_details,
                status="open",
                discovered_by_report_id=discovered_by_report_id
            )
            db.add(issue)

        logger.info(f" Created issue: {issue_id} ({severity})")
        return issue_id

    @staticmethod
    def resolve_issue(
        issue_id: str,
        resolved_by_action_id: str,
        resolution_notes: Optional[str] = None
    ):
        """Закрыть проблему"""
        with get_db() as db:
            issue = db.query(IssueTracking).filter(IssueTracking.issue_id == issue_id).first()
            if not issue:
                logger.error(f" Issue not found: {issue_id}")
                return

            issue.status = "resolved"
            issue.resolved_at = datetime.utcnow()
            issue.resolved_by_action_id = resolved_by_action_id
            if resolution_notes:
                issue.resolution_notes = resolution_notes

        logger.info(f" Resolved issue: {issue_id}")

    @staticmethod
    def save_metrics_snapshot(
        service_coverage: float,
        total_services: int,
        high_security_issues: int,
        avg_code_complexity: float,
        circular_dependencies: int,
        detailed_metrics: Dict
    ) -> str:
        """Сохранить snapshot метрик"""
        snapshot_id = str(uuid.uuid4())

        with get_db() as db:
            snapshot = MetricsSnapshot(
                snapshot_id=snapshot_id,
                service_coverage=service_coverage,
                total_services=total_services,
                high_security_issues=high_security_issues,
                avg_code_complexity=avg_code_complexity,
                circular_dependencies=circular_dependencies,
                detailed_metrics=detailed_metrics
            )
            db.add(snapshot)

        logger.info(f" Saved metrics snapshot: {snapshot_id}")
        return snapshot_id

    @staticmethod
    def get_pending_actions(limit: int = 50) -> List[MIOAction]:
        """Получить pending действия"""
        with get_db() as db:
            actions = db.query(MIOAction)\
                .filter(MIOAction.status == ActionStatus.PENDING)\
                .order_by(MIOAction.started_at.desc())\
                .limit(limit)\
                .all()
            return actions

    @staticmethod
    def get_open_issues(severity: Optional[IssueSeverity] = None) -> List[IssueTracking]:
        """Получить открытые проблемы"""
        with get_db() as db:
            query = db.query(IssueTracking).filter(IssueTracking.status == "open")

            if severity:
                query = query.filter(IssueTracking.severity == severity)

            issues = query.order_by(IssueTracking.created_at.desc()).all()
            return issues

    @staticmethod
    def get_action_stats() -> Dict:
        """Получить статистику действий"""
        with get_db() as db:
            total = db.query(MIOAction).count()
            completed = db.query(MIOAction).filter(MIOAction.status == ActionStatus.COMPLETED).count()
            failed = db.query(MIOAction).filter(MIOAction.status == ActionStatus.FAILED).count()
            pending = db.query(MIOAction).filter(MIOAction.status == ActionStatus.PENDING).count()

            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "pending": pending,
                "success_rate": (completed / total * 100) if total > 0 else 0
            }
