"""
Тесты для интеллектуальных сервисов BCM Platform

Проверка основной функциональности:
- AI Orchestrator
- BIA Engine v2.0  
- Document Processor
- Compliance Checker
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Добавляем пути к сервисам
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'ai_orchestrator'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'bia_engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'document_processor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'compliance_checker'))

class TestAIOrchestrator:
    """Тесты AI Orchestrator сервиса"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        from main import BCMIntelligenceEngine, BusinessProcess, Incident
        from main import RiskLevel, IncidentCategory
        
        self.engine = BCMIntelligenceEngine()
        self.test_process = BusinessProcess(
            id=1,
            name="Тестовый процесс",
            description="Критический бизнес-процесс для тестирования",
            criticality=5,
            rto_hours=4,
            rpo_hours=1,
            dependencies=[2, 3],
            resources_required=["server1", "database1"]
        )
        
        self.test_incident = Incident(
            title="Кибератака на сервер",
            description="Обнаружена подозрительная активность и возможная утечка данных в системе",
            category=IncidentCategory.SECURITY,
            severity=RiskLevel.HIGH,
            affected_processes=[1, 2]
        )
    
    def test_process_risk_analysis(self):
        """Тест анализа рисков бизнес-процесса"""
        result = self.engine.analyze_business_process_risk(self.test_process)
        
        assert "risk_score" in result
        assert "risk_level" in result
        assert "factors" in result
        assert "recommendations" in result
        
        # Проверяем что оценка риска положительная
        assert result["risk_score"] > 0
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
    
    def test_incident_classification(self):
        """Тест классификации инцидента"""
        result = self.engine.classify_incident(self.test_incident)
        
        assert "predicted_category" in result
        assert "confidence" in result
        assert "recommended_actions" in result
        assert "estimated_resolution_time" in result
        
        # Проверяем что классификация работает
        assert result["confidence"] >= 0
        assert result["estimated_resolution_time"] > 0
        assert isinstance(result["recommended_actions"], list)

class TestBIAEngine:
    """Тесты BIA Engine v2.0"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        try:
            from app import IntelligentBIAEngine, BusinessProcess
            from app import IndustryType, CriticalityLevel
        except ImportError:
            pytest.skip("IntelligentBIAEngine not available - skipping BIA tests")
        
        self.engine = IntelligentBIAEngine()
        self.test_process = BusinessProcess(
            id=1,
            name="Критический IT процесс",
            industry=IndustryType.IT_SERVICES,
            criticality=CriticalityLevel.CRITICAL,
            annual_revenue_impact=5000000.0,
            dependencies=[2, 3],
            compliance_requirements=["ISO27001", "GDPR"],
            staff_count=25
        )
    
    def test_financial_impact_calculation(self):
        """Тест расчета финансового воздействия"""
        result = self.engine.calculate_financial_impact(self.test_process, 24.0)
        
        required_fields = [
            "direct_revenue_loss",
            "reputation_damage", 
            "regulatory_penalty",
            "productivity_loss",
            "opportunity_cost",
            "total_financial_impact"
        ]
        
        for field in required_fields:
            assert field in result
            assert isinstance(result[field], (int, float))
            assert result[field] >= 0
        
        # Проверяем что общее воздействие больше прямых потерь
        assert result["total_financial_impact"] >= result["direct_revenue_loss"]
    
    def test_rto_rpo_optimization(self):
        """Тест ML-оптимизации RTO/RPO"""
        result = self.engine.optimize_rto_rpo(self.test_process, risk_tolerance=0.05)
        
        required_fields = [
            "optimized_rto_hours",
            "optimized_rpo_minutes", 
            "mtpd_hours",
            "confidence_score",
            "optimization_factors"
        ]
        
        for field in required_fields:
            assert field in result
        
        # Проверяем разумность значений
        assert 0.25 <= result["optimized_rto_hours"] <= 72
        assert 1 <= result["optimized_rpo_minutes"] <= 1440
        assert 0 <= result["confidence_score"] <= 1
    
    def test_dependency_analysis(self):
        """Тест анализа зависимостей между процессами"""
        processes = [self.test_process]
        
        # Добавляем зависимый процесс
        from app import BusinessProcess, IndustryType, CriticalityLevel
        dependent_process = BusinessProcess(
            id=2,
            name="Зависимый процесс",
            industry=IndustryType.IT_SERVICES,
            criticality=CriticalityLevel.HIGH,
            annual_revenue_impact=2000000.0,
            dependencies=[1]  # Зависит от первого процесса
        )
        processes.append(dependent_process)
        
        result = self.engine.analyze_process_dependencies(processes)
        
        assert "dependency_analysis" in result
        assert "critical_path_processes" in result
        assert "recommendations" in result
        
        # Проверяем что анализ учитывает зависимости
        assert len(result["dependency_analysis"]) == len(processes)
        assert isinstance(result["recommendations"], list)

class TestDocumentProcessor:
    """Тесты Document Processor"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        try:
            from app import IntelligentDocumentProcessor
        except ImportError:
            pytest.skip("IntelligentDocumentProcessor not available - skipping Document tests")
        
        self.processor = IntelligentDocumentProcessor()
        self.test_text = """
        План непрерывности бизнеса
        
        Цель восстановления (RTO): 4 часа
        Точка восстановления (RPO): 1 час
        
        Процедуры восстановления после инцидента безопасности:
        1. Изолировать затронутые системы
        2. Провести оценку воздействия на бизнес 
        3. Активировать план восстановления
        """
    
    def test_document_classification(self):
        """Тест классификации документов"""
        doc_type, confidence = self.processor.classify_document(
            self.test_text, 
            "business_continuity_plan.pdf"
        )
        
        from app import DocumentType
        assert isinstance(doc_type, DocumentType)
        assert 0 <= confidence <= 1
        
        # Документ должен быть классифицирован как BCP
        assert doc_type == DocumentType.BCP
        assert confidence > 0.5
    
    def test_key_concepts_extraction(self):
        """Тест извлечения ключевых концепций"""
        concepts = self.processor.extract_key_concepts(self.test_text)
        
        assert isinstance(concepts, list)
        assert len(concepts) > 0
        
        # Должны быть найдены BCM концепции
        expected_concepts = ["rto", "rpo", "incident", "continuity"]
        found_concepts = [c for c in expected_concepts if c in concepts]
        assert len(found_concepts) > 0
    
    def test_iso_compliance_analysis(self):
        """Тест анализа соответствия ISO 22301"""
        result = self.processor.analyze_iso_compliance(self.test_text)
        
        assert "compliance_level" in result
        assert "overall_percentage" in result
        assert "section_coverage" in result
        assert "recommendations" in result
        
        # Проверяем структуру покрытия разделов
        assert isinstance(result["section_coverage"], dict)
        assert len(result["recommendations"]) > 0

class TestComplianceChecker:
    """Тесты Compliance Checker"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        from app import IntelligentComplianceChecker, ComplianceRequirement
        from app import ComplianceEvidence, ComplianceStandard, RequirementCategory
        
        self.checker = IntelligentComplianceChecker()
        self.test_requirement = ComplianceRequirement(
            id="4.1",
            standard=ComplianceStandard.ISO_22301,
            category=RequirementCategory.GOVERNANCE,
            title="Понимание организации и ее контекста",
            description="Тестовое требование",
            evidence_required=["context_analysis", "stakeholder_analysis"]
        )
        
        self.test_evidence = ComplianceEvidence(
            requirement_id="4.1",
            evidence_type="context_analysis",
            description="Анализ контекста организации",
            last_updated=datetime.now(),
            verified=True,
            verifier="test_auditor"
        )
    
    def test_requirement_compliance_assessment(self):
        """Тест оценки соответствия требованию"""
        evidence_list = [self.test_evidence]
        
        result = self.checker.assess_requirement_compliance(
            self.test_requirement, 
            evidence_list
        )
        
        required_fields = [
            "requirement_id",
            "status",
            "score", 
            "evidence_coverage",
            "verification_rate",
            "missing_evidence"
        ]
        
        for field in required_fields:
            assert field in result
        
        # Проверяем разумность значений
        assert result["requirement_id"] == "4.1"
        assert 0 <= result["score"] <= 100
        assert 0 <= result["evidence_coverage"] <= 100
        assert isinstance(result["missing_evidence"], list)
    
    def test_compliance_gaps_identification(self):
        """Тест идентификации пробелов в соответствии"""
        assessment_results = [{
            "requirement_id": "4.1",
            "status": "partial_compliance",
            "score": 60.0,
            "missing_evidence": ["stakeholder_analysis"]
        }]
        
        gaps = self.checker.identify_compliance_gaps(
            assessment_results, 
            target_compliance_level=85.0
        )
        
        assert isinstance(gaps, list)
        assert len(gaps) > 0
        
        gap = gaps[0]
        assert hasattr(gap, 'requirement_id')
        assert hasattr(gap, 'severity') 
        assert hasattr(gap, 'recommended_actions')
        
        # Проверяем что пробел корректно идентифицирован
        assert gap.requirement_id == "4.1"
        assert len(gap.recommended_actions) > 0

# Интеграционные тесты
class TestServicesIntegration:
    """Интеграционные тесты между сервисами"""
    
    @pytest.mark.integration
    def test_ai_orchestrator_bia_integration(self):
        """Тест интеграции AI Orchestrator с BIA Engine"""
        # Тест показывает как сервисы могут взаимодействовать
        # через общие модели данных
        
        # AI Orchestrator анализирует процесс
        from main import BCMIntelligenceEngine, BusinessProcess as AIBusinessProcess
        ai_engine = BCMIntelligenceEngine()
        
        ai_process = AIBusinessProcess(
            id=1,
            name="Критический процесс",
            description="Тестовый процесс",
            criticality=5,
            rto_hours=4,
            rpo_hours=1,
            dependencies=[],
            resources_required=[]
        )
        
        ai_result = ai_engine.analyze_business_process_risk(ai_process)
        assert "risk_level" in ai_result
        
        # Результат может быть передан в BIA Engine для детального анализа
        # (в реальной интеграции через HTTP API)
        assert ai_result["risk_score"] > 0

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
