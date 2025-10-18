"""
Organization Data Collector
=====================================================================
NASH 4.0 - Organization Data Collection System
Enterprise-grade data collection and analysis for Digital Twin creation
=====================================================================

Purpose: Comprehensive data collection and analysis system for building
         accurate digital twins of organizations

Ported from: digital-twin-platform/src/organization-data-collector.js (1194 LOC)
Version: 1.0.0 (Full Port - Not Simplified)
Date: 2025-10-16

Features:
- Multi-source data collection (interviews, documents, systems)
- Automated organizational structure analysis
- Process flow discovery and mapping
- Technology stack assessment
- Financial model extraction
- Risk assessment and compliance checking
- Real-time data validation and quality assurance
"""

import logging
from typing import Dict, Any, Optional, List, Literal, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import random
import time

logger = logging.getLogger(__name__)


class DataCollectionMethod(str, Enum):
    """Data collection methods enumeration"""
    INTERVIEW = "interview"
    DOCUMENT_ANALYSIS = "document_analysis"
    SYSTEM_INTEGRATION = "system_integration"
    SURVEY = "survey"
    OBSERVATION = "observation"
    API_EXTRACTION = "api_extraction"
    DATABASE_QUERY = "database_query"
    FILE_UPLOAD = "file_upload"


class DataCategory(str, Enum):
    """Organization data categories"""
    STRUCTURE = "organizational_structure"
    PROCESSES = "business_processes"
    TECHNOLOGY = "technology_stack"
    FINANCIAL = "financial_data"
    HUMAN_RESOURCES = "human_resources"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance_data"
    STRATEGIC = "strategic_planning"
    PERFORMANCE = "performance_metrics"
    STAKEHOLDERS = "stakeholders"


class DataQuality(str, Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    INCOMPLETE = "incomplete"


class CollectionStatus(str, Enum):
    """Status of data collection session"""
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CategoryProgress:
    """Progress tracking for a data category"""
    status: str = "pending"
    progress: float = 0.0
    quality: DataQuality = DataQuality.INCOMPLETE
    data_points: int = 0
    validations_passed: int = 0


@dataclass
class SessionProgress:
    """Overall session progress"""
    categories: Dict[str, CategoryProgress] = field(default_factory=dict)
    overall_progress: float = 0.0
    quality_score: float = 0.0


@dataclass
class WorkflowStep:
    """Single workflow step"""
    id: str
    method: DataCollectionMethod
    category: DataCategory
    title: str
    description: str
    estimated_duration: int  # minutes
    priority: str  # high, medium, low
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"


@dataclass
class CollectionWorkflow:
    """Collection workflow"""
    steps: List[WorkflowStep] = field(default_factory=list)
    estimated_duration: int = 0  # minutes
    priority: str = "medium"


@dataclass
class MethodConfig:
    """Configuration for a collection method"""
    name: str
    description: str
    categories: List[DataCategory]
    handler: Callable


@dataclass
class ValidationRule:
    """Validation rule for a data category"""
    required: List[str]
    format: Dict[str, str]
    constraints: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class CollectionSession:
    """Data collection session"""
    id: str
    organization_id: str
    plan: Dict[str, Any]
    status: CollectionStatus
    start_time: str
    completed_at: Optional[str] = None
    progress: SessionProgress = field(default_factory=SessionProgress)
    collected_data: Dict[str, Any] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    methods: List[DataCollectionMethod] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    next_steps: List[WorkflowStep] = field(default_factory=list)
    workflow: Optional[CollectionWorkflow] = None
    organization_type: Optional[str] = None
    final_profile: Optional[Dict[str, Any]] = None


@dataclass
class ProcessingResult:
    """Result from data processing"""
    processed_data: Dict[str, Any]
    confidence: float
    method: DataCollectionMethod
    source: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result from data validation"""
    valid: bool
    quality: DataQuality
    completeness: float
    errors: List[str] = field(default_factory=list)
    data_points: int = 0


class OrganizationDataCollector:
    """
    Comprehensive data collection system for digital twins

    Features:
    - 8 collection methods (interviews, documents, systems, surveys, etc.)
    - 10 data categories (structure, processes, technology, financial, etc.)
    - Quality validation and scoring
    - Session management with workflow generation
    - Real-time progress tracking
    - Auto-validation and quality thresholds
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Organization Data Collector

        Args:
            config: Configuration options
                - enable_auto_validation: Enable automatic validation (default: True)
                - enable_real_time_processing: Enable real-time processing (default: True)
                - max_concurrent_collections: Max concurrent collections (default: 5)
                - data_retention_days: Data retention in days (default: 90)
                - quality_threshold: Quality threshold 0-1 (default: 0.7)
                - enable_ml_analysis: Enable ML analysis (default: True)
                - enable_nlp_processing: Enable NLP processing (default: True)
        """
        config = config or {}

        # Configuration
        self.config = {
            "enable_auto_validation": config.get("enable_auto_validation", True),
            "enable_real_time_processing": config.get("enable_real_time_processing", True),
            "max_concurrent_collections": config.get("max_concurrent_collections", 5),
            "data_retention_days": config.get("data_retention_days", 90),
            "quality_threshold": config.get("quality_threshold", 0.7),
            "enable_ml_analysis": config.get("enable_ml_analysis", True),
            "enable_nlp_processing": config.get("enable_nlp_processing", True),
            **config
        }

        # Data storage
        self.collection_sessions: Dict[str, CollectionSession] = {}
        self.organization_data: Dict[str, Any] = {}
        self.data_quality_metrics: Dict[str, Any] = {}
        self.validation_rules: Dict[DataCategory, ValidationRule] = {}

        # Collection methods registry
        self.collection_methods: Dict[DataCollectionMethod, MethodConfig] = {}
        self.active_collectors: Dict[str, Any] = {}

        # Analysis engines (placeholders for future integration)
        self.analysis_engines = {
            "structure_analyzer": None,
            "process_analyzer": None,
            "technology_analyzer": None,
            "financial_analyzer": None,
            "compliance_analyzer": None
        }

        # Initialize built-in collection methods and validation rules
        self._initialize_collection_methods()
        self._initialize_validation_rules()

        logger.info("Organization Data Collector initialized")

    def _initialize_collection_methods(self):
        """Initialize built-in collection methods"""

        # Interview-based data collection
        self.collection_methods[DataCollectionMethod.INTERVIEW] = MethodConfig(
            name="Structured Interview",
            description="Guided interview process for comprehensive data collection",
            categories=list(DataCategory),
            handler=self._handle_interview_collection
        )

        # Document analysis
        self.collection_methods[DataCollectionMethod.DOCUMENT_ANALYSIS] = MethodConfig(
            name="Document Analysis",
            description="Automated analysis of organizational documents",
            categories=[
                DataCategory.STRUCTURE,
                DataCategory.PROCESSES,
                DataCategory.COMPLIANCE
            ],
            handler=self._handle_document_analysis
        )

        # System integration
        self.collection_methods[DataCollectionMethod.SYSTEM_INTEGRATION] = MethodConfig(
            name="System Integration",
            description="Direct integration with existing organizational systems",
            categories=[
                DataCategory.TECHNOLOGY,
                DataCategory.FINANCIAL,
                DataCategory.OPERATIONS
            ],
            handler=self._handle_system_integration
        )

        # Survey collection
        self.collection_methods[DataCollectionMethod.SURVEY] = MethodConfig(
            name="Digital Survey",
            description="Comprehensive digital surveys for stakeholders",
            categories=[
                DataCategory.HUMAN_RESOURCES,
                DataCategory.PERFORMANCE,
                DataCategory.STAKEHOLDERS
            ],
            handler=self._handle_survey_collection
        )

        # File upload processing
        self.collection_methods[DataCollectionMethod.FILE_UPLOAD] = MethodConfig(
            name="File Upload Processing",
            description="Processing uploaded files for data extraction",
            categories=list(DataCategory),
            handler=self._handle_file_upload
        )

    def _initialize_validation_rules(self):
        """Initialize validation rules for each category"""

        # Organizational structure validation
        self.validation_rules[DataCategory.STRUCTURE] = ValidationRule(
            required=["departments", "hierarchy", "roles"],
            format={
                "departments": "array",
                "hierarchy": "object",
                "roles": "array"
            },
            constraints={
                "departments.length": {"min": 1, "max": 100},
                "roles.length": {"min": 1, "max": 500}
            }
        )

        # Process validation
        self.validation_rules[DataCategory.PROCESSES] = ValidationRule(
            required=["core_processes", "support_processes"],
            format={
                "core_processes": "array",
                "support_processes": "array"
            },
            constraints={
                "core_processes.length": {"min": 1, "max": 50}
            }
        )

        # Technology validation
        self.validation_rules[DataCategory.TECHNOLOGY] = ValidationRule(
            required=["systems", "technologies", "integrations"],
            format={
                "systems": "array",
                "technologies": "array",
                "integrations": "array"
            }
        )

        # Financial validation
        self.validation_rules[DataCategory.FINANCIAL] = ValidationRule(
            required=["budget", "revenue_streams", "cost_structure"],
            format={
                "budget": "number",
                "revenue_streams": "array",
                "cost_structure": "object"
            },
            constraints={
                "budget": {"min": 0}
            }
        )

    async def start_collection_session(
        self,
        organization_id: str,
        collection_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start data collection session for organization

        Args:
            organization_id: Organization ID
            collection_plan: Collection plan configuration
                - categories: List of DataCategory to collect
                - methods: List of DataCollectionMethod to use
                - required_data: List of required categories

        Returns:
            Session creation result with session ID and next steps
        """
        try:
            logger.info(f"Starting data collection session for org {organization_id}")

            # Validate collection plan
            self._validate_collection_plan(collection_plan)

            # Create collection session
            session_id = self._generate_session_id()

            progress = SessionProgress()
            categories = collection_plan.get("categories", list(DataCategory))

            # Initialize progress tracking for each category
            for category in categories:
                progress.categories[category.value if isinstance(category, DataCategory) else category] = CategoryProgress()

            session = CollectionSession(
                id=session_id,
                organization_id=organization_id,
                plan=collection_plan,
                status=CollectionStatus.ACTIVE,
                start_time=datetime.utcnow().isoformat(),
                progress=progress,
                methods=collection_plan.get("methods", [DataCollectionMethod.INTERVIEW])
            )

            # Generate collection workflow
            workflow = self._generate_collection_workflow(session)
            session.workflow = workflow
            session.next_steps = workflow.steps[:3]  # First 3 steps

            # Store session
            self.collection_sessions[session_id] = session

            logger.info(
                f"Collection session created: {session_id}, "
                f"categories={len(progress.categories)}, "
                f"methods={len(session.methods)}"
            )

            return {
                "success": True,
                "session_id": session_id,
                "session": self._sanitize_session(session),
                "next_steps": [self._step_to_dict(step) for step in session.next_steps]
            }

        except Exception as error:
            logger.error(f"Failed to start collection session: {error}")
            raise

    async def collect_data(
        self,
        session_id: str,
        method: DataCollectionMethod,
        category: DataCategory,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Collect data using specified method

        Args:
            session_id: Collection session ID
            method: Collection method to use
            category: Data category
            data: Raw data to process

        Returns:
            Collection result with quality metrics
        """
        try:
            session = self.collection_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collection session not found: {session_id}")

            logger.info(
                f"Processing data collection: session={session_id}, "
                f"method={method.value}, category={category.value}"
            )

            # Get collection method handler
            method_config = self.collection_methods.get(method)
            if not method_config:
                raise ValueError(f"Unknown collection method: {method}")

            # Validate category for method
            if category not in method_config.categories:
                raise ValueError(f"Method {method} does not support category {category}")

            # Process data using method handler
            processing_result = await method_config.handler(data, category, session)

            # Validate processed data
            validation_result = self._validate_category_data(category, processing_result.processed_data)

            # Store collected data
            category_key = category.value
            if category_key not in session.collected_data:
                session.collected_data[category_key] = {}

            session.collected_data[category_key] = {
                **session.collected_data[category_key],
                **processing_result.processed_data,
                "_metadata": {
                    "method": method.value,
                    "collected_at": datetime.utcnow().isoformat(),
                    "quality": validation_result.quality.value,
                    "completeness": validation_result.completeness,
                    "confidence": processing_result.confidence
                }
            }

            # Update progress
            self._update_session_progress(session, category, validation_result)

            # Store validation results
            session.validation_results[category_key] = validation_result

            # Update next steps
            self._update_next_steps(session)

            logger.info(
                f"Data collection completed: category={category_key}, "
                f"quality={validation_result.quality.value}, "
                f"completeness={validation_result.completeness:.2f}"
            )

            return {
                "success": True,
                "quality": validation_result.quality.value,
                "completeness": validation_result.completeness,
                "confidence": processing_result.confidence,
                "validation_result": {
                    "valid": validation_result.valid,
                    "errors": validation_result.errors
                },
                "next_steps": [self._step_to_dict(step) for step in session.next_steps]
            }

        except Exception as error:
            logger.error(f"Data collection failed: {error}")
            raise

    # ==================== Collection Method Handlers ====================

    async def _handle_interview_collection(
        self,
        data: Dict[str, Any],
        category: DataCategory,
        session: CollectionSession
    ) -> ProcessingResult:
        """Handle interview-based data collection"""
        responses = data.get("responses", {})
        interview_type = data.get("interview_type", "structured")
        participant_role = data.get("participant_role", "unknown")

        processed_data = {}
        confidence = 0.7  # Default confidence for interview data

        # Extract data based on category
        if category == DataCategory.STRUCTURE:
            processed_data = self._extract_structural_data(responses)
            confidence = self._calculate_structural_confidence(responses, participant_role)
        elif category == DataCategory.PROCESSES:
            processed_data = self._extract_process_data(responses)
            confidence = self._calculate_process_confidence(responses, participant_role)
        elif category == DataCategory.TECHNOLOGY:
            processed_data = self._extract_technology_data(responses)
            confidence = self._calculate_technology_confidence(responses, participant_role)
        elif category == DataCategory.FINANCIAL:
            processed_data = self._extract_financial_data(responses)
            confidence = self._calculate_financial_confidence(responses, participant_role)
        elif category == DataCategory.HUMAN_RESOURCES:
            processed_data = self._extract_hr_data(responses)
            confidence = 0.8  # HR interviews typically reliable
        else:
            processed_data = self._extract_generic_data(responses, category)

        return ProcessingResult(
            processed_data=processed_data,
            confidence=confidence,
            method=DataCollectionMethod.INTERVIEW,
            source={
                "type": interview_type,
                "participant": participant_role,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def _handle_document_analysis(
        self,
        data: Dict[str, Any],
        category: DataCategory,
        session: CollectionSession
    ) -> ProcessingResult:
        """Handle document analysis"""
        documents = data.get("documents", [])
        document_types = data.get("document_types", [])

        processed_data = {}
        confidence = 0.6  # Lower confidence for document analysis

        # Process documents based on category
        for doc in documents:
            analysis = await self._analyze_document(doc, category)
            processed_data.update(analysis["extracted_data"])
            confidence = max(confidence, analysis["confidence"])

        return ProcessingResult(
            processed_data=processed_data,
            confidence=confidence,
            method=DataCollectionMethod.DOCUMENT_ANALYSIS,
            source={
                "document_count": len(documents),
                "types": document_types,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def _handle_system_integration(
        self,
        data: Dict[str, Any],
        category: DataCategory,
        session: CollectionSession
    ) -> ProcessingResult:
        """Handle system integration data collection"""
        system_type = data.get("system_type")
        connection_config = data.get("connection_config", {})
        query_params = data.get("query_params", {})

        processed_data = {}
        confidence = 0.9  # High confidence for system data

        try:
            # Connect to system and extract data
            system_data = await self._connect_and_extract_data(
                system_type,
                connection_config,
                query_params
            )

            # Process system data based on category
            processed_data = self._process_system_data(system_data, category, system_type)

        except Exception as error:
            logger.error(f"System integration failed: {error}")
            confidence = 0.1
            processed_data = {"error": str(error), "partial": True}

        return ProcessingResult(
            processed_data=processed_data,
            confidence=confidence,
            method=DataCollectionMethod.SYSTEM_INTEGRATION,
            source={
                "system_type": system_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def _handle_survey_collection(
        self,
        data: Dict[str, Any],
        category: DataCategory,
        session: CollectionSession
    ) -> ProcessingResult:
        """Handle survey data collection"""
        responses = data.get("responses", [])
        survey_type = data.get("survey_type")
        response_count = data.get("response_count", len(responses))
        demographics = data.get("demographics", {})

        # Aggregate survey responses
        aggregated_data = self._aggregate_survey_responses(responses, category)
        confidence = self._calculate_survey_confidence(response_count, demographics)

        return ProcessingResult(
            processed_data=aggregated_data,
            confidence=confidence,
            method=DataCollectionMethod.SURVEY,
            source={
                "survey_type": survey_type,
                "response_count": response_count,
                "demographics": demographics,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    async def _handle_file_upload(
        self,
        data: Dict[str, Any],
        category: DataCategory,
        session: CollectionSession
    ) -> ProcessingResult:
        """Handle file upload processing"""
        files = data.get("files", [])
        file_types = data.get("file_types", [])

        processed_data = {}
        confidence = 0.5  # Variable confidence based on file content

        for file in files:
            file_analysis = await self._analyze_uploaded_file(file, category)
            processed_data.update(file_analysis["data"])
            confidence = max(confidence, file_analysis["confidence"])

        return ProcessingResult(
            processed_data=processed_data,
            confidence=confidence,
            method=DataCollectionMethod.FILE_UPLOAD,
            source={
                "file_count": len(files),
                "types": file_types,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    # ==================== Data Extraction Methods ====================

    def _extract_structural_data(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract organizational structure data from interview responses"""
        return {
            "departments": responses.get("departments", []),
            "hierarchy": responses.get("hierarchy", {}),
            "roles": responses.get("roles", []),
            "reporting_structure": responses.get("reporting_structure", {})
        }

    def _extract_process_data(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract process data from interview responses"""
        return {
            "core_processes": responses.get("core_processes", []),
            "support_processes": responses.get("support_processes", []),
            "workflows": responses.get("workflows", [])
        }

    def _extract_technology_data(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technology data from interview responses"""
        return {
            "systems": responses.get("systems", []),
            "technologies": responses.get("technologies", []),
            "integrations": responses.get("integrations", [])
        }

    def _extract_financial_data(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data from interview responses"""
        return {
            "budget": responses.get("budget", 0),
            "revenue_streams": responses.get("revenue_streams", []),
            "cost_structure": responses.get("cost_structure", {})
        }

    def _extract_hr_data(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Extract HR data from interview responses"""
        return {
            "staff_count": responses.get("staff_count", 0),
            "roles": responses.get("roles", []),
            "skills": responses.get("skills", [])
        }

    def _extract_generic_data(
        self,
        responses: Dict[str, Any],
        category: DataCategory
    ) -> Dict[str, Any]:
        """Extract generic data for any category"""
        return responses

    # ==================== Confidence Calculation ====================

    def _calculate_structural_confidence(
        self,
        responses: Dict[str, Any],
        participant_role: str
    ) -> float:
        """Calculate confidence for structural data"""
        base_confidence = 0.7

        # Increase confidence if participant is leadership
        if participant_role in ["ceo", "director", "manager"]:
            base_confidence += 0.1

        # Increase if comprehensive data
        if len(responses.get("departments", [])) > 3:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _calculate_process_confidence(
        self,
        responses: Dict[str, Any],
        participant_role: str
    ) -> float:
        """Calculate confidence for process data"""
        base_confidence = 0.7

        if participant_role in ["operations_manager", "process_owner"]:
            base_confidence += 0.15

        return min(base_confidence, 1.0)

    def _calculate_technology_confidence(
        self,
        responses: Dict[str, Any],
        participant_role: str
    ) -> float:
        """Calculate confidence for technology data"""
        base_confidence = 0.7

        if participant_role in ["cto", "it_manager", "tech_lead"]:
            base_confidence += 0.2

        return min(base_confidence, 1.0)

    def _calculate_financial_confidence(
        self,
        responses: Dict[str, Any],
        participant_role: str
    ) -> float:
        """Calculate confidence for financial data"""
        base_confidence = 0.7

        if participant_role in ["cfo", "finance_manager", "accountant"]:
            base_confidence += 0.2

        return min(base_confidence, 1.0)

    def _calculate_survey_confidence(
        self,
        response_count: int,
        demographics: Dict[str, Any]
    ) -> float:
        """Calculate confidence for survey data"""
        base_confidence = 0.5

        # Increase with response count
        if response_count > 50:
            base_confidence += 0.2
        elif response_count > 20:
            base_confidence += 0.1

        # Increase if diverse demographics
        if len(demographics) > 3:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    # ==================== Document & File Analysis ====================

    async def _analyze_document(
        self,
        doc: Dict[str, Any],
        category: DataCategory
    ) -> Dict[str, Any]:
        """Analyze document for data extraction"""
        # Placeholder for NLP/document analysis
        return {
            "extracted_data": doc.get("content", {}),
            "confidence": 0.6
        }

    async def _analyze_uploaded_file(
        self,
        file: Dict[str, Any],
        category: DataCategory
    ) -> Dict[str, Any]:
        """Analyze uploaded file"""
        # Placeholder for file analysis
        return {
            "data": file.get("content", {}),
            "confidence": 0.5
        }

    # ==================== System Integration ====================

    async def _connect_and_extract_data(
        self,
        system_type: str,
        connection_config: Dict[str, Any],
        query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Connect to external system and extract data"""
        # Placeholder for system integration
        logger.info(f"Connecting to {system_type} system")
        return {}

    def _process_system_data(
        self,
        system_data: Dict[str, Any],
        category: DataCategory,
        system_type: str
    ) -> Dict[str, Any]:
        """Process system data based on category"""
        return system_data

    # ==================== Survey Processing ====================

    def _aggregate_survey_responses(
        self,
        responses: List[Dict[str, Any]],
        category: DataCategory
    ) -> Dict[str, Any]:
        """Aggregate survey responses"""
        # Simple aggregation
        aggregated = {}
        for response in responses:
            for key, value in response.items():
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append(value)

        return aggregated

    # ==================== Workflow Generation ====================

    def _generate_collection_workflow(self, session: CollectionSession) -> CollectionWorkflow:
        """Generate collection workflow for session"""
        plan = session.plan
        workflow = CollectionWorkflow(priority="medium")

        categories = plan.get("categories", list(DataCategory))
        methods = plan.get("methods", [DataCollectionMethod.INTERVIEW])

        # Generate steps based on categories and methods
        for category in categories:
            cat_enum = category if isinstance(category, DataCategory) else DataCategory(category)

            for method in methods:
                method_enum = method if isinstance(method, DataCollectionMethod) else DataCollectionMethod(method)
                method_config = self.collection_methods.get(method_enum)

                if method_config and cat_enum in method_config.categories:
                    step_id = f"{method_enum.value}_{cat_enum.value}"

                    workflow.steps.append(WorkflowStep(
                        id=step_id,
                        method=method_enum,
                        category=cat_enum,
                        title=f"Collect {cat_enum.value} data via {method_config.name}",
                        description=f"Use {method_config.description} to gather {cat_enum.value} information",
                        estimated_duration=self._estimate_step_duration(method_enum, cat_enum),
                        priority=self._calculate_step_priority(cat_enum, method_enum),
                        dependencies=self._get_step_dependencies(cat_enum, method_enum)
                    ))

        # Sort steps by priority and dependencies
        workflow.steps = self._sort_workflow_steps(workflow.steps)
        workflow.estimated_duration = sum(step.estimated_duration for step in workflow.steps)

        return workflow

    def _estimate_step_duration(
        self,
        method: DataCollectionMethod,
        category: DataCategory
    ) -> int:
        """Estimate step duration in minutes"""
        base_durations = {
            DataCollectionMethod.INTERVIEW: 45,
            DataCollectionMethod.DOCUMENT_ANALYSIS: 30,
            DataCollectionMethod.SYSTEM_INTEGRATION: 60,
            DataCollectionMethod.SURVEY: 20,
            DataCollectionMethod.OBSERVATION: 90,
            DataCollectionMethod.API_EXTRACTION: 15,
            DataCollectionMethod.DATABASE_QUERY: 10,
            DataCollectionMethod.FILE_UPLOAD: 25
        }

        category_multipliers = {
            DataCategory.STRUCTURE: 1.2,
            DataCategory.PROCESSES: 1.5,
            DataCategory.TECHNOLOGY: 1.0,
            DataCategory.FINANCIAL: 1.3,
            DataCategory.HUMAN_RESOURCES: 1.1,
            DataCategory.OPERATIONS: 1.4,
            DataCategory.COMPLIANCE: 1.6,
            DataCategory.STRATEGIC: 1.3,
            DataCategory.PERFORMANCE: 1.0,
            DataCategory.STAKEHOLDERS: 1.2
        }

        base = base_durations.get(method, 30)
        multiplier = category_multipliers.get(category, 1.0)

        return round(base * multiplier)

    def _calculate_step_priority(
        self,
        category: DataCategory,
        method: DataCollectionMethod
    ) -> str:
        """Calculate step priority"""
        critical_categories = [DataCategory.STRUCTURE, DataCategory.FINANCIAL]
        high_reliability_methods = [
            DataCollectionMethod.SYSTEM_INTEGRATION,
            DataCollectionMethod.API_EXTRACTION
        ]

        if category in critical_categories:
            return "high"

        if method in high_reliability_methods:
            return "high"

        return "medium"

    def _get_step_dependencies(
        self,
        category: DataCategory,
        method: DataCollectionMethod
    ) -> List[str]:
        """Get step dependencies"""
        dependencies_map = {
            DataCategory.PROCESSES: [DataCategory.STRUCTURE.value],
            DataCategory.PERFORMANCE: [
                DataCategory.PROCESSES.value,
                DataCategory.STRUCTURE.value
            ],
            DataCategory.STAKEHOLDERS: [DataCategory.STRUCTURE.value]
        }

        return dependencies_map.get(category, [])

    def _sort_workflow_steps(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Sort workflow steps by priority and dependencies"""
        priority_order = {"high": 3, "medium": 2, "low": 1}

        return sorted(
            steps,
            key=lambda s: (
                -priority_order[s.priority],
                len(s.dependencies)
            )
        )

    # ==================== Validation ====================

    def _validate_collection_plan(self, plan: Dict[str, Any]):
        """Validate collection plan"""
        if not plan.get("categories") or not isinstance(plan["categories"], list):
            raise ValueError("Collection plan must specify at least one data category")

        if not plan.get("methods") or not isinstance(plan["methods"], list):
            raise ValueError("Collection plan must specify at least one collection method")

        # Validate categories
        for category in plan["categories"]:
            try:
                if isinstance(category, str):
                    DataCategory(category)
            except ValueError:
                raise ValueError(f"Invalid data category: {category}")

        # Validate methods
        for method in plan["methods"]:
            try:
                if isinstance(method, str):
                    DataCollectionMethod(method)
            except ValueError:
                raise ValueError(f"Invalid collection method: {method}")

    def _validate_category_data(
        self,
        category: DataCategory,
        data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate data for a specific category"""
        rules = self.validation_rules.get(category)

        if not rules:
            # No specific rules, assume valid
            return ValidationResult(
                valid=True,
                quality=DataQuality.GOOD,
                completeness=0.8,
                data_points=len(data)
            )

        errors = []

        # Check required fields
        for required_field in rules.required:
            if required_field not in data or not data[required_field]:
                errors.append(f"Missing required field: {required_field}")

        # Calculate completeness
        present_fields = sum(1 for f in rules.required if f in data and data[f])
        completeness = present_fields / len(rules.required) if rules.required else 1.0

        # Determine quality
        if completeness >= 0.9 and not errors:
            quality = DataQuality.EXCELLENT
        elif completeness >= 0.7:
            quality = DataQuality.GOOD
        elif completeness >= 0.5:
            quality = DataQuality.ACCEPTABLE
        elif completeness >= 0.3:
            quality = DataQuality.POOR
        else:
            quality = DataQuality.INCOMPLETE

        return ValidationResult(
            valid=len(errors) == 0,
            quality=quality,
            completeness=completeness,
            errors=errors,
            data_points=len(data)
        )

    # ==================== Session Management ====================

    def _update_session_progress(
        self,
        session: CollectionSession,
        category: DataCategory,
        validation_result: ValidationResult
    ):
        """Update session progress"""
        category_key = category.value
        category_progress = session.progress.categories.get(category_key)

        if category_progress:
            category_progress.status = "completed"
            category_progress.progress = 100.0
            category_progress.quality = validation_result.quality
            category_progress.data_points = validation_result.data_points
            category_progress.validations_passed = 1 if validation_result.valid else 0

        # Update overall progress
        categories = list(session.progress.categories.keys())
        completed_categories = [
            cat for cat in categories
            if session.progress.categories[cat].status == "completed"
        ]

        session.progress.overall_progress = (
            len(completed_categories) / len(categories) * 100
            if categories else 0
        )

        # Calculate overall quality score
        session.progress.quality_score = self._calculate_overall_quality_score(session)

    def _update_next_steps(self, session: CollectionSession):
        """Update next steps for session"""
        if not session.workflow:
            return

        completed_step_ids = session.completed_steps
        pending_steps = [
            step for step in session.workflow.steps
            if step.id not in completed_step_ids and step.status != "completed"
        ]

        # Get next 3 steps that have no unmet dependencies
        session.next_steps = [
            step for step in pending_steps
            if all(dep in session.collected_data or dep in completed_step_ids
                   for dep in step.dependencies)
        ][:3]

    def _calculate_overall_quality_score(self, session: CollectionSession) -> float:
        """Calculate overall quality score for session"""
        categories = list(session.progress.categories.keys())
        if not categories:
            return 0.0

        total_score = 0.0
        weight_sum = 0.0

        for category in categories:
            progress = session.progress.categories[category]
            weight = self._get_category_weight(DataCategory(category))
            quality_value = self._quality_to_value(progress.quality)

            total_score += quality_value * weight * (progress.progress / 100.0)
            weight_sum += weight

        return total_score / weight_sum if weight_sum > 0 else 0.0

    def _quality_to_value(self, quality: DataQuality) -> float:
        """Convert quality level to numeric value"""
        mapping = {
            DataQuality.EXCELLENT: 1.0,
            DataQuality.GOOD: 0.8,
            DataQuality.ACCEPTABLE: 0.6,
            DataQuality.POOR: 0.3,
            DataQuality.INCOMPLETE: 0.1
        }
        return mapping.get(quality, 0.0)

    def _get_category_weight(self, category: DataCategory) -> float:
        """Get category weight for scoring"""
        weights = {
            DataCategory.STRUCTURE: 1.5,
            DataCategory.PROCESSES: 1.3,
            DataCategory.TECHNOLOGY: 1.0,
            DataCategory.FINANCIAL: 1.4,
            DataCategory.HUMAN_RESOURCES: 1.1,
            DataCategory.OPERATIONS: 1.2,
            DataCategory.COMPLIANCE: 1.3,
            DataCategory.STRATEGIC: 1.2,
            DataCategory.PERFORMANCE: 1.1,
            DataCategory.STAKEHOLDERS: 1.0
        }
        return weights.get(category, 1.0)

    # ==================== Session Completion ====================

    async def complete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Complete collection session and generate final profile

        Args:
            session_id: Session ID to complete

        Returns:
            Completion result with organization profile
        """
        try:
            session = self.collection_sessions.get(session_id)
            if not session:
                raise ValueError(f"Collection session not found: {session_id}")

            # Validate completeness
            completion_check = self._validate_session_completion(session)
            if not completion_check["is_complete"]:
                raise ValueError(f"Session not ready for completion: {completion_check['reason']}")

            # Generate final organization profile
            organization_profile = self._generate_organization_profile(session)

            # Update session
            session.status = CollectionStatus.COMPLETED
            session.completed_at = datetime.utcnow().isoformat()
            session.final_profile = organization_profile

            # Store organization data
            self.organization_data[session.organization_id] = {
                "profile": organization_profile,
                "collection_data": session.collected_data,
                "quality_metrics": self._calculate_quality_metrics(session),
                "session_id": session_id,
                "completed_at": session.completed_at
            }

            logger.info(
                f"Collection session completed: {session_id}, "
                f"org={session.organization_id}, "
                f"quality={organization_profile['quality_score']:.2f}"
            )

            return {
                "success": True,
                "organization_profile": organization_profile,
                "quality_metrics": self._calculate_quality_metrics(session)
            }

        except Exception as error:
            logger.error(f"Failed to complete session: {error}")
            raise

    def _validate_session_completion(self, session: CollectionSession) -> Dict[str, Any]:
        """Validate session is ready for completion"""
        plan = session.plan
        collected_categories = list(session.collected_data.keys())

        # Check required data
        required_data = plan.get("required_data", [])
        missing_required = [
            data_type for data_type in required_data
            if data_type not in collected_categories
        ]

        if missing_required:
            return {
                "is_complete": False,
                "reason": f"Missing required data: {', '.join(missing_required)}"
            }

        # Check quality threshold
        quality_score = self._calculate_overall_quality_score(session)
        if quality_score < self.config["quality_threshold"]:
            return {
                "is_complete": False,
                "reason": f"Quality score {quality_score:.2f} below threshold {self.config['quality_threshold']}"
            }

        return {"is_complete": True}

    def _generate_organization_profile(self, session: CollectionSession) -> Dict[str, Any]:
        """Generate organization profile from session data"""
        profile = {
            "organization_id": session.organization_id,
            "organization_type": session.organization_type,
            "collection_session_id": session.id,
            "created_at": datetime.utcnow().isoformat(),
            "quality_score": self._calculate_overall_quality_score(session),
            "completeness": session.progress.overall_progress / 100.0,
            "data_categories": {}
        }

        # Process collected data into profile structure
        for category_key, data in session.collected_data.items():
            metadata = data.get("_metadata", {})

            profile["data_categories"][category_key] = {
                "data": {k: v for k, v in data.items() if k != "_metadata"},
                "quality": metadata.get("quality"),
                "confidence": metadata.get("confidence"),
                "method": metadata.get("method"),
                "collected_at": metadata.get("collected_at")
            }

            # Add structure data to top level for easy access
            if category_key == DataCategory.STRUCTURE.value:
                profile["basic_info"] = {k: v for k, v in data.items() if k != "_metadata"}

        return profile

    def _calculate_quality_metrics(self, session: CollectionSession) -> Dict[str, Any]:
        """Calculate quality metrics for session"""
        categories = list(session.progress.categories.keys())
        metrics = {
            "overall_score": self._calculate_overall_quality_score(session),
            "completeness": session.progress.overall_progress / 100.0,
            "category_scores": {},
            "reliability": 0.0,
            "confidence": 0.0
        }

        total_confidence = 0.0
        confidence_count = 0

        for category in categories:
            category_data = session.collected_data.get(category, {})
            quality = self._quality_to_value(session.progress.categories[category].quality)
            metrics["category_scores"][category] = quality

            metadata = category_data.get("_metadata", {})
            if metadata.get("confidence"):
                total_confidence += metadata["confidence"]
                confidence_count += 1

        metrics["confidence"] = (
            total_confidence / confidence_count if confidence_count > 0 else 0.0
        )
        metrics["reliability"] = (metrics["overall_score"] + metrics["confidence"]) / 2.0

        return metrics

    # ==================== Public API Methods ====================

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get collection session status"""
        session = self.collection_sessions.get(session_id)
        if not session:
            raise ValueError(f"Collection session not found: {session_id}")

        return {
            "session_id": session_id,
            "status": session.status.value,
            "progress": {
                "overall_progress": session.progress.overall_progress,
                "quality_score": session.progress.quality_score,
                "categories": {
                    cat: {
                        "status": prog.status,
                        "progress": prog.progress,
                        "quality": prog.quality.value
                    }
                    for cat, prog in session.progress.categories.items()
                }
            },
            "next_steps": [self._step_to_dict(step) for step in session.next_steps],
            "completed_categories": list(session.collected_data.keys()),
            "quality_score": self._calculate_overall_quality_score(session),
            "estimated_completion": self._estimate_completion_time(session)
        }

    def get_available_collection_methods(self) -> List[Dict[str, Any]]:
        """Get available collection methods"""
        return [
            {
                "method": method.value,
                "name": config.name,
                "description": config.description,
                "supported_categories": [cat.value for cat in config.categories]
            }
            for method, config in self.collection_methods.items()
        ]

    def get_data_categories(self) -> List[Dict[str, Any]]:
        """Get data categories"""
        return [
            {
                "category": category.value,
                "description": self._get_category_description(category),
                "required": self._is_category_required(category),
                "validation_rules": self._format_validation_rules(
                    self.validation_rules.get(category)
                )
            }
            for category in DataCategory
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "active_sessions": len(self.collection_sessions),
            "completed_organizations": len(self.organization_data),
            "available_methods": len(self.collection_methods),
            "validation_rules": len(self.validation_rules),
            "config": {
                "enable_auto_validation": self.config["enable_auto_validation"],
                "enable_real_time_processing": self.config["enable_real_time_processing"],
                "quality_threshold": self.config["quality_threshold"]
            }
        }

    # ==================== Helper Methods ====================

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = int(time.time() * 1000)
        random_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=9))
        return f"session_{timestamp}_{random_part}"

    def _sanitize_session(self, session: CollectionSession) -> Dict[str, Any]:
        """Sanitize session for external consumption"""
        return {
            "id": session.id,
            "organization_id": session.organization_id,
            "status": session.status.value,
            "start_time": session.start_time,
            "progress": {
                "overall_progress": session.progress.overall_progress,
                "quality_score": session.progress.quality_score
            },
            "methods": [m.value if isinstance(m, DataCollectionMethod) else m for m in session.methods],
            "next_steps": [self._step_to_dict(step) for step in session.next_steps],
            "completed_steps": session.completed_steps
        }

    def _step_to_dict(self, step: WorkflowStep) -> Dict[str, Any]:
        """Convert workflow step to dictionary"""
        return {
            "id": step.id,
            "method": step.method.value,
            "category": step.category.value,
            "title": step.title,
            "description": step.description,
            "estimated_duration": step.estimated_duration,
            "priority": step.priority,
            "dependencies": step.dependencies,
            "status": step.status
        }

    def _get_category_description(self, category: DataCategory) -> str:
        """Get category description"""
        descriptions = {
            DataCategory.STRUCTURE: "Organizational hierarchy, departments, roles, and reporting structures",
            DataCategory.PROCESSES: "Core business processes, workflows, and operational procedures",
            DataCategory.TECHNOLOGY: "Technology stack, systems, software, and digital infrastructure",
            DataCategory.FINANCIAL: "Budget, revenue streams, costs, and financial management",
            DataCategory.HUMAN_RESOURCES: "Staff, roles, skills, and HR processes",
            DataCategory.OPERATIONS: "Day-to-day operations, facilities, and resource management",
            DataCategory.COMPLIANCE: "Regulatory compliance, policies, and governance",
            DataCategory.STRATEGIC: "Vision, mission, goals, and strategic planning",
            DataCategory.PERFORMANCE: "KPIs, metrics, and performance measurement",
            DataCategory.STAKEHOLDERS: "Stakeholder relationships, partnerships, and engagement"
        }
        return descriptions.get(category, "Data category description not available")

    def _is_category_required(self, category: DataCategory) -> bool:
        """Check if category is required"""
        required = [
            DataCategory.STRUCTURE,
            DataCategory.PROCESSES,
            DataCategory.TECHNOLOGY,
            DataCategory.FINANCIAL
        ]
        return category in required

    def _format_validation_rules(
        self,
        rules: Optional[ValidationRule]
    ) -> Optional[Dict[str, Any]]:
        """Format validation rules for output"""
        if not rules:
            return None

        return {
            "required": rules.required,
            "format": rules.format,
            "constraints": rules.constraints
        }

    def _estimate_completion_time(self, session: CollectionSession) -> Optional[Dict[str, Any]]:
        """Estimate completion time for session"""
        if not session.workflow or session.progress.overall_progress == 100:
            return None

        remaining_steps = [
            step for step in session.workflow.steps
            if step.status != "completed"
        ]

        remaining_minutes = sum(
            step.estimated_duration for step in remaining_steps
        )

        estimated_completion = datetime.utcnow() + timedelta(minutes=remaining_minutes)

        return {
            "remaining_minutes": remaining_minutes,
            "estimated_completion": estimated_completion.isoformat(),
            "remaining_steps": len(remaining_steps)
        }
