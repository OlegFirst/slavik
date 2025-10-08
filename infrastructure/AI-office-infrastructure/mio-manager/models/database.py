#!/usr/bin/env python3
"""
MIO Manager Database Models
Таблицы для хранения отчётов и действий
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class AnalysisType(str, enum.Enum):
    """Типы анализа"""
    SERVICE_DISCOVERY = "service_discovery"
    SECURITY_SCAN = "security_scan"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    COMPLEXITY_ANALYSIS = "complexity_analysis"
    TEST_GENERATION = "test_generation"


class ActionType(str, enum.Enum):
    """Типы действий"""
    SERVICE_RESTART = "service_restart"
    CONFIG_UPDATE = "config_update"
    GATEWAY_REGISTRATION = "gateway_registration"
    TASK_DELEGATION = "task_delegation"
    CIRCUIT_BREAKER = "circuit_breaker"
    ALERT_SENT = "alert_sent"


class ActionStatus(str, enum.Enum):
    """Статусы действий"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueSeverity(str, enum.Enum):
    """Уровни серьёзности проблем"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# TABLES
# ============================================================================

class AnalysisReport(Base):
    """
    Отчёты анализа от Automation Toolkit
    Каждый запуск анализа сохраняется здесь
    """
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, index=True)  # UUID
    analysis_type = Column(SQLEnum(AnalysisType), nullable=False, index=True)

    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    duration_seconds = Column(Float)  # Сколько времени занял анализ

    # Результаты (JSON)
    results = Column(JSON)  # Полные результаты анализа
    summary = Column(JSON)  # Краткая сводка

    # Статистика
    items_analyzed = Column(Integer)  # Сколько элементов проанализировано
    issues_found = Column(Integer, default=0)  # Сколько проблем найдено
    high_severity_issues = Column(Integer, default=0)

    # Дополнительная информация
    triggered_by = Column(String(50))  # 'scheduler', 'manual', 'api'
    notes = Column(Text)


class ServiceDiscovery(Base):
    """
    История service discovery
    Каждое сканирование сервисов сохраняется
    """
    __tablename__ = "service_discoveries"

    id = Column(Integer, primary_key=True, index=True)
    discovery_id = Column(String(100), unique=True, index=True)

    # Результаты
    total_services = Column(Integer)
    monitored_services = Column(Integer)
    unmonitored_services = Column(Integer)
    coverage_percentage = Column(Float)

    # Обнаруженные сервисы (JSON)
    services_list = Column(JSON)

    # Метаданные
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    scan_duration_seconds = Column(Float)


class SecurityScanResult(Base):
    """
    Результаты security сканирования (Bandit)
    """
    __tablename__ = "security_scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(100), unique=True, index=True)

    # Статистика
    high_severity_count = Column(Integer, default=0)
    medium_severity_count = Column(Integer, default=0)
    low_severity_count = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)

    # Детали (JSON)
    high_issues = Column(JSON)  # Список HIGH severity issues
    all_issues = Column(JSON)   # Полный список

    # Метаданные
    scanned_at = Column(DateTime, default=datetime.utcnow, index=True)
    scan_duration_seconds = Column(Float)
    scan_status = Column(String(20))  # 'clean', 'issues_found'


class CodeComplexityResult(Base):
    """
    Результаты анализа сложности кода (Radon)
    """
    __tablename__ = "code_complexity_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(100), unique=True, index=True)

    # Сервис
    service_name = Column(String(100), index=True)

    # Метрики
    avg_complexity = Column(Float)
    max_complexity = Column(Integer)
    high_complexity_count = Column(Integer, default=0)

    # Функции с высокой сложностью (JSON)
    high_complexity_functions = Column(JSON)

    # Метаданные
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)


class DependencyAnalysisResult(Base):
    """
    Результаты анализа зависимостей
    """
    __tablename__ = "dependency_analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(100), unique=True, index=True)

    # Статистика
    total_modules = Column(Integer)
    total_dependencies = Column(Integer)
    circular_dependencies_count = Column(Integer, default=0)

    # Циклические зависимости (JSON)
    circular_dependencies = Column(JSON)

    # Граф зависимостей (JSON)
    dependency_graph = Column(JSON)

    # Метаданные
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)


class MIOAction(Base):
    """
    Действия, выполненные MIO Manager
    Каждое действие логируется
    """
    __tablename__ = "mio_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(100), unique=True, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)

    # Детали действия
    target_service = Column(String(100), index=True)  # На какой сервис
    action_details = Column(JSON)  # Детали действия

    # Статус
    status = Column(SQLEnum(ActionStatus), default=ActionStatus.PENDING, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)

    # Результат
    success = Column(Boolean)
    error_message = Column(Text)
    result_data = Column(JSON)

    # Связь с отчётом
    triggered_by_report_id = Column(String(100), index=True)  # FK к AnalysisReport
    triggered_by = Column(String(50))  # 'scheduler', 'manual', 'alert'


class TaskDelegation(Base):
    """
    Задачи, делегированные Orchestrator
    """
    __tablename__ = "task_delegations"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True)
    task_type = Column(String(50), index=True)

    # Детали задачи
    priority = Column(String(20))  # 'low', 'medium', 'high', 'critical'
    task_details = Column(JSON)

    # Статус
    status = Column(String(20), default="pending", index=True)
    delegated_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)

    # Результат от Orchestrator
    orchestrator_response = Column(JSON)
    assigned_to = Column(String(100))  # Какой AI Agent назначен

    # Связь с MIO Action
    mio_action_id = Column(String(100), index=True)  # FK к MIOAction


class IssueTracking(Base):
    """
    Отслеживание проблем
    Проблемы из анализа -> действия -> статус
    """
    __tablename__ = "issue_tracking"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(String(100), unique=True, index=True)

    # Проблема
    issue_type = Column(String(50), index=True)  # 'security', 'complexity', 'dependency'
    severity = Column(SQLEnum(IssueSeverity), index=True)
    description = Column(Text)
    affected_service = Column(String(100), index=True)

    # Детали (JSON)
    issue_details = Column(JSON)

    # Статус
    status = Column(String(20), default="open", index=True)  # 'open', 'in_progress', 'resolved', 'ignored'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)

    # Связи
    discovered_by_report_id = Column(String(100), index=True)  # FK к AnalysisReport
    resolved_by_action_id = Column(String(100), index=True)    # FK к MIOAction

    # Резолюция
    resolution_notes = Column(Text)


class MetricsSnapshot(Base):
    """
    Snapshots метрик для трендов
    Сохраняет метрики каждый час для отслеживания трендов
    """
    __tablename__ = "metrics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String(100), unique=True, index=True)

    # Метрики
    service_coverage = Column(Float)
    total_services = Column(Integer)
    high_security_issues = Column(Integer)
    avg_code_complexity = Column(Float)
    circular_dependencies = Column(Integer)

    # Детальные метрики (JSON)
    detailed_metrics = Column(JSON)

    # Метаданные
    captured_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================================================
# INDEXES для быстрых запросов
# ============================================================================

# Composite indexes для частых запросов
# CREATE INDEX idx_analysis_type_created ON analysis_reports(analysis_type, created_at DESC);
# CREATE INDEX idx_action_status_created ON mio_actions(status, created_at DESC);
# CREATE INDEX idx_issue_severity_status ON issue_tracking(severity, status);
# CREATE INDEX idx_task_status_delegated ON task_delegations(status, delegated_at DESC);
