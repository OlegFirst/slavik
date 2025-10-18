"""
BIA (Business Impact Analysis) Router
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from models import (
    BIACreate,
    BIAUpdate,
    BIAResponse,
    BIADetailed,
    BIAStats,
    BIAProcessCreate,
    BIAProcessUpdate,
    BIAProcessResponse,
    BIADependencyCreate,
    BIADependencyResponse,
    BIAQuestionGenerate,
    BIAQuestionResponse,
    BIAAnswerSubmit,
    BIAFindingCreate,
    BIAFindingUpdate,
    BIAFindingResponse,
    AICalculateRTORequest,
    AIRTORecommendation
)
from auth import get_current_user_id
from database import DatabaseClient
from ai_service import AIService

router = APIRouter(prefix="/api/bia", tags=["bia"])


def get_db() -> DatabaseClient:
    """Get database client"""
    return DatabaseClient()


def get_ai() -> AIService:
    """Get AI service"""
    return AIService()


async def verify_bia_access(analysis_id: str, user_id: str, db: DatabaseClient):
    """Verify user has access to BIA analysis"""
    analysis = await db.get_bia_analysis(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BIA analysis not found"
        )

    org = await db.get_organization(analysis["organization_id"])
    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return analysis


# ============================================
# BIA ANALYSIS ENDPOINTS
# ============================================

@router.post("", response_model=BIAResponse, status_code=status.HTTP_201_CREATED)
async def create_bia_analysis(
    request: BIACreate,
    org_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Create new BIA analysis
    """
    org = await db.get_organization(org_id)
    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    analysis_data = {
        "organization_id": org_id,
        "name": request.name,
        "status": "draft",
        "collection_method": request.collection_method.value,
        "compliance_score": 0
    }

    analysis = await db.create_bia_analysis(analysis_data)

    # Log audit
    await db.create_audit_log({
        "user_id": user_id,
        "organization_id": org_id,
        "action": "bia.created",
        "resource_type": "bia_analysis",
        "resource_id": analysis["id"]
    })

    return BIAResponse(**analysis)


@router.get("", response_model=List[BIAResponse])
async def list_bia_analyses(
    org_id: str,
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    List BIA analyses for organization
    """
    org = await db.get_organization(org_id)
    if not org or org["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    analyses = await db.list_bia_analyses(org_id, status=status)

    return [BIAResponse(**a) for a in analyses]


@router.get("/{analysis_id}", response_model=BIADetailed)
async def get_bia_analysis(
    analysis_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Get BIA analysis details
    """
    analysis = await verify_bia_access(analysis_id, user_id, db)

    # Get statistics
    processes = await db.list_bia_processes(analysis_id)
    dependencies = await db.list_bia_dependencies(analysis_id)
    findings = await db.list_bia_findings(analysis_id)

    critical_processes = [p for p in processes if p["criticality"] == "critical"]

    stats = BIAStats(
        processes_count=len(processes),
        critical_processes_count=len(critical_processes),
        dependencies_count=len(dependencies),
        findings_count=len(findings)
    )

    return BIADetailed(**analysis, stats=stats)


@router.patch("/{analysis_id}", response_model=BIAResponse)
async def update_bia_analysis(
    analysis_id: str,
    request: BIAUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Update BIA analysis
    """
    await verify_bia_access(analysis_id, user_id, db)

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.status is not None:
        update_data["status"] = request.status.value
        if request.status.value == "completed":
            update_data["completed_at"] = datetime.utcnow()

    updated_analysis = await db.update_bia_analysis(analysis_id, update_data)

    return BIAResponse(**updated_analysis)


# ============================================
# BIA PROCESS ENDPOINTS
# ============================================

@router.post("/{analysis_id}/processes", response_model=BIAProcessResponse, status_code=status.HTTP_201_CREATED)
async def create_bia_process(
    analysis_id: str,
    request: BIAProcessCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Create BIA process
    """
    await verify_bia_access(analysis_id, user_id, db)

    process_data = {
        "analysis_id": analysis_id,
        "process_id": request.process_id,
        "name": request.name,
        "description": request.description,
        "criticality": request.criticality.value,
        "category": request.category,
        "owner_department": request.owner_department,
        "owner_person": request.owner_person
    }

    process = await db.create_bia_process(process_data)

    return BIAProcessResponse(**process)


@router.get("/{analysis_id}/processes", response_model=List[BIAProcessResponse])
async def list_bia_processes(
    analysis_id: str,
    criticality: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    List BIA processes
    """
    await verify_bia_access(analysis_id, user_id, db)

    processes = await db.list_bia_processes(analysis_id, criticality=criticality)

    return [BIAProcessResponse(**p) for p in processes]


@router.patch("/{analysis_id}/processes/{process_id}", response_model=BIAProcessResponse)
async def update_bia_process(
    analysis_id: str,
    process_id: str,
    request: BIAProcessUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Update BIA process
    """
    await verify_bia_access(analysis_id, user_id, db)

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.criticality is not None:
        update_data["criticality"] = request.criticality.value
    if request.rto_hours is not None:
        update_data["rto_hours"] = request.rto_hours
    if request.rpo_hours is not None:
        update_data["rpo_hours"] = request.rpo_hours
    if request.mtpd_hours is not None:
        update_data["mtpd_hours"] = request.mtpd_hours
    if request.financial_impact_per_hour is not None:
        update_data["financial_impact_per_hour"] = request.financial_impact_per_hour

    updated_process = await db.update_bia_process(process_id, update_data)

    return BIAProcessResponse(**updated_process)


# ============================================
# BIA DEPENDENCY ENDPOINTS
# ============================================

@router.post("/{analysis_id}/dependencies", response_model=BIADependencyResponse, status_code=status.HTTP_201_CREATED)
async def create_bia_dependency(
    analysis_id: str,
    request: BIADependencyCreate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Create BIA dependency
    """
    await verify_bia_access(analysis_id, user_id, db)

    dependency_data = {
        "analysis_id": analysis_id,
        "source_process_id": request.source_process_id,
        "target_process_id": request.target_process_id,
        "dependency_type": request.dependency_type,
        "dependency_strength": request.dependency_strength,
        "ai_detected": False
    }

    dependency = await db.create_bia_dependency(dependency_data)

    return BIADependencyResponse(**dependency)


@router.get("/{analysis_id}/dependencies", response_model=List[BIADependencyResponse])
async def list_bia_dependencies(
    analysis_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    List BIA dependencies
    """
    await verify_bia_access(analysis_id, user_id, db)

    dependencies = await db.list_bia_dependencies(analysis_id)

    return [BIADependencyResponse(**d) for d in dependencies]


# ============================================
# BIA QUESTIONNAIRE ENDPOINTS
# ============================================

@router.post("/{analysis_id}/questionnaire/generate", response_model=List[BIAQuestionResponse])
async def generate_questionnaire(
    analysis_id: str,
    request: BIAQuestionGenerate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db),
    ai: AIService = Depends(get_ai)
):
    """
    AI generates personalized BIA questionnaire
    """
    analysis = await verify_bia_access(analysis_id, user_id, db)

    # For MVP, create simple static questions
    # In production, use AI to generate custom questions
    questions = [
        {
            "analysis_id": analysis_id,
            "question_text": "What are your organization's critical business processes?",
            "question_type": "text",
            "options": None,
            "sequence_number": 1,
            "ai_generated": False
        },
        {
            "analysis_id": analysis_id,
            "question_text": "What is the maximum acceptable downtime for your most critical process?",
            "question_type": "choice",
            "options": ["< 1 hour", "1-4 hours", "4-24 hours", "1-3 days", "> 3 days"],
            "sequence_number": 2,
            "ai_generated": False
        },
        {
            "analysis_id": analysis_id,
            "question_text": "What dependencies exist between your business processes?",
            "question_type": "text",
            "options": None,
            "sequence_number": 3,
            "ai_generated": False
        }
    ]

    created_questions = await db.create_bia_questions_bulk(questions)

    return [BIAQuestionResponse(**q) for q in created_questions]


@router.get("/{analysis_id}/questionnaire/questions", response_model=List[BIAQuestionResponse])
async def get_questionnaire_questions(
    analysis_id: str,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Get BIA questionnaire questions
    """
    await verify_bia_access(analysis_id, user_id, db)

    questions = await db.list_bia_questions(analysis_id)

    return [BIAQuestionResponse(**q) for q in questions]


@router.post("/{analysis_id}/questionnaire/answers", status_code=status.HTTP_201_CREATED)
async def submit_questionnaire_answers(
    analysis_id: str,
    answers: List[BIAAnswerSubmit],
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Submit answers to BIA questionnaire
    """
    await verify_bia_access(analysis_id, user_id, db)

    answer_data = []
    for answer in answers:
        answer_data.append({
            "question_id": answer.question_id,
            "answer_text": answer.answer_text,
            "answer_number": answer.answer_number,
            "answer_choice": answer.answer_choice,
            "answered_by": user_id
        })

    await db.create_bia_answers_bulk(answer_data)

    # Update analysis status
    await db.update_bia_analysis(analysis_id, {"status": "in_progress"})

    return {
        "status": "success",
        "saved_count": len(answers),
        "message": "Answers saved successfully"
    }


# ============================================
# BIA FINDING ENDPOINTS
# ============================================

@router.get("/{analysis_id}/findings", response_model=List[BIAFindingResponse])
async def list_bia_findings(
    analysis_id: str,
    finding_type: Optional[str] = None,
    severity: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    List BIA findings
    """
    await verify_bia_access(analysis_id, user_id, db)

    findings = await db.list_bia_findings(analysis_id, finding_type=finding_type, severity=severity)

    return [BIAFindingResponse(**f) for f in findings]


@router.patch("/{analysis_id}/findings/{finding_id}", response_model=BIAFindingResponse)
async def update_bia_finding(
    analysis_id: str,
    finding_id: str,
    request: BIAFindingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db)
):
    """
    Update BIA finding status
    """
    await verify_bia_access(analysis_id, user_id, db)

    update_data = {}
    if request.status is not None:
        update_data["status"] = request.status
    if request.user_notes is not None:
        update_data["user_notes"] = request.user_notes

    updated_finding = await db.update_bia_finding(finding_id, update_data)

    return BIAFindingResponse(**updated_finding)


# ============================================
# AI ENDPOINTS
# ============================================

@router.post("/{analysis_id}/ai/calculate-rto", response_model=AIRTORecommendation)
async def ai_calculate_rto(
    analysis_id: str,
    request: AICalculateRTORequest,
    user_id: str = Depends(get_current_user_id),
    db: DatabaseClient = Depends(get_db),
    ai: AIService = Depends(get_ai)
):
    """
    AI calculates RTO/RPO recommendations
    """
    analysis = await verify_bia_access(analysis_id, user_id, db)
    org = await db.get_organization(analysis["organization_id"])

    try:
        result = await ai.calculate_process_rto(
            process_name=request.process_name,
            process_description=request.process_description or "",
            industry=request.industry,
            criticality=request.criticality,
            user_id=user_id,
            organization_id=org["id"]
        )

        return AIRTORecommendation(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI calculation failed: {str(e)}"
        )
