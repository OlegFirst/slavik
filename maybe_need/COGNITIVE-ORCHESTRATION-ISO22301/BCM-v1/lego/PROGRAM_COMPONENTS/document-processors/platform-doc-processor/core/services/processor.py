"""Main document processing logic"""

import asyncio
import logging
import time
from typing import Dict, Any
import json

from models import DocumentAnalysisResult, DocumentStatus, AnalysisEngine, ComplianceScore, ISOClause
from services.eventbus import EventBusService
from services.document_processor import DocumentProcessorService

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing orchestrator"""
    
    def __init__(self, eventbus_service: EventBusService, document_service: DocumentProcessorService):
        self.eventbus = eventbus_service
        self.document_service = document_service
        self.processing_tasks = {}  # Track ongoing processing tasks
        
    async def handle_document_uploaded(self, event_data: Dict[str, Any]):
        """Handle bcm.doc.uploaded event"""
        try:
            logger.info(f"Processing document upload event: {event_data}")
            
            tenant_id = event_data.get('tenant_id')
            document_id = event_data.get('data', {}).get('document_id')
            
            if not tenant_id or not document_id:
                logger.error("Missing tenant_id or document_id in event")
                return
            
            # Start document analysis
            await self._start_document_analysis(tenant_id, document_id, event_data)
            
        except Exception as e:
            logger.error(f"Error handling document upload event: {str(e)}")
    
    async def handle_evidence_uploaded(self, event_data: Dict[str, Any]):
        """Handle bcm.evidence.uploaded event (from portal)"""
        try:
            logger.info(f"Processing evidence upload event: {event_data}")
            
            tenant_id = event_data.get('tenant_id')
            document_data = event_data.get('data', {})
            
            # Convert evidence to document format
            converted_event = {
                'tenant_id': tenant_id,
                'data': {
                    'document_id': document_data.get('evidence_id'),
                    'filename': document_data.get('filename'),
                    'document_type': 'evidence',
                    'audit_id': document_data.get('audit_id'),
                    'user_id': document_data.get('user_id')
                }
            }
            
            await self.handle_document_uploaded(converted_event)
            
        except Exception as e:
            logger.error(f"Error handling evidence upload event: {str(e)}")
    
    async def _start_document_analysis(self, tenant_id: str, document_id: str, event_data: Dict[str, Any]):
        """Start document analysis process"""
        try:
            # Update document status to processing
            await self.document_service.update_document_status(
                document_id, tenant_id, DocumentStatus.PROCESSING
            )
            
            # Publish processing started event
            await self.eventbus.publish({
                'event_type': 'bcm.doc.processing_started',
                'tenant_id': tenant_id,
                'data': {
                    'document_id': document_id,
                    'status': 'processing'
                }
            })
            
            # Start analysis in background
            task_key = f"{tenant_id}:{document_id}"
            if task_key not in self.processing_tasks:
                task = asyncio.create_task(
                    self._analyze_document(tenant_id, document_id, event_data)
                )
                self.processing_tasks[task_key] = task
                
                # Clean up task when completed
                task.add_done_callback(lambda t: self.processing_tasks.pop(task_key, None))
            
        except Exception as e:
            logger.error(f"Error starting document analysis: {str(e)}")
            await self._handle_analysis_error(tenant_id, document_id, str(e))
    
    async def _analyze_document(self, tenant_id: str, document_id: str, event_data: Dict[str, Any]):
        """Perform document analysis"""
        start_time = time.time()
        
        try:
            # Get document content and metadata
            document_content = await self.document_service.get_document_content(document_id, tenant_id)
            document_metadata = await self.document_service.get_document_metadata(document_id, tenant_id)
            
            if not document_content or not document_metadata:
                raise Exception("Document content or metadata not found")
            
            # Perform content analysis
            content_analysis = await self._analyze_content(document_content, document_metadata)
            
            # Perform compliance analysis
            compliance_analysis = await self._analyze_compliance(document_content, document_metadata)
            
            # Create analysis result
            processing_time = time.time() - start_time
            analysis_result = DocumentAnalysisResult(
                document_id=document_id,
                tenant_id=tenant_id,
                status=DocumentStatus.ANALYZED,
                content_summary=content_analysis.get('summary'),
                word_count=content_analysis.get('word_count'),
                language=content_analysis.get('language', 'en'),
                compliance_score=compliance_analysis.get('score'),
                iso_clauses_found=compliance_analysis.get('clauses', []),
                readability_score=content_analysis.get('readability'),
                structure_score=content_analysis.get('structure_score'),
                key_terms=content_analysis.get('key_terms', []),
                processes=content_analysis.get('processes', []),
                risks=content_analysis.get('risks', []),
                controls=content_analysis.get('controls', []),
                analysis_engine=AnalysisEngine.LOCAL,
                processing_time=processing_time,
                confidence=content_analysis.get('confidence', 0.8)
            )
            
            # Store analysis result
            await self.document_service.store_analysis_result(analysis_result)
            
            # Update document status
            await self.document_service.update_document_status(
                document_id, tenant_id, DocumentStatus.ANALYZED
            )
            
            # Publish analysis completed event
            await self.eventbus.publish({
                'event_type': 'bcm.doc.analyzed',
                'tenant_id': tenant_id,
                'data': {
                    'document_id': document_id,
                    'compliance_score': compliance_analysis.get('score', {}).get('overall_score', 0.0),
                    'iso_clauses': [clause.clause_number for clause in compliance_analysis.get('clauses', [])],
                    'findings': compliance_analysis.get('score', {}).get('gaps', []),
                    'processing_time': processing_time,
                    'document_type': document_metadata.document_type,
                    'audit_id': document_metadata.audit_id
                }
            })
            
            logger.info(f"Document analysis completed for {document_id} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error analyzing document {document_id}: {str(e)}")
            await self._handle_analysis_error(tenant_id, document_id, str(e))
    
    async def _analyze_content(self, content: bytes, metadata) -> Dict[str, Any]:
        """Analyze document content"""
        try:
            # Convert content to text
            text_content = await self.document_service.extract_text(content, metadata.content_type)
            
            # Basic content analysis
            word_count = len(text_content.split())
            
            # Extract key terms using simple keyword extraction
            key_terms = self._extract_key_terms(text_content)
            
            # Identify business processes
            processes = self._identify_processes(text_content)
            
            # Identify risks
            risks = self._identify_risks(text_content)
            
            # Identify controls
            controls = self._identify_controls(text_content)
            
            # Calculate readability (simplified Flesch score)
            readability = self._calculate_readability(text_content)
            
            # Assess document structure
            structure_score = self._assess_structure(text_content)
            
            # Generate summary
            summary = self._generate_summary(text_content)
            
            return {
                'summary': summary,
                'word_count': word_count,
                'language': 'en',  # TODO: Implement language detection
                'readability': readability,
                'structure_score': structure_score,
                'key_terms': key_terms,
                'processes': processes,
                'risks': risks,
                'controls': controls,
                'confidence': 0.85
            }
            
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return {'confidence': 0.0}
    
    async def _analyze_compliance(self, content: bytes, metadata) -> Dict[str, Any]:
        """Analyze ISO 22301 compliance"""
        try:
            # Convert content to text
            text_content = await self.document_service.extract_text(content, metadata.content_type)
            
            # Load ISO 22301 clauses
            iso_clauses = await self._load_iso_clauses()
            
            # Analyze compliance for each clause
            clause_scores = {}
            found_clauses = []
            
            for clause in iso_clauses:
                score = self._calculate_clause_compliance(text_content, clause)
                clause_scores[clause['clause_number']] = score
                
                if score > 0.5:  # Threshold for considering clause present
                    found_clauses.append(ISOClause(
                        clause_number=clause['clause_number'],
                        title=clause['title'],
                        description=clause['description'],
                        requirements=clause.get('requirements', []),
                        keywords=clause.get('keywords', [])
                    ))
            
            # Calculate overall compliance score
            overall_score = sum(clause_scores.values()) / len(clause_scores) if clause_scores else 0.0
            coverage = len(found_clauses) / len(iso_clauses) if iso_clauses else 0.0
            
            # Identify gaps
            gaps = [
                clause['title'] for clause in iso_clauses 
                if clause_scores.get(clause['clause_number'], 0.0) < 0.3
            ]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(gaps, found_clauses)
            
            compliance_score = ComplianceScore(
                overall_score=overall_score,
                clause_scores=clause_scores,
                coverage=coverage,
                gaps=gaps,
                recommendations=recommendations
            )
            
            return {
                'score': compliance_score,
                'clauses': found_clauses
            }
            
        except Exception as e:
            logger.error(f"Error in compliance analysis: {str(e)}")
            return {'score': ComplianceScore(overall_score=0.0, coverage=0.0), 'clauses': []}
    
    async def _load_iso_clauses(self) -> list:
        """Load ISO 22301 clauses from configuration"""
        # Simplified ISO 22301 clauses - in production, load from file
        return [
            {
                'clause_number': '4.1',
                'title': 'Understanding the organization and its context',
                'description': 'Organization shall determine external and internal issues',
                'keywords': ['context', 'organization', 'external', 'internal', 'issues']
            },
            {
                'clause_number': '4.2',
                'title': 'Understanding the needs and expectations of interested parties',
                'description': 'Organization shall determine interested parties and their requirements',
                'keywords': ['interested parties', 'stakeholders', 'requirements', 'expectations']
            },
            {
                'clause_number': '4.3',
                'title': 'Determining the scope of the BCMS',
                'description': 'Organization shall determine boundaries and applicability',
                'keywords': ['scope', 'boundaries', 'applicability', 'BCMS']
            },
            {
                'clause_number': '4.4',
                'title': 'Business continuity management system',
                'description': 'Organization shall establish, implement, maintain and continually improve BCMS',
                'keywords': ['BCMS', 'establish', 'implement', 'maintain', 'improve']
            },
            {
                'clause_number': '8.2',
                'title': 'Business impact analysis and risk assessment',
                'description': 'Organization shall conduct BIA and risk assessment',
                'keywords': ['BIA', 'business impact analysis', 'risk assessment', 'impact', 'risk']
            },
            {
                'clause_number': '8.3',
                'title': 'Business continuity strategy',
                'description': 'Organization shall establish BC strategy',
                'keywords': ['strategy', 'business continuity', 'recovery', 'continuity']
            },
            {
                'clause_number': '8.4',
                'title': 'Business continuity procedures',
                'description': 'Organization shall establish BC procedures',
                'keywords': ['procedures', 'response', 'recovery', 'resumption', 'continuity']
            }
        ]
    
    def _calculate_clause_compliance(self, text: str, clause: Dict[str, Any]) -> float:
        """Calculate compliance score for a specific clause"""
        text_lower = text.lower()
        keywords = clause.get('keywords', [])
        
        if not keywords:
            return 0.0
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return min(matches / len(keywords), 1.0)
    
    def _extract_key_terms(self, text: str) -> list:
        """Extract key terms from text"""
        # Simplified key term extraction - in production, use NLP libraries
        bcm_terms = [
            'business continuity', 'disaster recovery', 'risk assessment',
            'impact analysis', 'recovery time', 'recovery point', 'MTPD',
            'RTO', 'RPO', 'incident', 'crisis', 'emergency', 'resilience'
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in bcm_terms if term in text_lower]
        return found_terms[:10]  # Return top 10
    
    def _identify_processes(self, text: str) -> list:
        """Identify business processes mentioned in text"""
        process_keywords = [
            'IT systems', 'human resources', 'finance', 'operations',
            'customer service', 'supply chain', 'manufacturing', 'sales'
        ]
        
        text_lower = text.lower()
        found_processes = [proc for proc in process_keywords if proc.lower() in text_lower]
        return found_processes
    
    def _identify_risks(self, text: str) -> list:
        """Identify risks mentioned in text"""
        risk_keywords = [
            'cyber attack', 'data breach', 'system failure', 'natural disaster',
            'fire', 'flood', 'pandemic', 'supplier failure', 'key person risk'
        ]
        
        text_lower = text.lower()
        found_risks = [risk for risk in risk_keywords if risk.lower() in text_lower]
        return found_risks
    
    def _identify_controls(self, text: str) -> list:
        """Identify controls mentioned in text"""
        control_keywords = [
            'backup', 'redundancy', 'monitoring', 'testing', 'training',
            'insurance', 'alternative site', 'vendor management'
        ]
        
        text_lower = text.lower()
        found_controls = [control for control in control_keywords if control.lower() in text_lower]
        return found_controls
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate simplified readability score"""
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simplified readability score (0-100, higher is more readable)
        score = max(0, 100 - (avg_words_per_sentence * 2))
        return min(score, 100.0)
    
    def _assess_structure(self, text: str) -> float:
        """Assess document structure quality"""
        # Check for headings, bullet points, numbering
        structure_indicators = ['#', '1.', '2.', '•', '-', 'Section', 'Chapter']
        
        indicator_count = sum(1 for indicator in structure_indicators if indicator in text)
        
        # Simple score based on structure indicators
        return min(indicator_count / 10.0, 1.0)
    
    def _generate_summary(self, text: str) -> str:
        """Generate simple document summary"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) <= 3:
            return text[:500] + "..." if len(text) > 500 else text
        
        # Return first few sentences as summary
        summary_sentences = sentences[:3]
        return '. '.join(summary_sentences) + '.'
    
    def _generate_recommendations(self, gaps: list, found_clauses: list) -> list:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        if gaps:
            recommendations.append(f"Address missing compliance areas: {', '.join(gaps[:3])}")
        
        if len(found_clauses) < 5:
            recommendations.append("Consider adding more detailed procedures and controls")
        
        recommendations.append("Regular review and update of documentation recommended")
        
        return recommendations
    
    async def _handle_analysis_error(self, tenant_id: str, document_id: str, error_message: str):
        """Handle analysis error"""
        try:
            # Update document status to failed
            await self.document_service.update_document_status(
                document_id, tenant_id, DocumentStatus.FAILED
            )
            
            # Publish error event
            await self.eventbus.publish({
                'event_type': 'bcm.doc.analysis_failed',
                'tenant_id': tenant_id,
                'data': {
                    'document_id': document_id,
                    'error': error_message,
                    'status': 'failed'
                }
            })
            
        except Exception as e:
            logger.error(f"Error handling analysis error: {str(e)}")
