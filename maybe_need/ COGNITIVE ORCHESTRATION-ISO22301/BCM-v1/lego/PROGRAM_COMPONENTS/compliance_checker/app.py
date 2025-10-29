"""
BCM Platform - Compliance Checker Service

Интеллектуальная система проверки соответствия требованиям:
- Автоматическая проверка соответствия ISO 22301
- Анализ пробелов в документации
- Генерация отчетов по соответствию
- Трекинг изменений требований
- Рекомендации по улучшению соответствия
- Интеграция с системами аудита
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Compliance Checker - BCM Platform",
    description="Интеллектуальная система проверки соответствия требованиям BCM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class ComplianceStandard(str, Enum):
    ISO_22301 = "iso_22301"
    ISO_27001 = "iso_27001" 
    SOX = "sarbanes_oxley"
    GDPR = "gdpr"
    COBIT = "cobit"
    NIST = "nist_framework"
    CUSTOM = "custom"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial_compliance"
    NON_COMPLIANT = "non_compliant"
    NOT_ASSESSED = "not_assessed"
    PENDING_REVIEW = "pending_review"

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RequirementCategory(str, Enum):
    GOVERNANCE = "governance"
    RISK_MANAGEMENT = "risk_management"
    BUSINESS_CONTINUITY = "business_continuity"
    INCIDENT_MANAGEMENT = "incident_management"
    DOCUMENTATION = "documentation"
    TRAINING = "training"
    MONITORING = "monitoring"
    IMPROVEMENT = "improvement"

class ComplianceRequirement(BaseModel):
    id: str
    standard: ComplianceStandard
    category: RequirementCategory
    title: str
    description: str
    mandatory: bool = True
    evidence_required: List[str] = []
    weight: float = Field(default=1.0, ge=0.1, le=5.0)

class ComplianceEvidence(BaseModel):
    requirement_id: str
    evidence_type: str
    description: str
    document_references: List[str] = []
    last_updated: datetime
    verified: bool = False
    verifier: Optional[str] = None

class ComplianceAssessment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    standard: ComplianceStandard
    assessment_date: datetime = Field(default_factory=datetime.now)
    assessor: str
    scope: str
    requirements_assessed: List[str] = []
    overall_status: ComplianceStatus
    score: float = Field(ge=0.0, le=100.0)
    
class ComplianceGap(BaseModel):
    requirement_id: str
    current_status: ComplianceStatus
    target_status: ComplianceStatus
    severity: Severity
    gap_description: str
    recommended_actions: List[str] = []
    estimated_effort_hours: Optional[int] = None
    target_completion_date: Optional[datetime] = None

class IntelligentComplianceChecker:
    """Интеллектуальная система проверки соответствия"""
    
    # ISO 22301 требования
    ISO_22301_REQUIREMENTS = {
        "4.1": ComplianceRequirement(
            id="4.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.GOVERNANCE,
            title="Понимание организации и ее контекста",
            description="Организация должна определить внешние и внутренние вопросы, которые относятся к ее назначению",
            evidence_required=["context_analysis", "stakeholder_analysis", "external_factors_assessment"],
            weight=1.5
        ),
        "4.2": ComplianceRequirement(
            id="4.2", 
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.GOVERNANCE,
            title="Понимание потребностей заинтересованных сторон",
            description="Организация должна определить заинтересованные стороны и их требования",
            evidence_required=["stakeholder_register", "requirements_matrix"],
            weight=1.3
        ),
        "5.1": ComplianceRequirement(
            id="5.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.GOVERNANCE,
            title="Лидерство и обязательства",
            description="Высшее руководство должно продемонстрировать лидерство в отношении BCMS",
            evidence_required=["leadership_commitment", "resource_allocation", "policy_approval"],
            weight=2.0
        ),
        "5.2": ComplianceRequirement(
            id="5.2",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.GOVERNANCE,
            title="Политика",
            description="Высшее руководство должно установить политику непрерывности бизнеса",
            evidence_required=["bc_policy", "policy_communication", "policy_review"],
            weight=1.8
        ),
        "6.1": ComplianceRequirement(
            id="6.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.RISK_MANAGEMENT,
            title="Действия по рискам и возможностям",
            description="Организация должна определить риски и возможности, требующие внимания",
            evidence_required=["risk_assessment", "risk_register", "risk_treatment_plan"],
            weight=2.5
        ),
        "8.2": ComplianceRequirement(
            id="8.2",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.BUSINESS_CONTINUITY,
            title="Анализ воздействия на бизнес и оценка риска",
            description="Организация должна установить процесс BIA и оценки рисков",
            evidence_required=["bia_methodology", "bia_results", "risk_assessment_results"],
            weight=3.0
        ),
        "8.3": ComplianceRequirement(
            id="8.3",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.BUSINESS_CONTINUITY,
            title="Стратегия непрерывности бизнеса",
            description="Организация должна установить стратегии непрерывности бизнеса",
            evidence_required=["bc_strategy", "recovery_strategies", "strategy_approval"],
            weight=2.8
        ),
        "8.4": ComplianceRequirement(
            id="8.4",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.BUSINESS_CONTINUITY,
            title="Планы и процедуры непрерывности бизнеса",
            description="Организация должна установить планы непрерывности бизнеса",
            evidence_required=["bc_plans", "procedures", "emergency_procedures"],
            weight=3.0
        ),
        "8.5": ComplianceRequirement(
            id="8.5",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.BUSINESS_CONTINUITY,
            title="Упражнения и тестирование",
            description="Организация должна проводить упражнения и тестирование",
            evidence_required=["exercise_program", "test_results", "improvement_actions"],
            weight=2.5
        ),
        "9.1": ComplianceRequirement(
            id="9.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.MONITORING,
            title="Мониторинг, измерение, анализ и оценка",
            description="Организация должна определить что мониторить и измерять",
            evidence_required=["monitoring_plan", "kpis", "measurement_results"],
            weight=2.0
        ),
        "9.2": ComplianceRequirement(
            id="9.2",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.MONITORING,
            title="Внутренний аудит",
            description="Организация должна проводить внутренние аудиты",
            evidence_required=["audit_program", "audit_reports", "corrective_actions"],
            weight=2.3
        ),
        "10.1": ComplianceRequirement(
            id="10.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.IMPROVEMENT,
            title="Несоответствие и корректирующие действия",
            description="При несоответствии организация должна предпринимать корректирующие действия",
            evidence_required=["nonconformity_register", "corrective_actions", "effectiveness_review"],
            weight=2.0
        ),
        "10.2": ComplianceRequirement(
            id="10.2",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.IMPROVEMENT,
            title="Постоянное улучшение",
            description="Организация должна постоянно улучшать BCMS",
            evidence_required=["improvement_plan", "improvement_evidence", "management_review"],
            weight=1.8
        )
    }
    
    @staticmethod
    def assess_requirement_compliance(requirement: ComplianceRequirement, available_evidence: List[ComplianceEvidence]) -> Dict[str, Any]:
        """Оценка соответствия конкретному требованию"""
        
        # Находим релевантные доказательства
        relevant_evidence = [e for e in available_evidence if e.requirement_id == requirement.id]
        
        # Определяем какие типы доказательств предоставлены
        provided_evidence_types = set(e.evidence_type for e in relevant_evidence)
        required_evidence_types = set(requirement.evidence_required)
        
        # Рассчитываем покрытие доказательствами
        if not required_evidence_types:
            evidence_coverage = 1.0
        else:
            evidence_coverage = len(provided_evidence_types.intersection(required_evidence_types)) / len(required_evidence_types)
        
        # Проверяем верификацию доказательств
        verified_evidence = [e for e in relevant_evidence if e.verified]
        verification_rate = len(verified_evidence) / max(1, len(relevant_evidence))
        
        # Определяем статус соответствия
        if evidence_coverage >= 0.9 and verification_rate >= 0.8:
            status = ComplianceStatus.COMPLIANT
        elif evidence_coverage >= 0.6:
            status = ComplianceStatus.PARTIAL
        elif evidence_coverage > 0:
            status = ComplianceStatus.PARTIAL
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        # Рассчитываем оценку (0-100)
        score = (evidence_coverage * 0.7 + verification_rate * 0.3) * 100
        
        return {
            "requirement_id": requirement.id,
            "status": status,
            "score": round(score, 2),
            "evidence_coverage": round(evidence_coverage * 100, 2),
            "verification_rate": round(verification_rate * 100, 2),
            "provided_evidence": len(relevant_evidence),
            "required_evidence": len(requirement.evidence_required),
            "missing_evidence": list(required_evidence_types - provided_evidence_types),
            "assessment_notes": IntelligentComplianceChecker._generate_assessment_notes(requirement, evidence_coverage, verification_rate)
        }
    
    @staticmethod
    def _generate_assessment_notes(requirement: ComplianceRequirement, evidence_coverage: float, verification_rate: float) -> List[str]:
        """Генерация примечаний к оценке"""
        notes = []
        
        if evidence_coverage < 0.5:
            notes.append("Критический недостаток доказательств соответствия")
        elif evidence_coverage < 0.8:
            notes.append("Частичное предоставление требуемых доказательств")
        
        if verification_rate < 0.5:
            notes.append("Большинство доказательств не верифицировано")
        elif verification_rate < 0.8:
            notes.append("Требуется дополнительная верификация доказательств")
        
        if requirement.mandatory and evidence_coverage < 0.9:
            notes.append("Обязательное требование - необходимо полное соответствие")
        
        if not notes:
            notes.append("Требование выполнено в полном объеме")
        
        return notes
    
    @staticmethod
    def identify_compliance_gaps(assessment_results: List[Dict], target_compliance_level: float = 85.0) -> List[ComplianceGap]:
        """Идентификация пробелов в соответствии"""
        gaps = []
        
        for result in assessment_results:
            if result["score"] < target_compliance_level:
                severity = IntelligentComplianceChecker._determine_gap_severity(
                    result["score"], target_compliance_level, result.get("requirement", {}).get("weight", 1.0)
                )
                
                gap = ComplianceGap(
                    requirement_id=result["requirement_id"],
                    current_status=result["status"],
                    target_status=ComplianceStatus.COMPLIANT,
                    severity=severity,
                    gap_description=f"Текущая оценка {result['score']}% не достигает целевого уровня {target_compliance_level}%",
                    recommended_actions=IntelligentComplianceChecker._generate_gap_actions(result),
                    estimated_effort_hours=IntelligentComplianceChecker._estimate_remediation_effort(result, severity)
                )
                
                gaps.append(gap)
        
        return gaps
    
    @staticmethod
    def _determine_gap_severity(current_score: float, target_score: float, weight: float) -> Severity:
        """Определение серьезности пробела"""
        gap_size = target_score - current_score
        weighted_gap = gap_size * weight
        
        if weighted_gap > 60 or current_score < 30:
            return Severity.CRITICAL
        elif weighted_gap > 40 or current_score < 50:
            return Severity.HIGH
        elif weighted_gap > 20 or current_score < 70:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    @staticmethod
    def _generate_gap_actions(assessment_result: Dict) -> List[str]:
        """Генерация рекомендуемых действий для устранения пробелов"""
        actions = []
        
        missing_evidence = assessment_result.get("missing_evidence", [])
        if missing_evidence:
            actions.append(f"Предоставить недостающие доказательства: {', '.join(missing_evidence)}")
        
        if assessment_result.get("verification_rate", 0) < 80:
            actions.append("Провести верификацию предоставленных доказательств")
        
        if assessment_result.get("evidence_coverage", 0) < 60:
            actions.append("Разработать дополнительную документацию")
        
        if not actions:
            actions.append("Провести детальную оценку для определения конкретных улучшений")
        
        return actions
    
    @staticmethod
    def _estimate_remediation_effort(assessment_result: Dict, severity: Severity) -> int:
        """Оценка усилий на устранение пробела"""
        base_hours = {
            Severity.CRITICAL: 40,
            Severity.HIGH: 24,
            Severity.MEDIUM: 16,
            Severity.LOW: 8
        }
        
        effort = base_hours[severity]
        missing_evidence_count = len(assessment_result.get("missing_evidence", []))
        effort += missing_evidence_count * 4
        
        return effort

# Инициализация системы проверки соответствия
compliance_checker = IntelligentComplianceChecker()

# Хранилища данных (в реальном приложении - база данных)
evidence_store: Dict[str, List[ComplianceEvidence]] = {}
assessment_store: Dict[str, ComplianceAssessment] = {}

@app.get("/health")
def health():
    return {
        "status": "operational", 
        "service": "compliance_checker",
        "version": "1.0.0",
        "capabilities": [
            "iso_22301_assessment",
            "gap_analysis", 
            "evidence_management",
            "compliance_reporting",
            "automated_recommendations"
        ]
    }

@app.get("/requirements/{standard}")
async def get_requirements(standard: ComplianceStandard):
    """Получение списка требований для стандарта"""
    if standard == ComplianceStandard.ISO_22301:
        requirements = list(compliance_checker.ISO_22301_REQUIREMENTS.values())
        return {
            "standard": standard,
            "total_requirements": len(requirements),
            "requirements": [req.dict() for req in requirements]
        }
    else:
        raise HTTPException(status_code=404, detail=f"Requirements for {standard} not implemented yet")

@app.post("/evidence")
async def submit_evidence(evidence: ComplianceEvidence):
    """Представление доказательств соответствия"""
    req_id = evidence.requirement_id
    
    if req_id not in evidence_store:
        evidence_store[req_id] = []
    
    evidence_store[req_id].append(evidence)
    
    logger.info(f"Добавлено доказательство для требования {req_id}")
    
    return {
        "status": "success",
        "message": "Evidence submitted successfully",
        "requirement_id": req_id,
        "evidence_count": len(evidence_store[req_id])
    }

@app.get("/evidence/{requirement_id}")
async def get_evidence(requirement_id: str):
    """Получение доказательств для конкретного требования"""
    evidence = evidence_store.get(requirement_id, [])
    
    return {
        "requirement_id": requirement_id,
        "evidence_count": len(evidence),
        "evidence": [e.dict() for e in evidence]
    }

@app.post("/assess", response_model=ComplianceAssessment)
async def conduct_assessment(
    standard: ComplianceStandard,
    assessor: str,
    scope: str = "Full organization assessment",
    target_compliance_level: float = Query(85.0, ge=50.0, le=100.0)
):
    """Проведение оценки соответствия"""
    try:
        if standard != ComplianceStandard.ISO_22301:
            raise HTTPException(status_code=400, detail=f"Assessment for {standard} not implemented yet")
        
        # Получаем все требования
        requirements = compliance_checker.ISO_22301_REQUIREMENTS
        
        # Собираем все доказательства
        all_evidence = []
        for evidence_list in evidence_store.values():
            all_evidence.extend(evidence_list)
        
        # Оцениваем каждое требование
        assessment_results = []
        total_weighted_score = 0
        total_weight = 0
        
        for req_id, requirement in requirements.items():
            result = compliance_checker.assess_requirement_compliance(requirement, all_evidence)
            result["requirement"] = requirement.dict()
            assessment_results.append(result)
            
            # Взвешенная оценка
            total_weighted_score += result["score"] * requirement.weight
            total_weight += requirement.weight
        
        # Общая оценка
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Определяем общий статус
        if overall_score >= target_compliance_level:
            overall_status = ComplianceStatus.COMPLIANT
        elif overall_score >= 60:
            overall_status = ComplianceStatus.PARTIAL
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        # Создаем объект оценки
        assessment = ComplianceAssessment(
            standard=standard,
            assessor=assessor,
            scope=scope,
            requirements_assessed=[req_id for req_id in requirements.keys()],
            overall_status=overall_status,
            score=round(overall_score, 2)
        )
        
        # Сохраняем оценку
        assessment_store[assessment.id] = assessment
        
        # Идентифицируем пробелы
        gaps = compliance_checker.identify_compliance_gaps(assessment_results, target_compliance_level)
        
        logger.info(f"Проведена оценка соответствия {standard}: {overall_score}%")
        
        return {
            "assessment": assessment,
            "detailed_results": assessment_results,
            "compliance_gaps": [gap.dict() for gap in gaps],
            "summary": {
                "total_requirements": len(requirements),
                "compliant_requirements": len([r for r in assessment_results if r["status"] == ComplianceStatus.COMPLIANT]),
                "critical_gaps": len([g for g in gaps if g.severity == Severity.CRITICAL]),
                "recommendations_count": sum(len(gap.recommended_actions) for gap in gaps)
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка при проведении оценки: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@app.get("/assessments")
async def get_assessments():
    """Получение списка проведенных оценок"""
    assessments = list(assessment_store.values())
    return {
        "total_assessments": len(assessments),
        "assessments": [assessment.dict() for assessment in assessments]
    }

@app.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Получение детальной информации об оценке"""
    if assessment_id not in assessment_store:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment_store[assessment_id]

@app.get("/analytics/compliance-trends")
async def get_compliance_trends(days: int = Query(30, ge=7, le=365)):
    """Аналитика трендов соответствия"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    recent_assessments = [
        assessment for assessment in assessment_store.values()
        if assessment.assessment_date >= cutoff_date
    ]
    
    if not recent_assessments:
        return {"message": f"No assessments in the last {days} days"}
    
    # Группируем по стандартам
    by_standard = {}
    for assessment in recent_assessments:
        standard = assessment.standard
        if standard not in by_standard:
            by_standard[standard] = []
        by_standard[standard].append(assessment.score)
    
    # Рассчитываем тренды
    trends = {}
    for standard, scores in by_standard.items():
        trends[standard] = {
            "average_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "assessments_count": len(scores),
            "trend": "improving" if len(scores) > 1 and scores[-1] > scores[0] else "stable"
        }
    
    return {
        "period_days": days,
        "total_assessments": len(recent_assessments),
        "trends_by_standard": trends,
        "generated_at": datetime.now().isoformat()
    }

@app.post("/verify-evidence/{requirement_id}/{evidence_index}")
async def verify_evidence(requirement_id: str, evidence_index: int, verifier: str):
    """Верификация доказательства"""
    if requirement_id not in evidence_store:
        raise HTTPException(status_code=404, detail="No evidence found for requirement")
    
    evidence_list = evidence_store[requirement_id]
    if evidence_index >= len(evidence_list):
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    evidence_list[evidence_index].verified = True
    evidence_list[evidence_index].verifier = verifier
    
    return {
        "status": "verified",
        "requirement_id": requirement_id,
        "verifier": verifier,
        "verification_date": datetime.now().isoformat()
    }

@app.delete("/evidence/{requirement_id}/{evidence_index}")
async def delete_evidence(requirement_id: str, evidence_index: int):
    """Удаление доказательства"""
    if requirement_id not in evidence_store:
        raise HTTPException(status_code=404, detail="No evidence found for requirement")
    
    evidence_list = evidence_store[requirement_id]
    if evidence_index >= len(evidence_list):
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    deleted_evidence = evidence_list.pop(evidence_index)
    
    if not evidence_list:
        del evidence_store[requirement_id]
    
    return {
        "status": "deleted",
        "requirement_id": requirement_id,
        "deleted_evidence_type": deleted_evidence.evidence_type
    }

@app.get("/")
async def root():
    return {
        "service": "Compliance Checker - BCM Platform", 
        "version": "1.0.0",
        "description": "Интеллектуальная система проверки соответствия требованиям BCM",
        "supported_standards": [
            "ISO 22301 (Business Continuity Management)",
            "ISO 27001 (Information Security) - Coming Soon",
            "SOX (Sarbanes-Oxley) - Coming Soon"
        ],
        "features": {
            "requirements_management": "Управление требованиями стандартов",
            "evidence_collection": "Сбор и управление доказательствами",
            "automated_assessment": "Автоматизированная оценка соответствия",
            "gap_analysis": "Анализ пробелов и рекомендации",
            "compliance_reporting": "Генерация отчетов по соответствию",
            "trend_analysis": "Анализ трендов соответствия"
        },
        "endpoints": {
            "requirements": "/requirements/{standard}",
            "evidence_submission": "/evidence",
            "assessment": "/assess", 
            "analytics": "/analytics/compliance-trends"
        },
        "status": "Compliance Checker Active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8084")))
