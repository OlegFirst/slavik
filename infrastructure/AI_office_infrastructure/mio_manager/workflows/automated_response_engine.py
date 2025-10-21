#!/usr/bin/env python3
"""
Automated Response Engine
Автоматические реакции MIO Manager на проблемы с использованием Workflow Intelligence
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Add parent path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.workflow_intelligence_client import WorkflowIntelligenceClient
from integrations.workflow_optimizer_client import WorkflowOptimizerClient
from integrations.orchestrator_client import OrchestratorClient
from integrations.gateway_manager import GatewayManager
from integrations.notification_client import NotificationClient
from repositories import ActionsRepository, ReportsRepository
from models.database import ActionType, ActionStatus, IssueSeverity

logger = logging.getLogger(__name__)


class AutomatedResponseEngine:
    """
    Движок автоматических реакций на проблемы

    Workflow:
    1. Обнаружение проблемы (через Automation Toolkit)
    2. Создание workflow (через Workflow Intelligence)
    3. AI рекомендации (через Workflow Intelligence)
    4. Автоматическая реакция (managed autonomy)
    5. Делегирование Orchestrator (если нужно)
    6. Мониторинг и эскалация
    7. Сохранение successful case
    """

    def __init__(
        self,
        workflow_intelligence_client: WorkflowIntelligenceClient,
        workflow_optimizer_client: WorkflowOptimizerClient,
        orchestrator_client: OrchestratorClient,
        gateway_manager: GatewayManager,
        notification_client: NotificationClient
    ):
        self.wf_intelligence = workflow_intelligence_client
        self.wf_optimizer = workflow_optimizer_client
        self.orchestrator = orchestrator_client
        self.gateway = gateway_manager
        self.notifications = notification_client

    # ========================================================================
    # SECURITY INCIDENT WORKFLOW
    # ========================================================================

    async def handle_security_incident(
        self,
        scan_result: Dict,
        report_id: str
    ) -> Dict:
        """
        Автоматическая реакция на security проблемы

        Workflow:
        1. Создать incident workflow
        2. Найти похожие cases
        3. Получить AI рекомендации
        4. Создать issue tracking
        5. Если CRITICAL → немедленная реакция
        6. Если HIGH → создать task + делегировать
        7. Мониторить progress
        8. После успеха → сохранить case
        """
        logger.info(f" Handling security incident: {scan_result['high_severity']} HIGH issues")

        # Определить severity
        high_count = scan_result['high_severity']
        if high_count >= 5:
            severity = "critical"
        elif high_count >= 3:
            severity = "high"
        elif high_count >= 1:
            severity = "medium"
        else:
            severity = "low"

        # 1. Создать workflow в Workflow Intelligence
        workflow = await self.wf_intelligence.create_incident_workflow(
            incident_type="security",
            incident_data=scan_result,
            severity=severity
        )

        if not workflow.get('workflow_id'):
            logger.error(" Failed to create workflow, using fallback")
            return await self._fallback_security_response(scan_result, report_id)

        workflow_id = workflow['workflow_id']

        # 2. Найти похожие successful cases
        similar_cases = await self.wf_intelligence.find_similar_cases(
            incident_type="security",
            incident_data=scan_result,
            limit=3
        )

        # 3. Получить AI рекомендации
        ai_recommendations = await self.wf_intelligence.get_ai_recommendations(
            workflow_id=workflow_id,
            current_context={
                "high_severity_count": high_count,
                "similar_cases_found": len(similar_cases),
                "scan_result": scan_result
            }
        )

        # 4. Создать MIO Action
        action_id = ActionsRepository.create_action(
            action_type=ActionType.ALERT_SENT,
            target_service="security",
            action_details={
                "workflow_id": workflow_id,
                "high_severity_count": high_count,
                "ai_recommendations": ai_recommendations[:3]
            },
            triggered_by="automation",
            triggered_by_report_id=report_id
        )

        # 5. Создать Issue Tracking
        for issue in scan_result.get('high_issues', [])[:5]:  # Top 5
            issue_id = ActionsRepository.create_issue(
                issue_type="security",
                severity=IssueSeverity.HIGH if severity in ['high', 'critical'] else IssueSeverity.MEDIUM,
                description=issue.get('issue_text', 'Security vulnerability detected'),
                affected_service=self._extract_service_from_filename(issue.get('filename', '')),
                issue_details=issue,
                discovered_by_report_id=report_id
            )

        # 6. Автоматическая реакция в зависимости от severity
        if severity == "critical":
            # КРИТИЧЕСКАЯ - немедленная реакция
            response = await self._immediate_security_response(
                workflow_id, scan_result, action_id
            )
        elif severity in ["high", "medium"]:
            # HIGH/MEDIUM - создать задачу и делегировать
            response = await self._delegated_security_response(
                workflow_id, scan_result, action_id, ai_recommendations
            )
        else:
            # LOW - только логирование
            response = {"action": "logged", "requires_manual_review": True}

        # 7. Transition workflow
        await self.wf_intelligence.transition_workflow(
            workflow_id=workflow_id,
            to_state="task_created",
            action_data=response
        )

        # 8. Предсказать время на исправление
        prediction = await self.wf_optimizer.predict_execution_time(
            process_type="security_fix",
            process_data={
                "severity": severity,
                "issue_count": high_count,
                "similar_cases": len(similar_cases)
            }
        )

        # 9. Отправить notification
        await self.notifications.send_security_alert(
            severity=severity,
            issue_count=high_count,
            high_issues=scan_result.get('high_issues', []),
            workflow_id=workflow_id
        )

        ActionsRepository.update_action_status(
            action_id=action_id,
            status=ActionStatus.COMPLETED,
            success=True,
            result_data={
                "workflow_id": workflow_id,
                "response": response,
                "predicted_resolution_minutes": prediction.get('predicted_minutes'),
                "ai_recommendations_count": len(ai_recommendations)
            }
        )

        logger.info(f" Security incident workflow created: {workflow_id}")

        return {
            "workflow_id": workflow_id,
            "action_id": action_id,
            "severity": severity,
            "response": response,
            "predicted_resolution_minutes": prediction.get('predicted_minutes'),
            "ai_recommendations": ai_recommendations[:3]
        }

    async def _immediate_security_response(
        self,
        workflow_id: str,
        scan_result: Dict,
        action_id: str
    ) -> Dict:
        """
        Немедленная реакция на CRITICAL security issues

        Actions:
        - Enable Circuit Breaker для affected services
        - Alert to Orchestrator HIGH priority
        - Create emergency task
        """
        logger.warning(" CRITICAL security issue - immediate response")

        # Enable circuit breaker
        affected_services = self._extract_affected_services(scan_result)
        for service in affected_services[:3]:  # Top 3 most affected
            try:
                await self.gateway.enable_circuit_breaker(service)
                logger.info(f"️  Enabled circuit breaker for {service}")
            except Exception as e:
                logger.error(f" Failed to enable circuit breaker for {service}: {e}")

        # Create emergency task
        task = await self.orchestrator.delegate_task({
            "task_type": "security_emergency",
            "priority": "critical",
            "workflow_id": workflow_id,
            "details": {
                "high_severity_count": scan_result['high_severity'],
                "affected_services": affected_services,
                "immediate_action_required": True
            }
        })

        # Save task delegation
        ActionsRepository.save_task_delegation(
            task_type="security_emergency",
            task_details=task,
            priority="critical",
            mio_action_id=action_id
        )

        # Send CRITICAL notification
        await self.notifications.send_security_alert(
            severity="critical",
            issue_count=scan_result['high_severity'],
            high_issues=scan_result.get('high_issues', []),
            workflow_id=workflow_id
        )

        return {
            "action": "immediate",
            "circuit_breakers_enabled": len(affected_services),
            "task_delegated": task.get('task_id'),
            "affected_services": affected_services
        }

    async def _delegated_security_response(
        self,
        workflow_id: str,
        scan_result: Dict,
        action_id: str,
        ai_recommendations: List[Dict]
    ) -> Dict:
        """
        Делегированная реакция на HIGH/MEDIUM security issues

        Actions:
        - Create task с AI рекомендациями
        - Delegate to Orchestrator
        - Monitor progress
        """
        logger.info(" Creating delegated security fix task")

        # Create task with AI recommendations
        task = await self.orchestrator.delegate_task({
            "task_type": "security_fix",
            "priority": "high" if scan_result['high_severity'] >= 3 else "medium",
            "workflow_id": workflow_id,
            "details": {
                "high_severity_count": scan_result['high_severity'],
                "medium_severity_count": scan_result.get('medium_severity', 0),
                "ai_recommendations": ai_recommendations[:5],
                "high_issues": scan_result.get('high_issues', [])[:10]
            }
        })

        # Save task delegation
        task_id = ActionsRepository.save_task_delegation(
            task_type="security_fix",
            task_details=task,
            priority="high" if scan_result['high_severity'] >= 3 else "medium",
            mio_action_id=action_id
        )

        # Send task delegation notification
        await self.notifications.send_task_delegation_notification(
            task_id=task.get('task_id'),
            task_type="security_fix",
            priority="high" if scan_result['high_severity'] >= 3 else "medium",
            ai_recommendations=ai_recommendations
        )

        return {
            "action": "delegated",
            "task_id": task.get('task_id'),
            "task_delegation_id": task_id,
            "ai_recommendations_provided": len(ai_recommendations)
        }

    async def _fallback_security_response(
        self,
        scan_result: Dict,
        report_id: str
    ) -> Dict:
        """Fallback если Workflow Intelligence недоступен"""
        logger.warning("️  Using fallback security response (Workflow Intelligence unavailable)")

        # Simple action without workflow
        action_id = ActionsRepository.create_action(
            action_type=ActionType.ALERT_SENT,
            target_service="security",
            action_details=scan_result,
            triggered_by="automation_fallback",
            triggered_by_report_id=report_id
        )

        if scan_result['high_severity'] >= 3:
            task = await self.orchestrator.delegate_task({
                "task_type": "security_fix",
                "priority": "high",
                "details": scan_result
            })

            ActionsRepository.update_action_status(
                action_id=action_id,
                status=ActionStatus.COMPLETED,
                success=True,
                result_data={"task_delegated": task.get('task_id')}
            )

        return {
            "action_id": action_id,
            "fallback_mode": True,
            "action": "logged_and_delegated" if scan_result['high_severity'] >= 3 else "logged"
        }

    # ========================================================================
    # SERVICE DOWN WORKFLOW
    # ========================================================================

    async def handle_service_down(
        self,
        service_name: str,
        health_check_result: Dict
    ) -> Dict:
        """
        Автоматическая реакция на падение сервиса

        Workflow:
        1. Создать incident workflow
        2. Root cause analysis (dependency graph)
        3. Automatic restart attempt
        4. Если не помогло → делегировать
        5. Enable circuit breaker
        """
        logger.warning(f" Service DOWN: {service_name}")

        # Create workflow
        workflow = await self.wf_intelligence.create_incident_workflow(
            incident_type="service_down",
            incident_data={
                "service_name": service_name,
                "health_check": health_check_result
            },
            severity="critical"
        )

        workflow_id = workflow.get('workflow_id')

        # Create action
        action_id = ActionsRepository.create_action(
            action_type=ActionType.SERVICE_RESTART,
            target_service=service_name,
            action_details=health_check_result,
            triggered_by="health_check"
        )

        # Send service down alert
        await self.notifications.send_service_down_alert(
            service_name=service_name,
            health_check_result=health_check_result,
            workflow_id=workflow_id
        )

        # TODO: Implement service restart logic
        # TODO: Root cause analysis via dependency graph
        # TODO: Circuit breaker

        return {
            "workflow_id": workflow_id,
            "action_id": action_id,
            "status": "in_progress"
        }

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _extract_service_from_filename(self, filename: str) -> str:
        """Extract service name from file path"""
        if 'platform-services/' in filename:
            parts = filename.split('platform-services/')[1].split('/')
            if parts and '-service' in parts[0]:
                return parts[0].replace('-service', '')
        return "unknown"

    def _extract_affected_services(self, scan_result: Dict) -> List[str]:
        """Extract list of affected services from scan result"""
        services = set()
        for issue in scan_result.get('high_issues', []):
            service = self._extract_service_from_filename(issue.get('filename', ''))
            if service != "unknown":
                services.add(service)
        return list(services)
