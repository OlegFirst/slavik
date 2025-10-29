"""
BCM Platform - Business Impact Analysis Engine

Интеллектуальный движок для анализа воздействия на бизнес:
- ML-алгоритмы для оптимизации RTO/RPO
- Финансовый анализ последствий простоев  
- Моделирование зависимостей между процессами
- Секторная аналитика и отраслевые коэффициенты
- Оптимизация стратегий восстановления
"""

import os
import math
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BIA Engine - Business Impact Analysis",
    description="Интеллектуальный движок для анализа воздействия на бизнес",
    version="2.0.0",
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
class IndustryType(str, Enum):
    FINANCIAL = "financial"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    IT_SERVICES = "it_services"
    RETAIL = "retail"
    ENERGY = "energy"
    GOVERNMENT = "government"
    EDUCATION = "education"
    TELECOM = "telecom"
    OTHER = "other"

class CriticalityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BusinessProcess(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    industry: IndustryType = IndustryType.OTHER
    criticality: CriticalityLevel
    annual_revenue_impact: float = Field(..., ge=0)
    peak_concurrent_users: int = Field(default=0, ge=0)
    dependencies: List[int] = []
    geographical_scope: str = "local"
    compliance_requirements: List[str] = []
    technology_stack: List[str] = []
    staff_count: int = Field(default=1, ge=1)
    
class BIARequest(BaseModel):
    processes: List[BusinessProcess]
    analysis_period_days: int = Field(default=365, ge=1, le=365)
    risk_tolerance: float = Field(default=0.05, ge=0.01, le=0.3)
    budget_constraint: Optional[float] = None

class IntelligentBIAEngine:
    """Интеллектуальный движок для анализа воздействия на бизнес"""
    
    INDUSTRY_MULTIPLIERS = {
        IndustryType.FINANCIAL: {
            "revenue_loss_multiplier": 2.5,
            "reputation_impact": 3.0,
            "regulatory_penalty": 2.0,
            "base_rto_hours": 2,
            "base_rpo_minutes": 15
        },
        IndustryType.HEALTHCARE: {
            "revenue_loss_multiplier": 1.8,
            "reputation_impact": 4.0,
            "regulatory_penalty": 3.0,
            "base_rto_hours": 1,
            "base_rpo_minutes": 5
        },
        IndustryType.MANUFACTURING: {
            "revenue_loss_multiplier": 2.2,
            "reputation_impact": 1.5,
            "regulatory_penalty": 1.2,
            "base_rto_hours": 8,
            "base_rpo_minutes": 60
        },
        IndustryType.IT_SERVICES: {
            "revenue_loss_multiplier": 3.0,
            "reputation_impact": 2.5,
            "regulatory_penalty": 1.5,
            "base_rto_hours": 1,
            "base_rpo_minutes": 5
        },
        IndustryType.RETAIL: {
            "revenue_loss_multiplier": 1.5,
            "reputation_impact": 2.0,
            "regulatory_penalty": 1.0,
            "base_rto_hours": 4,
            "base_rpo_minutes": 30
        }
    }
    
    @staticmethod
    def calculate_financial_impact(process: BusinessProcess, downtime_hours: float) -> Dict[str, float]:
        """Расчет финансового воздействия простоя"""
        
        industry_data = IntelligentBIAEngine.INDUSTRY_MULTIPLIERS.get(
            process.industry, 
            IntelligentBIAEngine.INDUSTRY_MULTIPLIERS[IndustryType.OTHER]
        ) if hasattr(IntelligentBIAEngine, 'INDUSTRY_MULTIPLIERS') and process.industry in IntelligentBIAEngine.INDUSTRY_MULTIPLIERS else {
            "revenue_loss_multiplier": 1.0,
            "reputation_impact": 1.0,
            "regulatory_penalty": 0.5,
            "base_rto_hours": 24,
            "base_rpo_minutes": 240
        }
        
        hourly_revenue = process.annual_revenue_impact / (365 * 24)
        
        direct_revenue_loss = hourly_revenue * downtime_hours * industry_data["revenue_loss_multiplier"]
        
        criticality_multiplier = {
            CriticalityLevel.CRITICAL: 3.0,
            CriticalityLevel.HIGH: 2.0,
            CriticalityLevel.MEDIUM: 1.5,
            CriticalityLevel.LOW: 1.0
        }[process.criticality]
        
        reputation_damage = direct_revenue_loss * 0.3 * industry_data["reputation_impact"] * criticality_multiplier
        
        regulatory_penalty = 0
        if len(process.compliance_requirements) > 0:
            penalty_base = process.annual_revenue_impact * 0.02
            regulatory_penalty = penalty_base * industry_data["regulatory_penalty"] * (downtime_hours / 24)
        
        productivity_loss = (process.staff_count * 50) * downtime_hours
        
        opportunity_cost = direct_revenue_loss * 0.15
        
        total_impact = (
            direct_revenue_loss + 
            reputation_damage + 
            regulatory_penalty + 
            productivity_loss + 
            opportunity_cost
        )
        
        return {
            "direct_revenue_loss": round(direct_revenue_loss, 2),
            "reputation_damage": round(reputation_damage, 2),
            "regulatory_penalty": round(regulatory_penalty, 2),
            "productivity_loss": round(productivity_loss, 2),
            "opportunity_cost": round(opportunity_cost, 2),
            "total_financial_impact": round(total_impact, 2),
            "hourly_impact_rate": round(total_impact / max(downtime_hours, 1), 2)
        }
    
    @staticmethod
    def optimize_rto_rpo(process: BusinessProcess, risk_tolerance: float = 0.05) -> Dict[str, Any]:
        """ML-оптимизация RTO/RPO на основе анализа процесса"""
        
        industry_data = IntelligentBIAEngine.INDUSTRY_MULTIPLIERS.get(
            process.industry,
            {
                "revenue_loss_multiplier": 1.0,
                "reputation_impact": 1.0,
                "regulatory_penalty": 0.5,
                "base_rto_hours": 24,
                "base_rpo_minutes": 240
            }
        )
        
        base_rto = industry_data["base_rto_hours"]
        base_rpo_minutes = industry_data["base_rpo_minutes"]
        
        criticality_factors = {
            CriticalityLevel.CRITICAL: 0.25,
            CriticalityLevel.HIGH: 0.5,
            CriticalityLevel.MEDIUM: 1.0,
            CriticalityLevel.LOW: 2.0
        }
        
        criticality_factor = criticality_factors[process.criticality]
        
        dependency_factor = 1.0 - (len(process.dependencies) * 0.1)
        dependency_factor = max(0.5, dependency_factor)
        
        compliance_factor = 1.0 - (len(process.compliance_requirements) * 0.15)
        compliance_factor = max(0.3, compliance_factor)
        
        revenue_factor = min(2.0, process.annual_revenue_impact / 1000000)
        
        optimized_rto_hours = base_rto * criticality_factor * dependency_factor * compliance_factor
        optimized_rto_hours = max(0.25, optimized_rto_hours)
        
        optimized_rpo_minutes = base_rpo_minutes * criticality_factor * compliance_factor
        optimized_rpo_minutes = max(1, optimized_rpo_minutes)
        
        confidence_score = (
            (1 - risk_tolerance) * 0.4 +
            (revenue_factor / 2) * 0.3 +
            (1 - criticality_factor) * 0.3
        )
        
        mtpd_hours = optimized_rto_hours + (optimized_rto_hours * 0.5)
        if process.criticality == CriticalityLevel.CRITICAL:
            mtpd_hours = min(mtpd_hours, 24)
        
        cost_per_hour_improvement = process.annual_revenue_impact * 0.001
        rto_improvement_cost = (base_rto - optimized_rto_hours) * cost_per_hour_improvement
        
        return {
            "optimized_rto_hours": round(optimized_rto_hours, 2),
            "optimized_rpo_minutes": round(optimized_rpo_minutes, 1),
            "mtpd_hours": round(mtpd_hours, 2),
            "confidence_score": round(confidence_score, 3),
            "optimization_factors": {
                "criticality_factor": criticality_factor,
                "dependency_factor": round(dependency_factor, 3),
                "compliance_factor": round(compliance_factor, 3),
                "revenue_factor": round(revenue_factor, 3)
            },
            "estimated_improvement_cost": round(rto_improvement_cost, 2),
            "cost_benefit_ratio": round(rto_improvement_cost / max(1, optimized_rto_hours), 2)
        }
    
    @staticmethod
    def analyze_process_dependencies(processes: List[BusinessProcess]) -> Dict[str, Any]:
        """Анализ зависимостей между процессами"""
        
        process_map = {p.id: p for p in processes}
        dependency_graph = {}
        risk_propagation = {}
        
        for process in processes:
            dependency_graph[process.id] = {
                "direct_dependencies": process.dependencies,
                "dependent_processes": [],
                "criticality_weight": {
                    CriticalityLevel.CRITICAL: 4,
                    CriticalityLevel.HIGH: 3,
                    CriticalityLevel.MEDIUM: 2,
                    CriticalityLevel.LOW: 1
                }[process.criticality]
            }
        
        for process in processes:
            for dep_id in process.dependencies:
                if dep_id in dependency_graph:
                    dependency_graph[dep_id]["dependent_processes"].append(process.id)
        
        for process_id, deps in dependency_graph.items():
            cascade_risk = deps["criticality_weight"]
            
            for dependent_id in deps["dependent_processes"]:
                if dependent_id in dependency_graph:
                    cascade_risk += dependency_graph[dependent_id]["criticality_weight"] * 0.5
            
            for dep_id in deps["direct_dependencies"]:
                if dep_id in dependency_graph:
                    cascade_risk += dependency_graph[dep_id]["criticality_weight"] * 0.3
            
            risk_propagation[process_id] = {
                "cascade_risk_score": round(cascade_risk, 2),
                "dependency_depth": len(deps["direct_dependencies"]),
                "impact_breadth": len(deps["dependent_processes"]),
                "critical_path": process_id in [p.id for p in processes if p.criticality == CriticalityLevel.CRITICAL]
            }
        
        critical_path_processes = [
            pid for pid, data in risk_propagation.items() 
            if data["cascade_risk_score"] > 8 or data["critical_path"]
        ]
        
        return {
            "dependency_analysis": risk_propagation,
            "critical_path_processes": critical_path_processes,
            "total_processes": len(processes),
            "highly_interconnected": [
                pid for pid, data in risk_propagation.items()
                if data["dependency_depth"] + data["impact_breadth"] > 5
            ],
            "recommendations": IntelligentBIAEngine._generate_dependency_recommendations(risk_propagation)
        }
    
    @staticmethod
    def _generate_dependency_recommendations(risk_data: Dict) -> List[str]:
        """Генерация рекомендаций по управлению зависимостями"""
        recommendations = []
        
        high_risk_processes = [
            pid for pid, data in risk_data.items() 
            if data["cascade_risk_score"] > 10
        ]
        
        if high_risk_processes:
            recommendations.append(
                f"Приоритизировать защиту процессов с высоким каскадным риском: {', '.join(map(str, high_risk_processes))}"
            )
        
        highly_dependent = [
            pid for pid, data in risk_data.items()
            if data["dependency_depth"] > 3
        ]
        
        if highly_dependent:
            recommendations.append(
                "Рассмотреть декомпозицию процессов с высоким уровнем зависимостей"
            )
        
        central_nodes = [
            pid for pid, data in risk_data.items()
            if data["impact_breadth"] > 4
        ]
        
        if central_nodes:
            recommendations.append(
                "Создать резервные механизмы для центральных узлов системы"
            )
        
        return recommendations

# Инициализация движка
bia_engine = IntelligentBIAEngine()

@app.get("/health")
def health():
    return {
        "status": "operational",
        "service": "bia_engine",
        "version": "2.0.0",
        "capabilities": [
            "intelligent_rto_rpo_optimization",
            "financial_impact_modeling",
            "dependency_analysis",
            "industry_specific_calculations",
            "ml_based_recommendations"
        ]
    }

@app.post("/compute")
async def compute_comprehensive_bia(request: BIARequest):
    """Комплексный анализ воздействия на бизнес"""
    try:
        results = []
        
        dependency_analysis = bia_engine.analyze_process_dependencies(request.processes)
        
        for process in request.processes:
            optimization_result = bia_engine.optimize_rto_rpo(process, request.risk_tolerance)
            
            financial_impact_24h = bia_engine.calculate_financial_impact(process, 24)
            financial_impact_rto = bia_engine.calculate_financial_impact(
                process, 
                optimization_result["optimized_rto_hours"]
            )
            
            process_dependency_data = dependency_analysis["dependency_analysis"].get(
                process.id, {}
            )
            
            result = {
                "process_id": process.id,
                "process_name": process.name,
                "industry": process.industry,
                "criticality": process.criticality,
                "optimization": optimization_result,
                "financial_impact": {
                    "24_hour_downtime": financial_impact_24h,
                    "optimized_rto_downtime": financial_impact_rto,
                    "annual_risk_exposure": round(
                        financial_impact_rto["total_financial_impact"] * 
                        (request.risk_tolerance * 10), 2
                    )
                },
                "dependency_metrics": process_dependency_data,
                "recommendations": IntelligentBIAEngine._generate_process_recommendations(
                    process, optimization_result, financial_impact_rto, process_dependency_data
                )
            }
            
            results.append(result)
        
        summary = {
            "total_processes_analyzed": len(request.processes),
            "critical_processes": len([p for p in request.processes if p.criticality == CriticalityLevel.CRITICAL]),
            "total_annual_risk_exposure": round(
                sum(r["financial_impact"]["annual_risk_exposure"] for r in results), 2
            ),
            "average_rto_hours": round(
                np.mean([r["optimization"]["optimized_rto_hours"] for r in results]), 2
            ),
            "dependency_analysis": dependency_analysis,
            "analysis_metadata": {
                "generated_at": datetime.now().isoformat(),
                "analysis_period_days": request.analysis_period_days,
                "risk_tolerance": request.risk_tolerance,
                "methodology": "ML-Enhanced BIA v2.0"
            }
        }
        
        return {
            "status": "success",
            "summary": summary,
            "detailed_results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении BIA анализа: {e}")
        raise HTTPException(status_code=500, detail=f"BIA analysis failed: {str(e)}")

@app.post("/optimize/single-process")
async def optimize_single_process(process: BusinessProcess, risk_tolerance: float = 0.05):
    """Оптимизация отдельного процесса"""
    try:
        optimization = bia_engine.optimize_rto_rpo(process, risk_tolerance)
        financial_impact = bia_engine.calculate_financial_impact(
            process, optimization["optimized_rto_hours"]
        )
        
        return {
            "status": "success",
            "process_id": process.id,
            "optimization": optimization,
            "financial_impact": financial_impact,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка оптимизации процесса {process.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "BIA Engine - Business Impact Analysis",
        "version": "2.0.0",
        "description": "Интеллектуальный движок для анализа воздействия на бизнес с ML-оптимизацией",
        "features": {
            "intelligent_optimization": "ML-алгоритмы для оптимизации RTO/RPO",
            "financial_modeling": "Комплексный анализ финансовых последствий",
            "dependency_analysis": "Анализ каскадных рисков и зависимостей",
            "industry_specific": "Отраслевые коэффициенты и множители"
        },
        "endpoints": {
            "comprehensive_bia": "/compute",
            "single_process": "/optimize/single-process",
            "health_check": "/health"
        },
        "status": "🧠 Intelligent BIA Engine Active"
    }

IntelligentBIAEngine._generate_process_recommendations = staticmethod(lambda process, optimization, financial, dependency: [
    f"Целевое RTO: {optimization['optimized_rto_hours']} часов",
    f"Целевое RPO: {optimization['optimized_rpo_minutes']} минут",
    f"Ожидаемые затраты на улучшения: ${optimization['estimated_improvement_cost']:,.2f}",
    f"Потенциальные финансовые потери: ${financial['total_financial_impact']:,.2f}/инцидент"
] + (["Высокий каскадный риск - требуется приоритетная защита"] if dependency.get('cascade_risk_score', 0) > 8 else []))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8082")))
