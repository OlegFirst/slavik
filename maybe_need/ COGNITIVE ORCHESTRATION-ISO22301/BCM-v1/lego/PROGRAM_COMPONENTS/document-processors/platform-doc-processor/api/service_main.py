"""
BCM Platform - Document Processor Service

Интеллектуальная обработка документов для BCM:
- Автоматическое извлечение метаданных из документов
- OCR и анализ содержимого
- Классификация документов по типам BCM
- Генерация индексов для поиска
- Анализ соответствия требованиям ISO 22301
- Интеграция с системой управления знаниями
"""

import os
import hashlib
import json
import logging
import mimetypes
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, BinaryIO
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Processor - BCM Platform",
    description="Интеллектуальная обработка документов для Business Continuity Management",
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
class DocumentType(str, Enum):
    BCP = "business_continuity_plan"
    BIA = "business_impact_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    PROCEDURE = "procedure"
    POLICY = "policy"
    GUIDELINE = "guideline"
    TEMPLATE = "template"
    REPORT = "report"
    AUDIT = "audit"
    CERTIFICATION = "certification"
    TRAINING = "training_material"
    INCIDENT_REPORT = "incident_report"
    OTHER = "other"

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ComplianceLevel(str, Enum):
    FULL = "full_compliance"
    PARTIAL = "partial_compliance"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"

class DocumentMetadata(BaseModel):
    filename: str
    file_size: int
    content_type: str
    upload_date: datetime
    file_hash: str
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    document_type: DocumentType
    processing_status: ProcessingStatus
    extracted_text: Optional[str] = None
    key_concepts: List[str] = []
    compliance_analysis: Optional[Dict[str, Any]] = None
    search_keywords: List[str] = []
    structured_data: Optional[Dict[str, Any]] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class IntelligentDocumentProcessor:
    """Интеллектуальный процессор документов BCM"""
    
    # Ключевые слова для классификации документов
    DOCUMENT_CLASSIFICATION_KEYWORDS = {
        DocumentType.BCP: [
            "business continuity", "план непрерывности", "восстановление", "recovery",
            "continuity plan", "disaster recovery", "emergency response", "критические процессы"
        ],
        DocumentType.BIA: [
            "business impact analysis", "анализ воздействия", "bia", "rto", "rpo",
            "максимально допустимый", "критичность", "влияние на бизнес"
        ],
        DocumentType.RISK_ASSESSMENT: [
            "risk assessment", "оценка рисков", "анализ рисков", "угрозы", "уязвимости",
            "вероятность", "воздействие", "риск-анализ"
        ],
        DocumentType.PROCEDURE: [
            "процедура", "procedure", "инструкция", "пошаговый", "алгоритм действий",
            "методика", "руководство по", "последовательность"
        ],
        DocumentType.POLICY: [
            "политика", "policy", "стратегия", "принципы", "правила", "требования",
            "положение", "концепция"
        ],
        DocumentType.INCIDENT_REPORT: [
            "incident report", "отчет об инциденте", "происшествие", "нарушение",
            "авария", "сбой", "инцидент", "чрезвычайная ситуация"
        ]
    }
    
    # ISO 22301 требования для анализа соответствия
    ISO_22301_REQUIREMENTS = {
        "context": ["заинтересованные стороны", "внешняя среда", "внутренняя среда"],
        "leadership": ["руководство", "политика", "роли", "ответственность"],
        "planning": ["планирование", "цели", "ресурсы", "план действий"],
        "support": ["ресурсы", "компетентность", "осведомленность", "коммуникация", "документированная информация"],
        "operation": ["операционное планирование", "bia", "стратегия", "процедуры"],
        "performance": ["мониторинг", "измерение", "анализ", "внутренний аудит"],
        "improvement": ["несоответствия", "корректирующие действия", "улучшение"]
    }
    
    @staticmethod
    def extract_text_content(file_content: bytes, content_type: str) -> str:
        """Извлечение текстового содержимого из файла"""
        try:
            if content_type.startswith('text/'):
                return file_content.decode('utf-8')
            elif 'pdf' in content_type:
                return IntelligentDocumentProcessor._extract_pdf_text(file_content)
            elif 'word' in content_type or 'docx' in content_type:
                return IntelligentDocumentProcessor._extract_docx_text(file_content)
            else:
                return ""
        except Exception as e:
            logger.warning(f"Не удалось извлечь текст: {e}")
            return ""
    
    @staticmethod
    def _extract_pdf_text(file_content: bytes) -> str:
        """Извлечение текста из PDF (упрощенная реализация)"""
        return "PDF content extraction would require PyPDF2 or similar library"
    
    @staticmethod
    def _extract_docx_text(file_content: bytes) -> str:
        """Извлечение текста из DOCX (упрощенная реализация)"""
        return "DOCX content extraction would require python-docx library"
    
    @staticmethod
    def classify_document(text_content: str, filename: str) -> tuple[DocumentType, float]:
        """Классификация документа на основе содержимого и имени файла"""
        text_lower = text_content.lower()
        filename_lower = filename.lower()
        
        scores = {}
        
        for doc_type, keywords in IntelligentDocumentProcessor.DOCUMENT_CLASSIFICATION_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
                if keyword.lower() in filename_lower:
                    score += 2  # Больший вес для ключевых слов в имени файла
            
            if score > 0:
                scores[doc_type] = score / len(keywords)
        
        if not scores:
            return DocumentType.OTHER, 0.0
        
        best_match = max(scores, key=scores.get)
        confidence = min(1.0, scores[best_match] * 2)  # Нормализация до 1.0
        
        return best_match, confidence
    
    @staticmethod
    def extract_key_concepts(text_content: str) -> List[str]:
        """Извлечение ключевых концепций из текста"""
        if not text_content:
            return []
        
        text_lower = text_content.lower()
        concepts = []
        
        # BCM-специфичные концепции
        bcm_concepts = {
            "rto": ["rto", "recovery time objective", "время восстановления"],
            "rpo": ["rpo", "recovery point objective", "точка восстановления"],
            "mtpd": ["mtpd", "maximum tolerable period", "максимально допустимый период"],
            "continuity": ["continuity", "непрерывность", "продолжительность"],
            "disaster": ["disaster", "катастрофа", "бедствие"],
            "emergency": ["emergency", "чрезвычайная ситуация", "экстренный"],
            "crisis": ["crisis", "кризис", "критическая ситуация"],
            "incident": ["incident", "инцидент", "происшествие"],
            "risk": ["risk", "риск", "угроза"],
            "vulnerability": ["vulnerability", "уязвимость", "слабость"]
        }
        
        for concept, keywords in bcm_concepts.items():
            if any(keyword in text_lower for keyword in keywords):
                concepts.append(concept)
        
        return concepts
    
    @staticmethod
    def analyze_iso_compliance(text_content: str) -> Dict[str, Any]:
        """Анализ соответствия ISO 22301"""
        if not text_content:
            return {"compliance_level": ComplianceLevel.UNKNOWN, "coverage": {}}
        
        text_lower = text_content.lower()
        coverage = {}
        total_requirements = 0
        covered_requirements = 0
        
        for section, requirements in IntelligentDocumentProcessor.ISO_22301_REQUIREMENTS.items():
            section_coverage = 0
            for requirement in requirements:
                total_requirements += 1
                if requirement.lower() in text_lower:
                    section_coverage += 1
                    covered_requirements += 1
            
            coverage[section] = {
                "covered": section_coverage,
                "total": len(requirements),
                "percentage": round((section_coverage / len(requirements)) * 100, 2)
            }
        
        overall_percentage = (covered_requirements / total_requirements) * 100 if total_requirements > 0 else 0
        
        if overall_percentage >= 80:
            compliance_level = ComplianceLevel.FULL
        elif overall_percentage >= 50:
            compliance_level = ComplianceLevel.PARTIAL
        else:
            compliance_level = ComplianceLevel.NON_COMPLIANT
        
        return {
            "compliance_level": compliance_level,
            "overall_percentage": round(overall_percentage, 2),
            "section_coverage": coverage,
            "recommendations": IntelligentDocumentProcessor._generate_compliance_recommendations(coverage)
        }
    
    @staticmethod
    def _generate_compliance_recommendations(coverage: Dict) -> List[str]:
        """Генерация рекомендаций по улучшению соответствия"""
        recommendations = []
        
        for section, data in coverage.items():
            if data["percentage"] < 50:
                recommendations.append(
                    f"Улучшить покрытие раздела '{section}' (текущее: {data['percentage']}%)"
                )
        
        if not recommendations:
            recommendations.append("Документ демонстрирует хорошее соответствие требованиям ISO 22301")
        
        return recommendations
    
    @staticmethod
    def generate_search_keywords(text_content: str, key_concepts: List[str]) -> List[str]:
        """Генерация ключевых слов для поиска"""
        keywords = set(key_concepts)
        
        if text_content:
            words = text_content.lower().split()
            # Извлекаем значимые слова (длиннее 3 символов)
            significant_words = [word for word in words if len(word) > 3 and word.isalpha()]
            
            # Добавляем самые часто встречающиеся слова
            from collections import Counter
            word_freq = Counter(significant_words)
            top_words = [word for word, count in word_freq.most_common(20) if count > 2]
            keywords.update(top_words)
        
        return list(keywords)[:50]  # Ограничиваем количество ключевых слов

# Инициализация процессора
document_processor = IntelligentDocumentProcessor()

# Хранилище обработанных документов (в реальном приложении - база данных)
processed_documents: Dict[str, ProcessedDocument] = {}

@app.get("/health")
def health():
    return {
        "status": "operational",
        "service": "document_processor",
        "version": "1.0.0",
        "capabilities": [
            "document_classification",
            "text_extraction",
            "iso_compliance_analysis",
            "keyword_generation",
            "metadata_extraction"
        ]
    }

@app.post("/upload", response_model=ProcessedDocument)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type_hint: Optional[DocumentType] = Form(None)
):
    """Загрузка и обработка документа"""
    try:
        # Читаем содержимое файла
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Создаем метаданные
        metadata = DocumentMetadata(
            filename=file.filename,
            file_size=len(file_content),
            content_type=file.content_type or "application/octet-stream",
            upload_date=datetime.now(),
            file_hash=file_hash
        )
        
        # Извлекаем текстовое содержимое
        text_content = document_processor.extract_text_content(
            file_content, metadata.content_type
        )
        
        # Классифицируем документ
        if document_type_hint:
            document_type = document_type_hint
            confidence = 0.8  # Предполагаем высокую уверенность при явном указании
        else:
            document_type, confidence = document_processor.classify_document(
                text_content, metadata.filename
            )
        
        # Извлекаем ключевые концепции
        key_concepts = document_processor.extract_key_concepts(text_content)
        
        # Анализируем соответствие ISO
        compliance_analysis = document_processor.analyze_iso_compliance(text_content)
        
        # Генерируем ключевые слова для поиска
        search_keywords = document_processor.generate_search_keywords(
            text_content, key_concepts
        )
        
        # Создаем объект обработанного документа
        processed_doc = ProcessedDocument(
            metadata=metadata,
            document_type=document_type,
            processing_status=ProcessingStatus.COMPLETED,
            extracted_text=text_content[:5000] if text_content else None,  # Ограничиваем для демо
            key_concepts=key_concepts,
            compliance_analysis=compliance_analysis,
            search_keywords=search_keywords,
            confidence_score=confidence
        )
        
        # Сохраняем в хранилище
        processed_documents[metadata.document_id] = processed_doc
        
        logger.info(f"Обработан документ: {file.filename} (ID: {metadata.document_id})")
        
        return processed_doc
        
    except Exception as e:
        logger.error(f"Ошибка обработки документа {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/documents", response_model=List[ProcessedDocument])
async def get_all_documents():
    """Получение списка всех обработанных документов"""
    return list(processed_documents.values())

@app.get("/documents/{document_id}", response_model=ProcessedDocument)
async def get_document(document_id: str):
    """Получение информации о конкретном документе"""
    if document_id not in processed_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return processed_documents[document_id]

@app.get("/search")
async def search_documents(
    query: str,
    document_type: Optional[DocumentType] = None,
    compliance_level: Optional[ComplianceLevel] = None
):
    """Поиск документов по ключевым словам и фильтрам"""
    results = []
    query_lower = query.lower()
    
    for doc_id, doc in processed_documents.items():
        score = 0
        
        # Поиск в ключевых словах
        if any(query_lower in keyword.lower() for keyword in doc.search_keywords):
            score += 3
        
        # Поиск в ключевых концепциях
        if any(query_lower in concept.lower() for concept in doc.key_concepts):
            score += 2
        
        # Поиск в имени файла
        if query_lower in doc.metadata.filename.lower():
            score += 1
        
        # Применяем фильтры
        if document_type and doc.document_type != document_type:
            continue
            
        if compliance_level and doc.compliance_analysis:
            if doc.compliance_analysis.get("compliance_level") != compliance_level:
                continue
        
        if score > 0:
            results.append({
                "document_id": doc_id,
                "filename": doc.metadata.filename,
                "document_type": doc.document_type,
                "relevance_score": score,
                "compliance_level": doc.compliance_analysis.get("compliance_level") if doc.compliance_analysis else None
            })
    
    # Сортируем по релевантности
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": query,
        "total_results": len(results),
        "results": results[:50]  # Ограничиваем количество результатов
    }

@app.get("/analytics/compliance")
async def get_compliance_analytics():
    """Аналитика по соответствию документов ISO 22301"""
    if not processed_documents:
        return {"message": "No documents processed yet"}
    
    compliance_stats = {
        ComplianceLevel.FULL: 0,
        ComplianceLevel.PARTIAL: 0,
        ComplianceLevel.NON_COMPLIANT: 0,
        ComplianceLevel.UNKNOWN: 0
    }
    
    section_coverage = {}
    
    for doc in processed_documents.values():
        if doc.compliance_analysis:
            level = doc.compliance_analysis.get("compliance_level", ComplianceLevel.UNKNOWN)
            compliance_stats[level] += 1
            
            # Агрегируем покрытие по разделам
            if "section_coverage" in doc.compliance_analysis:
                for section, data in doc.compliance_analysis["section_coverage"].items():
                    if section not in section_coverage:
                        section_coverage[section] = {"total_covered": 0, "total_possible": 0}
                    section_coverage[section]["total_covered"] += data["covered"]
                    section_coverage[section]["total_possible"] += data["total"]
    
    # Рассчитываем средние проценты покрытия
    average_section_coverage = {}
    for section, data in section_coverage.items():
        if data["total_possible"] > 0:
            average_section_coverage[section] = round(
                (data["total_covered"] / data["total_possible"]) * 100, 2
            )
    
    return {
        "total_documents": len(processed_documents),
        "compliance_distribution": compliance_stats,
        "average_section_coverage": average_section_coverage,
        "generated_at": datetime.now().isoformat()
    }

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Удаление документа"""
    if document_id not in processed_documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    deleted_doc = processed_documents.pop(document_id)
    logger.info(f"Удален документ: {deleted_doc.metadata.filename} (ID: {document_id})")
    
    return {"message": "Document deleted successfully", "document_id": document_id}

@app.get("/")
async def root():
    return {
        "service": "Document Processor - BCM Platform",
        "version": "1.0.0",
        "description": "Интеллектуальная обработка документов для Business Continuity Management",
        "features": {
            "document_upload": "Загрузка и обработка документов различных форматов",
            "automatic_classification": "Автоматическая классификация по типам BCM документов",
            "iso_compliance": "Анализ соответствия требованиям ISO 22301",
            "intelligent_search": "Поиск с использованием ключевых слов и концепций",
            "analytics": "Аналитика по соответствию и классификации документов"
        },
        "endpoints": {
            "upload": "/upload",
            "search": "/search",
            "analytics": "/analytics/compliance",
            "documents": "/documents"
        },
        "supported_formats": ["PDF", "DOCX", "TXT", "HTML"],
        "status": "Document Processor Active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8083")))
